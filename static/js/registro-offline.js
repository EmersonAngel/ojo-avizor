// Cola de avistamientos sin conexión (RF-23), con fotografías incluidas.
// Usa IndexedDB en vez de localStorage: las fotos son binarias y pueden
// pesar varios MB, y localStorage solo guarda texto con un límite de
// ~5-10MB por origen — insuficiente para fotos de campo.
(function () {
    const NOMBRE_BD = 'ojo_avizor_offline';
    const VERSION_BD = 1;
    const ALMACEN = 'cola_registros';

    function abrirBD() {
        return new Promise((resolve, reject) => {
            const peticion = indexedDB.open(NOMBRE_BD, VERSION_BD);
            peticion.onupgradeneeded = () => {
                peticion.result.createObjectStore(ALMACEN, { keyPath: 'id', autoIncrement: true });
            };
            peticion.onsuccess = () => resolve(peticion.result);
            peticion.onerror = () => reject(peticion.error);
        });
    }

    async function leerCola() {
        const bd = await abrirBD();
        return new Promise((resolve, reject) => {
            const peticion = bd.transaction(ALMACEN, 'readonly').objectStore(ALMACEN).getAll();
            peticion.onsuccess = () => resolve(peticion.result);
            peticion.onerror = () => reject(peticion.error);
        });
    }

    async function actualizarIndicador() {
        const cantidad = (await leerCola()).length;
        document.querySelectorAll('[data-cola-registros]').forEach((elemento) => {
            elemento.textContent = cantidad > 0 ? `${cantidad} en cola` : '';
            elemento.classList.toggle('hidden', cantidad === 0);
        });
    }

    async function encolar(datos, fotos) {
        const bd = await abrirBD();
        await new Promise((resolve, reject) => {
            const tx = bd.transaction(ALMACEN, 'readwrite');
            tx.objectStore(ALMACEN).add({ datos, fotos: fotos || [] });
            tx.oncomplete = resolve;
            tx.onerror = () => reject(tx.error);
        });
        await actualizarIndicador();
    }

    async function eliminarDeCola(id) {
        const bd = await abrirBD();
        return new Promise((resolve, reject) => {
            const tx = bd.transaction(ALMACEN, 'readwrite');
            tx.objectStore(ALMACEN).delete(id);
            tx.oncomplete = resolve;
            tx.onerror = () => reject(tx.error);
        });
    }

    function obtenerCsrfToken() {
        const coincidencia = document.cookie.match(/csrftoken=([^;]+)/);
        return coincidencia ? coincidencia[1] : '';
    }

    async function enviarUno(item) {
        const formData = new FormData();
        Object.entries(item.datos).forEach(([clave, valor]) => formData.append(clave, valor));
        (item.fotos || []).forEach((foto, indice) => {
            formData.append('fotos', foto, foto.name || `foto-${indice}.jpg`);
        });
        const respuesta = await fetch(window.OJO_AVIZOR_URL_REGISTRO_CREAR, {
            method: 'POST',
            headers: { 'X-CSRFToken': obtenerCsrfToken() },
            body: formData,
        });
        // Un envío válido redirige a "mis avistamientos" (302 → 200 tras
        // seguir la redirección). Si el formulario tuviera errores de
        // validación, el servidor vuelve a mostrar la página del
        // formulario con 200 pero sin redirigir: por eso se usa
        // `redirected` como señal de éxito, no el código de estado.
        return respuesta.redirected;
    }

    async function procesarCola() {
        if (!navigator.onLine) return;
        const cola = await leerCola();
        for (const item of cola) {
            try {
                const exito = await enviarUno(item);
                if (exito) await eliminarDeCola(item.id);
            } catch (error) {
                // Sin red de verdad todavía, o error de conexión: se
                // reintenta solo con el próximo evento 'online'.
            }
        }
        await actualizarIndicador();
    }

    window.OjoAvizorOffline = { encolar, procesarCola, actualizarIndicador, leerCola };

    window.addEventListener('online', procesarCola);
    document.addEventListener('DOMContentLoaded', () => {
        actualizarIndicador();
        procesarCola();
    });
})();

// Cola de avistamientos sin conexión (RF-23).
// Alcance acotado: guarda los campos de texto del formulario de registro
// en localStorage cuando no hay conexión y los envía al servidor en
// cuanto se detecta conexión de nuevo. No incluye fotografías: si el
// dispositivo está sin conexión y el observador adjuntó una foto, se le
// pide esperar a tener señal (ver comentario en registro_crear.html).
(function () {
    const CLAVE_COLA = 'ojo_avizor_cola_registros';

    function leerCola() {
        try {
            return JSON.parse(localStorage.getItem(CLAVE_COLA)) || [];
        } catch (error) {
            return [];
        }
    }

    function guardarCola(cola) {
        localStorage.setItem(CLAVE_COLA, JSON.stringify(cola));
        actualizarIndicador();
    }

    function actualizarIndicador() {
        const cantidad = leerCola().length;
        document.querySelectorAll('[data-cola-registros]').forEach((elemento) => {
            elemento.textContent = cantidad > 0 ? `${cantidad} en cola` : '';
            elemento.classList.toggle('hidden', cantidad === 0);
        });
    }

    function obtenerCsrfToken() {
        const coincidencia = document.cookie.match(/csrftoken=([^;]+)/);
        return coincidencia ? coincidencia[1] : '';
    }

    async function enviarUno(datos) {
        const formData = new FormData();
        Object.entries(datos).forEach(([clave, valor]) => formData.append(clave, valor));
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
        const cola = leerCola();
        if (cola.length === 0) return;
        const restantes = [];
        for (const item of cola) {
            try {
                const exito = await enviarUno(item);
                if (!exito) restantes.push(item);
            } catch (error) {
                restantes.push(item);
            }
        }
        guardarCola(restantes);
    }

    function encolar(datos) {
        const cola = leerCola();
        cola.push(datos);
        guardarCola(cola);
    }

    window.OjoAvizorOffline = { encolar, procesarCola, actualizarIndicador, leerCola };

    window.addEventListener('online', procesarCola);
    document.addEventListener('DOMContentLoaded', () => {
        actualizarIndicador();
        procesarCola();
    });
})();

// Componente Alpine para el mapa de distribución de una especie (ficha
// pública de solo lectura y vista previa en el formulario de gestión).
// Colorea países por id sobre el SVG ya incrustado en la página y permite
// acercar/alejar y arrastrar el mapa manipulando el viewBox — sin ninguna
// librería de mapas, para no pesar en celulares de gama baja (RNF-01).
function mapaDistribucion(codigosIniciales) {
    const ZOOM_MAXIMO = 6;
    const ZOOM_MINIMO = 1;

    return {
        codigos: Array.isArray(codigosIniciales) ? codigosIniciales.slice() : [],
        arrastrando: false,
        nivelZoom: 1,
        _vbOriginal: null,
        _vbActual: null,
        _ultimoPuntero: null,

        init() {
            const svg = this.$refs.svg;
            const partes = svg.getAttribute('viewBox').split(' ').map(Number);
            this._vbOriginal = { x: partes[0], y: partes[1], ancho: partes[2], alto: partes[3] };
            this._vbActual = { ...this._vbOriginal };
            this.colorear();
        },

        colorear() {
            const svg = this.$refs.svg;
            svg.querySelectorAll('[data-pais-coloreado]').forEach((el) => {
                el.style.fill = '';
                el.style.opacity = '';
                el.removeAttribute('data-pais-coloreado');
            });
            this.codigos.forEach((codigo) => {
                [codigo, `${codigo}-`, `${codigo}_`].forEach((id) => {
                    const el = svg.querySelector(`#${CSS.escape(id)}`);
                    if (!el) return;
                    el.style.fill = 'var(--azul-medio)';
                    if (id !== codigo) el.style.opacity = '1';
                    el.setAttribute('data-pais-coloreado', '1');
                });
            });
        },

        _aplicarViewBox() {
            const vb = this._vbActual;
            this.$refs.svg.setAttribute('viewBox', `${vb.x} ${vb.y} ${vb.ancho} ${vb.alto}`);
        },

        acercar() {
            this._zoom(1.5);
        },

        alejar() {
            this._zoom(1 / 1.5);
        },

        _zoom(factor) {
            const base = this._vbOriginal;
            const actual = this._vbActual;
            const nuevoAncho = Math.min(base.ancho, Math.max(base.ancho / ZOOM_MAXIMO, actual.ancho / factor));
            const centroX = actual.x + actual.ancho / 2;
            const centroY = actual.y + actual.alto / 2;
            const nuevoAlto = nuevoAncho * (base.alto / base.ancho);
            this._vbActual = {
                x: centroX - nuevoAncho / 2,
                y: centroY - nuevoAlto / 2,
                ancho: nuevoAncho,
                alto: nuevoAlto,
            };
            this.nivelZoom = Math.round((base.ancho / nuevoAncho) * 10) / 10;
            this._aplicarViewBox();
        },

        restablecer() {
            this._vbActual = { ...this._vbOriginal };
            this.nivelZoom = ZOOM_MINIMO;
            this._aplicarViewBox();
        },

        ruedaMouse(evento) {
            evento.preventDefault();
            this._zoom(evento.deltaY < 0 ? 1.2 : 1 / 1.2);
        },

        iniciarArrastre(evento) {
            this.arrastrando = true;
            this._ultimoPuntero = { x: evento.clientX, y: evento.clientY };
            evento.currentTarget.setPointerCapture(evento.pointerId);
        },

        moverArrastre(evento) {
            if (!this.arrastrando) return;
            const contenedor = this.$refs.contenedor;
            const escala = this._vbActual.ancho / contenedor.clientWidth;
            const dx = (evento.clientX - this._ultimoPuntero.x) * escala;
            const dy = (evento.clientY - this._ultimoPuntero.y) * escala;
            this._vbActual.x -= dx;
            this._vbActual.y -= dy;
            this._ultimoPuntero = { x: evento.clientX, y: evento.clientY };
            this._aplicarViewBox();
        },

        terminarArrastre() {
            this.arrastrando = false;
        },
    };
}

// Componente Alpine para marcar el punto exacto de un avistamiento en el
// formulario de registro. Usa Leaflet + OpenStreetMap (gratis, sin API key
// ni facturación, a diferencia de Google Maps) — coherente con RNF-01/08.
// Las coordenadas son opcionales y nunca se publican (RN-06): este mapa
// solo aparece en el formulario de registro, nunca en vistas públicas.
function mapaUbicacion(latInicial, lngInicial) {
    const CENTRO_PIJAO = [4.333, -75.700];
    const ZOOM_MUNICIPIO = 13;
    const ZOOM_PUNTO = 16;

    return {
        lat: latInicial || '',
        lng: lngInicial || '',
        buscandoUbicacion: false,
        // El mapa en sí (Leaflet) ya se sirve local, pero las teselas de
        // OpenStreetMap son imágenes que se piden en vivo a un servidor
        // externo — sin conexión no hay forma de mostrarlas. Se avisa en
        // vez de dejar un mapa en blanco sin explicación; los campos de
        // latitud/longitud siguen funcionando a mano igual.
        sinConexion: !navigator.onLine,
        _mapa: null,
        _marcador: null,

        init() {
            const hayPuntoInicial = this.lat !== '' && this.lng !== '';
            const centro = hayPuntoInicial ? [Number(this.lat), Number(this.lng)] : CENTRO_PIJAO;

            this._mapa = L.map(this.$refs.mapa).setView(centro, hayPuntoInicial ? ZOOM_PUNTO : ZOOM_MUNICIPIO);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>',
            }).addTo(this._mapa);

            if (hayPuntoInicial) {
                this._colocarMarcador(Number(this.lat), Number(this.lng));
            }

            this._mapa.on('click', (evento) => this._colocarMarcador(evento.latlng.lat, evento.latlng.lng));

            // El mapa nace dentro de un contenedor que puede empezar oculto
            // por transiciones/layout; sin este recalculo, Leaflet a veces
            // renderiza solo la esquina superior izquierda de los tiles.
            setTimeout(() => this._mapa.invalidateSize(), 0);
        },

        _colocarMarcador(lat, lng) {
            this.lat = lat.toFixed(6);
            this.lng = lng.toFixed(6);
            if (this._marcador) {
                this._marcador.setLatLng([lat, lng]);
                return;
            }
            this._marcador = L.marker([lat, lng], { draggable: true }).addTo(this._mapa);
            this._marcador.on('dragend', () => {
                const posicion = this._marcador.getLatLng();
                this.lat = posicion.lat.toFixed(6);
                this.lng = posicion.lng.toFixed(6);
            });
        },

        actualizarDesdeCampos() {
            const lat = parseFloat(this.lat);
            const lng = parseFloat(this.lng);
            if (Number.isNaN(lat) || Number.isNaN(lng) || lat < -90 || lat > 90 || lng < -180 || lng > 180) return;
            this._mapa.panTo([lat, lng]);
            this._colocarMarcador(lat, lng);
        },

        usarMiUbicacion() {
            if (!navigator.geolocation) return;
            this.buscandoUbicacion = true;
            navigator.geolocation.getCurrentPosition(
                (posicion) => {
                    this.buscandoUbicacion = false;
                    const { latitude, longitude } = posicion.coords;
                    this._mapa.setView([latitude, longitude], ZOOM_PUNTO);
                    this._colocarMarcador(latitude, longitude);
                },
                () => { this.buscandoUbicacion = false; },
                { enableHighAccuracy: true, timeout: 10000 },
            );
        },

        quitarPunto() {
            this.lat = '';
            this.lng = '';
            if (this._marcador) {
                this._mapa.removeLayer(this._marcador);
                this._marcador = null;
            }
        },
    };
}

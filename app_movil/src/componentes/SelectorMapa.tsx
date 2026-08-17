// El mismo mapa que la web (static/js/mapa-ubicacion.js): Leaflet +
// OpenStreetMap, gratis y sin API key. Aquí se embebe en un WebView porque
// react-native-maps necesitaría un dev client nativo — WebView sí viene
// incluido en la Expo Go de la tienda. Igual que en la web, las teselas
// del mapa necesitan conexión; sin ella se avisa y los campos de
// latitud/longitud siguen funcionando a mano.
import React, { useRef } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';
import { WebView } from 'react-native-webview';

import { useConectividad } from '../contexto/ConectividadContexto';

interface Props {
  latitud: string;
  longitud: string;
  onCambiar: (lat: string, lng: string) => void;
}

const CENTRO_PIJAO = { lat: 4.333, lng: -75.7 };

function generarHtml(latInicial: string, lngInicial: string): string {
  const hayPunto = latInicial !== '' && lngInicial !== '';
  const centro = hayPunto ? { lat: Number(latInicial), lng: Number(lngInicial) } : CENTRO_PIJAO;
  const zoom = hayPunto ? 16 : 13;
  return `
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    html, body, #mapa { height: 100%; margin: 0; padding: 0; }
  </style>
</head>
<body>
  <div id="mapa"></div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const mapa = L.map('mapa').setView([${centro.lat}, ${centro.lng}], ${zoom});
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap',
    }).addTo(mapa);

    let marcador = null;
    function colocar(lat, lng) {
      if (marcador) {
        marcador.setLatLng([lat, lng]);
      } else {
        marcador = L.marker([lat, lng], { draggable: true }).addTo(mapa);
        marcador.on('dragend', () => {
          const p = marcador.getLatLng();
          window.ReactNativeWebView.postMessage(JSON.stringify({ lat: p.lat, lng: p.lng }));
        });
      }
      window.ReactNativeWebView.postMessage(JSON.stringify({ lat, lng }));
    }
    ${hayPunto ? `colocar(${centro.lat}, ${centro.lng});` : ''}
    mapa.on('click', (e) => colocar(e.latlng.lat, e.latlng.lng));
  </script>
</body>
</html>`;
}

export default function SelectorMapa({ latitud, longitud, onCambiar }: Props) {
  const { conectado } = useConectividad();
  const webViewRef = useRef<WebView>(null);

  function alRecibirMensaje(datos: string) {
    try {
      const { lat, lng } = JSON.parse(datos);
      onCambiar(Number(lat).toFixed(6), Number(lng).toFixed(6));
    } catch {
      // mensaje inesperado del WebView, se ignora
    }
  }

  if (!conectado) {
    return (
      <View style={estilos.sinConexion}>
        <Text style={estilos.sinConexionTexto}>
          Sin conexión no se ve el mapa (las imágenes vienen de internet), pero puedes escribir la
          latitud y longitud a mano si las conoces.
        </Text>
      </View>
    );
  }

  return (
    <View style={estilos.contenedor}>
      <WebView
        ref={webViewRef}
        key={`${latitud}-${longitud}`}
        originWhitelist={['*']}
        source={{ html: generarHtml(latitud, longitud) }}
        onMessage={(evento) => alRecibirMensaje(evento.nativeEvent.data)}
        startInLoadingState
        renderLoading={() => (
          <View style={estilos.cargando}>
            <ActivityIndicator />
          </View>
        )}
      />
      {latitud !== '' && (
        <Pressable style={estilos.botonQuitar} onPress={() => onCambiar('', '')}>
          <Text style={estilos.botonQuitarTexto}>Quitar punto</Text>
        </Pressable>
      )}
    </View>
  );
}

const estilos = StyleSheet.create({
  contenedor: { height: 220, borderRadius: 8, overflow: 'hidden', marginBottom: 10 },
  cargando: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  sinConexion: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
    backgroundColor: '#f7f7f7',
  },
  sinConexionTexto: { color: '#666', fontSize: 13 },
  botonQuitar: {
    position: 'absolute',
    bottom: 8,
    right: 8,
    backgroundColor: '#fff',
    borderRadius: 6,
    paddingVertical: 6,
    paddingHorizontal: 10,
    elevation: 2,
  },
  botonQuitarTexto: { color: '#B3261E', fontSize: 12, fontWeight: '600' },
});

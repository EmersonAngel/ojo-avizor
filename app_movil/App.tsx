import { StatusBar } from 'expo-status-bar';
import React from 'react';
import { ActivityIndicator, View } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { ConectividadProveedor } from './src/contexto/ConectividadContexto';
import { SesionProveedor, useSesion } from './src/contexto/SesionContexto';
import Navegador from './src/navegacion/Navegador';
import PantallaLogin from './src/pantallas/PantallaLogin';

function Raiz() {
  const { sesion, cargando } = useSesion();

  if (cargando) {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
        <ActivityIndicator />
      </View>
    );
  }

  return sesion ? <Navegador /> : <PantallaLogin />;
}

export default function App() {
  return (
    <SafeAreaProvider>
      <SesionProveedor>
        <ConectividadProveedor>
          <Raiz />
          <StatusBar style="auto" />
        </ConectividadProveedor>
      </SesionProveedor>
    </SafeAreaProvider>
  );
}

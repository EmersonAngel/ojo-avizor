import { Ionicons } from '@expo/vector-icons';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { DefaultTheme, NavigationContainer } from '@react-navigation/native';
import React from 'react';
import { Pressable, Text, View } from 'react-native';

import { useSesion } from '../contexto/SesionContexto';
import PantallaBorradores from '../pantallas/PantallaBorradores';
import PantallaRegistrarAvistamiento from '../pantallas/PantallaRegistrarAvistamiento';

const Tab = createBottomTabNavigator();

// Racha de días seguidos registrando (fuera del MVP original, pedido
// explícito del 22/08/2026) — mismos dos estados que la web: apagada en
// gris cuando es 0, encendida en el color cálido de marca cuando hay
// racha activa. Sin el pulso animado de la web: aquí es solo un ícono de
// cabecera, no vale la pena una animación por eso.
function TituloConRacha({ seudonimo, racha }: { seudonimo: string; racha: number | null }) {
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
      <Text style={{ fontSize: 17, fontWeight: '600', color: '#111' }}>Hola, {seudonimo}</Text>
      {racha !== null && racha > 0 && (
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 2 }}>
          <Ionicons name="flame" size={16} color="#E8460F" />
          <Text style={{ fontSize: 14, fontWeight: '700', color: '#E8460F' }}>{racha}</Text>
        </View>
      )}
    </View>
  );
}

export default function Navegador() {
  const { sesion, racha, cerrarSesion } = useSesion();

  return (
    // theme fijo en claro, sin importar el modo del sistema del celular:
    // toda la app está pensada en fondo claro (ver PantallaLogin.tsx,
    // PantallaRegistrarAvistamiento.tsx, etc.) — sin esto, la cabecera y la
    // barra de pestañas podían pasar a oscuro solas en un celular con tema
    // oscuro del sistema, mientras el resto de la pantalla se queda claro.
    <NavigationContainer theme={DefaultTheme}>
      <Tab.Navigator
        screenOptions={{
          tabBarActiveTintColor: '#1B2D55',
          tabBarInactiveTintColor: '#999',
          headerRight: () => (
            <Pressable onPress={cerrarSesion} style={{ marginRight: 16 }}>
              <Ionicons name="log-out-outline" size={22} color="#B3261E" />
            </Pressable>
          ),
          headerTitle: () =>
            sesion ? (
              <TituloConRacha seudonimo={sesion.seudonimo} racha={racha} />
            ) : (
              <Text style={{ fontSize: 17, fontWeight: '600', color: '#111' }}>Ojo Avizor</Text>
            ),
        }}
      >
        <Tab.Screen
          name="Registrar"
          component={PantallaRegistrarAvistamiento}
          options={{
            tabBarIcon: ({ color, size }) => <Ionicons name="add-circle-outline" size={size} color={color} />,
          }}
        />
        <Tab.Screen
          name="Borradores"
          component={PantallaBorradores}
          options={{
            tabBarIcon: ({ color, size }) => <Ionicons name="folder-open-outline" size={size} color={color} />,
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}

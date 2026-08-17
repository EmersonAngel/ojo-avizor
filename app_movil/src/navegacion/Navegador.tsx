import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { NavigationContainer } from '@react-navigation/native';
import React from 'react';
import { Pressable, Text } from 'react-native';

import { useSesion } from '../contexto/SesionContexto';
import PantallaBorradores from '../pantallas/PantallaBorradores';
import PantallaRegistrarAvistamiento from '../pantallas/PantallaRegistrarAvistamiento';

const Tab = createBottomTabNavigator();

export default function Navegador() {
  const { sesion, cerrarSesion } = useSesion();

  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={{
          headerRight: () => (
            <Pressable onPress={cerrarSesion} style={{ marginRight: 16 }}>
              <Text style={{ color: '#B3261E' }}>Salir</Text>
            </Pressable>
          ),
          headerTitle: sesion ? `Hola, ${sesion.seudonimo}` : 'Ojo Avizor',
        }}
      >
        <Tab.Screen name="Registrar" component={PantallaRegistrarAvistamiento} />
        <Tab.Screen name="Borradores" component={PantallaBorradores} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}

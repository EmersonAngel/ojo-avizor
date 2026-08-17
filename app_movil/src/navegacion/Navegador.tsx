import { Ionicons } from '@expo/vector-icons';
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
          tabBarActiveTintColor: '#1B2D55',
          tabBarInactiveTintColor: '#999',
          headerRight: () => (
            <Pressable onPress={cerrarSesion} style={{ marginRight: 16 }}>
              <Ionicons name="log-out-outline" size={22} color="#B3261E" />
            </Pressable>
          ),
          headerTitle: sesion ? `Hola, ${sesion.seudonimo}` : 'Ojo Avizor',
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

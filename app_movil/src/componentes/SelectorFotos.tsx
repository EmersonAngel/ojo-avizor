import * as ImagePicker from 'expo-image-picker';
import React from 'react';
import { Alert, Image, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { copiarFotoAPersistente, eliminarFotoPersistente } from '../almacenamiento/fotos';

interface Props {
  fotos: string[];
  onCambiar: (fotos: string[]) => void;
}

export default function SelectorFotos({ fotos, onCambiar }: Props) {
  async function agregarDesdeGaleria() {
    const permiso = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permiso.granted) {
      Alert.alert('Permiso necesario', 'Sin permiso a la galería no se pueden elegir fotos.');
      return;
    }
    const resultado = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      quality: 0.7,
      allowsMultipleSelection: true,
    });
    if (!resultado.canceled) {
      const nuevas = resultado.assets.map((activo) => copiarFotoAPersistente(activo.uri));
      onCambiar([...fotos, ...nuevas]);
    }
  }

  async function agregarDesdeCamara() {
    const permiso = await ImagePicker.requestCameraPermissionsAsync();
    if (!permiso.granted) {
      Alert.alert('Permiso necesario', 'Sin permiso a la cámara no se puede tomar la foto.');
      return;
    }
    const resultado = await ImagePicker.launchCameraAsync({ quality: 0.7 });
    if (!resultado.canceled) {
      const nueva = copiarFotoAPersistente(resultado.assets[0].uri);
      onCambiar([...fotos, nueva]);
    }
  }

  function quitar(uri: string) {
    eliminarFotoPersistente(uri);
    onCambiar(fotos.filter((f) => f !== uri));
  }

  return (
    <View>
      <ScrollView horizontal style={estilos.tira}>
        {fotos.map((uri) => (
          <View key={uri} style={estilos.miniatura}>
            <Image source={{ uri }} style={estilos.imagen} />
            <Pressable style={estilos.quitar} onPress={() => quitar(uri)}>
              <Text style={estilos.quitarTexto}>×</Text>
            </Pressable>
          </View>
        ))}
      </ScrollView>
      <View style={estilos.botones}>
        <Pressable style={estilos.boton} onPress={agregarDesdeCamara}>
          <Text style={estilos.botonTexto}>Tomar foto</Text>
        </Pressable>
        <Pressable style={estilos.boton} onPress={agregarDesdeGaleria}>
          <Text style={estilos.botonTexto}>Elegir de galería</Text>
        </Pressable>
      </View>
    </View>
  );
}

const estilos = StyleSheet.create({
  tira: { marginBottom: 8 },
  miniatura: { marginRight: 8, position: 'relative' },
  imagen: { width: 72, height: 72, borderRadius: 8, backgroundColor: '#eee' },
  quitar: {
    position: 'absolute',
    top: -6,
    right: -6,
    backgroundColor: '#B3261E',
    width: 22,
    height: 22,
    borderRadius: 11,
    alignItems: 'center',
    justifyContent: 'center',
  },
  quitarTexto: { color: '#fff', fontWeight: 'bold', lineHeight: 18 },
  botones: { flexDirection: 'row', gap: 8 },
  boton: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#1B2D55',
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: 'center',
  },
  botonTexto: { color: '#1B2D55', fontWeight: '600' },
});

import { Ionicons } from '@expo/vector-icons';
import React, { useState } from 'react';
import { FlatList, Image, Modal, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import type { EspecieCacheGuardada } from '../almacenamiento/especiesCache';

interface Props {
  especies: EspecieCacheGuardada[];
  especieId: number | null;
  nombreEspecie: string | null;
  onSeleccionar: (especie: EspecieCacheGuardada | null) => void;
}

export default function SelectorEspecie({ especies, especieId, nombreEspecie, onSeleccionar }: Props) {
  const [abierto, setAbierto] = useState(false);
  const [busqueda, setBusqueda] = useState('');

  const filtradas = especies.filter((especie) => {
    const texto = busqueda.trim().toLowerCase();
    if (!texto) return true;
    return (
      especie.nombreCientifico.toLowerCase().includes(texto) ||
      especie.nombresComunes.some((nombre) => nombre.toLowerCase().includes(texto))
    );
  });

  return (
    <View>
      <Pressable style={estilos.campo} onPress={() => setAbierto(true)}>
        <Ionicons name="search-outline" size={18} color="#888" />
        <Text style={[especieId ? estilos.textoElegido : estilos.textoPlaceholder, estilos.textoCampo]}>
          {especieId ? nombreEspecie : 'Toca para elegir una especie (opcional)'}
        </Text>
      </Pressable>

      <Modal visible={abierto} animationType="slide" onRequestClose={() => setAbierto(false)}>
        <View style={estilos.contenedorModal}>
          <TextInput
            style={estilos.buscador}
            placeholder="Buscar por nombre…"
            value={busqueda}
            onChangeText={setBusqueda}
            autoFocus
          />
          <FlatList
            data={filtradas}
            keyExtractor={(item) => String(item.id)}
            ListEmptyComponent={
              <Text style={estilos.vacio}>
                {especies.length === 0
                  ? 'Sin catálogo guardado todavía — inicia sesión con conexión al menos una vez.'
                  : 'Sin resultados.'}
              </Text>
            }
            renderItem={({ item }) => (
              <Pressable
                style={estilos.fila}
                onPress={() => {
                  onSeleccionar(item);
                  setAbierto(false);
                  setBusqueda('');
                }}
              >
                {item.fotoLocal || item.fotoReferencia ? (
                  <Image source={{ uri: item.fotoLocal ?? item.fotoReferencia! }} style={estilos.miniatura} />
                ) : (
                  <View style={[estilos.miniatura, estilos.miniaturaVacia]}>
                    <Ionicons name="image-outline" size={20} color="#aaa" />
                  </View>
                )}
                <View style={estilos.textoFila}>
                  <Text style={estilos.nombreCientifico}>{item.nombreCientifico}</Text>
                  {item.nombresComunes.length > 0 && (
                    <Text style={estilos.nombresComunes}>{item.nombresComunes.join(', ')}</Text>
                  )}
                </View>
              </Pressable>
            )}
          />
          <Pressable
            style={estilos.botonSinIdentificar}
            onPress={() => {
              onSeleccionar(null);
              setAbierto(false);
              setBusqueda('');
            }}
          >
            <Ionicons name="help-circle-outline" size={18} color="#1B2D55" />
            <Text style={estilos.botonSinIdentificarTexto}>No sé identificarla / pedir ayuda</Text>
          </Pressable>
          <Pressable style={estilos.botonCerrar} onPress={() => setAbierto(false)}>
            <Text style={estilos.botonCerrarTexto}>Cerrar</Text>
          </Pressable>
        </View>
      </Modal>
    </View>
  );
}

const estilos = StyleSheet.create({
  campo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  },
  textoCampo: { flex: 1 },
  textoElegido: { fontStyle: 'italic', color: '#111' },
  textoPlaceholder: { color: '#888' },
  contenedorModal: { flex: 1, paddingTop: 60, paddingHorizontal: 16 },
  buscador: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 10,
    marginBottom: 12,
  },
  vacio: { textAlign: 'center', color: '#888', marginTop: 24 },
  fila: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  miniatura: { width: 48, height: 48, borderRadius: 8, backgroundColor: '#eee' },
  miniaturaVacia: { alignItems: 'center', justifyContent: 'center' },
  textoFila: { flex: 1 },
  nombreCientifico: { fontStyle: 'italic', fontSize: 16 },
  nombresComunes: { color: '#666', marginTop: 2 },
  botonSinIdentificar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    paddingVertical: 14,
    marginTop: 8,
  },
  botonSinIdentificarTexto: { color: '#1B2D55', fontWeight: '600' },
  botonCerrar: { paddingVertical: 14, alignItems: 'center' },
  botonCerrarTexto: { color: '#888' },
});

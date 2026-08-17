import React, { useState } from 'react';
import { FlatList, Modal, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import type { EspecieCache } from '../almacenamiento/especiesCache';

interface Props {
  especies: EspecieCache[];
  especieId: number | null;
  nombreEspecie: string | null;
  onSeleccionar: (especie: EspecieCache | null) => void;
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
        <Text style={especieId ? estilos.textoElegido : estilos.textoPlaceholder}>
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
                <Text style={estilos.nombreCientifico}>{item.nombreCientifico}</Text>
                {item.nombresComunes.length > 0 && (
                  <Text style={estilos.nombresComunes}>{item.nombresComunes.join(', ')}</Text>
                )}
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
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  },
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
  fila: { paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: '#eee' },
  nombreCientifico: { fontStyle: 'italic', fontSize: 16 },
  nombresComunes: { color: '#666', marginTop: 2 },
  botonSinIdentificar: { paddingVertical: 14, alignItems: 'center', marginTop: 8 },
  botonSinIdentificarTexto: { color: '#1B2D55', fontWeight: '600' },
  botonCerrar: { paddingVertical: 14, alignItems: 'center' },
  botonCerrarTexto: { color: '#888' },
});

import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import type { RegistroLocal } from '../almacenamiento/registrosLocales';

interface Props {
  registro: RegistroLocal;
  onAbrir?: () => void;
  onEliminar: () => void;
  onReintentar?: () => void;
}

const ETIQUETAS: Record<RegistroLocal['estadoLocal'], string> = {
  BORRADOR: 'Borrador',
  PENDIENTE_ENVIO: 'Esperando conexión…',
  ERROR_ENVIO: 'No se pudo enviar',
};

export default function TarjetaRegistroLocal({ registro, onAbrir, onEliminar, onReintentar }: Props) {
  return (
    <View style={estilos.tarjeta}>
      <Pressable onPress={onAbrir} disabled={!onAbrir} style={estilos.contenido}>
        <Text style={estilos.especie}>
          {registro.nombreEspecie ?? 'Ave sin identificar'}
        </Text>
        <Text style={estilos.lugar}>
          {registro.lugar} · {registro.fechaAvistamiento}
        </Text>
        <Text style={[estilos.estado, registro.estadoLocal === 'ERROR_ENVIO' && estilos.estadoError]}>
          {ETIQUETAS[registro.estadoLocal]}
        </Text>
        {registro.estadoLocal === 'ERROR_ENVIO' && registro.errorDetalle && (
          <Text style={estilos.detalleError}>{registro.errorDetalle}</Text>
        )}
      </Pressable>
      <View style={estilos.acciones}>
        {onReintentar && (
          <Pressable style={estilos.boton} onPress={onReintentar}>
            <Text style={estilos.botonTexto}>Reintentar ahora</Text>
          </Pressable>
        )}
        <Pressable style={[estilos.boton, estilos.botonEliminar]} onPress={onEliminar}>
          <Text style={estilos.botonEliminarTexto}>Eliminar</Text>
        </Pressable>
      </View>
    </View>
  );
}

const estilos = StyleSheet.create({
  tarjeta: {
    borderWidth: 1,
    borderColor: '#e2e2e2',
    borderRadius: 10,
    padding: 12,
    marginBottom: 10,
  },
  contenido: { marginBottom: 8 },
  especie: { fontStyle: 'italic', fontSize: 16, fontWeight: '600' },
  lugar: { color: '#555', marginTop: 2 },
  estado: { marginTop: 6, fontSize: 12, color: '#1B2D55', fontWeight: '600' },
  estadoError: { color: '#B3261E' },
  detalleError: { fontSize: 12, color: '#B3261E', marginTop: 2 },
  acciones: { flexDirection: 'row', gap: 8 },
  boton: {
    borderWidth: 1,
    borderColor: '#1B2D55',
    borderRadius: 8,
    paddingVertical: 6,
    paddingHorizontal: 10,
  },
  botonTexto: { color: '#1B2D55', fontSize: 12, fontWeight: '600' },
  botonEliminar: { borderColor: '#B3261E' },
  botonEliminarTexto: { color: '#B3261E', fontSize: 12, fontWeight: '600' },
});

import DateTimePicker, { type DateTimePickerEvent } from '@react-native-community/datetimepicker';
import React, { useState } from 'react';
import { Platform, Pressable, StyleSheet, Text } from 'react-native';

interface Props {
  valor: string; // 'AAAA-MM-DD' o ''
  onCambiar: (valor: string) => void;
}

function aTexto(fecha: Date): string {
  const anio = fecha.getFullYear();
  const mes = String(fecha.getMonth() + 1).padStart(2, '0');
  const dia = String(fecha.getDate()).padStart(2, '0');
  return `${anio}-${mes}-${dia}`;
}

export default function SelectorFecha({ valor, onCambiar }: Props) {
  const [mostrando, setMostrando] = useState(false);
  const fechaActual = valor ? new Date(`${valor}T00:00:00`) : new Date();

  function alCambiar(evento: DateTimePickerEvent, seleccionada?: Date) {
    if (Platform.OS === 'android') setMostrando(false);
    if (evento.type === 'dismissed') return;
    if (seleccionada) onCambiar(aTexto(seleccionada));
  }

  return (
    <>
      <Pressable style={estilos.campo} onPress={() => setMostrando(true)}>
        <Text style={valor ? estilos.textoElegido : estilos.textoPlaceholder}>
          {valor || 'Toca para elegir la fecha del avistamiento'}
        </Text>
      </Pressable>
      {mostrando && (
        <DateTimePicker
          value={fechaActual}
          mode="date"
          display={Platform.OS === 'ios' ? 'inline' : 'default'}
          maximumDate={new Date()}
          onChange={alCambiar}
        />
      )}
    </>
  );
}

const estilos = StyleSheet.create({
  campo: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
  },
  textoElegido: { color: '#111' },
  textoPlaceholder: { color: '#888' },
});

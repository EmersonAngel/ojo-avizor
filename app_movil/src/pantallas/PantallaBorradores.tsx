import { useFocusEffect, useNavigation } from '@react-navigation/native';
import React, { useCallback, useState } from 'react';
import { Alert, RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native';

import {
  eliminar,
  listarBorradores,
  listarPendientes,
  type RegistroLocal,
} from '../almacenamiento/registrosLocales';
import { eliminarFotoPersistente } from '../almacenamiento/fotos';
import { sincronizarPendientes } from '../sincronizacion/cola';
import TarjetaRegistroLocal from '../componentes/TarjetaRegistroLocal';

export default function PantallaBorradores() {
  const navigation = useNavigation<any>();
  const [borradores, setBorradores] = useState<RegistroLocal[]>([]);
  const [pendientes, setPendientes] = useState<RegistroLocal[]>([]);
  const [refrescando, setRefrescando] = useState(false);

  const cargar = useCallback(async () => {
    const [listaBorradores, listaPendientes] = await Promise.all([listarBorradores(), listarPendientes()]);
    setBorradores(listaBorradores);
    setPendientes(listaPendientes);
  }, []);

  useFocusEffect(
    useCallback(() => {
      cargar();
    }, [cargar]),
  );

  async function refrescar() {
    setRefrescando(true);
    await sincronizarPendientes();
    await cargar();
    setRefrescando(false);
  }

  async function eliminarRegistro(registro: RegistroLocal) {
    Alert.alert('Eliminar', '¿Borrar este registro guardado en el celular?', [
      { text: 'Cancelar', style: 'cancel' },
      {
        text: 'Eliminar',
        style: 'destructive',
        onPress: async () => {
          registro.fotos.forEach(eliminarFotoPersistente);
          await eliminar(registro.id);
          cargar();
        },
      },
    ]);
  }

  return (
    <ScrollView
      style={estilos.contenedor}
      contentContainerStyle={estilos.contenido}
      refreshControl={<RefreshControl refreshing={refrescando} onRefresh={refrescar} />}
    >
      <Text style={estilos.seccion}>Borradores guardados</Text>
      {borradores.length === 0 && <Text style={estilos.vacio}>No tienes borradores.</Text>}
      {borradores.map((registro) => (
        <TarjetaRegistroLocal
          key={registro.id}
          registro={registro}
          onAbrir={() => navigation.navigate('Registrar', { idBorrador: registro.id })}
          onEliminar={() => eliminarRegistro(registro)}
        />
      ))}

      <Text style={estilos.seccion}>Pendientes de sincronizar</Text>
      {pendientes.length === 0 && <Text style={estilos.vacio}>Nada esperando conexión.</Text>}
      {pendientes.map((registro) => (
        <TarjetaRegistroLocal
          key={registro.id}
          registro={registro}
          onEliminar={() => eliminarRegistro(registro)}
          onReintentar={refrescar}
        />
      ))}
    </ScrollView>
  );
}

const estilos = StyleSheet.create({
  contenedor: { flex: 1, backgroundColor: '#fff' },
  contenido: { padding: 16, paddingBottom: 48 },
  seccion: {
    fontSize: 13,
    fontWeight: '700',
    color: '#666',
    textTransform: 'uppercase',
    marginTop: 16,
    marginBottom: 8,
  },
  vacio: { color: '#888', marginBottom: 8 },
});

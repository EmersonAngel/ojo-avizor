import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect, useNavigation } from '@react-navigation/native';
import React, { useCallback, useState } from 'react';
import { ActivityIndicator, Alert, Pressable, RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native';

import {
  eliminar,
  listarBorradores,
  listarPendientes,
  type RegistroLocal,
} from '../almacenamiento/registrosLocales';
import { eliminarFotoPersistente } from '../almacenamiento/fotos';
import { sincronizarPendientes } from '../sincronizacion/cola';
import { useSesion } from '../contexto/SesionContexto';
import TarjetaRegistroLocal from '../componentes/TarjetaRegistroLocal';

export default function PantallaBorradores() {
  const navigation = useNavigation<any>();
  const { sincronizarCatalogo, actualizarRacha } = useSesion();
  const [borradores, setBorradores] = useState<RegistroLocal[]>([]);
  const [pendientes, setPendientes] = useState<RegistroLocal[]>([]);
  const [refrescando, setRefrescando] = useState(false);
  const [actualizandoCatalogo, setActualizandoCatalogo] = useState(false);

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
    await Promise.all([sincronizarPendientes(), sincronizarCatalogo()]);
    await Promise.all([cargar(), actualizarRacha()]);
    setRefrescando(false);
  }

  async function actualizarCatalogo() {
    setActualizandoCatalogo(true);
    const exito = await sincronizarCatalogo();
    setActualizandoCatalogo(false);
    Alert.alert(
      exito ? 'Catálogo actualizado' : 'No se pudo actualizar',
      exito
        ? 'Las fichas de especies del sitio quedaron guardadas en el celular.'
        // No siempre es falta de señal: revisa también que el celular esté en
        // la misma red que el servidor y que la URL en config.ts sea la
        // correcta (ver el mensaje detallado en la consola de Metro).
        : 'No se pudo descargar el catálogo ahora. Puede ser falta de señal, pero también que el celular no alcance el servidor — revisa que estén en la misma red. Se reintenta la próxima vez.',
    );
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
      <Pressable style={estilos.botonCatalogo} onPress={actualizarCatalogo} disabled={actualizandoCatalogo}>
        {actualizandoCatalogo ? (
          <ActivityIndicator size="small" color="#1B2D55" />
        ) : (
          <Ionicons name="download-outline" size={16} color="#1B2D55" />
        )}
        <Text style={estilos.botonCatalogoTexto}>Actualizar catálogo de especies</Text>
      </Pressable>

      <View style={estilos.filaSeccion}>
        <Ionicons name="document-outline" size={16} color="#666" />
        <Text style={estilos.seccion}>Borradores guardados</Text>
      </View>
      {borradores.length === 0 && (
        <View style={estilos.filaVacio}>
          <Ionicons name="checkmark-circle-outline" size={16} color="#999" />
          <Text style={estilos.vacio}>No tienes borradores.</Text>
        </View>
      )}
      {borradores.map((registro) => (
        <TarjetaRegistroLocal
          key={registro.id}
          registro={registro}
          onAbrir={() => navigation.navigate('Registrar', { idBorrador: registro.id })}
          onEliminar={() => eliminarRegistro(registro)}
        />
      ))}

      <View style={estilos.filaSeccion}>
        <Ionicons name="cloud-upload-outline" size={16} color="#666" />
        <Text style={estilos.seccion}>Pendientes de sincronizar</Text>
      </View>
      {pendientes.length === 0 && (
        <View style={estilos.filaVacio}>
          <Ionicons name="checkmark-circle-outline" size={16} color="#999" />
          <Text style={estilos.vacio}>Nada esperando conexión.</Text>
        </View>
      )}
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
  filaSeccion: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 16, marginBottom: 8 },
  seccion: {
    fontSize: 13,
    fontWeight: '700',
    color: '#666',
    textTransform: 'uppercase',
  },
  filaVacio: { flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 8 },
  vacio: { color: '#888' },
  botonCatalogo: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    borderWidth: 1,
    borderColor: '#1B2D55',
    borderRadius: 8,
    paddingVertical: 10,
  },
  botonCatalogoTexto: { color: '#1B2D55', fontWeight: '600', fontSize: 13 },
});

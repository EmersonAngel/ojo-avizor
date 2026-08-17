import { useNavigation, useRoute } from '@react-navigation/native';
import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { listarEspeciesCache, type EspecieCache } from '../almacenamiento/especiesCache';
import {
  guardarBorrador,
  guardarPendiente,
  obtenerPorId,
  eliminar,
  type DatosRegistro,
} from '../almacenamiento/registrosLocales';
import { eliminarFotoPersistente } from '../almacenamiento/fotos';
import { ErrorApi } from '../api/cliente';
import { enviarRegistro } from '../api/registros';
import { useConectividad } from '../contexto/ConectividadContexto';
import SelectorEspecie from '../componentes/SelectorEspecie';
import SelectorFotos from '../componentes/SelectorFotos';

const DATOS_VACIOS: DatosRegistro = {
  especieId: null,
  nombreEspecie: null,
  sinIdentificar: false,
  lugar: '',
  fechaAvistamiento: '',
  latitud: '',
  longitud: '',
  comportamiento: '',
  sustrato: '',
  infoAdicional: '',
  fotos: [],
};

export default function PantallaRegistrarAvistamiento() {
  const navigation = useNavigation<any>();
  const ruta = useRoute<any>();
  const idBorrador: number | undefined = ruta.params?.idBorrador;
  const { conectado } = useConectividad();

  const [especies, setEspecies] = useState<EspecieCache[]>([]);
  const [datos, setDatos] = useState<DatosRegistro>(DATOS_VACIOS);
  const [cargando, setCargando] = useState(Boolean(idBorrador));
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    listarEspeciesCache().then(setEspecies);
  }, []);

  useEffect(() => {
    if (!idBorrador) return;
    obtenerPorId(idBorrador).then((registro) => {
      if (registro) setDatos(registro);
      setCargando(false);
    });
  }, [idBorrador]);

  function actualizar<C extends keyof DatosRegistro>(campo: C, valor: DatosRegistro[C]) {
    setDatos((anterior) => ({ ...anterior, [campo]: valor }));
  }

  function limpiarFormulario() {
    setDatos(DATOS_VACIOS);
  }

  function validarMinimo(): string | null {
    if (!datos.lugar.trim()) return 'Escribe el lugar del avistamiento.';
    if (!/^\d{4}-\d{2}-\d{2}$/.test(datos.fechaAvistamiento)) return 'La fecha debe tener el formato AAAA-MM-DD.';
    return null;
  }

  async function guardarComoBorrador() {
    const problema = validarMinimo();
    if (problema) {
      Alert.alert('Falta información', problema);
      return;
    }
    await guardarBorrador(datos, idBorrador);
    Alert.alert('Guardado', 'Quedó como borrador. Puedes retomarlo desde "Borradores".');
    limpiarFormulario();
    navigation.navigate('Borradores');
  }

  async function enviar() {
    const problema = validarMinimo();
    if (problema) {
      Alert.alert('Falta información', problema);
      return;
    }
    setEnviando(true);
    try {
      if (conectado) {
        const respuesta = await enviarRegistro({
          ...datos,
          id: idBorrador ?? 0,
          estadoLocal: 'PENDIENTE_ENVIO',
          errorDetalle: null,
          fechaCreacion: '',
          fechaActualizacion: '',
        });
        datos.fotos.forEach(eliminarFotoPersistente);
        if (idBorrador) await eliminar(idBorrador);
        Alert.alert('Enviado', `Tu avistamiento quedó ${respuesta.estado.toLowerCase()} de revisión.`);
        limpiarFormulario();
        navigation.navigate('Borradores');
        return;
      }
      throw new Error('sin-conexion');
    } catch (error) {
      if (error instanceof ErrorApi && error.status === 400) {
        Alert.alert('Revisa el formulario', JSON.stringify(error.cuerpo?.errores ?? error.cuerpo));
        return;
      }
      // Sin conexión, o falló la red: se guarda como pendiente y se
      // reintenta solo — igual que la cola de la PWA, pero visible en
      // "Borradores" bajo su propia sección.
      await guardarPendiente(datos, idBorrador);
      Alert.alert(
        'Sin conexión',
        'El registro quedó guardado en el celular y se enviará solo cuando vuelva la señal.',
      );
      limpiarFormulario();
      navigation.navigate('Borradores');
    } finally {
      setEnviando(false);
    }
  }

  if (cargando) {
    return (
      <View style={estilos.cargando}>
        <ActivityIndicator />
      </View>
    );
  }

  return (
    <ScrollView style={estilos.contenedor} contentContainerStyle={estilos.contenido}>
      <Text style={estilos.seccion}>¿Qué viste?</Text>
      <SelectorEspecie
        especies={especies}
        especieId={datos.especieId}
        nombreEspecie={datos.nombreEspecie}
        onSeleccionar={(especie) =>
          setDatos((anterior) => ({
            ...anterior,
            especieId: especie?.id ?? null,
            nombreEspecie: especie?.nombreCientifico ?? null,
            sinIdentificar: especie === null,
          }))
        }
      />

      <Text style={estilos.seccion}>¿Dónde y cuándo?</Text>
      <TextInput
        style={estilos.campo}
        placeholder="Lugar"
        value={datos.lugar}
        onChangeText={(v) => actualizar('lugar', v)}
      />
      <TextInput
        style={estilos.campo}
        placeholder="Fecha (AAAA-MM-DD)"
        value={datos.fechaAvistamiento}
        onChangeText={(v) => actualizar('fechaAvistamiento', v)}
      />
      <View style={estilos.filaDoble}>
        <TextInput
          style={[estilos.campo, estilos.mitad]}
          placeholder="Latitud (opcional)"
          keyboardType="numbers-and-punctuation"
          value={datos.latitud}
          onChangeText={(v) => actualizar('latitud', v)}
        />
        <TextInput
          style={[estilos.campo, estilos.mitad]}
          placeholder="Longitud (opcional)"
          keyboardType="numbers-and-punctuation"
          value={datos.longitud}
          onChangeText={(v) => actualizar('longitud', v)}
        />
      </View>

      <Text style={estilos.seccion}>Detalles (opcional)</Text>
      <TextInput
        style={estilos.campo}
        placeholder="Comportamiento"
        value={datos.comportamiento}
        onChangeText={(v) => actualizar('comportamiento', v)}
        multiline
      />
      <TextInput
        style={estilos.campo}
        placeholder="Sustrato"
        value={datos.sustrato}
        onChangeText={(v) => actualizar('sustrato', v)}
      />
      <TextInput
        style={estilos.campo}
        placeholder="Info adicional"
        value={datos.infoAdicional}
        onChangeText={(v) => actualizar('infoAdicional', v)}
        multiline
      />

      <Text style={estilos.seccion}>Fotografías</Text>
      <SelectorFotos fotos={datos.fotos} onCambiar={(fotos) => actualizar('fotos', fotos)} />

      <View style={estilos.acciones}>
        <Pressable style={estilos.botonSecundario} onPress={guardarComoBorrador} disabled={enviando}>
          <Text style={estilos.botonSecundarioTexto}>Guardar borrador</Text>
        </Pressable>
        <Pressable style={estilos.botonPrimario} onPress={enviar} disabled={enviando}>
          {enviando ? <ActivityIndicator color="#fff" /> : <Text style={estilos.botonPrimarioTexto}>Enviar</Text>}
        </Pressable>
      </View>
    </ScrollView>
  );
}

const estilos = StyleSheet.create({
  cargando: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  contenedor: { flex: 1, backgroundColor: '#fff' },
  contenido: { padding: 16, paddingBottom: 48 },
  seccion: { fontSize: 13, fontWeight: '700', color: '#666', textTransform: 'uppercase', marginTop: 16, marginBottom: 8 },
  campo: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
  },
  filaDoble: { flexDirection: 'row', gap: 10 },
  mitad: { flex: 1 },
  acciones: { flexDirection: 'row', gap: 10, marginTop: 20 },
  botonSecundario: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#1B2D55',
    borderRadius: 8,
    paddingVertical: 14,
    alignItems: 'center',
  },
  botonSecundarioTexto: { color: '#1B2D55', fontWeight: '600' },
  botonPrimario: {
    flex: 1,
    backgroundColor: '#1B2D55',
    borderRadius: 8,
    paddingVertical: 14,
    alignItems: 'center',
  },
  botonPrimarioTexto: { color: '#fff', fontWeight: '600' },
});

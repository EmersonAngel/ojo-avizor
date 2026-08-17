import React, { useState } from 'react';
import {
  ActivityIndicator,
  Image,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { useSesion } from '../contexto/SesionContexto';

export default function PantallaLogin() {
  const { iniciarSesion } = useSesion();
  const [correo, setCorreo] = useState('');
  const [password, setPassword] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function entrar() {
    setError(null);
    setEnviando(true);
    try {
      await iniciarSesion(correo.trim(), password);
    } catch {
      setError('Correo o contraseña incorrectos, o no hay conexión con el servidor.');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={estilos.contenedor}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <Image source={require('../../assets/logo.png')} style={estilos.logo} resizeMode="contain" />
      <Text style={estilos.titulo}>Ojo Avizor</Text>
      <Text style={estilos.subtitulo}>Registro de campo</Text>

      <TextInput
        style={estilos.campo}
        placeholder="Correo"
        autoCapitalize="none"
        keyboardType="email-address"
        value={correo}
        onChangeText={setCorreo}
      />
      <TextInput
        style={estilos.campo}
        placeholder="Contraseña"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />

      {error && <Text style={estilos.error}>{error}</Text>}

      <Pressable style={estilos.boton} onPress={entrar} disabled={enviando}>
        {enviando ? <ActivityIndicator color="#fff" /> : <Text style={estilos.botonTexto}>Entrar</Text>}
      </Pressable>
    </KeyboardAvoidingView>
  );
}

const estilos = StyleSheet.create({
  contenedor: { flex: 1, justifyContent: 'center', padding: 24, backgroundColor: '#fff' },
  logo: { width: 96, height: 96, alignSelf: 'center', marginBottom: 12 },
  titulo: { fontSize: 28, fontWeight: 'bold', color: '#1B2D55', textAlign: 'center' },
  subtitulo: { textAlign: 'center', color: '#666', marginBottom: 32 },
  campo: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  },
  error: { color: '#B3261E', marginBottom: 12, textAlign: 'center' },
  boton: {
    backgroundColor: '#1B2D55',
    borderRadius: 8,
    paddingVertical: 14,
    alignItems: 'center',
  },
  botonTexto: { color: '#fff', fontWeight: '600', fontSize: 16 },
});

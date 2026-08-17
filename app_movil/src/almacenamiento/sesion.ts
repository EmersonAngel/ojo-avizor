// Token de acceso guardado en el almacén seguro del dispositivo (Keychain en
// iOS, Keystore en Android) — nunca en texto plano.
import * as SecureStore from 'expo-secure-store';

const CLAVE_SESION = 'ojo_avizor_sesion';

export interface Sesion {
  token: string;
  seudonimo: string;
  rol: string;
}

export async function guardarSesion(sesion: Sesion): Promise<void> {
  await SecureStore.setItemAsync(CLAVE_SESION, JSON.stringify(sesion));
}

export async function leerSesion(): Promise<Sesion | null> {
  const valor = await SecureStore.getItemAsync(CLAVE_SESION);
  return valor ? (JSON.parse(valor) as Sesion) : null;
}

export async function borrarSesion(): Promise<void> {
  await SecureStore.deleteItemAsync(CLAVE_SESION);
}

import { peticion } from './cliente';
import type { Sesion } from '../almacenamiento/sesion';

export async function iniciarSesion(correo: string, password: string): Promise<Sesion> {
  const cuerpo = await peticion(
    'login/',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ correo, password }),
    },
    false,
  );
  return { token: cuerpo.token, seudonimo: cuerpo.seudonimo, rol: cuerpo.rol };
}

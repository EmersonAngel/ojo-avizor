import { URL_API } from '../config';
import { leerSesion } from '../almacenamiento/sesion';

export class ErrorApi extends Error {
  status: number;
  cuerpo: any;
  constructor(status: number, cuerpo: any) {
    super(`Error de la API (${status})`);
    this.status = status;
    this.cuerpo = cuerpo;
  }
}

export async function peticion(ruta: string, opciones: RequestInit = {}, requiereToken = true): Promise<any> {
  const headers: Record<string, string> = { ...(opciones.headers as Record<string, string>) };
  if (requiereToken) {
    const sesion = await leerSesion();
    if (!sesion) throw new Error('No hay sesión activa.');
    headers.Authorization = `Token ${sesion.token}`;
  }
  const respuesta = await fetch(`${URL_API}${ruta}`, { ...opciones, headers });
  let cuerpo: any = null;
  try {
    cuerpo = await respuesta.json();
  } catch {
    // Respuesta sin cuerpo JSON (poco común en esta API, pero no debe romper).
  }
  if (!respuesta.ok) throw new ErrorApi(respuesta.status, cuerpo);
  return cuerpo;
}

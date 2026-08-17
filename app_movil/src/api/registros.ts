import { URL_API } from '../config';
import { leerSesion } from '../almacenamiento/sesion';
import { ErrorApi, peticion } from './cliente';
import type { RegistroLocal } from '../almacenamiento/registrosLocales';

export interface RespuestaRegistroCreado {
  id: number;
  estado: string;
}

export async function enviarRegistro(registro: RegistroLocal): Promise<RespuestaRegistroCreado> {
  const sesion = await leerSesion();
  if (!sesion) throw new Error('No hay sesión activa.');

  const formData = new FormData();
  if (registro.especieId) formData.append('especie', String(registro.especieId));
  // Django trata un checkbox como marcado si la clave está presente, sin
  // importar el valor — por eso NO se agrega la clave cuando es falso.
  if (registro.sinIdentificar) formData.append('sin_identificar', 'on');
  formData.append('lugar', registro.lugar);
  formData.append('fecha_avistamiento', registro.fechaAvistamiento);
  if (registro.latitud) formData.append('latitud', registro.latitud);
  if (registro.longitud) formData.append('longitud', registro.longitud);
  formData.append('comportamiento', registro.comportamiento);
  formData.append('sustrato', registro.sustrato);
  formData.append('info_adicional', registro.infoAdicional);
  registro.fotos.forEach((uri, indice) => {
    // Forma esperada por el FormData/fetch de React Native para adjuntar
    // un archivo local por su uri — no un objeto File/Blob como en la web.
    formData.append('fotos', { uri, name: `foto-${indice}.jpg`, type: 'image/jpeg' } as unknown as Blob);
  });

  // No se fija Content-Type a mano: fetch necesita calcular el boundary de
  // multipart/form-data él mismo a partir del FormData.
  const respuesta = await fetch(`${URL_API}registros/`, {
    method: 'POST',
    headers: { Authorization: `Token ${sesion.token}` },
    body: formData,
  });
  let cuerpo: any = null;
  try {
    cuerpo = await respuesta.json();
  } catch {
    // sin cuerpo JSON
  }
  if (!respuesta.ok) throw new ErrorApi(respuesta.status, cuerpo);
  return cuerpo;
}

export async function obtenerMisRegistros(): Promise<any[]> {
  const cuerpo = await peticion('registros/mios/');
  return cuerpo.registros;
}

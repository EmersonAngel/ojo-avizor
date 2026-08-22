// Registros guardados en el celular. Dos estados que NO se mezclan:
//
// - BORRADOR: el usuario tocó "Guardar borrador". Nunca se envía solo —
//   solo se sube si el usuario vuelve a abrirlo y toca "Enviar".
// - PENDIENTE_ENVIO: el usuario tocó "Enviar" pero no había conexión (o la
//   red falló). Se reintenta sola cuando vuelve la señal (ver
//   sincronizacion/cola.ts), igual que la cola de la PWA
//   (static/js/registro-offline.js) pero distinguida de un borrador real.
// - ERROR_ENVIO: el servidor devolvió un error de validación (400). No se
//   reintenta en loop — se le muestra al usuario para que corrija.
import { abrirBD } from './db';

export type EstadoLocal = 'BORRADOR' | 'PENDIENTE_ENVIO' | 'ERROR_ENVIO';

export interface DatosRegistro {
  especieId: number | null;
  nombreEspecie: string | null;
  sinIdentificar: boolean;
  lugar: string;
  fechaAvistamiento: string; // YYYY-MM-DD
  latitud: string;
  longitud: string;
  comportamiento: string;
  sustrato: string;
  infoAdicional: string;
  nombreComunPropuesto: string;
  fotos: string[]; // rutas locales persistentes (ver almacenamiento/fotos.ts)
}

export interface RegistroLocal extends DatosRegistro {
  id: number;
  estadoLocal: EstadoLocal;
  errorDetalle: string | null;
  fechaCreacion: string;
  fechaActualizacion: string;
}

interface FilaSQLite {
  id: number;
  estado_local: EstadoLocal;
  especie_id: number | null;
  nombre_especie: string | null;
  sin_identificar: number;
  lugar: string;
  fecha_avistamiento: string;
  latitud: string | null;
  longitud: string | null;
  comportamiento: string | null;
  sustrato: string | null;
  info_adicional: string | null;
  nombre_comun_propuesto: string | null;
  fotos_json: string;
  error_detalle: string | null;
  fecha_creacion: string;
  fecha_actualizacion: string;
}

function filaARegistro(fila: FilaSQLite): RegistroLocal {
  return {
    id: fila.id,
    estadoLocal: fila.estado_local,
    especieId: fila.especie_id,
    nombreEspecie: fila.nombre_especie,
    sinIdentificar: fila.sin_identificar === 1,
    lugar: fila.lugar,
    fechaAvistamiento: fila.fecha_avistamiento,
    latitud: fila.latitud ?? '',
    longitud: fila.longitud ?? '',
    comportamiento: fila.comportamiento ?? '',
    sustrato: fila.sustrato ?? '',
    infoAdicional: fila.info_adicional ?? '',
    nombreComunPropuesto: fila.nombre_comun_propuesto ?? '',
    fotos: JSON.parse(fila.fotos_json),
    errorDetalle: fila.error_detalle,
    fechaCreacion: fila.fecha_creacion,
    fechaActualizacion: fila.fecha_actualizacion,
  };
}

async function guardarConEstado(
  datos: DatosRegistro,
  estadoLocal: EstadoLocal,
  idExistente?: number,
): Promise<number> {
  const bd = await abrirBD();
  const ahora = new Date().toISOString();
  if (idExistente) {
    await bd.runAsync(
      `UPDATE registros_locales SET
        estado_local = ?, especie_id = ?, nombre_especie = ?, sin_identificar = ?,
        lugar = ?, fecha_avistamiento = ?, latitud = ?, longitud = ?,
        comportamiento = ?, sustrato = ?, info_adicional = ?, nombre_comun_propuesto = ?, fotos_json = ?,
        error_detalle = NULL, fecha_actualizacion = ?
       WHERE id = ?`,
      estadoLocal,
      datos.especieId,
      datos.nombreEspecie,
      datos.sinIdentificar ? 1 : 0,
      datos.lugar,
      datos.fechaAvistamiento,
      datos.latitud,
      datos.longitud,
      datos.comportamiento,
      datos.sustrato,
      datos.infoAdicional,
      datos.nombreComunPropuesto,
      JSON.stringify(datos.fotos),
      ahora,
      idExistente,
    );
    return idExistente;
  }
  const resultado = await bd.runAsync(
    `INSERT INTO registros_locales
      (estado_local, especie_id, nombre_especie, sin_identificar, lugar, fecha_avistamiento,
       latitud, longitud, comportamiento, sustrato, info_adicional, nombre_comun_propuesto, fotos_json,
       fecha_creacion, fecha_actualizacion)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    estadoLocal,
    datos.especieId,
    datos.nombreEspecie,
    datos.sinIdentificar ? 1 : 0,
    datos.lugar,
    datos.fechaAvistamiento,
    datos.latitud,
    datos.longitud,
    datos.comportamiento,
    datos.sustrato,
    datos.infoAdicional,
    datos.nombreComunPropuesto,
    JSON.stringify(datos.fotos),
    ahora,
    ahora,
  );
  return resultado.lastInsertRowId;
}

export function guardarBorrador(datos: DatosRegistro, idExistente?: number): Promise<number> {
  return guardarConEstado(datos, 'BORRADOR', idExistente);
}

export function guardarPendiente(datos: DatosRegistro, idExistente?: number): Promise<number> {
  return guardarConEstado(datos, 'PENDIENTE_ENVIO', idExistente);
}

export async function marcarError(id: number, detalle: string): Promise<void> {
  const bd = await abrirBD();
  await bd.runAsync(
    `UPDATE registros_locales SET estado_local = 'ERROR_ENVIO', error_detalle = ?, fecha_actualizacion = ? WHERE id = ?`,
    detalle,
    new Date().toISOString(),
    id,
  );
}

export async function marcarPendienteDeNuevo(id: number): Promise<void> {
  const bd = await abrirBD();
  await bd.runAsync(
    `UPDATE registros_locales SET estado_local = 'PENDIENTE_ENVIO', error_detalle = NULL, fecha_actualizacion = ? WHERE id = ?`,
    new Date().toISOString(),
    id,
  );
}

export async function eliminar(id: number): Promise<void> {
  const bd = await abrirBD();
  await bd.runAsync('DELETE FROM registros_locales WHERE id = ?', id);
}

export async function obtenerPorId(id: number): Promise<RegistroLocal | null> {
  const bd = await abrirBD();
  const fila = await bd.getFirstAsync<FilaSQLite>('SELECT * FROM registros_locales WHERE id = ?', id);
  return fila ? filaARegistro(fila) : null;
}

export async function listarBorradores(): Promise<RegistroLocal[]> {
  const bd = await abrirBD();
  const filas = await bd.getAllAsync<FilaSQLite>(
    `SELECT * FROM registros_locales WHERE estado_local = 'BORRADOR' ORDER BY fecha_actualizacion DESC`,
  );
  return filas.map(filaARegistro);
}

export async function listarPendientes(): Promise<RegistroLocal[]> {
  const bd = await abrirBD();
  const filas = await bd.getAllAsync<FilaSQLite>(
    `SELECT * FROM registros_locales WHERE estado_local IN ('PENDIENTE_ENVIO', 'ERROR_ENVIO') ORDER BY fecha_creacion ASC`,
  );
  return filas.map(filaARegistro);
}

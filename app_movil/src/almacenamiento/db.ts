// Base de datos local (SQLite) — el equivalente nativo del IndexedDB que ya
// usa la PWA (static/js/registro-offline.js), pero con una distinción que
// esa versión no tiene: "borrador" (guardado a mano, nunca se envía solo)
// separado de "pendiente de envío" (cola automática por falta de conexión).
import * as SQLite from 'expo-sqlite';

let bdPromesa: Promise<SQLite.SQLiteDatabase> | null = null;

export function abrirBD(): Promise<SQLite.SQLiteDatabase> {
  if (!bdPromesa) {
    bdPromesa = SQLite.openDatabaseAsync('ojo_avizor_movil.db').then(async (bd) => {
      await bd.execAsync(`
        CREATE TABLE IF NOT EXISTS registros_locales (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          estado_local TEXT NOT NULL,
          especie_id INTEGER,
          nombre_especie TEXT,
          sin_identificar INTEGER NOT NULL DEFAULT 0,
          lugar TEXT NOT NULL,
          fecha_avistamiento TEXT NOT NULL,
          latitud TEXT,
          longitud TEXT,
          comportamiento TEXT,
          sustrato TEXT,
          info_adicional TEXT,
          fotos_json TEXT NOT NULL DEFAULT '[]',
          error_detalle TEXT,
          fecha_creacion TEXT NOT NULL,
          fecha_actualizacion TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS especies_cache (
          id INTEGER PRIMARY KEY,
          nombre_cientifico TEXT NOT NULL,
          nombres_comunes_json TEXT NOT NULL DEFAULT '[]'
        );
      `);
      return bd;
    });
  }
  return bdPromesa;
}

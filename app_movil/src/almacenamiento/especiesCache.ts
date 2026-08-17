// Copia local del catálogo de especies (fichas ya creadas en el sitio web),
// para que el selector del formulario funcione, con foto incluida, aunque
// el observador ya esté sin señal en el campo. Se llena al iniciar sesión
// con conexión (ver contexto/SesionContexto.tsx).
import { Directory, File, Paths } from 'expo-file-system';

import { abrirBD } from './db';

export interface EspecieCache {
  id: number;
  nombreCientifico: string;
  nombresComunes: string[];
  fotoReferencia: string | null; // URL remota, tal como la da la API
}

export interface EspecieCacheGuardada extends EspecieCache {
  fotoLocal: string | null; // ruta local ya descargada, si se pudo
}

function carpetaEspecies(): Directory {
  const carpeta = new Directory(Paths.document, 'especies_cache');
  if (!carpeta.exists) carpeta.create({ intermediates: true, idempotent: true });
  return carpeta;
}

async function descargarFoto(url: string): Promise<string | null> {
  try {
    const archivo = await File.downloadFileAsync(url, carpetaEspecies());
    return archivo.uri;
  } catch {
    // Sin conexión suficiente para bajar la imagen: se sigue usando la URL
    // remota cuando haya señal, no es un error fatal para el catálogo.
    return null;
  }
}

export async function guardarEspeciesEnCache(especies: EspecieCache[]): Promise<void> {
  const bd = await abrirBD();
  await bd.execAsync('DELETE FROM especies_cache');
  for (const especie of especies) {
    const fotoLocal = especie.fotoReferencia ? await descargarFoto(especie.fotoReferencia) : null;
    await bd.runAsync(
      `INSERT INTO especies_cache
        (id, nombre_cientifico, nombres_comunes_json, foto_referencia, foto_local)
       VALUES (?, ?, ?, ?, ?)`,
      especie.id,
      especie.nombreCientifico,
      JSON.stringify(especie.nombresComunes),
      especie.fotoReferencia,
      fotoLocal,
    );
  }
}

export async function listarEspeciesCache(): Promise<EspecieCacheGuardada[]> {
  const bd = await abrirBD();
  const filas = await bd.getAllAsync<{
    id: number;
    nombre_cientifico: string;
    nombres_comunes_json: string;
    foto_referencia: string | null;
    foto_local: string | null;
  }>('SELECT id, nombre_cientifico, nombres_comunes_json, foto_referencia, foto_local FROM especies_cache ORDER BY nombre_cientifico');
  return filas.map((fila) => ({
    id: fila.id,
    nombreCientifico: fila.nombre_cientifico,
    nombresComunes: JSON.parse(fila.nombres_comunes_json),
    fotoReferencia: fila.foto_referencia,
    fotoLocal: fila.foto_local,
  }));
}

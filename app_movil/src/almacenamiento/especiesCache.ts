// Copia local del catálogo de especies, para que el selector del formulario
// funcione aunque el observador ya esté sin señal en el campo (se llena una
// sola vez, al iniciar sesión con conexión).
import { abrirBD } from './db';

export interface EspecieCache {
  id: number;
  nombreCientifico: string;
  nombresComunes: string[];
}

export async function guardarEspeciesEnCache(especies: EspecieCache[]): Promise<void> {
  const bd = await abrirBD();
  await bd.execAsync('DELETE FROM especies_cache');
  for (const especie of especies) {
    await bd.runAsync(
      'INSERT INTO especies_cache (id, nombre_cientifico, nombres_comunes_json) VALUES (?, ?, ?)',
      especie.id,
      especie.nombreCientifico,
      JSON.stringify(especie.nombresComunes),
    );
  }
}

export async function listarEspeciesCache(): Promise<EspecieCache[]> {
  const bd = await abrirBD();
  const filas = await bd.getAllAsync<{ id: number; nombre_cientifico: string; nombres_comunes_json: string }>(
    'SELECT id, nombre_cientifico, nombres_comunes_json FROM especies_cache ORDER BY nombre_cientifico',
  );
  return filas.map((fila) => ({
    id: fila.id,
    nombreCientifico: fila.nombre_cientifico,
    nombresComunes: JSON.parse(fila.nombres_comunes_json),
  }));
}

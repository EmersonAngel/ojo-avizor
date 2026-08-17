import { peticion } from './cliente';
import type { EspecieCache } from '../almacenamiento/especiesCache';

export async function obtenerEspecies(): Promise<EspecieCache[]> {
  const cuerpo = await peticion('especies/');
  return cuerpo.especies.map((especie: any) => ({
    id: especie.id,
    nombreCientifico: especie.nombre_cientifico,
    nombresComunes: especie.nombres_comunes,
  }));
}

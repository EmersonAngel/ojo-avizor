// Copia las fotos elegidas a una carpeta persistente de la app (sobrevive a
// que el SO limpie cachés) — necesario porque un borrador puede quedar
// guardado en el celular por días antes de enviarse.
import { Directory, File, Paths } from 'expo-file-system';

const NOMBRE_CARPETA = 'avistamientos';

function carpetaAvistamientos(): Directory {
  const carpeta = new Directory(Paths.document, NOMBRE_CARPETA);
  if (!carpeta.exists) {
    carpeta.create({ intermediates: true, idempotent: true });
  }
  return carpeta;
}

export function copiarFotoAPersistente(uriOrigen: string): string {
  const carpeta = carpetaAvistamientos();
  const nombreArchivo = `${Date.now()}-${Math.round(Math.random() * 1e6)}.jpg`;
  const origen = new File(uriOrigen);
  origen.copy(new Directory(carpeta.uri));
  const destino = new File(carpeta, origen.name);
  // File.copy conserva el nombre original; lo renombramos para evitar
  // colisiones entre fotos de distintos registros con el mismo nombre.
  const destinoFinal = new File(carpeta, nombreArchivo);
  destino.move(destinoFinal);
  return destinoFinal.uri;
}

export function eliminarFotoPersistente(uri: string): void {
  try {
    const archivo = new File(uri);
    if (archivo.exists) archivo.delete();
  } catch {
    // Si ya no existe o el uri es inválido, no hay nada que limpiar.
  }
}

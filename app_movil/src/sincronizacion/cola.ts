// Motor de sincronización de "Pendientes de envío" — equivalente nativo de
// procesarCola() en static/js/registro-offline.js, disparado por
// ConectividadContexto cuando vuelve la señal (o a mano desde la pantalla
// de Borradores). Los BORRADORES nunca pasan por aquí: solo se envían si
// el usuario los reabre y toca "Enviar" explícitamente.
import { ErrorApi } from '../api/cliente';
import { enviarRegistro } from '../api/registros';
import { eliminarFotoPersistente } from '../almacenamiento/fotos';
import { eliminar, listarPendientes, marcarError } from '../almacenamiento/registrosLocales';

let sincronizando = false;

export async function sincronizarPendientes(): Promise<void> {
  if (sincronizando) return; // evita carreras si se dispara dos veces seguidas
  sincronizando = true;
  try {
    const pendientes = await listarPendientes();
    for (const registro of pendientes) {
      try {
        await enviarRegistro(registro);
        registro.fotos.forEach(eliminarFotoPersistente);
        await eliminar(registro.id);
      } catch (error) {
        if (error instanceof ErrorApi && error.status === 400) {
          const detalle = error.cuerpo?.errores
            ? JSON.stringify(error.cuerpo.errores)
            : 'El servidor rechazó el registro.';
          await marcarError(registro.id, detalle);
        }
        // Errores de red (sin ErrorApi, o status distinto de 400): se deja
        // como PENDIENTE_ENVIO, se reintenta en la próxima sincronización.
      }
    }
  } finally {
    sincronizando = false;
  }
}

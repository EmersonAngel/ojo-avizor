import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';

import { iniciarSesion as iniciarSesionApi } from '../api/auth';
import { obtenerEspecies } from '../api/especies';
import { guardarEspeciesEnCache } from '../almacenamiento/especiesCache';
import { borrarSesion, guardarSesion, leerSesion, type Sesion } from '../almacenamiento/sesion';

interface SesionContextoValor {
  sesion: Sesion | null;
  cargando: boolean;
  iniciarSesion: (correo: string, password: string) => Promise<void>;
  cerrarSesion: () => Promise<void>;
  sincronizarCatalogo: () => Promise<boolean>;
}

const SesionContexto = createContext<SesionContextoValor | undefined>(undefined);

export function SesionProveedor({ children }: { children: React.ReactNode }) {
  const [sesion, setSesion] = useState<Sesion | null>(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    leerSesion()
      .then(setSesion)
      .finally(() => setCargando(false));
  }, []);

  // Descarga las fichas de especies que ya existen en el sitio (nombre,
  // nombres comunes y foto) para que el selector del formulario funcione
  // sin conexión. Devuelve si tuvo éxito, para poder avisar al usuario
  // cuando se dispara a mano (ver PantallaBorradores) en vez de fallar
  // en silencio como en el inicio de sesión.
  const sincronizarCatalogo = useCallback(async (): Promise<boolean> => {
    try {
      const especies = await obtenerEspecies();
      await guardarEspeciesEnCache(especies);
      return true;
    } catch {
      return false;
    }
  }, []);

  const iniciarSesion = useCallback(
    async (correo: string, password: string) => {
      const nuevaSesion = await iniciarSesionApi(correo, password);
      await guardarSesion(nuevaSesion);
      setSesion(nuevaSesion);
      // No bloquea el inicio de sesión si falla: el selector simplemente
      // queda vacío hasta la próxima sincronización con conexión.
      await sincronizarCatalogo();
    },
    [sincronizarCatalogo],
  );

  const cerrarSesion = useCallback(async () => {
    await borrarSesion();
    setSesion(null);
  }, []);

  return (
    <SesionContexto.Provider value={{ sesion, cargando, iniciarSesion, cerrarSesion, sincronizarCatalogo }}>
      {children}
    </SesionContexto.Provider>
  );
}

export function useSesion(): SesionContextoValor {
  const contexto = useContext(SesionContexto);
  if (!contexto) throw new Error('useSesion debe usarse dentro de SesionProveedor');
  return contexto;
}

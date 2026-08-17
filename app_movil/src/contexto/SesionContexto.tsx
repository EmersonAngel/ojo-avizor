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

  const iniciarSesion = useCallback(async (correo: string, password: string) => {
    const nuevaSesion = await iniciarSesionApi(correo, password);
    await guardarSesion(nuevaSesion);
    setSesion(nuevaSesion);
    // Cachea el catálogo para que el selector funcione ya sin señal en
    // campo. Si falla (poco probable justo tras loguearse con éxito), no
    // bloquea el inicio de sesión — el selector simplemente queda vacío
    // hasta la próxima vez que haya conexión.
    try {
      const especies = await obtenerEspecies();
      await guardarEspeciesEnCache(especies);
    } catch {
      // silencioso a propósito, ver comentario arriba
    }
  }, []);

  const cerrarSesion = useCallback(async () => {
    await borrarSesion();
    setSesion(null);
  }, []);

  return (
    <SesionContexto.Provider value={{ sesion, cargando, iniciarSesion, cerrarSesion }}>
      {children}
    </SesionContexto.Provider>
  );
}

export function useSesion(): SesionContextoValor {
  const contexto = useContext(SesionContexto);
  if (!contexto) throw new Error('useSesion debe usarse dentro de SesionProveedor');
  return contexto;
}

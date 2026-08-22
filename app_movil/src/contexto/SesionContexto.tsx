import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';

import { iniciarSesion as iniciarSesionApi } from '../api/auth';
import { obtenerEspecies } from '../api/especies';
import { obtenerRacha } from '../api/registros';
import { guardarEspeciesEnCache } from '../almacenamiento/especiesCache';
import { borrarSesion, guardarSesion, leerSesion, type Sesion } from '../almacenamiento/sesion';

interface SesionContextoValor {
  sesion: Sesion | null;
  cargando: boolean;
  racha: number | null;
  iniciarSesion: (correo: string, password: string) => Promise<void>;
  cerrarSesion: () => Promise<void>;
  sincronizarCatalogo: () => Promise<boolean>;
  actualizarRacha: () => Promise<void>;
}

const SesionContexto = createContext<SesionContextoValor | undefined>(undefined);

export function SesionProveedor({ children }: { children: React.ReactNode }) {
  const [sesion, setSesion] = useState<Sesion | null>(null);
  const [cargando, setCargando] = useState(true);
  const [racha, setRacha] = useState<number | null>(null);

  // Sin bloquear la carga de la sesión si falla (sin conexión, por
  // ejemplo): la racha simplemente no se muestra hasta que se pueda pedir.
  const actualizarRacha = useCallback(async () => {
    try {
      setRacha(await obtenerRacha());
    } catch {
      // se queda con el último valor conocido, o null si nunca se pudo pedir
    }
  }, []);

  useEffect(() => {
    leerSesion()
      .then((valor) => {
        setSesion(valor);
        if (valor) actualizarRacha();
      })
      .finally(() => setCargando(false));
  }, [actualizarRacha]);

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
      await actualizarRacha();
    },
    [sincronizarCatalogo, actualizarRacha],
  );

  const cerrarSesion = useCallback(async () => {
    await borrarSesion();
    setSesion(null);
    setRacha(null);
  }, []);

  return (
    <SesionContexto.Provider
      value={{ sesion, cargando, racha, iniciarSesion, cerrarSesion, sincronizarCatalogo, actualizarRacha }}
    >
      {children}
    </SesionContexto.Provider>
  );
}

export function useSesion(): SesionContextoValor {
  const contexto = useContext(SesionContexto);
  if (!contexto) throw new Error('useSesion debe usarse dentro de SesionProveedor');
  return contexto;
}

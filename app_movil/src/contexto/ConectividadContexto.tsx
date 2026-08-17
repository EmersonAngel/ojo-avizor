import NetInfo from '@react-native-community/netinfo';
import React, { createContext, useContext, useEffect, useState } from 'react';

import { sincronizarPendientes } from '../sincronizacion/cola';

interface ConectividadContextoValor {
  conectado: boolean;
}

const ConectividadContexto = createContext<ConectividadContextoValor>({ conectado: true });

export function ConectividadProveedor({ children }: { children: React.ReactNode }) {
  const [conectado, setConectado] = useState(true);

  useEffect(() => {
    // Equivalente nativo de window.addEventListener('online', procesarCola)
    // en static/js/registro-offline.js: en cuanto detecta conexión real
    // (no solo "hay wifi", sino que efectivamente hay internet), intenta
    // subir todo lo que quedó en PENDIENTE_ENVIO.
    const cancelarSuscripcion = NetInfo.addEventListener((estado) => {
      const hayConexion = Boolean(estado.isConnected && estado.isInternetReachable !== false);
      setConectado(hayConexion);
      if (hayConexion) sincronizarPendientes();
    });
    return cancelarSuscripcion;
  }, []);

  return <ConectividadContexto.Provider value={{ conectado }}>{children}</ConectividadContexto.Provider>;
}

export function useConectividad(): ConectividadContextoValor {
  return useContext(ConectividadContexto);
}

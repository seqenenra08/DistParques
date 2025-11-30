/**
 * Hook personalizado para manejar Socket.IO en componentes React
 */

import { useEffect, useState } from 'react';
import socketService from '../services/socketService';

export function useSocket() {
  const [connected, setConnected] = useState(false);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    // Conectar al montar el componente
    const socketInstance = socketService.connect();
    setSocket(socketInstance);

    // Escuchar eventos de conexión
    socketInstance.on('connect', () => {
      setConnected(true);
      
      // ✨ Intentar reconexión automática al conectar
      if (typeof window !== 'undefined') {
        const savedRoomCode = sessionStorage.getItem('room_code');
        const savedPlayerId = sessionStorage.getItem('player_id');
        
        if (savedRoomCode) {
          console.log('[RECONNECT] Intentando reconectar a sala:', savedRoomCode);
          setTimeout(() => {
            socketInstance.emit('reconnect_to_game', {
              roomCode: savedRoomCode,
              playerId: savedPlayerId || socketInstance.id
            });
          }, 500); // Pequeño delay para asegurar que el servidor esté listo
        }
      }
    });

    socketInstance.on('disconnect', () => {
      setConnected(false);
    });

    // Cleanup al desmontar
    return () => {
      socketService.disconnect();
    };
  }, []);

  return {
    socket,
    connected,
    emit: (event, data) => socketService.emit(event, data),
    on: (event, callback) => socketService.on(event, callback),
    off: (event, callback) => socketService.off(event, callback)
  };
}

/**
 * Servicio de Socket.IO para la comunicación con el servidor
 */

import { io } from 'socket.io-client';

class SocketService {
  constructor() {
    this.socket = null;
    this.connected = false;
  }

  /**
   * Conecta al servidor de Socket.IO
   */
  connect() {
    const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:5000';
    
    this.socket = io(SOCKET_URL, {
      transports: ['websocket'],
      autoConnect: true
    });

    this.socket.on('connect', () => {
      console.log('Conectado al servidor:', this.socket.id);
      this.connected = true;
    });

    this.socket.on('disconnect', () => {
      console.log('Desconectado del servidor');
      this.connected = false;
    });

    this.socket.on('connect_error', (error) => {
      console.error('Error de conexión:', error);
    });

    return this.socket;
  }

  /**
   * Desconecta del servidor
   */
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connected = false;
    }
  }

  /**
   * Emite un evento al servidor
   */
  emit(event, data) {
    if (this.socket) {
      this.socket.emit(event, data);
    } else {
      console.error('Socket no conectado');
    }
  }

  /**
   * Escucha un evento del servidor
   */
  on(event, callback) {
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  /**
   * Deja de escuchar un evento
   */
  off(event, callback) {
    if (this.socket) {
      this.socket.off(event, callback);
    }
  }

  /**
   * Obtiene el socket actual
   */
  getSocket() {
    return this.socket;
  }

  /**
   * Verifica si está conectado
   */
  isConnected() {
    return this.connected && this.socket?.connected;
  }
}

// Exportar una instancia única (Singleton)
const socketService = new SocketService();
export default socketService;

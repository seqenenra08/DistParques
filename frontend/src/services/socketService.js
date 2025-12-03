/**
 * Servicio de WebSocket para la comunicación con el servidor
 * Usa WebSocket nativo en lugar de Socket.IO
 */

class WebSocketService {
  constructor() {
    this.ws = null;
    this.connected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
    this.messageQueue = [];
    this.eventHandlers = new Map();
    this.messageIdCounter = 0;
  }

  /**
   * Conecta al servidor WebSocket
   */
  connect() {
    const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:5555';
    
    try {
      this.ws = new WebSocket(WS_URL);

      this.ws.onopen = () => {
        console.log('✅ Conectado al servidor WebSocket');
        this.connected = true;
        this.reconnectAttempts = 0;
        
        // Enviar mensajes en cola
        while (this.messageQueue.length > 0) {
          const msg = this.messageQueue.shift();
          this.send(msg);
        }
        
        // Emitir evento de conexión
        this.trigger('connect', { connected: true });
        this.trigger('connection_success', { message: 'Conectado exitosamente' });
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('[WS] Mensaje recibido:', data);
          
          // Mapear tipos de mensaje del backend al frontend
          const tipo = data.tipo || data.type;
          
          if (tipo) {
            // Transformar datos del backend al formato del frontend
            const transformedData = this.transformBackendData(tipo, data);
            this.trigger(this.mapBackendToFrontend(tipo), transformedData);
          }
        } catch (error) {
          console.error('[WS] Error al parsear mensaje:', error);
        }
      };

      this.ws.onclose = (event) => {
        console.log('❌ Desconectado del servidor:', event.reason);
        this.connected = false;
        this.trigger('disconnect', { reason: event.reason });
        
        // Intentar reconectar
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          console.log(`🔄 Reintentando conexión (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
          setTimeout(() => this.connect(), this.reconnectDelay);
        }
      };

      this.ws.onerror = (error) => {
        console.error('❌ Error de WebSocket:', error);
        this.trigger('connect_error', { error });
      };

      return this.ws;
    } catch (error) {
      console.error('❌ Error al crear WebSocket:', error);
      return null;
    }
  }

  /**
   * Mapea tipos de mensaje del backend al formato esperado por el frontend
   */
  mapBackendToFrontend(backendType) {
    const typeMap = {
      // Conexión
      'CONECTADO': 'connection_success',
      
      // Salas
      'SALA_CREADA': 'SALA_CREADA',
      'UNIDO_A_SALA': 'UNIDO_A_SALA',
      'JUGADOR_UNIDO': 'JUGADOR_UNIDO',
      'JUGADOR_DESCONECTADO': 'player_left_room',
      'COLORES_DISPONIBLES': 'COLORES_DISPONIBLES',
      
      // Partida
      'PARTIDA_INICIADA': 'PARTIDA_INICIADA',
      'DADOS_LANZADOS': 'dice_rolled',
      'RESULTADO_MOVIMIENTO': 'piece_moved',
      'ESTADO_ACTUALIZADO': 'game_state_updated',
      
      // Protocolo completo servidor.py
      'DADO_INICIO': 'DADO_INICIO',
      'DADO_INICIO_RESULT': 'DADO_INICIO_RESULT',
      'TURNO_DETERMINADO': 'TURNO_DETERMINADO',
      'DICE_RESULT': 'DICE_RESULT',
      'MOVE_RESULT': 'MOVE_RESULT',
      'FICHAS_INFO': 'FICHAS_INFO',
      'UPDATE': 'UPDATE',
      
      // Eventos de desempate y reinicio
      'tiebreaker_started': 'tiebreaker_started',
      'reroll_started': 'reroll_started',
      'COMENZAR_JUEGO_CONFIRMADO': 'COMENZAR_JUEGO_CONFIRMADO',
      
      // Errores
      'ERROR': 'ERROR'
    };
    
    return typeMap[backendType] || backendType.toLowerCase();
  }

  /**
   * Mapea colores del backend (español) al frontend (inglés)
   */
  mapColorBackendToFrontend(color) {
    const colorMap = {
      'rojo': 'red',
      'azul': 'blue',
      'verde': 'green',
      'amarillo': 'yellow'
    };
    return colorMap[color] || color;
  }

  /**
   * Transforma los datos del backend al formato esperado por el frontend
   */
  transformBackendData(tipo, data) {
    // Transformar según el tipo de mensaje
    if (tipo === 'SALA_CREADA') {
      return {
        ...data,
        success: data.exito,
        room_code: data.codigo_sala,
        room_state: data.estado_sala,
        available_colors: data.colores_disponibles
      };
    }
    
    if (tipo === 'UNIDO_A_SALA') {
      return {
        ...data,
        success: data.exito,
        room_code: data.codigo_sala,
        room_state: data.estado_sala,
        is_host: data.es_host,
        available_colors: data.colores_disponibles
      };
    }
    
    if (tipo === 'PARTIDA_INICIADA') {
      const estado = data.estado || data.estado_juego;
      
      // Transformar el estado del backend al formato del frontend
      const gameState = estado ? {
        ...estado,
        // Mapear campos del backend al frontend
        current_player: estado.jugador_actual,
        players: estado.jugadores ? estado.jugadores.map(j => ({
          player_id: j.id,
          name: j.nombre,
          color: this.mapColorBackendToFrontend(j.color),
          pieces: j.fichas ? j.fichas.map(f => {
            // Convertir estado a position según las reglas del juego
            let position;
            if (f.estado === 'carcel') {
              position = -1; // Fichas en cárcel tienen position -1
            } else if (f.estado === 'meta') {
              position = 'goal'; // Fichas en meta
            } else {
              position = f.posicion; // Posición normal en el tablero
            }
            
            return {
              piece_id: f.id,
              position: position,
              state: f.estado, // carcel, jugando, meta
              corridor_position: f.posicion_pasillo,
              squares_traveled: f.casillas_recorridas,
              is_in_goal: f.estado === 'meta'
            };
          }) : [],
          is_turn: j.es_su_turno,
          start_position: j.casilla_salida,
          prison_attempts: j.intentos_carcel,
          has_rolled: j.ya_lanzo_dados,
          can_roll_again: j.puede_lanzar_de_nuevo
        })) : [],
        board: estado.tablero,
        winner: estado.ganador,
        waiting_for_start_dice: estado.esperando_dados_inicio,
        start_dice_results: estado.dados_inicio
      } : null;
      
      return {
        ...data,
        success: true, // La partida iniciada siempre es exitosa
        game_state: gameState
      };
    }
    
    if (tipo === 'DADOS_LANZADOS') {
      const estado = data.estado;
      
      // Transformar el estado del juego si existe
      const gameState = estado ? {
        ...estado,
        current_player: estado.jugador_actual,
        players: estado.jugadores ? estado.jugadores.map(j => ({
          player_id: j.id,
          name: j.nombre,
          color: this.mapColorBackendToFrontend(j.color),
          pieces: j.fichas ? j.fichas.map(f => {
            let position;
            if (f.estado === 'carcel') {
              position = -1;
            } else if (f.estado === 'meta') {
              position = 'goal';
            } else {
              position = f.posicion;
            }
            
            return {
              piece_id: f.id,
              position: position,
              state: f.estado,
              corridor_position: f.posicion_pasillo,
              squares_traveled: f.casillas_recorridas,
              is_in_goal: f.estado === 'meta'
            };
          }) : [],
          is_turn: j.es_su_turno
        })) : []
      } : null;
      
      return {
        ...data,
        success: true,
        dice: data.dados,
        dice_values: data.dados,
        player: data.jugador,
        sum: data.suma,
        is_double: data.es_par,
        game_state: gameState
      };
    }
    
    if (tipo === 'ESTADO_ACTUALIZADO') {
      const estado = data.estado;
      
      // Transformar el estado del juego
      const gameState = estado ? {
        ...estado,
        current_player: estado.jugador_actual,
        players: estado.jugadores ? estado.jugadores.map(j => ({
          player_id: j.id,
          name: j.nombre,
          color: this.mapColorBackendToFrontend(j.color),
          pieces: j.fichas ? j.fichas.map(f => {
            let position;
            if (f.estado === 'carcel') {
              position = -1;
            } else if (f.estado === 'meta') {
              position = 'goal';
            } else {
              position = f.posicion;
            }
            
            return {
              piece_id: f.id,
              position: position,
              state: f.estado,
              corridor_position: f.posicion_pasillo,
              squares_traveled: f.casillas_recorridas,
              is_in_goal: f.estado === 'meta'
            };
          }) : [],
          is_turn: j.es_su_turno
        })) : []
      } : null;
      
      return {
        ...data,
        game_state: gameState
      };
    }
    
    if (tipo === 'RESULTADO_MOVIMIENTO') {
      return {
        ...data,
        success: data.exito
      };
    }
    
    // Por defecto, devolver los datos sin cambios
    return data;
  }

  /**
   * Mapea eventos del frontend al formato esperado por el backend
   */
  mapFrontendToBackend(frontendEvent) {
    const eventMap = {
      // Salas
      'create_room': 'CREAR_SALA',
      'create_game': 'CREAR_SALA',  // Crear partida es crear sala
      'join_room': 'UNIRSE_SALA',
      'start_game_from_lobby': 'INICIAR_PARTIDA',
      
      // Juego
      'roll_dice': 'LANZAR_DADOS',
      'move_piece': 'MOVER_FICHA',
      'release_piece': 'LIBERAR_FICHA'
    };
    
    return eventMap[frontendEvent] || frontendEvent.toUpperCase();
  }

  /**
   * Envía un mensaje al servidor
   */
  send(message) {
    if (this.connected && this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('[WS] No conectado, encolando mensaje:', message);
      this.messageQueue.push(message);
    }
  }

  /**
   * Desconecta del servidor
   */
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.connected = false;
    }
  }

  /**
   * Emite un evento al servidor (compatibilidad con Socket.IO)
   */
  emit(event, data = {}) {
    const tipo = this.mapFrontendToBackend(event);
    
    // Adaptar datos según el evento
    let mensaje = { tipo, ...data };
    
    // Mapear campos específicos según el tipo de evento
    if (tipo === 'CREAR_SALA') {
      // Si viene de create_game (tiene players array)
      if (data.players && Array.isArray(data.players)) {
        const humanPlayer = data.players.find(p => p.isHuman);
        const botPlayers = data.players.filter(p => !p.isHuman);
        
        mensaje = {
          tipo,
          playerName: humanPlayer ? humanPlayer.name : 'Jugador',
          maxPlayers: data.numberOfPlayers || data.players.length,
          numBots: botPlayers.length,
          color: humanPlayer ? humanPlayer.color : 'red',
          // ✅ NUEVO: Enviar información completa de todos los jugadores con sus colores
          players: data.players.map((p, index) => ({
            name: p.name,
            color: p.color,
            isHuman: p.isHuman,
            id: p.id,
            turnOrder: index
          }))
        };
        console.log('🎨 [WS] Enviando jugadores con colores:', mensaje.players);
      } else {
        // Formato normal de create_room
        mensaje = {
          tipo,
          playerName: data.playerName,
          maxPlayers: data.maxPlayers || 4,
          numBots: data.numBots || 0,
          color: data.color
        };
      }
    } else if (tipo === 'UNIRSE_SALA') {
      mensaje = {
        tipo,
        roomCode: data.roomCode,
        playerName: data.playerName,
        color: data.color || null
      };
    }
    
    console.log('[WS] Enviando:', mensaje);
    this.send(mensaje);
  }

  /**
   * Registra un manejador de eventos
   */
  on(event, callback) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event).push(callback);
  }

  /**
   * Elimina un manejador de eventos
   */
  off(event, callback) {
    if (this.eventHandlers.has(event)) {
      const handlers = this.eventHandlers.get(event);
      const index = handlers.indexOf(callback);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  /**
   * Dispara un evento a todos los manejadores registrados
   */
  trigger(event, data) {
    if (this.eventHandlers.has(event)) {
      const handlers = this.eventHandlers.get(event);
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`[WS] Error en handler de ${event}:`, error);
        }
      });
    }
  }

  /**
   * Obtiene el WebSocket actual
   */
  getSocket() {
    return this.ws;
  }

  /**
   * Verifica si está conectado
   */
  isConnected() {
    return this.connected && this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

// Exportar una instancia única (Singleton)
const socketService = new WebSocketService();
export default socketService;

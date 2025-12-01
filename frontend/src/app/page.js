'use client';

import { useSocket } from '../hooks/useSocket';
import { useEffect, useState } from 'react';
import Board from '../components/Board/Board';
import Dice from '../components/Game/Dice';
import Menu from '../components/Menu/Menu';
import Lobby from '../components/Menu/Lobby';
import TurnOrderDetermination from '../components/Menu/TurnOrderDetermination';
import Rules from '../components/Menu/Rules';
import Celebration from '../components/Game/Celebration';
import AudioControl from '../components/Game/AudioControl';
import MoveSelector from '../components/Game/MoveSelector';
import Notification from '../components/Notification/Notification';
import { 
  initialGameState, 
  testMixedState
} from '../utils/mockData';
import { SPECIAL_POSITIONS, PLAYER_COLORS } from '../utils/constants';
import styles from './page.module.css';
import audioService from '../services/audioService';

export default function Home() {
  const { socket, connected, emit } = useSocket();
  const [message, setMessage] = useState('');
  const [gameState, setGameState] = useState(initialGameState); // Empezar con todas las fichas en cárcel
  const [isTestMode, setIsTestMode] = useState(false); // Simple toggle para test
  const [diceValue, setDiceValue] = useState(null);
  const [isRolling, setIsRolling] = useState(false);
  const [canMove, setCanMove] = useState(false); // Si se puede mover una ficha
  const [selectedPiece, setSelectedPiece] = useState(null); // Ficha seleccionada para mover
  const [showingNoMovesResult, setShowingNoMovesResult] = useState(false); // Flag para mostrar resultado sin movimientos
  const [maxPiecesToRelease, setMaxPiecesToRelease] = useState(0); // Cuántas fichas se pueden liberar con los dobles actuales
  const [isReleasingPiece, setIsReleasingPiece] = useState(false); // Flag para prevenir múltiples envíos
  
  // Estados para selector de movimiento
  const [availableMoves, setAvailableMoves] = useState([]); // Movimientos disponibles [dado1, dado2, suma]
  const [showMoveSelector, setShowMoveSelector] = useState(false); // Mostrar selector de movimiento
  const [pendingPieceForMove, setPendingPieceForMove] = useState(null); // Ficha esperando selección de movimiento
  
  // Estados para transición entre turnos
  const [isTransitioning, setIsTransitioning] = useState(false); // Si está en transición de turno
  const [transitionMessage, setTransitionMessage] = useState(''); // Mensaje de transición
  
  // Estados para el menú
  const [gameStarted, setGameStarted] = useState(false);
  const [showRules, setShowRules] = useState(false);
  const [numberOfPlayers, setNumberOfPlayers] = useState(4); // 4 jugadores por defecto
  const [activePlayers, setActivePlayers] = useState([]); // Jugadores activos en el juego
  
  // Estados para el sistema de salas multijugador
  const [inLobby, setInLobby] = useState(false);
  const [roomCode, setRoomCode] = useState(null);
  const [roomState, setRoomState] = useState(null);
  const [isHost, setIsHost] = useState(false);
  const [availableColors, setAvailableColors] = useState(['red', 'blue', 'green', 'yellow']);
  const [showColorSelector, setShowColorSelector] = useState(false);
  
  // Estados para determinación de orden desde lobby
  const [inTurnOrderDetermination, setInTurnOrderDetermination] = useState(false);
  const [lobbyPlayers, setLobbyPlayers] = useState([]);
  
  // Estados para celebración de victoria
  const [showCelebration, setShowCelebration] = useState(false);
  const [winner, setWinner] = useState(null);
  // Debug UI toggle (mostrar/ocultar panel sin eliminarlo)
  const [showDebug, setShowDebug] = useState(false);
  
  // Estados para notificaciones
  const [notification, setNotification] = useState(null);
  
  // Función para mostrar notificaciones
  const showNotification = (message, type = 'info') => {
    console.log('[NOTIFICATION] 🔔 showNotification llamado');
    console.log('[NOTIFICATION] Message:', message);
    console.log('[NOTIFICATION] Type:', type);
    setNotification({ message, type });
    console.log('[NOTIFICATION] Estado notification actualizado:', { message, type });
  };

  // Función auxiliar para obtener información del jugador por color
  const getPlayerInfo = (color) => {
    if (!color) {
      return { name: 'Esperando...', color: '' };
    }
    
    console.log('[DEBUG] getPlayerInfo llamado con color:', color);
    
    // Buscar en el estado del juego (más confiable)
    if (gameState.players && gameState.players.length > 0) {
      const gamePlayer = gameState.players.find(p => p.color === color);
      if (gamePlayer) {
        console.log('[DEBUG] Encontrado en gameState.players:', gamePlayer);
        return { name: gamePlayer.name, color: color };
      }
    }
    
    // Buscar en jugadores activos como backup
    const activePlayer = activePlayers.find(p => p.color === color);
    if (activePlayer) {
      console.log('[DEBUG] Encontrado en activePlayers:', activePlayer);
      return { name: activePlayer.name, color: color };
    }
    
    // Fallback a nombres por defecto
    const colorNames = {
      red: 'Rojo',
      blue: 'Azul', 
      green: 'Verde',
      yellow: 'Amarillo'
    };
    
    const fallbackName = colorNames[color] || 'Desconocido';
    console.log('[DEBUG] Usando fallback para color:', color, '-> name:', fallbackName);
    return { name: fallbackName, color: color };
  };

  // Función auxiliar para obtener los colores de jugadores activos (solo humanos para UI, no bots)
  const getActivePlayerColors = () => {
    // Si estamos en juego, obtener jugadores reales del gameState
    if (gameState?.players && Array.isArray(gameState.players)) {
      // Filtrar solo jugadores humanos (no bots) SOLO PARA LA UI DEL PANEL DE JUGADORES
      // Los bots tienen IDs que empiezan con "bot_" o "player_"
      return gameState.players
        .filter(p => p.player_id && typeof p.player_id === 'string' && !p.player_id.startsWith('bot_') && !p.isHuman === false)
        .map(p => p.color);
    }
    
    // Si estamos en lobby/turnOrder, obtener de roomState
    if (roomState?.players && Array.isArray(roomState.players)) {
      return roomState.players
        .filter(p => p.color) // Solo jugadores con color asignado
        .map(p => p.color);
    }
    
    // Si tenemos activePlayers, usarlos (filtrar bots)
    if (activePlayers.length > 0) {
      return activePlayers
        .filter(p => p.isHuman !== false && (!p.id || typeof p.id !== 'string' || !p.id.startsWith('bot_')))
        .map(p => p.color);
    }
    
    // Fallback por defecto (no debería llegar aquí normalmente)
    return [];
  };

  // Función para mostrar transición entre turnos
  const showTurnTransition = (nextPlayerColor, reason = '') => {
    console.log('[TRANSITION] 🔄🔄🔄 showTurnTransition LLAMADO');
    console.log('[TRANSITION] nextPlayerColor:', nextPlayerColor);
    console.log('[TRANSITION] reason:', reason);
    
    const playerInfo = getPlayerInfo(nextPlayerColor);
    const colorNames = {
      red: 'Rojo',
      blue: 'Azul',
      green: 'Verde',
      yellow: 'Amarillo'
    };
    
    const displayName = playerInfo.name || colorNames[nextPlayerColor] || 'Desconocido';
    const reasonText = reason ? ` (${reason})` : '';
    
    console.log('[TRANSITION] 🔄 Iniciando transición a:', displayName, reasonText);
    console.log('[TRANSITION] Configurando isTransitioning = true');
    
    setIsTransitioning(true);
    setTransitionMessage(`Turno de ${displayName}${reasonText}`);
    
    console.log('[TRANSITION] Estado configurado:', {
      isTransitioning: true,
      transitionMessage: `Turno de ${displayName}${reasonText}`
    });
    
    // Bloquear todas las acciones
    setCanMove(false);
    setIsRolling(false);
    setDiceValue(null);
    
    // Terminar transición después de 3 segundos (aumentado para ver movimientos)
    setTimeout(() => {
      console.log('[TRANSITION] ✅ Transición completada');
      setIsTransitioning(false);
      setTransitionMessage('');
    }, 3000); // Aumentado de 2000 a 3000ms
  };

  // Debug: Loggear cambios en diceValue
  useEffect(() => {
    console.log('[STATE CHANGE] 🎲 diceValue cambió a:', diceValue);
  }, [diceValue]);

  // Debug: Loggear cambios en canMove
  useEffect(() => {
    console.log('[STATE CHANGE] ✋ canMove cambió a:', canMove);
  }, [canMove]);
  
  // Inicializar servicio de audio al montar el componente
  useEffect(() => {
    const initAudio = async () => {
      await audioService.initialize();
      console.log('[AUDIO] Servicio de audio inicializado');
    };
    
    // Inicializar después de una interacción del usuario (requisito del navegador)
    const handleFirstInteraction = () => {
      initAudio();
      // Remover los listeners después de la primera interacción
      document.removeEventListener('click', handleFirstInteraction);
      document.removeEventListener('keydown', handleFirstInteraction);
    };
    
    document.addEventListener('click', handleFirstInteraction);
    document.addEventListener('keydown', handleFirstInteraction);
    
    return () => {
      document.removeEventListener('click', handleFirstInteraction);
      document.removeEventListener('keydown', handleFirstInteraction);
    };
  }, []);

  useEffect(() => {
    if (!socket) return;

    // Escuchar respuesta de conexión exitosa
    socket.on('connection_success', (data) => {
      console.log('[DEBUG] Conexión exitosa. Mensaje del servidor:', data);
      setMessage(data.message);
      
      // Guardar ID del socket para reconexión
      if (typeof window !== 'undefined') {
        sessionStorage.setItem('player_id', data.client_id);
      }
    });

    // Escuchar respuesta de ping
    socket.on('pong', (data) => {
      console.log('Pong recibido:', data);
    });

    // Escuchar resultado del lanzamiento de dado
    socket.on('dice_rolled', (data) => {
      console.log('[dice_rolled EVENT] ========================================');
      console.log('[dice_rolled EVENT] Dados lanzados:', data);
      console.log('[dice_rolled EVENT] CurrentPlayer:', data.game_state?.current_player);
      console.log('[dice_rolled EVENT] MyPlayerColor:', myPlayerColor);
      
      // ✅ Si no es mi turno (es el bot u otro jugador), activar animación visual
      const isMyTurn = data.game_state?.current_player === myPlayerColor;
      if (!isMyTurn) {
        console.log('[dice_rolled] 🤖 No es mi turno - activando animación visual');
        setIsRolling(true);
        // Reproducir sonido de dados
        audioService.playDiceRoll();
      }
      
      // ✅ Sincronizar con la animación de los dados (1s)
      setTimeout(() => {
        if (data.success) {
          // IMPORTANTE: Usar data.dice_values directamente
          console.log('[dice_rolled] 🎲🎲 Configurando diceValue a:', data.dice_values);
          setDiceValue(data.dice_values);
          setIsRolling(false);
          
          // Actualizar movimientos disponibles
          if (data.available_moves && data.available_moves.length > 0) {
            console.log('[dice_rolled] 📊 Movimientos disponibles:', data.available_moves);
            setAvailableMoves(data.available_moves);
          } else {
            setAvailableMoves([]);
          }
          
          // Actualizar estado del juego
          if (data.game_state) {
            console.log('[DEBUG] Actualizando gameState con:', data.game_state);
            
            const newGameState = {
              ...data.game_state,
              currentPlayer: data.game_state.current_player,
              canMove: data.game_state.can_move,
              diceValues: data.dice_values,
              // Información de fase de inicio - PRIORIZAR game_state sobre data
              startPhase: data.game_state.start_phase !== undefined ? data.game_state.start_phase : (data.start_phase || false),
              currentAttempts: data.game_state.current_attempts || data.attempts_used || 0,
              attemptsRemaining: data.game_state.attempts_remaining || data.attempts_remaining || 0,
              // ✅ CRÍTICO: Incluir campos de selección de ficha desde data (nivel superior)
              pendingPieceRelease: data.game_state.pending_piece_release,
              piecesInPrison: data.pieces_in_prison
            };
            
            // Si el turno pasó (fallo en fase de inicio), retrasar la actualización del estado
            // para que el usuario vea el resultado con su color antes de cambiar
            if (data.turn_passed) {
              console.log('[dice_rolled] ⏳ Turno pasado - retrasando actualización de estado');
              setTimeout(() => {
                setGameState(newGameState);
              }, 1500);
            } else {
              setGameState(newGameState);
            }
            
            // Actualizar jugadores activos si no están configurados
            if (data.game_state.players && activePlayers.length === 0) {
              const newActivePlayers = data.game_state.players.map(p => ({
                id: p.player_id,
                name: p.name,
                color: p.color
              }));
              setActivePlayers(newActivePlayers);
            }
          }
          
          // Manejar fase de inicio (intentos para sacar dobles)
          if (data.start_phase) {
            // ... Lógica de fase de inicio ...
            // PRIORIDAD 1: Verificar si necesita selección de ficha
            if (data.needs_piece_selection === true) {
              // ...
              audioService.playDoubles();
              setCanMove(true);
              const piecesToRelease = data.max_pieces_to_release || 1;
              setMaxPiecesToRelease(piecesToRelease);
              setMessage(`🎲🎲 ¡DOBLES! Selecciona ${piecesToRelease === 2 ? 'DOS fichas' : 'una ficha'} para sacar de la cárcel (Intento ${data.attempts_used}/3)`);
              return;
            }
            
            // PRIORIDAD 1B: Puede liberar ficha O mover
            if (data.can_release_piece === true) {
              setCanMove(true);
              setMessage('¡Dobles! Puedes sacar una ficha de la cárcel o mover una que está fuera');
              return;
            }
            
            // PRIORIDAD 2: Dobles pero sin fichas
            if (data.is_doubles === true && !data.needs_piece_selection) {
              setMessage('Sacaste dobles pero no tienes fichas en la cárcel');
              setCanMove(false);
              setTimeout(() => {
                setDiceValue(null);
                setMessage('');
              }, 2000);
              return;
            }
            
            // PRIORIDAD 3: Se acabaron los intentos
            if (data.turn_passed === true) {
              setMessage('No sacaste dobles en 3 intentos. Pasando turno...');
              setCanMove(false);
              
              setTimeout(() => {
                setDiceValue(null);
                setMessage('');
                
                const nextPlayerColor = data.game_state?.current_player;
                if (nextPlayerColor) {
                  setTimeout(() => {
                    showTurnTransition(nextPlayerColor, '3 intentos sin éxito');
                  }, 500);
                }
              }, 1500);
              return;
            }
            
            // PRIORIDAD 4: Puede intentar de nuevo
            if (data.can_retry === true) {
              setMessage(`No sacaste dobles. Te quedan ${data.attempts_remaining} intentos.`);
              setCanMove(false);
              setShowingNoMovesResult(false);
              setIsRolling(false);
              setTimeout(() => {
                setMessage('');
              }, 5000);
              return;
            }
            return;
          }
          
          // Juego normal
          if (data.no_moves) {
            setCanMove(false);
            setShowingNoMovesResult(true);
            setTimeout(() => {
              setDiceValue(null);
              setShowingNoMovesResult(false);
            }, 3000);
          } else {
            setCanMove(true);
            setShowingNoMovesResult(false);
          }
        } else {
          setIsRolling(false);
          console.error('Error al lanzar dado:', data.error);
          audioService.playError();
          setMessage(data.error || 'Error al lanzar los dados');
          if (data.pending_piece_release && data.pieces_to_select) {
            setMessage(`⚠️ Debes seleccionar ${data.pieces_to_select} ficha(s) más de la cárcel`);
          }
          setTimeout(() => {
            setMessage('');
          }, 3000);
        }
      }, 1000); // Fin del timeout de animación
    });

    // Escuchar resultado de la liberación de ficha desde la cárcel
    socket.on('piece_released', (data) => {
      console.log('[piece_released EVENT] ========================================');
      console.log('[piece_released EVENT] Ficha liberada:', data);
      console.log('[piece_released EVENT] bonus_turn:', data.bonus_turn);
      console.log('[piece_released EVENT] can_release_more:', data.can_release_more);
      console.log('[piece_released EVENT] pieces_released_count:', data.pieces_released_count);
      console.log('[piece_released EVENT] game_state.can_move:', data.game_state?.can_move);
      console.log('[piece_released EVENT] ========================================');
      
      // ✅ Limpiar flag de procesamiento
      setIsReleasingPiece(false);
      
      if (data.success) {
        // 🔊 Reproducir sonido de movimiento de ficha
        audioService.playPieceMove();
        
        // Actualizar estado del juego CON LAS FICHAS ACTUALIZADAS
        if (data.game_state) {
          // Calcular fichas que quedan en prisión para el jugador actual
          const currentPlayerData = data.game_state.players.find(p => p.color === data.game_state.current_player);
          const piecesStillInPrison = currentPlayerData ? 
            currentPlayerData.pieces.filter(piece => piece.position === -1).map(piece => piece.piece_id) : [];
          
          console.log('[DEBUG] Fichas que quedan en prisión:', piecesStillInPrison);
          console.log('[DEBUG] can_release_more:', data.can_release_more);
          
          const newGameState = {
            ...data.game_state,
            currentPlayer: data.game_state.current_player,
            canMove: false, // ✅ Siempre false después de liberar - el jugador debe tirar dados de nuevo
            startPhase: data.game_state.start_phase,
            pendingPieceRelease: data.can_release_more ? data.game_state.pending_piece_release : false,
            piecesInPrison: data.can_release_more ? piecesStillInPrison : [],
            // ✅ CRÍTICO: Incluir los jugadores actualizados para que las fichas se muestren en su nueva posición
            players: data.game_state.players
          };
          
          console.log('[DEBUG] Estado después de liberar ficha:', newGameState);
          console.log('[DEBUG] pendingPieceRelease:', newGameState.pendingPieceRelease);
          console.log('[DEBUG] piecesInPrison:', newGameState.piecesInPrison);
          console.log('[DEBUG] bonus_turn:', data.bonus_turn);
          console.log('[DEBUG] can_release_more:', data.can_release_more);
          console.log('[DEBUG] Fichas actualizadas:', newGameState.players);
          setGameState(newGameState);
        }
        
        // Si puede liberar más fichas, mantener estado para selección
        if (data.can_release_more) {
          setCanMove(true); // Permitir seleccionar otra ficha
          const piecesCount = data.pieces_released_count || 1;
          const totalPieces = maxPiecesToRelease || 2;
          setMessage(`🎉 ¡Ficha liberada! (${piecesCount}/${totalPieces}) - Selecciona otra ficha de la cárcel`);
        } else {
          // Limpiar estado para permitir nueva tirada
          setCanMove(false);
          setDiceValue(null); // ✅ Limpiar dados para que el jugador pueda tirar de nuevo
          setSelectedPiece(null);
          setIsRolling(false); // ✅ Asegurar que isRolling esté en false
          setMaxPiecesToRelease(0); // Limpiar el contador
          
          // Mostrar mensaje apropiado
          setMessage(data.message || '¡Fichas liberadas! Tira los dados de nuevo');
          
          setTimeout(() => {
            setMessage('');
          }, 3000);
        }
      } else {
        console.error('Error al liberar ficha:', data.error);
        // 🔊 Reproducir sonido de error
        audioService.playError();
        setMessage(`Error: ${data.error}`);
        setTimeout(() => {
          setMessage('');
        }, 2000);
      }
    });
    
    // Escuchar resultado del movimiento de ficha
    socket.on('piece_moved', (data) => {
      console.log('[piece_moved EVENT] ========================================');
      console.log('[piece_moved EVENT] Ficha movida:', data);
      console.log('[piece_moved EVENT] old_position:', data.old_position);
      console.log('[piece_moved EVENT] new_position:', data.new_position);
      console.log('[piece_moved EVENT] extra_turn:', data.extra_turn);
      console.log('[piece_moved EVENT] available_moves:', data.available_moves);
      console.log('[piece_moved EVENT] can_move:', data.can_move);
      console.log('[piece_moved EVENT] ========================================');
      
      if (data.success) {
        // 🔊 Reproducir sonido de movimiento de ficha
        audioService.playPieceMove();
        
        // Actualizar movimientos disponibles
        if (data.available_moves !== undefined) {
          console.log('[piece_moved] 📊 Actualizando movimientos disponibles:', data.available_moves);
          setAvailableMoves(data.available_moves);
          
          // Si todavía hay movimientos disponibles, mantener canMove
          if (data.available_moves.length > 0 && data.can_move) {
            setCanMove(true);
            console.log('[piece_moved] ✅ Todavía hay movimientos disponibles, manteniendo canMove=true');
          } else {
            setCanMove(false);
            console.log('[piece_moved] ❌ No hay más movimientos disponibles, canMove=false');
          }
        }
        
        // Actualizar estado del juego CON TODAS LAS FICHAS ACTUALIZADAS
        if (data.game_state) {
          // Mapear correctamente los campos del backend al frontend
          const newGameState = {
            ...data.game_state,
            currentPlayer: data.game_state.current_player, // Mapear current_player -> currentPlayer
            canMove: data.can_move !== undefined ? data.can_move : data.game_state.can_move, // Usar el más reciente
            diceValue: data.game_state.dice_value, // Y dice_value -> diceValue
            // ✅ CRÍTICO: Incluir los jugadores actualizados para que las fichas se muestren en su nueva posición
            players: data.game_state.players
          };
          
          console.log('[DEBUG] Estado después de mover ficha:', newGameState);
          console.log('[DEBUG] Fichas actualizadas:', newGameState.players);
          setGameState(newGameState);
        }
        
        // Limpiar selección de ficha y cerrar selector
        setPendingPieceForMove(null);
        setShowMoveSelector(false);
        
        // ✅ IMPORTANTE: NO limpiar diceValue si aún hay movimientos disponibles
        if (data.available_moves && data.available_moves.length > 0) {
          console.log('[piece_moved] 🎲 Manteniendo diceValue porque quedan movimientos');
          // NO limpiar diceValue ni selectedPiece aún
        } else {
          // No hay más movimientos, limpiar todo
          console.log('[piece_moved] 🧹 Limpiando diceValue porque no quedan movimientos');
          setDiceValue(null);
          setSelectedPiece(null);
          setCanMove(false);
        }
        
        // Si hay turno extra, limpiar dados y permitir lanzar de nuevo
        if (data.extra_turn) {
          console.log('[piece_moved] ✅ Turno extra concedido:', data.reason);
          setDiceValue(null);
          setSelectedPiece(null);
          setCanMove(false);
          setAvailableMoves([]);
          setMessage(data.reason || 'Turno extra');
          
          // Limpiar mensaje después de 3 segundos
          setTimeout(() => {
            setMessage('');
          }, 3000);
          
          // NO mostrar transición porque el turno continúa
          return; // Salir del handler
        }
        
        // Mostrar mensajes especiales
        if (data.captured && data.captured.length > 0) {
          console.log('Fichas capturadas:', data.captured);
          // 🔊 Reproducir sonido de captura
          audioService.playPieceCapture();
          const capturedColors = data.captured.map(p => p.color).join(', ');
          setMessage(`¡Capturaste ${data.captured.length} ficha(s) ${capturedColors}!`);
          setTimeout(() => setMessage(''), 3000);
        }
        
        if (data.reached_goal) {
          console.log('¡Ficha llegó a la meta!');
          // 🔊 Reproducir sonido de meta
          audioService.playPieceGoal();
          setMessage('¡Ficha llegó a la meta!');
          setTimeout(() => setMessage(''), 3000);
        }
        
        if (data.three_sixes) {
          console.log('¡Tres seis consecutivos! Ficha enviada a casa.');
        }
        
        if (data.game_won) {
          console.log('¡Juego ganado por:', data.winner);
        }
      } else {
        console.error('Error al mover ficha:', data.error);
        // 🔊 Reproducir sonido de error
        audioService.playError();
      }
    });

    // Escuchar turno extra
    socket.on('extra_turn', (data) => {
      console.log('[extra_turn EVENT] ========================================');
      console.log('[extra_turn EVENT] Turno extra otorgado:', data);
      console.log('[extra_turn EVENT] Reason:', data.reason);
      console.log('[extra_turn EVENT] can_roll_again:', data.can_roll_again);
      console.log('[extra_turn EVENT] ========================================');
      
      // Mostrar mensaje de turno extra
      setMessage(data.reason || '¡Turno extra!');
      
      // Limpiar mensaje después de 3 segundos
      setTimeout(() => {
        setMessage('');
      }, 3000);
      
      // Asegurar que puede lanzar de nuevo
      setIsRolling(false);
      setCanMove(false);
    });

    // Escuchar fin del juego
    socket.on('game_over', (data) => {
      console.log('Juego terminado. Ganador:', data.winner);
      
      // 🔊 Reproducir sonido de victoria
      audioService.playGameWin();
      
      // Mostrar celebración
      setWinner({
        name: data.winner.name,
        color: data.winner.color
      });
      setShowCelebration(true);
    });

    // Escuchar creación de juego
    socket.on('game_created', (data) => {
      console.log('[game_created] ==========================================');
      console.log('[game_created] Evento recibido:', data);
      console.log('[game_created] data.game_state.players:', data.game_state?.players);
      console.log('[game_created] Total players en game_state:', data.game_state?.players?.length);
      console.log('[game_created] Players detalle:', data.game_state?.players?.map(p => `${p.name} (${p.player_id}) - ${p.color}`));
      console.log('[game_created] ==========================================');
      
      if (data.success) {
        console.log('[DEBUG] Juego creado exitosamente');
        console.log('[DEBUG] Estado inicial del juego:', data.game_state);
        console.log('[DEBUG] Jugador actual inicial:', data.game_state?.current_player);
        
        // 🔊 Reproducir sonido de inicio de juego
        audioService.playGameStart();
        
        // Salir de la fase de determinación de orden si estamos ahí
        setInTurnOrderDetermination(false);
        setLobbyPlayers([]);
        
        // Salir del lobby si estamos ahí
        setInLobby(false);
        
        // Iniciar el juego
        setGameStarted(true);
        
        // Mapear correctamente los campos del backend al frontend
        const newGameState = {
          ...data.game_state,
          currentPlayer: data.game_state.current_player, // Mapear current_player -> currentPlayer
          canMove: data.game_state.can_move, // También mapear can_move -> canMove
          diceValue: data.game_state.dice_value // Y dice_value -> diceValue
        };
        
        console.log('[DEBUG] Estado inicial mapeado:', newGameState);
        console.log('[DEBUG] newGameState.players:', newGameState.players);
        console.log('[DEBUG] Total players en newGameState:', newGameState.players?.length);
        setGameState(newGameState);
        console.log('[DEBUG] Unido como jugador:', data.player_color);
        
        // Extraer jugadores activos del estado del juego (INCLUIR BOTS)
        if (data.game_state && data.game_state.players) {
          console.log('[game_created] Procesando players - Total:', data.game_state.players.length);
          const newActivePlayers = data.game_state.players.map(p => {
            const isBot = (p.player_id || p.id).startsWith('bot_');
            console.log(`[game_created] Player: ${p.name}, ID: ${p.player_id}, Color: ${p.color}, IsBot: ${isBot}`);
            return {
              id: p.player_id || p.id,
              name: p.name,
              color: p.color,
              isBot: isBot
            };
          });
          console.log('[DEBUG] Jugadores activos iniciales (con bots):', newActivePlayers);
          console.log('[DEBUG] Total activePlayers:', newActivePlayers.length);
          setActivePlayers(newActivePlayers);
        }
        
        // Si el juego está en estado 'ready' pero no 'playing', iniciarlo manualmente
        if (data.game_state.status === 'ready') {
          console.log('[DEBUG] Iniciando juego manualmente...');
          emit('start_game', {});
        } else if (data.game_state.status === 'waiting') {
          console.log('[DEBUG] Juego creado pero esperando más jugadores. Iniciando de todos modos...');
          // Para pruebas de un solo jugador, forzar inicio
          setTimeout(() => {
            emit('start_game', {});
          }, 1000);
        }
      } else {
        console.error('[ERROR] Error al crear juego:', data.error);
        showNotification('Error al crear juego: ' + data.error, 'error');
      }
    });

    // Escuchar inicio de juego
    socket.on('game_started', (data) => {
      console.log('[game_started] ==========================================');
      console.log('[game_started] Evento recibido:', data);
      console.log('[game_started] data.game_state.players:', data.game_state?.players);
      console.log('[game_started] Total players:', data.game_state?.players?.length);
      console.log('[game_started] Players detalle:', data.game_state?.players?.map(p => `${p.name} (${p.player_id}) - ${p.color}`));
      console.log('[game_started] ==========================================');
      
      if (data.success) {
        console.log('[DEBUG] Estado del juego al iniciar:', data.game_state);
        console.log('[DEBUG] Jugador actual al iniciar:', data.game_state?.current_player);
        
        // Mapear correctamente los campos del backend al frontend
        const newGameState = {
          ...data.game_state,
          // Si current_player es null, buscar el jugador con is_turn = true
          currentPlayer: data.game_state.current_player || 
            (data.game_state.players && data.game_state.players.find(p => p.is_turn)?.name) || 
            (data.game_state.players && data.game_state.players[0]?.name) || null,
          canMove: data.game_state.can_move, // También mapear can_move -> canMove
          diceValue: data.game_state.dice_value // Y dice_value -> diceValue
        };
        
        console.log('[DEBUG] Estado de inicio mapeado:', newGameState);
        setGameState(newGameState);
        
        // Actualizar jugadores activos (INCLUIR BOTS para que sus fichas se rendericen)
        // NOTA: getActivePlayerColors() filtrará los bots solo para la UI de jugadores
        if (data.game_state && data.game_state.players) {
          const newActivePlayers = data.game_state.players
            .map(p => ({
              id: p.player_id || p.id,
              name: p.name,
              color: p.color,
              isBot: p.player_id.startsWith('bot_') // Marcar si es bot
            }));
          console.log('[DEBUG] Actualizando jugadores activos al iniciar (con bots):', newActivePlayers);
          setActivePlayers(newActivePlayers);
        }
        
        // ✅ IMPORTANTE: Activar el juego para mostrar el tablero
        console.log('[DEBUG] Activando gameStarted = true');
        setGameStarted(true);
        setInLobby(false);
        setInTurnOrderDetermination(false);
        
        audioService.playSuccess();
      } else {
        console.error('Error al iniciar juego:', data.error);
      }
    });

    // Escuchar cuando un jugador se une
    socket.on('player_joined', (data) => {
      console.log('[DEBUG] Jugador unido:', data);
      
      if (data.game_state) {
        setGameState(data.game_state);
      }
    });

    // Escuchar cambios de turno
    socket.on('turn_changed', (data) => {
      console.log('[turn_changed EVENT] ========================================');
      console.log('[turn_changed EVENT] Cambio de turno recibido:', data);
      console.log('[turn_changed EVENT] Nuevo current_player:', data.current_player);
      console.log('[turn_changed EVENT] Previous player:', data.previous_player);
      console.log('[turn_changed EVENT] Reason:', data.reason);
      console.log('[turn_changed EVENT] Mi color:', myPlayerColor);
      console.log('[turn_changed EVENT] ========================================');
      
      // Bloquear interacciones inmediatamente
      setCanMove(false);
      
      // Verificar si realmente cambió el jugador usando previous_player del evento
      const playerChanged = data.previous_player !== data.current_player;
      console.log('[turn_changed] Jugador anterior (del evento):', data.previous_player);
      console.log('[turn_changed] Jugador nuevo (del evento):', data.current_player);
      console.log('[turn_changed] ¿Cambió el jugador?', playerChanged);
      
      // ✅ Actualizar estado del juego inmediatamente
      setGameState(prevState => {
        const newState = {
          ...prevState,
          currentPlayer: data.current_player,
          canMove: false,
          diceValue: null
        };
        
        console.log('[turn_changed] Estado actualizado:', newState);
        return newState;
      });
      
      // Limpiar estados
      setDiceValue(null);
      setCanMove(false);
      setShowingNoMovesResult(false);
      setMaxPiecesToRelease(0); // Limpiar contador de fichas a liberar
      
      // ✅ SOLO mostrar transición visual si el jugador realmente cambió
      if (playerChanged) {
        // 🔊 Reproducir sonido de cambio de turno
        audioService.playTurnPass();
        
        // Bloquear interacciones solo durante la animación visual
        setIsTransitioning(true);
        
        console.log('[turn_changed] 🔄 Cambio de jugador - mostrando transición');
        showTurnTransition(data.current_player, data.reason || 'Cambio de turno');
        
        // Desbloquear después de la animación
        setTimeout(() => {
          setIsTransitioning(false);
        }, 1500);
      } else {
        console.log('[turn_changed] ⚠️ Mismo jugador - NO mostrar transición');
      }
    });

    // ✅ Escuchar actualizaciones de estado del juego (cuando otros jugadores hacen acciones)
    socket.on('game_state_updated', (data) => {
      console.log('[game_state_updated EVENT] ========================================');
      console.log('[game_state_updated EVENT] Estado actualizado:', data);
      console.log('[game_state_updated EVENT] Action:', data.action);
      console.log('[game_state_updated EVENT] Current player:', data.current_player);
      console.log('[game_state_updated EVENT] ========================================');
      
      if (data.game_state) {
        // Actualizar el estado del juego con la información más reciente
        const newGameState = {
          ...data.game_state,
          currentPlayer: data.game_state.current_player,
          canMove: data.game_state.can_move,
          diceValues: data.game_state.dice_values,
          startPhase: data.game_state.start_phase,
          currentAttempts: data.game_state.current_attempts || 0,
          attemptsRemaining: data.game_state.attempts_remaining || 0
        };
        
        console.log('[game_state_updated] Actualizando estado del juego:', newGameState);
        setGameState(newGameState);
        
        // Si el current_player cambió, limpiar estados locales
        if (gameState.currentPlayer && gameState.currentPlayer !== data.game_state.current_player) {
          console.log('[game_state_updated] Turno cambió - limpiando estados locales');
          setDiceValue(null);
          setCanMove(false);
          setIsRolling(false);
          setMaxPiecesToRelease(0); // Limpiar contador de fichas a liberar
        }
      }
    });

    // ============================================================
    // EVENTOS DE SALA MULTIJUGADOR
    // ============================================================

    // Sala creada exitosamente
    socket.on('room_created', (data) => {
      console.log('[ROOM] Sala creada:', data);
      if (data.success) {
        setRoomCode(data.room_code);
        setRoomState(data.room_state);
        setIsHost(true);
        
        // Guardar en sessionStorage para reconexión
        if (typeof window !== 'undefined') {
          sessionStorage.setItem('room_code', data.room_code);
          sessionStorage.setItem('is_host', 'true');
        }
        
        audioService.playSuccess();
        
        // Iniciar la partida automáticamente (sin pasar por el lobby)
        console.log('[ROOM] Iniciando partida automáticamente...');
        setTimeout(() => {
          emit('start_game_from_lobby', {
            roomCode: data.room_code
          });
        }, 500);
      } else {
        audioService.playError();
        showNotification('Error al crear sala: ' + data.error, 'error');
      }
    });

    // Se unió exitosamente a una sala
    socket.on('room_joined', (data) => {
      console.log('[ROOM] Se unió a sala:', data);
      if (data.success) {
        setRoomCode(data.room_code);
        setRoomState(data.room_state);
        setIsHost(data.is_host || false);
        setInLobby(true);
        setGameStarted(false);
        
        // Actualizar colores disponibles
        if (data.available_colors) {
          setAvailableColors(data.available_colors);
        }
        
        // Guardar en sessionStorage
        if (typeof window !== 'undefined') {
          sessionStorage.setItem('room_code', data.room_code);
          sessionStorage.setItem('is_host', data.is_host ? 'true' : 'false');
        }
        
        audioService.playSuccess();
      } else {
        audioService.playError();
        showNotification('Error al unirse: ' + data.error, 'error');
      }
    });

    // Un jugador se unió a la sala
    socket.on('player_joined_room', (data) => {
      console.log('[ROOM] Jugador se unió:', data);
      setRoomState(data.room_state);
      
      // Actualizar colores disponibles
      if (data.available_colors) {
        setAvailableColors(data.available_colors);
      }
      
      audioService.playPlayerJoin();
    });

    // Información de la sala (para selección de color)
    socket.on('room_info', (data) => {
      console.log('[ROOM] ========================================');
      console.log('[ROOM] Información de sala recibida:', data);
      console.log('[ROOM] Success:', data.success);
      console.log('[ROOM] Error:', data.error);
      console.log('[ROOM] Available colors:', data.available_colors);
      console.log('[ROOM] ========================================');
      
      if (data.success && data.available_colors) {
        setAvailableColors(data.available_colors);
        setShowColorSelector(true);
      } else if (!data.success) {
        console.log('[ROOM] ⚠️ ERROR DETECTADO - Reproduciendo sonido y mostrando notificación');
        audioService.playError();
        showNotification(data.error || 'Error al obtener información de la sala', 'error');
        // Limpiar el estado para que el usuario pueda volver a intentar
        setShowColorSelector(false);
      }
    });

    // Un jugador salió de la sala
    socket.on('player_left_room', (data) => {
      console.log('[ROOM] Jugador salió:', data);
      setRoomState(data.room_state);
      if (data.new_host === socket.id) {
        setIsHost(true);
        if (typeof window !== 'undefined') {
          sessionStorage.setItem('is_host', 'true');
        }
      }
    });

    // Estado de "listo" cambió
    socket.on('player_ready_changed', (data) => {
      console.log('[ROOM] Estado listo cambió:', data);
      setRoomState(data.room_state);
    });

    // Iniciar determinación de orden desde el lobby
    socket.on('start_turn_order_determination', (data) => {
      console.log('[ROOM] Iniciar determinación de orden:', data);
      console.log('[ROOM] Jugadores recibidos:', data.players);
      
      // Guardar los jugadores del lobby
      setLobbyPlayers(data.players || []);
      
      // Salir del lobby y entrar en determinación de orden
      setInLobby(false);
      setInTurnOrderDetermination(true);
      setGameStarted(false); // Todavía no iniciamos el juego
      
      // Reproducir sonido
      audioService.playClick();
    });

    // Reconexión exitosa a un juego en curso
    socket.on('reconnected_to_game', (data) => {
      console.log('[RECONNECT] Reconexión exitosa:', data);
      
      if (data.room_state) {
        // Restaurar estado del lobby
        setRoomCode(data.room_code);
        setRoomState(data.room_state);
        
        // Verificar si es host
        const currentPlayer = data.room_state.players?.find(
          p => p.socket_id === socket.id
        );
        setIsHost(currentPlayer?.is_host || false);
        
        if (data.game_state && data.room_state.status === 'playing') {
          // El juego ya está en curso - restaurar estado del juego
          setGameState(data.game_state);
          setGameStarted(true);
          setInLobby(false);
          
          audioService.playSuccess();
        } else {
          // Todavía en lobby
          setInLobby(true);
          setGameStarted(false);
          
          audioService.playSuccess();
        }
      }
    });

    // Reconexión al lobby
    socket.on('reconnected_to_lobby', (data) => {
      console.log('[RECONNECT] Reconectado al lobby:', data);
      
      setRoomCode(data.room_code);
      setRoomState(data.room_state);
      setInLobby(true);
      setGameStarted(false);
      
      audioService.playSuccess();
    });

    // Fallo al reconectar
    socket.on('reconnect_failed', (data) => {
      console.log('[RECONNECT] Reconexión fallida:', data.error);
      
      // Limpiar sessionStorage y volver al menú
      if (typeof window !== 'undefined') {
        sessionStorage.removeItem('room_code');
        sessionStorage.removeItem('is_host');
        sessionStorage.removeItem('player_id');
      }
      
      setInLobby(false);
      setGameStarted(false);
      
      showNotification('No se pudo reconectar a la partida: ' + data.error, 'error');
    });

    // Escuchar resultado del debug status
    socket.on('debug_status_result', (data) => {
      console.log('[DEBUG] Status del servidor:', data);
      showNotification('Debug Status - Ver console para detalles', 'info');
    });

    return () => {
      socket.off('connection_success');
      socket.off('pong');
      socket.off('dice_rolled');
      socket.off('piece_moved');
      socket.off('turn_changed');
      socket.off('extra_turn');
      socket.off('game_over');
      socket.off('game_created');
      socket.off('game_started');
      socket.off('player_joined');
      socket.off('debug_status_result');
      // Eventos de sala
      socket.off('room_created');
      socket.off('room_joined');
      socket.off('room_info');
      socket.off('player_joined_room');
      socket.off('player_left_room');
      socket.off('player_ready_changed');
      socket.off('start_turn_order_determination');
      socket.off('reconnected_to_game');
      socket.off('reconnected_to_lobby');
      socket.off('reconnect_failed');
    };
  }, [socket]);

  const handlePing = () => {
    console.log('[DEBUG] Enviando ping...');
    emit('ping', {});
  };

  const handleDebugStatus = () => {
    console.log('[DEBUG] Solicitando debug status...');
    emit('debug_status', {});
  };

  // Obtener el estado actual del juego
  const getCurrentGameState = () => {
    const baseState = isTestMode ? testMixedState : gameState;
    
    // Validar que el estado base existe
    if (!baseState) {
      console.error('baseState is undefined');
      return { pieces: [], players: [] };
    }
    
    // NO FILTRAR JUGADORES - incluir TODOS (humanos Y bots) para que sus fichas se rendericen
    console.log('[getCurrentGameState] baseState.players:', baseState.players?.length);
    console.log('[getCurrentGameState] currentPlayer:', baseState.currentPlayer);
    
    // Convertir formato para el Board: extraer fichas de TODOS los jugadores (incluidos bots)
    const pieces = [];
    
    if (baseState.players) {
      baseState.players.forEach(player => {
        if (player.pieces) {
          player.pieces.forEach(piece => {
            const pieceData = {
              id: `${player.color}_${piece.piece_id}`,
              color: player.color,
              position: piece.position === -1 ? 'prison' : piece.position,
              pieceId: piece.piece_id,
              isInGoal: piece.is_in_goal || false
            };
            pieces.push(pieceData);
            
            // Log solo para fichas en prisión del jugador actual
            if (piece.position === -1 && player.color === baseState.currentPlayer) {
              console.log('[getCurrentGameState] Ficha en prisión del jugador actual:', pieceData);
            }
          });
        }
      });
    }
    
    console.log('[getCurrentGameState] Total de fichas generadas:', pieces.length);
    console.log('[getCurrentGameState] Jugadores incluidos:', baseState.players?.map(p => `${p.name} (${p.color})`));

    // Retornar el estado completo CON TODOS LOS JUGADORES (incluidos bots)
    return {
      ...baseState,
      pieces,
      players: baseState.players || []
    };
  };

  const handleDiceRoll = () => {
    // Verificar si estamos en modo offline (sin conexión al servidor)
    const isOfflineMode = !connected;
    
    // En modo test o modo offline, permitir juego local sin servidor
    if (isTestMode || isOfflineMode) {
      // No permitir lanzar si ya se puede mover
      if (isRolling || canMove) {
        console.log('[DEBUG] handleDiceRoll bloqueado en modo local:', { isRolling, canMove });
        return;
      }
      
      console.log('[DEBUG] Lanzando dado en modo local...', isOfflineMode ? '(offline)' : '(test)');
      setIsRolling(true);
      setSelectedPiece(null);
      
      // Reproducir sonido de dados
      audioService.playDiceRoll();
      
      // Simular lanzamiento de dados con animación
      setTimeout(() => {
        const dice1 = Math.floor(Math.random() * 6) + 1;
        const dice2 = Math.floor(Math.random() * 6) + 1;
        const diceResult = [dice1, dice2];
        
        console.log('[DEBUG] Dados lanzados:', diceResult);
        setDiceValue(diceResult);
        setIsRolling(false);
        
        // Verificar si es fase de inicio
        if (gameState.startPhase) {
          const isDoubles = dice1 === dice2;
          
          if (isDoubles) {
            console.log('[DEBUG] ¡DOBLES! Puede sacar ficha de la cárcel');
            audioService.playDoubles();
            setCanMove(true);
            setMessage('¡DOBLES! Selecciona una ficha para sacar de la cárcel');
            
            // Actualizar estado con pendingPieceRelease
            setGameState(prev => ({
              ...prev,
              pendingPieceRelease: true,
              piecesInPrison: [0, 1, 2, 3], // Todas las fichas en prisión disponibles
              currentAttempts: (prev.currentAttempts || 0) + 1,
              attemptsRemaining: 3 - ((prev.currentAttempts || 0) + 1)
            }));
          } else {
            // No sacó dobles
            const newAttempts = (gameState.currentAttempts || 0) + 1;
            const remaining = 3 - newAttempts;
            
            console.log('[DEBUG] No dobles, intentos:', newAttempts, '/', 3);
            
            if (remaining > 0) {
              setMessage(`No sacaste dobles. Te quedan ${remaining} intentos.`);
              setCanMove(false);
              
              // Actualizar intentos
              setGameState(prev => ({
                ...prev,
                currentAttempts: newAttempts,
                attemptsRemaining: remaining
              }));
              
              setTimeout(() => {
                setMessage('');
              }, 3000);
            } else {
              // Se acabaron los intentos
              setMessage('No sacaste dobles en 3 intentos. Pasando turno...');
              setCanMove(false);
              
              setTimeout(() => {
                setDiceValue(null);
                setMessage('');
                nextTurn();
              }, 2000);
            }
          }
        } else {
          // Juego normal
          setCanMove(true);
        }
      }, 1000);
      
      return;
    }
    
    // Modo online: requiere conexión al servidor
    // No permitir lanzar dado si:
    // - No está conectado
    // - Ya está rodando
    // - Ya se puede mover (ya se lanzó el dado)
    // - Se está mostrando un resultado sin movimientos
    if (!connected || isRolling || canMove || showingNoMovesResult) {
      console.log('[DEBUG] handleDiceRoll bloqueado:', {
        connected,
        isRolling,
        canMove,
        showingNoMovesResult,
        gameStateCanMove: gameState.canMove,
        gameStateStartPhase: gameState.startPhase
      });
      return;
    }
    
    console.log('[DEBUG] Lanzando dado (online)...');
    setIsRolling(true);
    setSelectedPiece(null);
    
    // Enviar evento al servidor para lanzar el dado
    emit('roll_dice', {});
  };

  // Esta función ya no es necesaria, el backend maneja los turnos
  // Mantenerla por compatibilidad con el modo test local
  const nextTurn = () => {
    const colors = ['red', 'blue', 'green', 'yellow'];
    const currentIndex = colors.indexOf(gameState.currentPlayer);
    const nextIndex = (currentIndex + 1) % numberOfPlayers;
    
    setGameState(prev => {
      const newGameState = { ...prev };
      
      // Limpiar el flag justExitedPrison de todas las fichas al cambiar turno
      newGameState.players.forEach(player => {
        player.pieces.forEach(piece => {
          if (piece.justExitedPrison) {
            delete piece.justExitedPrison;
          }
        });
      });
      
      newGameState.currentPlayer = colors[nextIndex];
      return newGameState;
    });
    
    setCanMove(false);
    setDiceValue(null);
    setSelectedPiece(null);
  };

  // Función para mover una ficha - ahora usa el backend
  const movePiece = (pieceId, diceValueParam = null) => {
    console.log('[DEBUG] movePiece llamado con pieceId:', pieceId, ', diceValueParam:', diceValueParam);
    console.log('[DEBUG] canMove:', canMove, ', diceValue:', diceValue);
    console.log('[DEBUG] availableMoves:', availableMoves);
    console.log('[DEBUG] gameState.currentPlayer:', gameState.currentPlayer);
    console.log('[DEBUG] isTestMode:', isTestMode);
    
    // ✅ Permitir movimiento si hay availableMoves O si canMove y diceValue están activos
    const hasMovesAvailable = (availableMoves && availableMoves.length > 0) || (canMove && diceValue);
    if (!hasMovesAvailable) {
      console.log('[ERROR] No puedes mover: canMove =', canMove, ', diceValue =', diceValue, ', availableMoves =', availableMoves);
      return;
    }

    const [color, pieceIndex] = pieceId.split('_');
    console.log('[DEBUG] Color extraído:', color, ', pieceIndex:', pieceIndex);
    
    // Solo permitir mover fichas del jugador actual
    if (color !== gameState.currentPlayer && !isTestMode) {
      console.log('[ERROR] No es tu turno! Tu color:', color, ', Turno actual:', gameState.currentPlayer);
      return;
    }
    
    // Validación adicional: verificar que sea mi turno (para multijugador)
    if (myPlayerName && gameState.currentPlayer !== myPlayerName && !isTestMode) {
      console.log('[ERROR] No es tu turno! Mi nombre:', myPlayerName, ', Turno actual:', gameState.currentPlayer);
      audioService.playError();
      return;
    }
    
    console.log('[DEBUG] Validación pasada, enviando move_piece al servidor con dice_value:', diceValueParam);

    // Si está en modo test, usar la lógica local
    if (isTestMode) {
      // Calcular el valor total del movimiento
      const moveValue = diceValueParam || (Array.isArray(diceValue) ? diceValue.reduce((a, b) => a + b, 0) : diceValue);
      console.log('[DEBUG] Modo test: moveValue =', moveValue, 'de diceValue =', diceValue);
      
      setGameState(prev => {
        const newGameState = { ...prev };
        const player = newGameState.players.find(p => p.color === color);
        const piece = player.pieces[parseInt(pieceIndex)];
        
        // Calcular nueva posición
        let newPosition;
        
        if (piece.position === -1) {
          // Ficha sale de la cárcel con 6 o más
          if (moveValue >= 6 || (Array.isArray(diceValue) && (diceValue[0] === 6 || diceValue[1] === 6))) {
            // Obtener casilla de salida según el color usando las constantes
            newPosition = SPECIAL_POSITIONS.START_POSITIONS[color];
            
            // Marcar que la ficha acaba de salir de la cárcel para evitar movimiento adicional
            piece.justExitedPrison = true;
            console.log('[DEBUG] Ficha sale de la cárcel a posición:', newPosition);
          } else {
            console.log('Necesitas sacar al menos un 6 para salir de la cárcel');
            return prev; // No se puede mover
          }
        } else {
          // Verificar si la ficha acaba de salir de la cárcel
          if (piece.justExitedPrison) {
            console.log('La ficha acaba de salir de la cárcel, no se puede mover hasta el siguiente turno');
            return prev; // No se puede mover en el mismo turno que sale de la cárcel
          }
          
          // Mover ficha normal
          newPosition = piece.position + moveValue;
          
          // Dar la vuelta al tablero (68 casillas)
          if (newPosition > 68) {
            newPosition = newPosition - 68;
          }
          console.log('[DEBUG] Ficha se mueve de', piece.position, 'a', newPosition);
        }
        
        // Actualizar posición de la ficha
        piece.position = newPosition;
        
        return newGameState;
      });

      // Limpiar y cambiar turno
      setCanMove(false);
      setDiceValue(null);
      
      setTimeout(() => {
        nextTurn();
      }, 500);
    } else {
      // Usar backend - enviar evento al servidor con el dice_value seleccionado
      emit('move_piece', {
        piece_id: parseInt(pieceIndex),
        dice_value: diceValueParam  // Enviar el valor específico del dado a usar
      });
    }
  };

  const handlePieceClick = (pieceId) => {
    // ✅ Bloquear durante transición de turno
    if (isTransitioning) {
      console.log('[DEBUG] ⛔ Click bloqueado - en transición de turno');
      return;
    }
    
    console.log('[DEBUG] ===== PIEZA CLICKEADA =====');
    console.log('[DEBUG] pieceId:', pieceId);
    console.log('[DEBUG] canMove:', canMove);
    console.log('[DEBUG] diceValue:', diceValue);
    console.log('[DEBUG] currentPlayer:', gameState.currentPlayer);
    console.log('[DEBUG] startPhase:', gameState.startPhase);
    console.log('[DEBUG] pendingPieceRelease:', gameState.pendingPieceRelease);
    console.log('[DEBUG] piecesInPrison:', gameState.piecesInPrison);
    
    // Verificar si estamos esperando selección de ficha para liberación
    // Esto puede pasar en fase de inicio O durante el juego normal con dobles
    if (gameState.pendingPieceRelease) {
      console.log('[DEBUG] ===== MODO LIBERACIÓN DE FICHA =====');
      
      // ✅ Prevenir múltiples envíos mientras se procesa una liberación
      if (isReleasingPiece) {
        console.log('[DEBUG] ⚠️ Ya hay una liberación en proceso, ignorando click');
        return;
      }
      
      // Extraer color y índice de la ficha
      const [color, pieceIndex] = pieceId.split('_');
      const pieceIndexNum = parseInt(pieceIndex);
      
      console.log('[DEBUG] Color extraído:', color);
      console.log('[DEBUG] Índice extraído:', pieceIndexNum);
      console.log('[DEBUG] Jugador actual:', gameState.currentPlayer);
      console.log('[DEBUG] Mi color:', myPlayerColor);
      
      // Verificar que sea del jugador correcto
      if (color !== gameState.currentPlayer) {
        console.log('[ERROR] No es tu ficha! Color:', color, ', Turno:', gameState.currentPlayer);
        setMessage('¡No es tu ficha!');
        setTimeout(() => setMessage(''), 2000);
        return;
      }
      
      // Validación adicional: verificar que sea mi turno (para multijugador)
      if (myPlayerName && gameState.currentPlayer !== myPlayerName && !isTestMode) {
        console.log('[ERROR] No es tu turno! Mi nombre:', myPlayerName, ', Turno actual:', gameState.currentPlayer);
        audioService.playError();
        setMessage('¡No es tu turno!');
        setTimeout(() => setMessage(''), 2000);
        return;
      }
      
      // Verificar que la ficha esté en la lista de fichas en prisión
      if (!gameState.piecesInPrison || !gameState.piecesInPrison.includes(pieceIndexNum)) {
        console.log('[DEBUG] Esta ficha NO está en la cárcel');
        console.log('[DEBUG] Fichas en prisión:', gameState.piecesInPrison);
        
        // Si tiene dobles y tiene fichas en prisión, puede elegir MOVER esta ficha en lugar de liberar
        if (diceValue && diceValue.length === 2 && diceValue[0] === diceValue[1]) {
          console.log('[DEBUG] ✅ Tiene dobles, moviendo ficha en lugar de liberar');
          // Limpiar pending_piece_release y continuar con el movimiento normal
          setGameState(prev => ({
            ...prev,
            pendingPieceRelease: false,
            piecesInPrison: []
          }));
          // NO return, continuar con la lógica de movimiento normal abajo
        } else {
          console.log('[ERROR] Esta ficha no está en la cárcel!');
          setMessage('¡Esta ficha no está en la cárcel!');
          setTimeout(() => setMessage(''), 2000);
          return;
        }
      } else {
        // La ficha SÍ está en la cárcel, proceder a liberarla
        console.log('[DEBUG] ✅ Validación pasada, liberando ficha');
        console.log('[DEBUG] Liberando ficha con ID:', pieceIndexNum);
        
        // ✅ Marcar que estamos procesando una liberación
        setIsReleasingPiece(true);
        
        // Verificar si estamos en modo offline
        const isOfflineMode = !connected;
        
        if (isTestMode || isOfflineMode) {
          // Modo local: liberar la ficha directamente
          console.log('[DEBUG] Modo local - liberando ficha sin servidor');
          
          audioService.playPieceMove();
          
          // Obtener la posición de salida según el color
          const startPositions = { red: 39, blue: 22, green: 5, yellow: 56 };
          const startPosition = startPositions[color];
          
          // Actualizar el estado del juego
          setGameState(prev => {
            const newState = { ...prev };
            const player = newState.players.find(p => p.color === color);
            if (player && player.pieces[pieceIndexNum]) {
              player.pieces[pieceIndexNum].position = startPosition;
              console.log('[DEBUG] Ficha movida de prisión a posición:', startPosition);
            }
            
            // Limpiar el estado de liberación
            return {
              ...newState,
              pendingPieceRelease: false,
              piecesInPrison: [],
              startPhase: false, // Terminar fase de inicio después de liberar
              currentAttempts: 0,
              attemptsRemaining: 3
            };
          });
          
          setIsReleasingPiece(false);
          setCanMove(false);
          setDiceValue(null);
          setMessage('¡Ficha liberada! Tira los dados de nuevo');
          
          setTimeout(() => {
            setMessage('');
          }, 2000);
          
          return;
        } else {
          // Modo online: enviar evento al servidor
          emit('release_piece', { piece_id: pieceIndexNum });
          
          // ✅ NO limpiar el estado aquí - esperar la respuesta del servidor
          // El servidor enviará piece_released con can_release_more y actualizará el estado
          console.log('[DEBUG] Esperando respuesta del servidor...');
          return;
        }
      }
    }
    
    // Durante la fase de inicio normal (no liberación), NO se pueden mover fichas
    if (gameState.startPhase && !gameState.pendingPieceRelease) {
      console.log('[ERROR] No se pueden mover fichas durante la fase de inicio sin dobles!');
      return;
    }
    
    // ✅ Permitir movimiento si canMove está activo O si hay movimientos disponibles
    if (!canMove && (!availableMoves || availableMoves.length === 0)) {
      console.log('[ERROR] Primero lanza el dado! canMove:', canMove, ', availableMoves:', availableMoves);
      return;
    }
    
    console.log('[DEBUG] ✅ Validación de canMove pasada. canMove:', canMove, ', availableMoves:', availableMoves);
    
    // ✅ VALIDACIÓN CRÍTICA: Verificar que la ficha NO esté en la cárcel
    // Solo fichas que están en el tablero pueden moverse
    const [color, pieceIndex] = pieceId.split('_');
    const pieceIndexNum = parseInt(pieceIndex);
    
    // Buscar la ficha en el gameState para verificar su posición
    const player = gameState.players?.find(p => p.color === color);
    if (player) {
      const piece = player.pieces?.find(p => p.piece_id === pieceIndexNum);
      if (piece && piece.position === -1) {
        console.log('[ERROR] No puedes mover una ficha que está en la cárcel!');
        console.log('[ERROR] Ficha:', piece);
        setMessage('No puedes mover una ficha que está en la cárcel. Necesitas sacar dobles para liberarla.');
        setTimeout(() => setMessage(''), 3000);
        return;
      }
    }
    
    console.log('[DEBUG] Ficha válida para mover, availableMoves:', availableMoves);
    
    // Si hay múltiples opciones de movimiento, mostrar selector
    if (availableMoves && availableMoves.length > 1) {
      console.log('[DEBUG] Múltiples movimientos disponibles, mostrando selector');
      setPendingPieceForMove(pieceId);
      setSelectedPiece(pieceId);
      setShowMoveSelector(true);
    } else if (availableMoves && availableMoves.length === 1) {
      // Solo hay un movimiento posible, usar automáticamente
      console.log('[DEBUG] Solo un movimiento disponible, moviendo automáticamente con valor:', availableMoves[0]);
      setSelectedPiece(pieceId);
      movePiece(pieceId, availableMoves[0]);
    } else {
      // Fallback: usar la suma de los dados (compatibilidad con código antiguo)
      console.log('[DEBUG] No hay availableMoves, usando suma de dados');
      const totalMove = Array.isArray(diceValue) ? diceValue.reduce((a, b) => a + b, 0) : diceValue;
      setSelectedPiece(pieceId);
      movePiece(pieceId, totalMove);
    }
  };

  const handleBoardClick = (e) => {
    console.log('Tablero clickeado:', e);
  };
  
  // Handlers para MoveSelector
  const handleSelectMove = (selectedMove) => {
    console.log('[MoveSelector] Movimiento seleccionado:', selectedMove);
    if (pendingPieceForMove) {
      setShowMoveSelector(false);
      movePiece(pendingPieceForMove, selectedMove);
    }
  };
  
  const handleCancelMoveSelector = () => {
    console.log('[MoveSelector] Cancelado');
    setShowMoveSelector(false);
    setPendingPieceForMove(null);
    setSelectedPiece(null);
  };

  // ============================================================
  // HANDLERS PARA SISTEMA DE SALAS MULTIJUGADOR
  // ============================================================

  const handleCreateRoom = (data) => {
    console.log('[ROOM] Creando sala:', data);
    if (socket && connected) {
      socket.emit('create_room', data);
    } else {
      audioService.playError();
      showNotification('No estás conectado al servidor', 'error');
    }
  };

  const handleJoinRoom = (data) => {
    console.log('[ROOM] Uniéndose a sala:', data);
    if (socket && connected) {
      socket.emit('join_room', data);
    } else {
      audioService.playError();
      showNotification('No estás conectado al servidor', 'error');
    }
  };

  const handleStartGameFromLobby = () => {
    console.log('[ROOM] Iniciando juego desde lobby');
    if (socket && connected && isHost) {
      socket.emit('start_game_from_lobby', {});
    } else if (!isHost) {
      audioService.playError();
      showNotification('Solo el host puede iniciar el juego', 'warning');
    } else {
      audioService.playError();
      showNotification('No estás conectado al servidor', 'error');
    }
  };

  const handleLeaveLobby = () => {
    console.log('[ROOM] Saliendo del lobby');
    if (socket && connected) {
      socket.emit('leave_room', { roomCode });
      setInLobby(false);
      setRoomCode(null);
      setRoomState(null);
      setIsHost(false);
      
      if (typeof window !== 'undefined') {
        sessionStorage.removeItem('room_code');
        sessionStorage.removeItem('is_host');
      }
      
      setGameStarted(false);
    }
  };
  
  const handleOrderDeterminedFromLobby = (orderedPlayers) => {
    console.log('[TURN ORDER] Orden determinado desde lobby:', orderedPlayers);
    
    // Salir de la fase de determinación
    setInTurnOrderDetermination(false);
    
    // Emitir evento al backend con el orden determinado
    if (socket && roomCode) {
      socket.emit('order_determined', {
        roomCode: roomCode,
        players: orderedPlayers
      });
      
      console.log('[TURN ORDER] Enviando orden al servidor');
    }
  };
  
  const handleBackFromTurnOrder = () => {
    console.log('[TURN ORDER] Volviendo al lobby');
    
    // Volver al lobby
    setInTurnOrderDetermination(false);
    setInLobby(true);
    setLobbyPlayers([]);
    
    // Reproducir sonido
    audioService.playClick();
  };

  const handleStartGame = (gameConfig) => {
    console.log(`[DEBUG] Iniciando juego con configuración:`, gameConfig);
    console.log(`[DEBUG] Estado de conexión: ${connected}`);
    console.log(`[DEBUG] Socket disponible:`, !!socket);
    
    // Extraer información de la configuración
    const { numberOfPlayers: numPlayers, players: orderedPlayers } = gameConfig;
    console.log(`[DEBUG] Número de jugadores: ${numPlayers}`);
    console.log(`[DEBUG] Jugadores ordenados: ${orderedPlayers.length}`);
    console.log(`[DEBUG] Detalles de jugadores:`, orderedPlayers);
    
    setNumberOfPlayers(numPlayers);
    
    if (connected) {
      // Crear un juego específico con los jugadores seleccionados
      const gameData = {
        numberOfPlayers: numPlayers,
        players: orderedPlayers.map((player, index) => ({
          id: player.id,
          name: player.name,
          color: player.color,
          isHuman: player.isHuman !== undefined ? player.isHuman : true, // Preservar valor original
          turnOrder: index // El orden ya viene determinado
        }))
      };
      
      console.log(`[DEBUG] Enviando create_game con datos:`, gameData);
      
      // Crear un nuevo juego en el servidor
      emit('create_game', gameData);
      
      console.log(`[DEBUG] Evento create_game enviado`);
    } else {
      console.log(`[DEBUG] No conectado, iniciando modo offline`);
      // Modo offline - iniciar localmente con los jugadores seleccionados
      setGameStarted(true);
      setActivePlayers(orderedPlayers);
      
      // Crear estado inicial del juego con los jugadores seleccionados
      const initialState = {
        currentPlayer: orderedPlayers[0].color,
        diceValue: null,
        startPhase: true, // Fase de inicio
        currentAttempts: 0,
        attemptsRemaining: 3,
        canMove: false,
        status: 'playing',
        players: orderedPlayers.map((player, index) => ({
          player_id: player.id,
          name: player.name,
          color: player.color,
          isHuman: player.isHuman !== undefined ? player.isHuman : true,
          turnOrder: index,
          pieces_in_goal: 0,
          pieces: [
            { piece_id: 0, position: -1, is_in_goal: false },
            { piece_id: 1, position: -1, is_in_goal: false },
            { piece_id: 2, position: -1, is_in_goal: false },
            { piece_id: 3, position: -1, is_in_goal: false }
          ]
        }))
      };
      
      console.log('[DEBUG] Estado inicial del juego offline:', initialState);
      setGameState(initialState);
      
      // Si el primer jugador es un bot, hacer que lance automáticamente
      if (!orderedPlayers[0].isHuman) {
        console.log('[DEBUG] Primer jugador es un bot, iniciando turno automático en 2s');
        setTimeout(() => {
          handleDiceRoll();
        }, 2000);
      }
    }
  };

  const handleShowRules = () => {
    setShowRules(true);
  };

  const handleCloseRules = () => {
    setShowRules(false);
  };
  
  const handleCloseCelebration = () => {
    setShowCelebration(false);
    setWinner(null);
    setGameStarted(false);
    // Reiniciar el estado del juego
    setGameState(initialGameState);
    setDiceValue(null);
    setCanMove(false);
    setSelectedPiece(null);
  };

  // Verificar si hay movimientos disponibles para el jugador actual
  const checkMovesAvailable = () => {
    if (!diceValue || !canMove) return true; // Si no hay dado lanzado, asumimos que puede mover
    
    const currentGameState = getCurrentGameState();
    
    // Encontrar el jugador actual
    const currentPlayer = currentGameState.players?.find(player => 
      player.color === gameState.currentPlayer
    );
    
    if (!currentPlayer || !currentPlayer.pieces) return false;
    
    const currentPlayerPieces = currentPlayer.pieces;
    
    // Verificar si alguna ficha puede moverse
    for (const piece of currentPlayerPieces) {
      if (piece.position === -1 || piece.position === 'prison') {
        // Puede salir de la cárcel con 6
        if (diceValue === 6) return true;
      } else {
        // Puede moverse si no está en la posición final
        if (!piece.is_in_goal && piece.position !== 'center') return true;
      }
    }
    
    return false; // No hay movimientos disponibles
  };

  // Durante la fase de inicio, nunca hay "sin movimientos disponibles"
  const noMovesAvailable = !gameState.startPhase && diceValue && canMove && !checkMovesAvailable();

  // Helper: Obtener el color del jugador local (este cliente)
  const getMyPlayerColor = () => {
    if (!socket?.id || !gameState.players) return null;
    const myPlayer = gameState.players.find(p => p.player_id === socket.id);
    return myPlayer ? myPlayer.color : null;
  };
  
  // Helper: Obtener el nombre del jugador local
  const getMyPlayerName = () => {
    if (!socket?.id || !gameState.players) return null;
    const myPlayer = gameState.players.find(p => p.player_id === socket.id);
    return myPlayer ? myPlayer.name : null;
  };
  
  const myPlayerColor = getMyPlayerColor();
  const myPlayerName = getMyPlayerName();

  // Obtener el estado actual del juego
  // Si estamos en determinación de orden desde lobby
  if (inTurnOrderDetermination && lobbyPlayers.length > 0) {
    return (
      <>
        <TurnOrderDetermination
          players={lobbyPlayers}
          onOrderDetermined={handleOrderDeterminedFromLobby}
          onBack={handleBackFromTurnOrder}
          socket={socket}
          roomCode={roomCode}
          myPlayerId={socket?.id}
          isHost={isHost}
        />
        
        {/* Notificaciones */}
        {notification && (
          <Notification
            message={notification.message}
            type={notification.type}
            onClose={() => setNotification(null)}
          />
        )}
      </>
    );
  }
  
  // Si estamos en el lobby, mostrar el lobby
  if (inLobby) {
    return (
      <>
        <Lobby
          roomCode={roomCode}
          roomState={roomState}
          isHost={isHost}
          onStartGame={handleStartGameFromLobby}
          onLeaveLobby={handleLeaveLobby}
          socket={socket}
        />
        
        {/* Notificaciones */}
        {notification && (
          <Notification
            message={notification.message}
            type={notification.type}
            onClose={() => setNotification(null)}
          />
        )}
      </>
    );
  }

  // Si el juego no ha iniciado, mostrar el menú
  if (!gameStarted) {
    return (
      <>
        <Menu 
          onStartGame={handleStartGame}
          onShowRules={handleShowRules}
          onCreateRoom={handleCreateRoom}
          onJoinRoom={handleJoinRoom}
          availableColors={availableColors}
          showColorSelector={showColorSelector}
          onRoomInfoReceived={() => setShowColorSelector(false)}
        />
        {showRules && <Rules onClose={handleCloseRules} />}
        
        {/* Notificaciones */}
        {notification && (
          <Notification
            message={notification.message}
            type={notification.type}
            onClose={() => setNotification(null)}
          />
        )}
      </>
    );
  }

  return (
    <div className={styles.container}>
      {/* Control de audio */}
      <AudioControl />
      
      {/* Celebración de victoria */}
      {showCelebration && winner && (
        <Celebration winner={winner} onClose={handleCloseCelebration} />
      )}
      
      {/* Selector de movimientos */}
      {showMoveSelector && (
        <MoveSelector 
          availableMoves={availableMoves}
          onSelectMove={handleSelectMove}
          onCancel={handleCancelMoveSelector}
          selectedPiece={selectedPiece}
        />
      )}
      
      {/* Overlay de transición de turno */}
      {isTransitioning && (
        <div className={styles.transitionOverlay}>
          <div className={styles.transitionMessage}>
            <h2>🔄 {transitionMessage}</h2>
            {console.log('[RENDER] 🎨 Overlay de transición renderizado')}
          </div>
        </div>
      )}
      {console.log('[RENDER] isTransitioning:', isTransitioning, 'transitionMessage:', transitionMessage)}
      
      <main className={styles.main}>
        <div className={styles.header}>
          <h1 className={styles.title}>Parchese Game</h1>
        </div>

        {/* Panel de debug en esquina superior derecha */}
        {process.env.NODE_ENV === 'development' && showDebug && (
          <div className={styles.debugPanel}>
            <button
              className={styles.debugClose}
              onClick={() => setShowDebug(false)}
              aria-label="Cerrar panel de debug"
            >
              ✖
            </button>
            <div className={styles.debugHeader}>🔍 DEBUG PANEL</div>
            <div className={styles.debugContent}>
              <div>Local canMove: {canMove ? 'true' : 'false'}</div>
              <div>Local diceValue: {Array.isArray(diceValue) ? `[${diceValue.join(', ')}]` : (diceValue || 'null')}</div>
              <div>Local currentPlayer: "{gameState.currentPlayer || 'empty'}"</div>
              <div>Local isRolling: {isRolling ? 'true' : 'false'}</div>
              <div>showingNoMovesResult: {showingNoMovesResult ? 'true' : 'false'}</div>
              <div>message: "{message || 'empty'}"</div>
              <hr className={styles.debugSeparator} />
              <div style={{color: gameState.startPhase ? '#f39c12' : 'white', fontWeight: gameState.startPhase ? 'bold' : 'normal'}}>
                startPhase: {gameState.startPhase ? 'true ⚠️' : 'false'}
              </div>
              <div>currentAttempts: {gameState.currentAttempts || 0}</div>
              <div>attemptsRemaining: {gameState.attemptsRemaining || 0}</div>
              <hr className={styles.debugSeparator} />
              <div>GameState canMove: {gameState.canMove ? 'true' : 'false'}</div>
              <div>GameState currentPlayer: "{gameState.currentPlayer || 'empty'}"</div>
              <hr className={styles.debugSeparator} />
              <div>gameStarted: {gameStarted ? 'true' : 'false'}</div>
              <div>activePlayers: {activePlayers.length}</div>
              <div>gameState.players: {gameState.players?.length || 0}</div>
              <div className={styles.debugPlayers}>
                Players: {gameState.players?.map(p => `${p.name}(${p.color})`).join(', ') || 'none'}
              </div>
            </div>
            <div className={styles.debugActions}>
              <button 
                onClick={handlePing} 
                disabled={!connected}
                className={styles.debugButton}
              >
                Test Ping
              </button>
              <button 
                onClick={handleDebugStatus} 
                disabled={!connected}
                className={styles.debugButton}
              >
                Debug Status
              </button>
              <button 
                onClick={() => setIsTestMode(!isTestMode)}
                className={styles.debugButton}
                style={{ 
                  backgroundColor: isTestMode ? '#f59e0b' : '#6366f1'
                }}
              >
                {isTestMode ? '🔍 Test ON' : '🎯 Test Mode'}
              </button>
            </div>
          </div>
        )}
        {process.env.NODE_ENV === 'development' && !showDebug && (
          <button
            className={styles.debugToggle}
            onClick={() => setShowDebug(true)}
            aria-label="Abrir panel de debug"
            title="Abrir panel de debug"
          >
            🐞
          </button>
        )}
        
        {/* Status de conexión y jugadores */}
        <div className={styles.status}>
          <p>Estado de conexión: 
            <span className={connected ? styles.connected : styles.disconnected}>
              {connected ? ' Conectado' : ' Desconectado'}
            </span>
          </p>
          <p>Jugadores activos: {getActivePlayerColors().length}</p>
          <div className={styles.playersInfo}>
            {getActivePlayerColors().map(color => {
              const playerInfo = getPlayerInfo(color);
              return (
                <span key={color} className={styles.playerBadge} style={{
                  backgroundColor: color === 'red' ? '#ff4444' : 
                                 color === 'blue' ? '#4444ff' :
                                 color === 'green' ? '#44ff44' : '#ffff44',
                  color: 'white',
                  padding: '4px 8px',
                  borderRadius: '12px',
                  margin: '2px',
                  fontSize: '0.8rem',
                  fontWeight: 'bold'
                }}>
                  {playerInfo.name}
                </span>
              );
            })}
          </div>
          {message && <p>Servidor: {message}</p>}
        </div>

        {/* Área principal de juego */}
        <div className={styles.gameArea}>
          {/* Tablero de juego */}
          <div className={styles.boardSection}>
            <Board
              gameState={getCurrentGameState()}
              onPieceClick={handlePieceClick}
              onBoardClick={handleBoardClick}
              canMove={canMove}
              currentPlayer={gameState.currentPlayer}
              selectedPiece={selectedPiece}
            />
          </div>

          {/* Panel lateral derecho con controles */}
          <div className={styles.sidePanel}>
            {/* Header del juego */}
            <div className={styles.gameHeader}>
              <div className={styles.gameTitle}>
                <h2>Parchese</h2>
                <button className={styles.menuButton}>
                  <span>←</span> Menú
                </button>
              </div>
              <div className={styles.gameStatus}>
                <div className={styles.statusBadge}>
                  <span className={styles.statusIcon}>🎯</span>
                  En Juego
                </div>
                <div className={styles.playersCount}>
                  <span className={styles.playersIcon}>👥</span>
                  {getActivePlayerColors().length} Jugadores
                </div>
              </div>
            </div>

            {/* Indicador de turno actual */}
            <div className={styles.currentTurn} style={{
              borderColor: gameState.currentPlayer === 'red' ? '#dc2626' :
                          gameState.currentPlayer === 'blue' ? '#2563eb' :
                          gameState.currentPlayer === 'green' ? '#16a34a' : '#ca8a04',
              opacity: isTransitioning ? 0.3 : 1
            }}>
              <div className={styles.turnHeader}>
                <h3>Turno de</h3>
                <div 
                  className={styles.playerAvatar}
                  style={{
                    backgroundColor: gameState.currentPlayer === 'red' ? '#dc2626' :
                                    gameState.currentPlayer === 'blue' ? '#2563eb' :
                                    gameState.currentPlayer === 'green' ? '#16a34a' : '#ca8a04'
                  }}
                >
                  👤
                </div>
              </div>
              <h2 className={styles.playerName}>
                {(() => {
                  if (gameState.currentPlayer) {
                    return getPlayerInfo(gameState.currentPlayer).name;
                  } else if (gameState.players && gameState.players.length > 0) {
                    return getPlayerInfo(gameState.players[0].color).name;
                  }
                  return 'Jugador 1';
                })()}
              </h2>
              {/* Indicador de turno propio */}
              {myPlayerName && gameState.currentPlayer && (
                <div style={{
                  marginTop: '8px',
                  padding: '6px 12px',
                  borderRadius: '12px',
                  fontSize: '0.85rem',
                  fontWeight: '600',
                  backgroundColor: myPlayerName === gameState.currentPlayer ? '#10b981' : '#6b7280',
                  color: 'white',
                  textAlign: 'center'
                }}>
                  {myPlayerName === gameState.currentPlayer ? '🎮 ¡Tu turno!' : '⏳ Esperando...'}
                </div>
              )}
              <div className={styles.turnStatus}>
                {gameState.startPhase ? (
                  <>
                    <p className={styles.statusText}>🎲 Fase de Inicio</p>
                    <p className={styles.statusSubtext}>Intenta sacar dobles para liberar tus fichas</p>
                  </>
                ) : (
                  <p className={styles.statusText}>
                    {message ? message : (
                      diceValue ? '🎯 Selecciona una ficha' : '🎲 Esperando movimiento...'
                    )}
                  </p>
                )}
              </div>
            </div>

            {/* Sección de dados */}
            <div className={styles.diceSection}>
              {/* Header arriba, centrado y en columna */}
              <div className={styles.diceHeader}>
                <h3>Lanzar Dados</h3>
                <div className={styles.diceIcon}>🎲</div>
              </div>
              
              {/* Usar el componente Dice que incluye el banner de dobles */}
              <Dice
                value={diceValue}
                isRolling={isRolling}
                onRoll={handleDiceRoll}
                disabled={
                  !connected || 
                  isRolling || 
                  (canMove && !gameState.startPhase) ||
                  showingNoMovesResult ||
                  gameState.pendingPieceRelease ||
                  (gameState.currentPlayer && myPlayerName && gameState.currentPlayer !== myPlayerName) ||
                  (isTransitioning && myPlayerName && gameState.currentPlayer !== myPlayerName)
                }
                playerColor={gameState.currentPlayer || 'blue'}
                noMovesAvailable={showingNoMovesResult}
                startPhaseAttempts={gameState.startPhase && gameState.currentAttempts ? {
                  current: gameState.currentAttempts,
                  max: 3
                } : null}
              />
            </div>

            {/* Lista de jugadores */}
            <div className={styles.playersList}>
              <div className={styles.playersHeader}>
                <div className={styles.playersIcon}>👥</div>
                <h3>Jugadores</h3>
              </div>
              
              <div className={styles.playersContainer}>
                {getActivePlayerColors().map((color, index) => {
                  const playerInfo = getPlayerInfo(color);
                  const isCurrentPlayer = color === gameState.currentPlayer;
                  
                  // Calculate real progress based on piece positions on the board
                  const player = gameState.players?.find(p => p.color === color);
                  const totalPieces = 4;
                  
                  let progress = 0;
                  if (player && player.pieces) {
                    const BOARD_SIZE = 68; // Main board squares
                    const GOAL_PATH_LENGTH = 8; // Squares in the goal path
                    const TOTAL_JOURNEY = BOARD_SIZE + GOAL_PATH_LENGTH; // 76 total squares
                    
                    let totalProgress = 0;
                    
                    player.pieces.forEach(piece => {
                      if (piece.is_in_goal) {
                        // Piece reached goal: 100% for this piece
                        totalProgress += 100;
                      } else if (piece.position === -1) {
                        // Piece in prison: 0% for this piece
                        totalProgress += 0;
                      } else if (piece.position >= 0 && piece.position < BOARD_SIZE) {
                        // Piece on main board: calculate percentage based on position
                        totalProgress += (piece.position / TOTAL_JOURNEY) * 100;
                      } else if (piece.position >= BOARD_SIZE) {
                        // Piece in goal path (68-75)
                        const goalPathPosition = piece.position - BOARD_SIZE;
                        const progressOnGoalPath = BOARD_SIZE + goalPathPosition;
                        totalProgress += (progressOnGoalPath / TOTAL_JOURNEY) * 100;
                      }
                    });
                    
                    // Average progress across all 4 pieces
                    progress = Math.round(totalProgress / 4);
                  }
                  
                  return (
                    <div 
                      key={color} 
                      className={`${styles.playerCard} ${isCurrentPlayer ? styles.activePlayer : ''}`}
                    >
                      <div 
                        className={styles.playerAvatar}
                        style={{
                          backgroundColor: color === 'red' ? '#dc2626' :
                                          color === 'blue' ? '#2563eb' :
                                          color === 'green' ? '#16a34a' : '#ca8a04'
                        }}
                      >
                        👤
                      </div>
                      <div className={styles.playerInfo}>
                        <h4 className={styles.playerCardName}>{playerInfo.name}</h4>
                        <p className={styles.playerStatus}>
                          {isCurrentPlayer ? 'Jugando...' : 'Esperando'}
                        </p>
                        <div className={styles.progressContainer}>
                          <span className={styles.progressLabel}>Progreso</span>
                          <span className={styles.progressValue}>{progress}%</span>
                        </div>
                        <div className={styles.progressBar}>
                          <div 
                            className={styles.progressFill}
                            style={{ 
                              width: `${progress}%`,
                              backgroundColor: color === 'red' ? '#dc2626' :
                                             color === 'blue' ? '#2563eb' :
                                             color === 'green' ? '#16a34a' : '#ca8a04'
                            }}
                          ></div>
                        </div>
                      </div>
                      {isCurrentPlayer && (
                        <div className={styles.crownIcon}>👑</div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </main>
      
      {/* Footer con información del proyecto */}
      <footer className={styles.gameFooter}>
        <div className={styles.footerContent}>
          <div className={styles.footerSection}>
            <h3>🎲 Parchese Digital</h3>
            <p>Juego tradicional de mesa adaptado para la era digital</p>
          </div>
          
          <div className={styles.footerSection}>
            <h4>🏆 Reglas del Juego</h4>
            <ul>
              <li>Saca todas tus fichas al tablero</li>
              <li>Lleva las 4 fichas a la meta</li>
              <li>Captura fichas enemigas para enviarlas a prisión</li>
              <li>Usa estrategia y suerte para ganar</li>
            </ul>
          </div>
          
          <div className={styles.footerSection}>
            <h4>💻 Tecnología</h4>
            <ul>
              <li>Next.js 14 - Framework React</li>
              <li>Socket.IO - Comunicación en tiempo real</li>
              <li>Python Flask - Backend del juego</li>
              <li>CSS Modules - Estilos modulares</li>
            </ul>
          </div>
          
          <div className={styles.footerSection}>
            <h4>📊 Estado del Tablero</h4>
            <div className={styles.boardStats}>
              <div className={styles.stat}>
                <span className={styles.statIcon}>👥</span>
                <span>{getActivePlayerColors().length}/4 Jugadores</span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statIcon}>🔄</span>
                <span>Turno: {gameState.currentPlayer || 'N/A'}</span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statIcon}>🎯</span>
                <span>{gameStarted ? 'En Juego' : 'Esperando'}</span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statIcon}>🌐</span>
                <span>{connected ? 'Conectado' : 'Desconectado'}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className={styles.footerBottom}>
          <p>&copy; 2025 Parchese Digital - Proyecto de Sistemas Distribuidos</p>
          <p>Universidad - Semestre 8</p>
        </div>
      </footer>
      
      {/* Notificaciones */}
      {notification && (
        <Notification
          message={notification.message}
          type={notification.type}
          onClose={() => setNotification(null)}
        />
      )}
    </div>
  );
}

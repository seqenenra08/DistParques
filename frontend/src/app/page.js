'use client';

import { useSocket } from '../hooks/useSocket';
import { useEffect, useState } from 'react';
import Board from '../components/Board/Board';
import Dice from '../components/Game/Dice';
import Menu from '../components/Menu/Menu';
import Rules from '../components/Menu/Rules';
import Celebration from '../components/Game/Celebration';

import TurnOrderDetermination from '../components/Menu/TurnOrderDetermination';
import Notification from '../components/Notification/Notification';
import { initialGameState } from '../utils/mockData';
import styles from './page.module.css';

export default function Home() {
  const { socket, connected, emit } = useSocket();
  
  // Estados principales
  const [gameState, setGameState] = useState(initialGameState);
  const [gameStarted, setGameStarted] = useState(false);
  const [myPlayerInfo, setMyPlayerInfo] = useState(null); // { id, nombre, color }
  const [showTurnOrderDetermination, setShowTurnOrderDetermination] = useState(false);
  
  // Estados de sala
  const [roomCode, setRoomCode] = useState(null);
  const [showRoomCode, setShowRoomCode] = useState(false);
  const [roomPlayers, setRoomPlayers] = useState([]);
  const [availableColors, setAvailableColors] = useState([]);
  const [pendingRoomCode, setPendingRoomCode] = useState(null);
  
  // Estados de dados
  const [diceValue, setDiceValue] = useState(null);
  const [lastDiceRolled, setLastDiceRolled] = useState(null);
  const [isRolling, setIsRolling] = useState(false);
  const [canMove, setCanMove] = useState(false);
  
  // Estados UI
  const [message, setMessage] = useState('');
  const [notification, setNotification] = useState(null);
  const [showRules, setShowRules] = useState(false);
  const [showCelebration, setShowCelebration] = useState(false);
  const [winner, setWinner] = useState(null);
  
  // Selector de movimientos
  const [availableMoves, setAvailableMoves] = useState([]);

  const [pendingPieceForMove, setPendingPieceForMove] = useState(null);
  const [selectedPiece, setSelectedPiece] = useState(null);
  
  // División de dados
  const [canSplitDice, setCanSplitDice] = useState(false);
  const [splitMode, setSplitMode] = useState(false);
  const [splitMovements, setSplitMovements] = useState([]);
  const [currentSplitDice, setCurrentSplitDice] = useState(null);

  // Normaliza el estado recibido del servidor para asegurar que siempre exista currentPlayer
  const normalizeState = (estado) => {
    const current = estado?.jugador_actual ?? estado?.currentPlayer ?? estado?.turno_actual ?? null;
    return { ...estado, currentPlayer: current };
  };
  
  useEffect(() => {
    
    const handleFirstInteraction = () => {
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

  // Escuchar eventos del servidor
  useEffect(() => {
    if (!socket) return;

    // Sala creada exitosamente
    socket.on('SALA_CREADA', (data) => {
      console.log('[SALA_CREADA] 📥 Evento recibido:', data);
      if (data.exito) {
        const playerInfo = {
          id: data.jugador.color,
          nombre: data.jugador.nombre,
          color: data.jugador.color,
          es_host: data.jugador.es_host
        };
        console.log('[SALA_CREADA] 👤 Guardando info del jugador:', playerInfo);
        console.log('[SALA_CREADA] 🔑 Código de sala:', data.codigo_sala);
        
        setMyPlayerInfo(playerInfo);
        setRoomCode(data.codigo_sala);
        setShowRoomCode(true);
        
        console.log('[SALA_CREADA] ✅ Estados actualizados - showRoomCode: true, roomCode:', data.codigo_sala);
        
        // Actualizar lista de jugadores si viene en el estado
        if (data.estado_sala?.jugadores) {
          console.log('[SALA_CREADA] 👥 Jugadores en sala:', data.estado_sala.jugadores);
          setRoomPlayers(data.estado_sala.jugadores);
        }
        
        showNotification(`Sala creada: ${data.codigo_sala}`, 'success');
      }
    });

    // Partida iniciada
    socket.on('PARTIDA_INICIADA', (data) => {
      console.log('[PARTIDA_INICIADA]', data);
      
      // Si está esperando dados iniciales, mostrar determinación de orden
      if (data.esperando_dados_inicio) {
        console.log('[PARTIDA_INICIADA] 🎲 Esperando dados iniciales para determinar orden');
        setShowTurnOrderDetermination(true);
        setGameState(normalizeState(data.estado));
      } else {
        // Iniciar juego directamente (modo antiguo)
        setGameStarted(true);
        setGameState(normalizeState(data.estado));
      }
    });

    // Resultado de lanzamiento de dados
    socket.on('DICE_RESULT', (data) => {
      console.log('[DICE_RESULT]', data);
      
      setIsRolling(false);
      
      // Solo actualizar dados si es mi turno
      // Verificar si este resultado de dados es para mí comparando nombres
      if (myPlayerInfo && data.jugador && data.jugador !== myPlayerInfo.nombre) {
        console.log('[DICE_RESULT] ⏭️ Ignorando - no es mi turno (jugador:', data.jugador, ', yo:', myPlayerInfo.nombre, ')');
        return;
      }
      
      setDiceValue(data.dados);
      setLastDiceRolled(data.dados);
      
      if (data.error) {
        showNotification(data.error, 'error');
        return;
      }
      
      // Si todas están en cárcel y no sacó par
      if (data.todas_en_carcel && !data.es_par) {
        
        // Si se pasó el turno (agotó los 3 intentos)
        if (data.turn_passed) {
          setTimeout(() => {
            setDiceValue(null);
            setLastDiceRolled(null);
            setMessage('');
            setCanMove(false);
            setIsRolling(false);
          }, 1000);
          return;
        }
        

        
        // Si aún tiene intentos, mantener los dados visibles
        if (data.can_retry) {
          setTimeout(() => {
            setDiceValue(null);
            setMessage('');
          }, 2000);
        } else {
          // Sin más intentos, limpiar
          setTimeout(() => {
            setDiceValue(null);
            setMessage('');
            setCanMove(false);
          }, 2000);
        }
        return;
      }
      
      // Si sacó par con todas en cárcel
      if (data.todas_en_carcel && data.es_par) {
        console.log('[DICE_RESULT] ✅ Par con todas en cárcel - Dados:', data.dados);
        setCanMove(true);
        setMessage('✅ ¡PAR! Haz clic en una ficha de la cárcel para sacarla');
        
        // Preparar movimientos (para sacar de cárcel)
        setAvailableMoves([data.dados[0]]);
        return;
      }
      
      // Puede mover (caso normal)
      if (data.es_par) {
        // Los dobles se manejan silenciosamente
      }
      
      setCanMove(true);
      
      // Preparar movimientos disponibles
      const moves = [data.dados[0], data.dados[1]];
      if (data.dados[0] !== data.dados[1]) {
        moves.push(data.suma);
      }
      setAvailableMoves(moves);
      
      // Verificar si puede dividir dados
      if (data.puede_dividir_dados && data.dados[0] !== data.dados[1]) {
        console.log('[DICE_RESULT] ✂️ Puede dividir dados');
        setCanSplitDice(true);
        setMessage(`✂️ Dados: ${data.dados[0]} y ${data.dados[1]}. Puedes dividirlos o usar la suma (${data.suma})`);
      } else {
        setCanSplitDice(false);
        setMessage(data.mensaje || '');
      }
      if (data.puede_dividir_dados) {
        console.log('[DICE_RESULT] ✂️ Puede dividir dados:', data.opciones_division);
        setCanSplitDice(true);
        setSplitOptions({
          dados: data.dados,
          suma: data.suma,
          fichas_movibles: data.fichas_movibles,
          opciones_division: data.opciones_division
        });
        setMessage(`Dados: ${data.dados[0]} + ${data.dados[1]} = ${data.suma}. Haz clic en 'Dividir dados' o elige una ficha`);
      } else {
        setCanSplitDice(false);
        setSplitOptions(null);
        setMessage(data.mensaje || '');
      }
    });

    // Resultado de movimiento
    socket.on('MOVE_RESULT', (data) => {
      console.log('[MOVE_RESULT]', data);
      
      if (data.error) {
        // Mostrar fichas sugeridas en el error si las hay
        let errorMsg = data.error;
        if (data.fichas_sugeridas && data.fichas_sugeridas.length > 0) {
          errorMsg += ` → Fichas disponibles: ${data.fichas_sugeridas.join(', ')}`;
        }
        showNotification(errorMsg, 'warning');
        
        // Si el error permite intentar con otra ficha, NO limpiar el estado
        if (data.mantener_turno || data.puede_intentar_otra) {
          console.log('[MOVE_RESULT] ⚠️ Error pero puedes intentar con otra ficha');
          console.log('[MOVE_RESULT] 🎲 Manteniendo: diceValue=', diceValue, ', canMove=', canMove);
          // Solo limpiar la ficha seleccionada para que pueda elegir otra
          setSelectedPiece(null);
          // MANTENER canMove en true para que pueda seleccionar otra ficha
          setCanMove(true);
          return;
        }
        
        // Si es un error grave, limpiar todo
        setCanMove(false);
        setDiceValue(null);
        setLastDiceRolled(null);
        setSelectedPiece(null);
        setIsRolling(false);
        return;
      }
      
      // Solo procesar si es el turno actual del que está jugando
      // El MOVE_RESULT se hace broadcast pero solo el jugador que se está moviendo debe procesarlo
      if (myPlayerInfo && gameState && gameState.jugador_actual !== myPlayerInfo.nombre) {
        console.log('[MOVE_RESULT] ⏭️ Ignorando - no es mi turno (jugador actual:', gameState.jugador_actual, ', yo:', myPlayerInfo.nombre, ')');
        return;
      }
      
      // Limpiar estado de movimiento
      setCanMove(false);
      setDiceValue(null);
      setLastDiceRolled(null);
      setSelectedPiece(null);
      setAvailableMoves([]);
      setPendingPieceForMove(null);
      setCanSplitDice(false);
      setSplitMode(false);
      setSplitMovements([]);
      setCurrentSplitDice(null);
      setIsRolling(false);
      
      // Las acciones del juego se manejan visualmente sin notificaciones molestas
      
      // Verificar victoria
      if (data.ganador) {
        setWinner({ name: data.ganador, color: gameState.currentPlayer });
        setShowCelebration(true);
      }
    });

    // Cambio de turno
    socket.on('TURN_CHANGE', (data) => {
      console.log('[TURN_CHANGE]', data);
      setGameState(normalizeState(data.estado));
      
      // Limpiar estado de dados y movimientos
      setDiceValue(null);
      setLastDiceRolled(null);
      setCanMove(false);
      setAvailableMoves([]);
      setSelectedPiece(null);
      setCanSplitDice(false);
      setSplitMode(false);
      setSplitMovements([]);
      setCurrentSplitDice(null);
      setMessage('');
      setIsRolling(false);
      
      // Los cambios de turno se manejan silenciosamente
    });

    // Estado actualizado
    socket.on('UPDATE', (data) => {
      console.log('[UPDATE]', data.estado);
      console.log('[UPDATE] Estado actual antes:', {
        previousPlayer: gameState?.jugador_actual,
        currentPlayer: data.estado?.jugador_actual,
        myPlayerInfo: myPlayerInfo?.nombre,
        canMove,
        diceValue,
        isRolling
      });
      
      const previousPlayerName = gameState?.jugador_actual;
      const currentPlayerName = data.estado.jugador_actual;
      const turnChanged = previousPlayerName && previousPlayerName !== currentPlayerName;
      const isMyTurnNow = myPlayerInfo && currentPlayerName === myPlayerInfo.nombre;
      
      setGameState(normalizeState(data.estado));
      
      if (!isMyTurnNow) {
        // No es mi turno, limpiar TODO
        console.log('[UPDATE] 🔄 No es mi turno, limpiando estado completo');
        setDiceValue(null);
        setLastDiceRolled(null);
        setCanMove(false);
        setAvailableMoves([]);
        setSelectedPiece(null);
        setCanSplitDice(false);
        setSplitMode(false);
        setSplitMovements([]);
        setCurrentSplitDice(null);
        setMessage('');
        setIsRolling(false);
      } else if (turnChanged) {
        // Es mi turno y CAMBIÓ (acabo de recibir el turno)
        console.log('[UPDATE] ✅ Recibí el turno, limpiando datos previos');
        setDiceValue(null);
        setLastDiceRolled(null);
        setCanMove(false);
        setAvailableMoves([]);
        setSelectedPiece(null);
        setCanSplitDice(false);
        setSplitMode(false);
        setSplitMovements([]);
        setCurrentSplitDice(null);
        setMessage('');
        setIsRolling(false);
      } else {
        // Es mi turno y NO cambió (continuación del turno, relanzar dados)
        console.log('[UPDATE] 📋 Turno continúa, limpiando datos pero mantiendo canMove');
        setDiceValue(null);
        setLastDiceRolled(null);
        setSelectedPiece(null);
        setMessage('');
        setIsRolling(false);
      }
    });

    // Información de fichas
    socket.on('FICHAS_INFO', (data) => {
      console.log('[FICHAS_INFO]', data.fichas);
      // Mostrar info de fichas si es necesario
    });

    // Jugador unido a la sala
    socket.on('JUGADOR_UNIDO', (data) => {
      console.log('[JUGADOR_UNIDO]', data);
      if (data.estado_sala && data.estado_sala.jugadores) {
        setRoomPlayers(data.estado_sala.jugadores);
        // Jugador se unió silenciosamente
      }
    });

    // Colores disponibles (cuando te unes a una sala)
    socket.on('COLORES_DISPONIBLES', (data) => {
      console.log('[COLORES_DISPONIBLES]', data);
      if (data.exito) {
        setAvailableColors(data.colores);
        setPendingRoomCode(data.codigo_sala);
        // Selección de color se maneja en la interfaz
      }
    });

    // Unido a sala exitosamente
    socket.on('UNIDO_A_SALA', (data) => {
      console.log('[UNIDO_A_SALA]', data);
      if (data.exito) {
        setMyPlayerInfo({
          id: data.jugador.color,
          nombre: data.jugador.nombre,
          color: data.jugador.color,
          es_host: data.jugador.es_host
        });
        setRoomCode(data.codigo_sala);
        setShowRoomCode(true);
        
        // Actualizar lista de jugadores
        if (data.estado_sala?.jugadores) {
          setRoomPlayers(data.estado_sala.jugadores);
        }
        
        // Limpiar colores disponibles y código pendiente
        setAvailableColors([]);
        setPendingRoomCode(null);
        
        showNotification(`Te has unido a la sala ${data.codigo_sala}`, 'success');
      }
    });

    // Dado inicial lanzado (para determinar orden)
    socket.on('DADO_INICIO', (data) => {
      console.log('[DADO_INICIO]', data);
      // Resultado de dados para orden se muestra visualmente
    });

    // Turno determinado (orden establecido)
    socket.on('TURNO_DETERMINADO', (data) => {
      console.log('[TURNO_DETERMINADO]', data);
      // NO cerrar el componente aquí, dejar que el usuario vea los resultados
      // El componente TurnOrderDetermination manejará este evento
      // El orden se muestra en la interfaz
    });

    // Error del servidor
    socket.on('ERROR', (data) => {
      console.log('[ERROR]', data);
      showNotification(data.mensaje || 'Error desconocido', 'error');
    });

    // Limpieza
    return () => {
      socket.off('SALA_CREADA');
      socket.off('PARTIDA_INICIADA');
      socket.off('DICE_RESULT');
      socket.off('MOVE_RESULT');
      socket.off('TURN_CHANGE');
      socket.off('UPDATE');
      socket.off('FICHAS_INFO');
      socket.off('JUGADOR_UNIDO');
      socket.off('COLORES_DISPONIBLES');
      socket.off('UNIDO_A_SALA');
      socket.off('DADO_INICIO');
      socket.off('TURNO_DETERMINADO');
      socket.off('ERROR');
    };
  }, [socket]);

  // Helpers
  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
  };

  const isMyTurn = () => {
    const current = gameState?.currentPlayer || gameState?.jugador_actual || null;
    if (!myPlayerInfo || !current) return false;
    return current === myPlayerInfo.nombre;
  };

  // Handlers
  const handleStartGame = (gameConfig) => {
    console.log('[START GAME]', gameConfig);
    
    const { numberOfPlayers, players } = gameConfig;
    
    if (!connected) {
      showNotification('No estás conectado al servidor', 'error');
      return;
    }
    
    // Crear sala con jugadores configurados
    emit('CREAR_SALA', {
      playerName: players[0].name,
      maxPlayers: numberOfPlayers,
      numBots: players.filter(p => !p.isHuman).length,
      color: players[0].color,
      players: players // Enviar array completo con info de todos los jugadores
    });
  };

  const handleCreateRoom = (roomConfig) => {
    console.log('[CREATE ROOM]', roomConfig);
    
    if (!connected) {
      showNotification('No estás conectado al servidor', 'error');
      return;
    }
    
    // Emitir evento para crear sala
    emit('CREAR_SALA', {
      playerName: roomConfig.playerName,
      maxPlayers: roomConfig.maxPlayers,
      numBots: roomConfig.numBots,
      color: roomConfig.color
    });
  };

  const handleJoinRoom = (joinConfig) => {
    console.log('[JOIN ROOM]', joinConfig);
    
    if (!connected) {
      showNotification('No estás conectado al servidor', 'error');
      return;
    }
    
    // Emitir evento para unirse a sala
    emit('UNIRSE_SALA', {
      roomCode: joinConfig.roomCode,
      playerName: joinConfig.playerName,
      color: joinConfig.color
    });
  };

  const handleDiceRoll = () => {
    console.log('[ROLL] 🎲 Intentando lanzar dados...', {
      connected,
      isMyTurn: isMyTurn(),
      isRolling,
      canMove,
      myPlayerInfo: myPlayerInfo?.nombre,
      currentPlayer: gameState?.jugador_actual
    });
    
    if (!connected) {
      console.log('[ROLL] ❌ Bloqueado: No conectado');
      showNotification('No estás conectado al servidor', 'error');
      return;
    }
    
    if (!isMyTurn()) {
      console.log('[ROLL] ❌ Bloqueado: No es mi turno');
      return;
    }
    
    if (isRolling || canMove) {
      console.log('[ROLL] ❌ Bloqueado: isRolling=', isRolling, ', canMove=', canMove);
      return;
    }
    
    console.log('[ROLL] ✅ Lanzando dados...');
    setIsRolling(true);
    emit('ROLL', { jugador: myPlayerInfo.nombre });
  };

  const handlePieceClick = (pieceId) => {
    console.log('[PIECE CLICK]', pieceId);
    
    if (!canMove) {
      return;
    }
    
    if (!isMyTurn()) {
      return;
    }
    
    const [color, pieceIndex] = pieceId.split('_');
    
    // Verificar que sea mi ficha
    if (color !== myPlayerInfo.color) {
      return;
    }
    
    
    // Verificar si la ficha está en la cárcel
    const player = gameState.players?.find(p => p.color === color);
    const piece = player?.pieces?.find(p => p.piece_id === parseInt(pieceIndex));
    const isInPrison = piece?.position === -1;
    
    console.log('[PIECE INFO]', { pieceId, isInPrison, position: piece?.position });
    
    // Si la ficha está en cárcel, mover directamente (sacar con par)
    if (isInPrison) {
      console.log('[PRISON PIECE] Sacando ficha de la cárcel...', { diceValue, canMove });
      
      // El backend validará si puede sacar de la cárcel
      // Solo verificamos que haya lanzado los dados
      if (!canMove) {
        showNotification('Debes lanzar los dados primero', 'warning');
        return;
      }
      
      movePiece(pieceId, 0); // No importa el valor, el backend detectará que es sacar de cárcel
      return;
    }
    
    // MODO DIVISIÓN DE DADOS
    if (splitMode) {
      const pieceId_num = parseInt(pieceIndex);
      
      // Verificar que no se use la misma ficha dos veces
      if (splitMovements.some(m => m.id_ficha === pieceId_num)) {
        showNotification('No puedes mover la misma ficha dos veces', 'warning');
        return;
      }
      
      // Agregar movimiento
      const nuevoMovimiento = {
        id_ficha: pieceId_num,
        valor_dado: currentSplitDice
      };
      
      const nuevosMovimientos = [...splitMovements, nuevoMovimiento];
      setSplitMovements(nuevosMovimientos);
      
      console.log('[SPLIT MODE] Movimiento agregado:', nuevoMovimiento);
      
      // Si ya tenemos 2 movimientos, enviar
      if (nuevosMovimientos.length === 2) {
        console.log('[SPLIT MODE] Enviando movimientos divididos:', nuevosMovimientos);
        emit('MOVE_DIVIDIDO', {
          dados: diceValue,
          movimientos: nuevosMovimientos
        });
        
        // Resetear modo división
        setSplitMode(false);
        setSplitMovements([]);
        setCurrentSplitDice(null);
        setCanMove(false);
        setCanSplitDice(false);
      } else {
        // Esperar segundo movimiento
        const siguienteDado = diceValue[0] === currentSplitDice ? diceValue[1] : diceValue[0];
        setCurrentSplitDice(siguienteDado);
        setMessage(`Ahora selecciona otra ficha para moverla ${siguienteDado} casillas`);
      }
      
      return;
    }
    
    // Para fichas fuera de la cárcel (modo normal):
    // Siempre usar la suma de los dados directamente (sin selector)
    const totalMove = Array.isArray(diceValue) ? diceValue.reduce((a, b) => a + b, 0) : diceValue;
    movePiece(pieceId, totalMove);
  };

  const handleEnableSplitMode = () => {
    if (!canSplitDice || !Array.isArray(diceValue) || diceValue.length !== 2) {
      return;
    }
    
    console.log('[SPLIT MODE] Activando modo división');
    setSplitMode(true);
    setSplitMovements([]);
    setCurrentSplitDice(diceValue[0]);
    setMessage(`Selecciona una ficha para moverla ${diceValue[0]} casillas`);
  };

  const handleCancelSplitMode = () => {
    console.log('[SPLIT MODE] Cancelando modo división');
    setSplitMode(false);
    setSplitMovements([]);
    setCurrentSplitDice(null);
    setMessage(`Dados: ${diceValue[0]} + ${diceValue[1]} = ${diceValue[0] + diceValue[1]}`);
  };

  const movePiece = (pieceId, diceValueToUse) => {
    const [color, pieceIndex] = pieceId.split('_');
    const pieceId_num = parseInt(pieceIndex);
    
    // Usar diceValue o lastDiceRolled como respaldo
    const dadosActuales = diceValue || lastDiceRolled;
    
    console.log('[MOVE]', { pieceId: pieceId_num, dados: dadosActuales, valor: diceValueToUse });
    
    // Asegurar que los dados siempre sean un array válido
    const dadosToSend = Array.isArray(dadosActuales) ? dadosActuales : [dadosActuales, dadosActuales];
    
    emit('MOVE', {
      id_ficha: pieceId_num,
      dados: dadosToSend
    });
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
    setGameState(initialGameState);
    setDiceValue(null);
    setCanMove(false);
    setSelectedPiece(null);
  };

  const handleBackToMenu = () => {
    if (window.confirm('¿Estás seguro de que quieres volver al menú? Se perderá el progreso del juego.')) {
      // Resetear todos los estados
      setGameStarted(false);
      setGameState(initialGameState);
      setDiceValue(null);
      setCanMove(false);
      setSelectedPiece(null);
      setIsRolling(false);
      setMessage('');
      setShowCelebration(false);
      setWinner(null);
      setShowRoomCode(false);
      setRoomCode(null);
      setRoomPlayers([]);
      setMyPlayerInfo(null);
      
      // Reproducir sonido
      
      // Opcional: desconectar del servidor si está en modo multijugador
      if (roomCode && socket) {
        // El servidor manejará la desconexión automáticamente
        console.log('[BACK TO MENU] Saliendo de la partida');
      }
    }
  };

  // Obtener colores activos para el tablero
  const getActivePlayerColors = () => {
    if (gameState?.players && Array.isArray(gameState.players)) {
      return gameState.players
        .filter(p => p.color)
        .map(p => p.color);
    }
    return [];
  };

  // Obtener color del jugador actual
  const getCurrentPlayerColor = () => {
    const current = gameState?.currentPlayer || gameState?.jugador_actual;
    if (!gameState?.players || !current) return null;
    const currentPlayerData = gameState.players.find(p => 
      p.nombre === current || p.name === current
    );
    return currentPlayerData?.color || null;
  };

  // Handler para iniciar partida desde sala de espera
  const handleStartFromLobby = () => {
    if (!connected) {
      showNotification('No estás conectado al servidor', 'error');
      return;
    }
    
    console.log('[START FROM LOBBY] Iniciando partida...');
    emit('INICIAR_PARTIDA', {});
  };

  // Renderizado
  if (!gameStarted) {
    console.log('[RENDER] 🎬 Renderizando - gameStarted:', gameStarted, 'showRoomCode:', showRoomCode, 'roomCode:', roomCode);
    
    // Mostrar determinación de orden si está activa
    if (showTurnOrderDetermination) {
      console.log('[RENDER] 🎲 Mostrando determinación de orden');
      
      // Transformar gameState.players al formato esperado por TurnOrderDetermination
      const playersForTurnOrder = gameState.players ? gameState.players.map(p => ({
        id: p.color, // Usar color como ID para comparación
        name: p.name,
        color: p.color,
        isHuman: !p.player_id.startsWith('bot_')
      })) : [];
      
      return (
        <TurnOrderDetermination
          players={playersForTurnOrder}
          onOrderDetermined={(order) => {
            console.log('[TURN ORDER] Orden determinado, iniciando juego:', order);
            // Cerrar el componente de determinación de orden e iniciar el juego
            setShowTurnOrderDetermination(false);
            setGameStarted(true);
          }}
          onBack={() => {
            setShowTurnOrderDetermination(false);
            setShowRoomCode(false);
          }}
          socket={socket}
          roomCode={roomCode}
          myPlayerId={myPlayerInfo?.id}
          isHost={myPlayerInfo?.es_host}
        />
      );
    }
    
    // Mostrar sala de espera si hay código de sala
    if (showRoomCode && roomCode) {
      console.log('[RENDER] 🏠 Mostrando lobby con código:', roomCode);
      return (
        <div className={styles.container}>
          <div className={styles.lobbyContainer}>
            <div className={styles.lobbyBox}>
              {/* Panel de control lateral izquierdo */}
              <div className={styles.controlPanel}>
                <div className={styles.lobbyHeader}>
                  <h1 className={styles.headerTitle}>LOBBY CONTROL</h1>
                  <div className={styles.statusIndicator}>
                    {connected ? '🟢 ONLINE' : '🔴 OFFLINE'}
                  </div>
                </div>
                
                <div className={styles.roomCodeSection}>
                  <div className={styles.sectionLabel}>ROOM ACCESS</div>
                  <div className={styles.roomCodeDisplay}>
                    <div className={styles.roomCodeText}>{roomCode}</div>
                    <button 
                      className={styles.copyButton}
                      onClick={() => {
                        navigator.clipboard.writeText(roomCode);
                        showNotification('Código copiado al portapapeles', 'success');
                      }}
                    >
                      COPY
                    </button>
                  </div>
                  <div className={styles.roomCodeHint}>
                    Share code with other players
                  </div>
                </div>

                <div className={styles.playersSection}>
                  <div className={styles.sectionLabel}>CONNECTED NODES</div>
                  <div className={styles.playersList}>
                    {roomPlayers.map((player, index) => (
                      <div key={index} className={styles.playerNode}>
                        <div 
                          className={styles.nodeIndicator} 
                          style={{ backgroundColor: player.color }}
                        ></div>
                        <div className={styles.nodeInfo}>
                          <span className={styles.nodeName}>{player.nombre}</span>
                          {player.nombre === myPlayerInfo?.nombre && (
                            <span className={styles.nodeTag}>YOU</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className={styles.actionMatrix}>
                  {myPlayerInfo?.es_host ? (
                    <button 
                      className={styles.startButton}
                      onClick={handleStartFromLobby}
                      disabled={!connected}
                    >
                      INITIALIZE GAME
                    </button>
                  ) : (
                    <div className={styles.waitingStatus}>
                      <div className={styles.waitingText}>
                        AWAITING HOST COMMAND...
                      </div>
                    </div>
                  )}
                </div>
              </div>
              
              {/* Panel de información lateral derecho */}
              <div className={styles.infoPanel}>
                <div className={styles.terminalWindow}>
                  <div className={styles.terminalHeader}>
                    <span className={styles.glitchText}>ROOM STATUS</span>
                  </div>
                  <div className={styles.terminalContent}>
                    {`Room ID: ${roomCode}
Status: WAITING
Nodes: ${roomPlayers.length}/2
Host: ${myPlayerInfo?.es_host ? 'YOU' : roomPlayers.find(p => p.es_host)?.nombre || 'UNKNOWN'}

---[NETWORK STATUS]---
Connection: ${connected ? 'STABLE' : 'DISCONNECTED'}
Latency: 23ms
Packet Loss: 0%
Protocol: WebSocket

---[PLAYER REGISTRY]---`}
                    {roomPlayers.map((player, index) => (
                      `
Node ${index + 1}: ${player.nombre}
Color: ${player.color.toUpperCase()}
Status: READY
Role: ${player.es_host ? 'HOST' : 'CLIENT'}`
                    )).join('')}
                    {`

---[GAME PARAMETERS]---
Mode: Multiplayer
Players: ${roomPlayers.length}
Max Players: 2
Ready State: ${myPlayerInfo?.es_host ? 'HOST_CONTROL' : 'AWAITING_START'}`}
                  </div>
                </div>
              </div>
            </div>
          </div>

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
    
    return (
      <>
        <Menu 
          onStartGame={handleStartGame}
          onShowRules={handleShowRules}
          onCreateRoom={handleCreateRoom}
          onJoinRoom={handleJoinRoom}
          availableColors={availableColors}
          showColorSelector={availableColors.length > 0}
        />
        {showRules && <Rules onClose={handleCloseRules} />}
        
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
      
      {showCelebration && winner && (
        <Celebration winner={winner} onClose={handleCloseCelebration} />
      )}
      

      
      <main className={styles.main}>
        <div className={styles.header}>
          <button 
            className={styles.backButton}
            onClick={handleBackToMenu}
          >
            ← Menú
          </button>
          <h1 className={styles.title}>Parchís Game</h1>
          <div className={styles.connectionStatus}>
            {connected ? '🟢 Conectado' : '🔴 Desconectado'}
          </div>
        </div>

        <div className={styles.gameContainer}>
          <div className={styles.boardSection}>
            <Board
              gameState={gameState}
              onPieceClick={handlePieceClick}
              canMove={canMove}
              currentPlayer={gameState.currentPlayer}
              currentPlayerColor={getCurrentPlayerColor()}
              selectedPieceFromParent={selectedPiece}
              diceValue={diceValue}
              onDiceRoll={handleDiceRoll}
              isRolling={isRolling}
              canRoll={isMyTurn() && !canMove && !isRolling}
              myPlayerInfo={myPlayerInfo}
              isMyTurn={isMyTurn}
              message={message}
              canSplitDice={canSplitDice}
              splitMode={splitMode}
              splitMovements={splitMovements}
              onEnableSplitMode={handleEnableSplitMode}
              onCancelSplitMode={handleCancelSplitMode}
            />
          </div>


        </div>
      </main>

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

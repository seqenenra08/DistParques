'use client';

import { useSocket } from '../hooks/useSocket';
import { useEffect, useState } from 'react';
import Board from '../components/Board/Board';
import Dice from '../components/Game/Dice';
import Menu from '../components/Menu/Menu';
import Rules from '../components/Menu/Rules';
import Celebration from '../components/Game/Celebration';
import AudioControl from '../components/Game/AudioControl';
import MoveSelector from '../components/Game/MoveSelector';
import TurnOrderDetermination from '../components/Menu/TurnOrderDetermination';
import Notification from '../components/Notification/Notification';
import { initialGameState } from '../utils/mockData';
import styles from './page.module.css';
import audioService from '../services/audioService';

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
  const [showMoveSelector, setShowMoveSelector] = useState(false);
  const [pendingPieceForMove, setPendingPieceForMove] = useState(null);
  const [selectedPiece, setSelectedPiece] = useState(null);
  
  // División de dados
  const [canSplitDice, setCanSplitDice] = useState(false);
  const [splitMode, setSplitMode] = useState(false);
  const [splitMovements, setSplitMovements] = useState([]);
  const [currentSplitDice, setCurrentSplitDice] = useState(null);
  
  // Inicializar audio
  useEffect(() => {
    const initAudio = async () => {
      await audioService.initialize();
    };
    
    const handleFirstInteraction = () => {
      initAudio();
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
        
        audioService.playSuccess();
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
        setGameState(data.estado);
        audioService.playGameStart();
      } else {
        // Iniciar juego directamente (modo antiguo)
        setGameStarted(true);
        setGameState(data.estado);
        audioService.playGameStart();
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
        audioService.playError();
        showNotification(data.error, 'error');
        return;
      }
      
      // Si todas están en cárcel y no sacó par
      if (data.todas_en_carcel && !data.es_par) {
        audioService.playError();
        
        // Si se pasó el turno (agotó los 3 intentos)
        if (data.turn_passed) {
          showNotification('❌ Agotaste los 3 intentos sin sacar par. Turno perdido.', 'error');
          setTimeout(() => {
            setDiceValue(null);
            setLastDiceRolled(null);
            setMessage('');
            setCanMove(false);
            setIsRolling(false);
          }, 2500);
          return;
        }
        
        showNotification(`❌ Sin par (${data.attempts_used}/${data.attempts_used + data.attempts_remaining}) - ${data.attempts_remaining > 0 ? 'Intenta de nuevo' : 'Turno perdido'}`, 'warning');
        
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
        audioService.playDiceRoll();
        audioService.playDoubles();
        setCanMove(true);
        showNotification('✅ ¡PAR! Selecciona una ficha para sacarla de la cárcel', 'success');
        setMessage('✅ ¡PAR! Haz clic en una ficha de la cárcel para sacarla');
        
        // Preparar movimientos (para sacar de cárcel)
        setAvailableMoves([data.dados[0]]);
        return;
      }
      
      // Puede mover (caso normal)
      audioService.playDiceRoll();
      if (data.es_par) {
        audioService.playDoubles();
        showNotification('🎲 ¡Dobles! Podrás lanzar de nuevo después de mover', 'info');
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
        audioService.playError();
        showNotification(data.error, 'error');
        return;
      }
      
      audioService.playPieceMove();
      
      // Limpiar estado de movimiento
      setCanMove(false);
      setDiceValue(null);
      setLastDiceRolled(null);
      setSelectedPiece(null);
      setAvailableMoves([]);
      setPendingPieceForMove(null);
      setShowMoveSelector(false);
      setCanSplitDice(false);
      setSplitMode(false);
      setSplitMovements([]);
      setCurrentSplitDice(null);
      
      // Mostrar mensaje de acción
      const accion = data.accion;
      if (accion === 'sacar_carcel') {
        showNotification('✅ Ficha sacada de la cárcel', 'success');
      } else if (accion === 'llego_meta') {
        audioService.playPieceGoal();
        showNotification('🏁 ¡Ficha llegó a la META!', 'success');
      } else if (data.fichas_capturadas && data.fichas_capturadas.length > 0) {
        audioService.playPieceCapture();
        showNotification(`💥 ¡Capturaste ${data.fichas_capturadas.length} ficha(s)!`, 'success');
      }
      
      // Verificar victoria
      if (data.ganador) {
        setWinner({ name: data.ganador, color: gameState.currentPlayer });
        setShowCelebration(true);
        audioService.playGameWin();
      }
    });

    // Cambio de turno
    socket.on('TURN_CHANGE', (data) => {
      console.log('[TURN_CHANGE]', data);
      setGameState(data.estado);
      
      // Limpiar estado de dados y movimientos
      setDiceValue(null);
      setLastDiceRolled(null);
      setCanMove(false);
      setAvailableMoves([]);
      setSelectedPiece(null);
      setShowMoveSelector(false);
      setCanSplitDice(false);
      setSplitMode(false);
      setSplitMovements([]);
      setCurrentSplitDice(null);
      setMessage('');
      setIsRolling(false);
      
      // Mostrar notificación del cambio de turno
      if (data.razon === 'intentos_agotados') {
        audioService.playError();
        showNotification(data.mensaje || `Turno de ${data.jugador_actual}`, 'info');
      }
    });

    // Estado actualizado
    socket.on('UPDATE', (data) => {
      console.log('[UPDATE]', data.estado);
      console.log('[UPDATE] Estado actual antes:', {
        previousPlayer: gameState?.jugador_actual,
        myPlayerInfo: myPlayerInfo?.nombre,
        canMove,
        diceValue,
        isRolling
      });
      
      // Detectar cambio de turno
      const previousPlayerName = gameState?.jugador_actual;
      const currentPlayerName = data.estado.jugador_actual;
      const turnChanged = previousPlayerName && previousPlayerName !== currentPlayerName;
      
      setGameState(data.estado);
      
      // Si cambió el turno, limpiar estado de TODOS los jugadores
      if (turnChanged) {
        console.log('[UPDATE] ✅ Turno cambió de', previousPlayerName, 'a', currentPlayerName);
        console.log('[UPDATE] ✅ Limpiando TODO el estado (canMove -> false)');
        setDiceValue(null);
        setLastDiceRolled(null);
        setCanMove(false);
        setAvailableMoves([]);
        setSelectedPiece(null);
        setShowMoveSelector(false);
        setCanSplitDice(false);
        setSplitMode(false);
        setSplitMovements([]);
        setCurrentSplitDice(null);
        setMessage('');
        setIsRolling(false);
      } else if (myPlayerInfo && data.estado.jugador_actual !== myPlayerInfo.nombre) {
        // Si no es mi turno (sin cambio de turno), limpiar estado
        console.log('[UPDATE] 🔄 No es mi turno, limpiando estado');
        setDiceValue(null);
        setLastDiceRolled(null);
        setCanMove(false);
        setAvailableMoves([]);
        setSelectedPiece(null);
        setShowMoveSelector(false);
        setCanSplitDice(false);
        setSplitMode(false);
        setSplitMovements([]);
        setCurrentSplitDice(null);
      } else {
        console.log('[UPDATE] ⚠️ Es mi turno pero no cambió el turno - manteniendo estado');
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
        showNotification(`${data.jugador} se ha unido a la sala`, 'info');
        audioService.playClick();
      }
    });

    // Colores disponibles (cuando te unes a una sala)
    socket.on('COLORES_DISPONIBLES', (data) => {
      console.log('[COLORES_DISPONIBLES]', data);
      if (data.exito) {
        setAvailableColors(data.colores);
        setPendingRoomCode(data.codigo_sala);
        showNotification('Selecciona tu color', 'info');
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
        
        audioService.playSuccess();
        showNotification(`Te has unido a la sala ${data.codigo_sala}`, 'success');
      }
    });

    // Dado inicial lanzado (para determinar orden)
    socket.on('DADO_INICIO', (data) => {
      console.log('[DADO_INICIO]', data);
      audioService.playDiceRoll();
      showNotification(`${data.jugador} sacó ${data.valor}`, 'info');
    });

    // Turno determinado (orden establecido)
    socket.on('TURNO_DETERMINADO', (data) => {
      console.log('[TURNO_DETERMINADO]', data);
      // NO cerrar el componente aquí, dejar que el usuario vea los resultados
      // El componente TurnOrderDetermination manejará este evento
      audioService.playSuccess();
      showNotification(data.mensaje || `¡${data.jugador_inicial} comienza!`, 'success');
    });

    // Error del servidor
    socket.on('ERROR', (data) => {
      console.log('[ERROR]', data);
      showNotification(data.mensaje || 'Error desconocido', 'error');
      audioService.playError();
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
    if (!myPlayerInfo || !gameState.currentPlayer) return false;
    return gameState.currentPlayer === myPlayerInfo.nombre;
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
      showNotification('No es tu turno', 'warning');
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
      audioService.playError();
      showNotification('Primero debes lanzar los dados', 'warning');
      return;
    }
    
    if (!isMyTurn()) {
      audioService.playError();
      showNotification('No es tu turno', 'warning');
      return;
    }
    
    const [color, pieceIndex] = pieceId.split('_');
    
    // Verificar que sea mi ficha
    if (color !== myPlayerInfo.color) {
      audioService.playError();
      showNotification('No es tu ficha', 'warning');
      return;
    }
    
    audioService.playClick();
    
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
        audioService.playError();
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
        audioService.playError();
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
    // Si hay múltiples opciones de movimiento, mostrar selector
    if (availableMoves.length > 1) {
      setSelectedPiece(pieceId);
      setPendingPieceForMove(pieceId);
      setShowMoveSelector(true);
    } else if (availableMoves.length === 1) {
      // Solo una opción, mover directamente
      movePiece(pieceId, availableMoves[0]);
    } else {
      // Usar suma por defecto
      const totalMove = Array.isArray(diceValue) ? diceValue.reduce((a, b) => a + b, 0) : diceValue;
      movePiece(pieceId, totalMove);
    }
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
    setShowMoveSelector(false);
    audioService.playClick();
  };

  const handleCancelSplitMode = () => {
    console.log('[SPLIT MODE] Cancelando modo división');
    setSplitMode(false);
    setSplitMovements([]);
    setCurrentSplitDice(null);
    setMessage(`Dados: ${diceValue[0]} + ${diceValue[1]} = ${diceValue[0] + diceValue[1]}`);
    audioService.playClick();
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

  const handleSelectMove = (selectedMove) => {
    console.log('[SELECT MOVE]', selectedMove);
    if (pendingPieceForMove) {
      setShowMoveSelector(false);
      movePiece(pendingPieceForMove, selectedMove);
    }
  };

  const handleCancelMoveSelector = () => {
    setShowMoveSelector(false);
    setPendingPieceForMove(null);
    setSelectedPiece(null);
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
      audioService.playClick();
      
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
    if (!gameState?.players || !gameState?.currentPlayer) return null;
    const currentPlayerData = gameState.players.find(p => 
      p.nombre === gameState.currentPlayer || p.name === gameState.currentPlayer
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
              <h1 className={styles.lobbyTitle}>🎮 Sala de Espera</h1>
              
              <div className={styles.roomCodeSection}>
                <p className={styles.roomCodeLabel}>Código de Sala:</p>
                <div className={styles.roomCodeDisplay}>
                  <span className={styles.roomCodeText}>{roomCode}</span>
                  <button 
                    className={styles.copyButton}
                    onClick={() => {
                      navigator.clipboard.writeText(roomCode);
                      showNotification('Código copiado al portapapeles', 'success');
                      audioService.playClick();
                    }}
                  >
                    📋 Copiar
                  </button>
                </div>
                <p className={styles.roomCodeHint}>
                  Comparte este código con otros jugadores para que se unan
                </p>
              </div>

              <div className={styles.playersSection}>
                <h2 className={styles.sectionTitle}>Jugadores en la sala:</h2>
                <div className={styles.playersList}>
                  {roomPlayers.map((player, index) => (
                    <div key={index} className={styles.playerItem}>
                      <div 
                        className={styles.playerColorBadge} 
                        style={{ backgroundColor: player.color }}
                      ></div>
                      <span className={styles.playerName}>{player.nombre}</span>
                      {player.nombre === myPlayerInfo?.nombre && (
                        <span className={styles.youBadge}>Tú</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className={styles.lobbyActions}>
                {myPlayerInfo?.es_host ? (
                  <button 
                    className={styles.startButton}
                    onClick={handleStartFromLobby}
                    disabled={!connected}
                  >
                    🚀 Iniciar Partida
                  </button>
                ) : (
                  <p className={styles.waitingText}>
                    Esperando a que el anfitrión inicie la partida...
                  </p>
                )}
              </div>

              <div className={styles.connectionStatus}>
                {connected ? '🟢 Conectado' : '🔴 Desconectado'}
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
      <AudioControl />
      
      {showCelebration && winner && (
        <Celebration winner={winner} onClose={handleCloseCelebration} />
      )}
      
      {showMoveSelector && (
        <MoveSelector 
          availableMoves={availableMoves}
          onSelectMove={handleSelectMove}
          onCancel={handleCancelMoveSelector}
          selectedPiece={selectedPiece}
        />
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
            />
          </div>

          <div className={styles.controlsSection}>
            <div className={styles.turnInfo}>
              <h2>Turno Actual</h2>
              <p className={styles.currentPlayerName}>
                {gameState.currentPlayer || 'Esperando...'}
              </p>
              {myPlayerInfo && (
                <p className={styles.myInfo}>
                  Tú: {myPlayerInfo.nombre} ({myPlayerInfo.color})
                </p>
              )}
              {isMyTurn() && <p className={styles.yourTurn}>¡ES TU TURNO!</p>}
            </div>

            <Dice
              value={diceValue}
              onRoll={handleDiceRoll}
              isRolling={isRolling}
              canRoll={isMyTurn() && !canMove && !isRolling}
            />

            {canSplitDice && !splitMode && (
              <div className={styles.splitButtonsContainer}>
                <button 
                  onClick={handleEnableSplitMode} 
                  className={styles.splitButton}
                >
                  ✂️ Dividir dados
                </button>
              </div>
            )}

            {splitMode && (
              <div className={styles.splitModeIndicator}>
                <p>🎯 Modo división activo</p>
                <p>Movimiento {splitMovements.length + 1} de 2</p>
                <button 
                  onClick={handleCancelSplitMode} 
                  className={styles.cancelSplitButton}
                >
                  ❌ Cancelar
                </button>
              </div>
            )}

            {message && (
              <div className={styles.messageBox}>
                {message}
              </div>
            )}

            <div className={styles.playersInfo}>
              <h3>Jugadores</h3>
              {gameState.players?.map(player => (
                <div 
                  key={player.player_id} 
                  className={`${styles.playerCard} ${player.es_su_turno ? styles.activePlayer : ''}`}
                >
                  <div className={styles.playerColor} style={{ backgroundColor: player.color }}></div>
                  <div className={styles.playerDetails}>
                    <span className={styles.playerName}>{player.nombre}</span>
                    <span className={styles.playerStats}>
                      Meta: {player.pieces_in_home || 0}/4
                    </span>
                  </div>
                </div>
              ))}
            </div>
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

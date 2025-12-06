'use client';

import { useSocket } from '../hooks/useSocket';
import { useEffect, useState } from 'react';
import Board from '../components/Board/Board';
import Dice from '../components/Game/Dice';
import Menu from '../components/Menu/Menu';
import Rules from '../components/Menu/Rules';
import Celebration from '../components/Game/Celebration';
import MoveSelector from '../components/Game/MoveSelector';
import Notification from '../components/Notification/Notification';
import { initialGameState } from '../utils/mockData';
import styles from './page.module.css';

export default function Home() {
  const { socket, connected, emit } = useSocket();
  
  // Estados principales
  const [gameState, setGameState] = useState(initialGameState);
  const [gameStarted, setGameStarted] = useState(false);
  const [myPlayerInfo, setMyPlayerInfo] = useState(null); // { id, nombre, color }
  
  // Estados de dados
  const [diceValue, setDiceValue] = useState(null);
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
  
  useEffect(() => {
    };
    
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
      console.log('[SALA_CREADA]', data);
      if (data.exito) {
        setMyPlayerInfo({
          id: data.jugador.color,
          nombre: data.jugador.nombre,
          color: data.jugador.color,
          es_host: data.jugador.es_host
        });
        
        // Iniciar partida automáticamente
        setTimeout(() => {
          emit('INICIAR_PARTIDA', {});
        }, 500);
      }
    });

    // Partida iniciada
    socket.on('PARTIDA_INICIADA', (data) => {
      console.log('[PARTIDA_INICIADA]', data);
      setGameStarted(true);
      setGameState(data.estado);
    });

    // Resultado de lanzamiento de dados
    socket.on('DICE_RESULT', (data) => {
      console.log('[DICE_RESULT]', data);
      
      setIsRolling(false);
      setDiceValue(data.dados);
      
      if (data.error) {
        showNotification(data.error, 'error');
        return;
      }
      
      // Si todas están en cárcel y no sacó par
      if (data.todas_en_carcel && !data.es_par) {
        setMessage('❌ Todas en cárcel - necesitas PAR');
        setTimeout(() => {
          setDiceValue(null);
          setMessage('');
        }, 2000);
        return;
      }
      
      // Puede mover
      if (data.es_par) {
      }
      
      setCanMove(true);
      
      // Preparar movimientos disponibles
      const moves = [data.dados[0], data.dados[1]];
      if (data.dados[0] !== data.dados[1]) {
        moves.push(data.suma);
      }
      setAvailableMoves(moves);
      
      setMessage(data.mensaje || '');
    });

    // Resultado de movimiento
    socket.on('MOVE_RESULT', (data) => {
      console.log('[MOVE_RESULT]', data);
      
      if (data.error) {
        showNotification(data.error, 'error');
        return;
      }
      
      // Solo procesar si es el turno actual del que está jugando
      // El MOVE_RESULT se hace broadcast pero solo el jugador que se está moviendo debe procesarlo
      if (myPlayerInfo && gameState && gameState.currentPlayer !== myPlayerInfo.nombre) {
        console.log('[MOVE_RESULT] ⏭️ Ignorando - no es mi turno');
        return;
      }
      
      // Limpiar estado de movimiento
      setCanMove(false);
      setDiceValue(null);
      setSelectedPiece(null);
      setAvailableMoves([]);
      setPendingPieceForMove(null);
      setShowMoveSelector(false);
      setIsRolling(false);
      
      // Mostrar mensaje de acción
      const accion = data.accion;
      if (accion === 'sacar_carcel') {
        setMessage('✅ Ficha sacada de la cárcel');
      } else if (accion === 'llego_meta') {
        setMessage('🏁 ¡Ficha llegó a la META!');
      } else if (data.fichas_capturadas && data.fichas_capturadas.length > 0) {
        setMessage(`💥 ¡Capturaste ${data.fichas_capturadas.length} ficha(s)!`);
      }
      
      setTimeout(() => setMessage(''), 3000);
      
      // Verificar victoria
      if (data.ganador) {
        setWinner({ name: data.ganador, color: gameState.currentPlayer });
        setShowCelebration(true);
      }
    });

    // Estado actualizado
    socket.on('UPDATE', (data) => {
      console.log('[UPDATE]', data.estado);
      
      const previousPlayerName = gameState?.currentPlayer;
      const currentPlayerName = data.estado?.currentPlayer || data.estado?.jugador_actual;
      const turnChanged = previousPlayerName && previousPlayerName !== currentPlayerName;
      const isMyTurnNow = myPlayerInfo && currentPlayerName === myPlayerInfo.nombre;
      
      setGameState(data.estado);
      
      if (!isMyTurnNow) {
        // No es mi turno, limpiar TODO
        console.log('[UPDATE] 🔄 No es mi turno, limpiando estado');
        setDiceValue(null);
        setCanMove(false);
        setSelectedPiece(null);
        setAvailableMoves([]);
        setIsRolling(false);
      } else if (turnChanged) {
        // Es mi turno y CAMBIÓ (acabo de recibir el turno)
        console.log('[UPDATE] ✅ Recibí el turno, limpiando datos previos');
        setDiceValue(null);
        setCanMove(false);
        setSelectedPiece(null);
        setAvailableMoves([]);
        setIsRolling(false);
      } else {
        // Es mi turno y NO cambió (continuación del turno)
        console.log('[UPDATE] 📋 Turno continúa, limpiando datos pero mantiendo canMove');
        setDiceValue(null);
        setSelectedPiece(null);
        setIsRolling(false);
      }
    });

    // Información de fichas
    socket.on('FICHAS_INFO', (data) => {
      console.log('[FICHAS_INFO]', data.fichas);
      // Mostrar info de fichas si es necesario
    });

    // Limpieza
    return () => {
      socket.off('SALA_CREADA');
      socket.off('PARTIDA_INICIADA');
      socket.off('DICE_RESULT');
      socket.off('MOVE_RESULT');
      socket.off('UPDATE');
      socket.off('FICHAS_INFO');
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

  const handleDiceRoll = () => {
    if (!connected) {
      showNotification('No estás conectado al servidor', 'error');
      return;
    }
    
    if (!isMyTurn()) {
      return;
    }
    
    if (isRolling || canMove) {
      return;
    }
    
    console.log('[ROLL] Lanzando dados...');
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

  const movePiece = (pieceId, diceValueToUse) => {
    const [color, pieceIndex] = pieceId.split('_');
    const pieceId_num = parseInt(pieceIndex);
    
    console.log('[MOVE]', { pieceId: pieceId_num, dados: diceValue, valor: diceValueToUse });
    
    emit('MOVE', {
      id_ficha: pieceId_num,
      dados: diceValue
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

  // Obtener colores activos para el tablero
  const getActivePlayerColors = () => {
    if (gameState?.players && Array.isArray(gameState.players)) {
      return gameState.players
        .filter(p => p.color)
        .map(p => p.color);
    }
    return [];
  };

  // Renderizado
  if (!gameStarted) {
    return (
      <>
        <Menu 
          onStartGame={handleStartGame}
          onShowRules={handleShowRules}
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
              disabled={!(isMyTurn() && !canMove && !isRolling)}
            />

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

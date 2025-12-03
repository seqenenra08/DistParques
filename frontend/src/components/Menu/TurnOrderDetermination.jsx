/**
 * Componente TurnOrderDetermination - Lanzamiento inicial para determinar orden
 */

import React, { useState, useEffect } from 'react';
import styles from './TurnOrderDetermination.module.css';
import audioService from '../../services/audioService';

const BOARD_ORDER = ['red', 'green', 'yellow', 'blue']; // Orden antihorario en el tablero

const TurnOrderDetermination = ({ players, onOrderDetermined, onBack, socket, roomCode, myPlayerId, isHost }) => {
  const [currentPlayerIndex, setCurrentPlayerIndex] = useState(0);
  const [diceResults, setDiceResults] = useState({});
  const [finalDiceResults, setFinalDiceResults] = useState({});
  const [isRolling, setIsRolling] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [finalOrder, setFinalOrder] = useState([]);
  const [animatedValue, setAnimatedValue] = useState(1);
  const [tiedPlayers, setTiedPlayers] = useState([]); // Jugadores empatados
  const [isTiebreaker, setIsTiebreaker] = useState(false); // ¿Estamos en desempate?
  const [activePlayers, setActivePlayers] = useState(players); // Jugadores activos en esta ronda
  const [isMultiplayer, setIsMultiplayer] = useState(false); // ¿Es partida multijugador?

  // Función auxiliar para ordenar jugadores (humanos primero, luego bots, ambos por color)
  const sortPlayersByTypeAndColor = (playersList) => {
    return [...playersList].sort((a, b) => {
      // Si uno es humano y el otro bot, el humano va primero
      if (a.isHuman && !b.isHuman) return -1;
      if (!a.isHuman && b.isHuman) return 1;
      
      // Si ambos son del mismo tipo, ordenar por color según BOARD_ORDER
      const indexA = BOARD_ORDER.indexOf(a.color);
      const indexB = BOARD_ORDER.indexOf(b.color);
      return indexA - indexB;
    });
  };

  // Log inicial para verificar datos
  useEffect(() => {
    console.log('[TURN ORDER] Component mounted with players:', 
      players.map(p => `${p.name} (${p.color})`));
    
    // Ordenar jugadores: primero humanos por color, luego bots por color
    const sortedPlayers = sortPlayersByTypeAndColor(players);
    
    console.log('[TURN ORDER] Jugadores ordenados:', 
      sortedPlayers.map(p => `${p.name} (${p.color}) ${p.isHuman ? 'HUMANO' : 'BOT'}`));
    
    setActivePlayers(sortedPlayers);
    
    // Detectar si es multijugador (tiene socket y roomCode)
    if (socket && roomCode) {
      setIsMultiplayer(true);
      console.log('[TURN ORDER] Modo multijugador detectado - Mi color:', myPlayerId);
    }
  }, []);
  
  // Lanzamiento automático para bots
  useEffect(() => {
    const currentPlayer = activePlayers[currentPlayerIndex];
    
    // Verificar si es turno de un bot y aún no ha lanzado
    if (currentPlayer && !currentPlayer.isHuman && !diceResults[currentPlayer.id] && !isRolling) {
      console.log(`[BOT] Es turno del bot ${currentPlayer.name}, lanzando automáticamente en 1.5s...`);
      
      // Esperar 1.5 segundos antes de lanzar (para que sea visible)
      const botTimer = setTimeout(() => {
        console.log(`[BOT] Ejecutando lanzamiento para ${currentPlayer.name}`);
        // Simular click del botón de lanzar
        document.querySelector('[data-bot-roll]')?.click();
      }, 1500);
      
      return () => clearTimeout(botTimer);
    }
  }, [currentPlayerIndex, activePlayers, diceResults, isRolling]);

  // Escuchar eventos de socket en modo multijugador
  useEffect(() => {
    if (!isMultiplayer || !socket) return;
    
    const handleDiceRolled = (data) => {
      console.log('[TURN ORDER] DADO_INICIO recibido:', data);
      const playerColor = data.color;
      const diceValue = data.valor;
      
      // Buscar el jugador por color
      const player = activePlayers.find(p => p.color === playerColor);
      if (!player) {
        console.error('[TURN ORDER] Jugador no encontrado para color:', playerColor);
        return;
      }
      
      const playerId = player.id;
      console.log('[TURN ORDER] Dado recibido desde servidor - Jugador:', player.name, 'Valor:', diceValue);
      
      // Actualizar los resultados
      setDiceResults(prev => ({
        ...prev,
        [playerId]: diceValue
      }));
      
      // Si es mi dado, detener la animación
      if (playerId === myPlayerId) {
        setAnimatedValue(diceValue);
        setIsRolling(false);
      }
      
      // Avanzar al siguiente jugador si todos los activos ya lanzaron
      const currentResults = { ...diceResults, [playerId]: diceValue };
      const rolledCount = Object.keys(currentResults).filter(id => 
        activePlayers.some(p => p.id === id)
      ).length;
      
      if (rolledCount < activePlayers.length) {
        // Todavía hay jugadores por lanzar
        const nextIndex = activePlayers.findIndex(p => !currentResults[p.id]);
        if (nextIndex !== -1) {
          setTimeout(() => setCurrentPlayerIndex(nextIndex), 1000);
        }
      } else {
        // Todos lanzaron - verificar empates
        setTimeout(() => {
          console.log('[TURN ORDER] Todos lanzaron. Verificando empates...');
          setFinalDiceResults(currentResults);
          checkForTies(currentResults);
        }, 3500);
      }
    };
    
    const handleTiebreakerStarted = (data) => {
      console.log('[TURN ORDER] ===== DESEMPATE INICIADO =====');
      console.log('[TURN ORDER] Data recibida:', data);
      console.log('[TURN ORDER] tiedPlayers en data:', data?.tiedPlayers);
      console.log('[TURN ORDER] tiedPlayers en estado:', tiedPlayers);
      
      // Reiniciar para el desempate
      const playersForTiebreak = data?.tiedPlayers || tiedPlayers;
      console.log('[TURN ORDER] Jugadores para desempate:', playersForTiebreak);
      
      if (!playersForTiebreak || playersForTiebreak.length === 0) {
        console.error('[TURN ORDER] No hay jugadores para desempate!');
        return;
      }
      
      // Ordenar jugadores empatados (humanos primero, luego bots)
      const sortedTiedPlayers = sortPlayersByTypeAndColor(playersForTiebreak);
      
      setIsTiebreaker(true);
      setActivePlayers(sortedTiedPlayers);
      setCurrentPlayerIndex(0);
      setDiceResults({});
      setTiedPlayers([]);
      
      console.log('[TURN ORDER] Estado actualizado - activePlayers:', sortedTiedPlayers);
      audioService.playClick();
    };
    
    const handleRerollStarted = () => {
      console.log('[TURN ORDER] Reinicio solicitado por el host');
      // Reiniciar todo y ordenar jugadores de nuevo
      const sortedPlayers = sortPlayersByTypeAndColor(players);
      
      setCurrentPlayerIndex(0);
      setDiceResults({});
      setFinalDiceResults({});
      setShowResults(false);
      setFinalOrder([]);
      setAnimatedValue(1);
      setTiedPlayers([]);
      setIsTiebreaker(false);
      setActivePlayers(sortedPlayers);
      audioService.playClick();
    };
    
    const handleTurnoDeterminado = (data) => {
      console.log('[TURN ORDER] ===== TURNO DETERMINADO =====');
      console.log('[TURN ORDER] Data recibida:', data);
      
      // Construir el orden final basado en los resultados
      if (data.resultados && Array.isArray(data.resultados)) {
        // Crear un mapa de resultados por color
        const resultsMap = {};
        data.resultados.forEach(r => {
          resultsMap[r.color] = r.valor;
        });
        
        // Actualizar finalDiceResults con los resultados del servidor
        const finalResults = {};
        players.forEach(p => {
          if (resultsMap[p.color] !== undefined) {
            finalResults[p.id] = resultsMap[p.color];
          }
        });
        
        setFinalDiceResults(finalResults);
        
        // Calcular el orden final
        calculateFinalOrder(finalResults);
      }
      
      audioService.playSuccess();
    };
    
    const handleComenzarJuego = (data) => {
      console.log('[TURN ORDER] ===== COMENZAR JUEGO CONFIRMADO =====');
      console.log('[TURN ORDER] Iniciando juego para todos los jugadores');
      
      // Llamar al callback para iniciar el juego
      onOrderDetermined(finalOrder);
    };
    
    socket.on('DADO_INICIO', handleDiceRolled);
    socket.on('tiebreaker_started', handleTiebreakerStarted);
    socket.on('reroll_started', handleRerollStarted);
    socket.on('TURNO_DETERMINADO', handleTurnoDeterminado);
    socket.on('COMENZAR_JUEGO_CONFIRMADO', handleComenzarJuego);
    
    return () => {
      socket.off('DADO_INICIO', handleDiceRolled);
      socket.off('tiebreaker_started', handleTiebreakerStarted);
      socket.off('reroll_started', handleRerollStarted);
      socket.off('TURNO_DETERMINADO', handleTurnoDeterminado);
      socket.off('COMENZAR_JUEGO_CONFIRMADO', handleComenzarJuego);
    };
  }, [isMultiplayer, socket, diceResults, activePlayers, myPlayerId, tiedPlayers, players]);

  const rollDice = () => {
    const currentPlayer = activePlayers[currentPlayerIndex];
    
    // En modo multijugador, solo permitir lanzar al jugador actual
    if (isMultiplayer && currentPlayer.id !== myPlayerId) {
      console.log('[TURN ORDER] No es tu turno de lanzar');
      audioService.playError();
      return;
    }
    
    setIsRolling(true);
    
    // 🔊 Reproducir sonido de dados girando
    audioService.playDiceRoll();
    
    // Animar el dado mostrando valores aleatorios
    let iterations = 0;
    const animationInterval = setInterval(() => {
      setAnimatedValue(Math.floor(Math.random() * 6) + 1);
      iterations++;
      
      if (iterations >= 10) {
        clearInterval(animationInterval);
      }
    }, 100);
    
    // Después de la animación, mostrar el resultado final
    setTimeout(() => {
      clearInterval(animationInterval);
      const result = Math.floor(Math.random() * 6) + 1;
      
      console.log(`[DICE ROLL] ${currentPlayer.name} (${currentPlayer.color}) rolled: ${result}`);
      
      setAnimatedValue(result);
      
      // 🔊 Reproducir sonido de click al mostrar resultado
      audioService.playClick();
      
      // En modo multijugador, emitir al servidor usando protocolo correcto
      if (isMultiplayer && socket && roomCode) {
        socket.send({
          tipo: 'ROLL_INICIO'
        });
        console.log('[TURN ORDER] Enviando ROLL_INICIO al servidor');
        setIsRolling(false);
      } else {
        // Modo local - actualizar directamente
        const updatedResults = {
          ...diceResults,
          [currentPlayer.id]: result
        };
        
        console.log('[DICE ROLL] Updated diceResults:', updatedResults);
        
        setDiceResults(updatedResults);
        setIsRolling(false);
        
        // Pasar al siguiente jugador o mostrar resultados
        if (currentPlayerIndex < activePlayers.length - 1) {
          setTimeout(() => {
            setCurrentPlayerIndex(currentPlayerIndex + 1);
          }, 1000);
        } else {
          // Último jugador - esperar para verificar empates
          setTimeout(() => {
            console.log('[DICE ROLL] Last player rolled. Checking for ties...');
            setFinalDiceResults(updatedResults);
            checkForTies(updatedResults);
          }, 3500);
        }
      }
    }, 1500);
  };

  const checkForTies = (results) => {
    console.log('[TIE CHECK] Checking for ties in results:', results);
    
    // Agrupar jugadores por resultado
    const scoreGroups = {};
    activePlayers.forEach(player => {
      const score = results[player.id];
      if (!scoreGroups[score]) {
        scoreGroups[score] = [];
      }
      scoreGroups[score].push(player);
    });
    
    console.log('[TIE CHECK] Score groups:', scoreGroups);
    
    // Buscar grupos con más de un jugador (empates)
    const ties = Object.values(scoreGroups).filter(group => group.length > 1);
    
    if (ties.length > 0) {
      // Hay empates - tomar el grupo con el puntaje más alto
      const maxScore = Math.max(...Object.keys(scoreGroups).map(Number));
      const tiedGroup = scoreGroups[maxScore];
      
      console.log('[TIE CHECK] Found tie with score', maxScore, ':', tiedGroup.map(p => p.name));
      
      setTiedPlayers(tiedGroup);
      // NO calcular orden todavía, esperar a que el usuario inicie el desempate
    } else {
      // No hay empates, calcular orden final
      console.log('[TIE CHECK] No ties found, calculating final order');
      calculateFinalOrder(results);
    }
  };
  
  const startTiebreaker = () => {
    // En modo multijugador, solo el host puede iniciar desempate
    if (isMultiplayer && !isHost) {
      console.log('[TIEBREAKER] Solo el host puede iniciar el desempate');
      audioService.playError();
      return;
    }
    
    console.log('[TIEBREAKER] Starting tiebreaker for:', tiedPlayers.map(p => p.name));
    
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    
    // En modo multijugador, emitir al servidor y ESPERAR el evento de vuelta
    if (isMultiplayer && socket && roomCode) {
      socket.send({
        tipo: 'start_tiebreaker',
        roomCode: roomCode,
        tiedPlayers: tiedPlayers.map(p => ({ id: p.id, name: p.name, color: p.color }))
      });
      console.log('[TIEBREAKER] Enviando evento al servidor - esperando confirmación');
      // ✅ NO actualizar estado aquí - esperar a recibir 'tiebreaker_started'
      return;
    }
    
    // Solo en modo local (sin multijugador)
    const sortedTiedPlayers = sortPlayersByTypeAndColor(tiedPlayers);
    
    setIsTiebreaker(true);
    setActivePlayers(sortedTiedPlayers);
    setCurrentPlayerIndex(0);
    setDiceResults({});
    setTiedPlayers([]);
  };

  const calculateFinalOrder = (finalDiceResults) => {
    console.log('[ORDER CALCULATION] Starting calculation...');
    console.log('[ORDER CALCULATION] Players:', players);
    console.log('[ORDER CALCULATION] Dice Results:', finalDiceResults);
    
    // Ordenar por resultado del dado (mayor primero)
    const finalOrderArray = [...players].sort((a, b) => {
      const diceA = finalDiceResults[a.id] || 0;
      const diceB = finalDiceResults[b.id] || 0;
      
      console.log(`[ORDER CALCULATION] Comparing: ${a.name}(color:${a.color}, dice:${diceA}) vs ${b.name}(color:${b.color}, dice:${diceB})`);
      
      if (diceA === diceB) {
        // En caso de empate, usar orden del tablero como desempate
        const indexA = BOARD_ORDER.indexOf(a.color);
        const indexB = BOARD_ORDER.indexOf(b.color);
        console.log(`[ORDER CALCULATION] TIE! Using board order: ${a.color}(${indexA}) vs ${b.color}(${indexB})`);
        return indexA - indexB;
      }
      
      // Mayor puntaje va primero (diceB - diceA para orden descendente)
      const comparison = diceB - diceA;
      console.log(`[ORDER CALCULATION] Result: ${comparison > 0 ? b.name : a.name} goes first`);
      return comparison;
    });

    console.log('[ORDER CALCULATION] Final order:', finalOrderArray.map((p, i) => 
      `${i+1}. ${p.name} (${p.color}) - Dice: ${finalDiceResults[p.id]}`
    ));
    
    setFinalOrder(finalOrderArray);
    setShowResults(true);
    
    // 🔊 Reproducir fanfarria especial al determinar el orden
    setTimeout(() => {
      audioService.playOrderDetermined();
    }, 300);
  };

  const handleContinue = () => {
    // En modo multijugador, solo el host puede continuar
    if (isMultiplayer && !isHost) {
      console.log('[ORDER DETERMINATION] Solo el host puede iniciar el juego');
      audioService.playError();
      return;
    }
    
    console.log('[ORDER DETERMINATION] Sending final order to parent:', 
      finalOrder.map((p, i) => `${i+1}. ${p.name} (${p.color})`));
    console.log('[ORDER DETERMINATION] Number of players:', finalOrder.length);
    
    // 🔊 Reproducir sonido de confirmación
    audioService.playClick();
    
    // En modo multijugador, enviar mensaje al servidor para que todos comiencen
    if (isMultiplayer && socket && roomCode) {
      socket.send({
        tipo: 'COMENZAR_JUEGO',
        roomCode: roomCode
      });
      console.log('[ORDER DETERMINATION] Enviando COMENZAR_JUEGO al servidor');
    } else {
      // En modo local, solo llamar al callback
      onOrderDetermined(finalOrder);
    }
  };

  const handleReroll = () => {
    // En modo multijugador, solo el host puede reiniciar
    if (isMultiplayer && !isHost) {
      console.log('[ORDER DETERMINATION] Solo el host puede reiniciar');
      audioService.playError();
      return;
    }
    
    console.log('[ORDER DETERMINATION] Rerolling dice...');
    
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    
    // En modo multijugador, emitir al servidor y ESPERAR el evento de vuelta
    if (isMultiplayer && socket && roomCode) {
      socket.send({
        tipo: 'start_reroll',
        roomCode: roomCode
      });
      console.log('[REROLL] Enviando evento al servidor - esperando confirmación');
      // ✅ NO actualizar estado aquí - esperar a recibir 'reroll_started'
      return;
    }
    
    // Solo en modo local (sin multijugador)
    const sortedPlayers = sortPlayersByTypeAndColor(players);
    
    setCurrentPlayerIndex(0);
    setDiceResults({});
    setFinalDiceResults({});
    setShowResults(false);
    setFinalOrder([]);
    setAnimatedValue(1);
    setTiedPlayers([]);
    setIsTiebreaker(false);
    setActivePlayers(sortedPlayers);
  };

  const currentPlayer = activePlayers[currentPlayerIndex];
  const allPlayersRolled = Object.keys(diceResults).length === activePlayers.length;
  const showCurrentPlayer = !allPlayersRolled || (allPlayersRolled && !showResults && tiedPlayers.length === 0);

  const getColorInfo = (colorId) => {
    const colorMap = {
      red: { name: 'Rojo', color: '#dc2626' },
      green: { name: 'Verde', color: '#16a34a' },
      yellow: { name: 'Amarillo', color: '#ca8a04' },
      blue: { name: 'Azul', color: '#2563eb' }
    };
    return colorMap[colorId];
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.header}>
          <button onClick={onBack} className={styles.backButton}>
            ← Atrás
          </button>
          <h1 className={styles.title}>Determinación del Orden</h1>
        </div>
        
        {!showResults ? (
          <>
            {isTiebreaker && (
              <div className={styles.tiebreakerBanner}>
                🎲 ¡DESEMPATE! 🎲
                <p>Los siguientes jugadores empataron y deben volver a lanzar:</p>
              </div>
            )}
            
            <p className={styles.instruction}>
              {isTiebreaker 
                ? 'Los jugadores empatados lanzarán de nuevo. El que obtenga el valor más alto ganará el desempate.'
                : 'Cada jugador lanzará el dado. El que obtenga el valor más alto comenzará primero. El orden continuará siguiendo el tablero en sentido antihorario.'}
            </p>

            {showCurrentPlayer && currentPlayer && (
              <div className={styles.currentPlayer}>
                <h2 className={styles.playerName}>
                  Turno de: {currentPlayer.name}
                  {isMultiplayer && currentPlayer.id === myPlayerId && (
                    <span style={{ color: '#10b981', marginLeft: '10px' }}>👤 (Tú)</span>
                  )}
                  {isMultiplayer && currentPlayer.id !== myPlayerId && (
                    <span style={{ color: '#f59e0b', marginLeft: '10px' }}>⏳ Esperando...</span>
                  )}
                </h2>
                <div 
                  className={styles.playerColor}
                  style={{ backgroundColor: getColorInfo(currentPlayer.color).color }}
                >
                  {getColorInfo(currentPlayer.color).name}
                </div>
                
                <div className={styles.diceContainer}>
                  <div className={`${styles.dice} ${isRolling ? styles.rolling : ''}`}>
                    {isRolling ? animatedValue : (diceResults[currentPlayer.id] || '🎲')}
                  </div>
                  
                  {!isRolling && !diceResults[currentPlayer.id] && (
                    <button 
                      className={styles.rollButton}
                      onClick={rollDice}
                      data-bot-roll="true"
                      disabled={isMultiplayer && currentPlayer.id !== myPlayerId}
                      style={{
                        opacity: (isMultiplayer && currentPlayer.id !== myPlayerId) ? 0.5 : 1,
                        cursor: (isMultiplayer && currentPlayer.id !== myPlayerId) ? 'not-allowed' : 'pointer'
                      }}
                    >
                      {isMultiplayer && currentPlayer.id !== myPlayerId 
                        ? '⏳ Esperando...' 
                        : currentPlayer.isHuman ? 'Lanzar Dado' : '🤖 Lanzando...'}
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Mostrar notificación de empate si todos lanzaron y hay empate */}
            {tiedPlayers.length > 0 && (
              <div className={styles.tieNotification}>
                <h3 className={styles.tieTitle}>⚠️ ¡Empate Detectado!</h3>
                <p className={styles.tieMessage}>
                  Los siguientes jugadores obtuvieron el mismo puntaje ({finalDiceResults[tiedPlayers[0].id]}):
                </p>
                <div className={styles.tiedPlayersList}>
                  {tiedPlayers.map(player => {
                    const colorInfo = getColorInfo(player.color);
                    return (
                      <div key={player.id} className={styles.tiedPlayer}>
                        <div 
                          className={styles.tiedPlayerColor}
                          style={{ backgroundColor: colorInfo.color }}
                        ></div>
                        <span>{player.name}</span>
                      </div>
                    );
                  })}
                </div>
                <button 
                  className={styles.tiebreakerButton}
                  onClick={startTiebreaker}
                  disabled={isMultiplayer && !isHost}
                  style={{
                    opacity: (isMultiplayer && !isHost) ? 0.7 : 1,
                    cursor: (isMultiplayer && !isHost) ? 'not-allowed' : 'pointer'
                  }}
                >
                  {isMultiplayer && !isHost ? '⏳ Esperando al host...' : 'Iniciar Desempate 🎲'}
                </button>
              </div>
            )}

            <div className={styles.results}>
              <h3 className={styles.resultsTitle}>Resultados:</h3>
              <div className={styles.resultsList}>
                {activePlayers.map((player) => {
                  const colorInfo = getColorInfo(player.color);
                  const result = diceResults[player.id] || finalDiceResults[player.id];
                  
                  return (
                    <div 
                      key={player.id} 
                      className={styles.playerResult}
                    >
                      <div 
                        className={styles.resultColor}
                        style={{ backgroundColor: colorInfo.color }}
                      ></div>
                      <span className={styles.resultName}>
                        {player.name}
                        {player.isHuman && ' 👤'}
                        {!player.isHuman && ' 🤖'}
                      </span>
                      <span className={styles.resultDice}>
                        {result ? `🎲 ${result}` : '⏳'}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </>
        ) : (
          <div className={styles.finalResults}>
            <h2 className={styles.orderTitle}>¡Orden de Juego Determinado!</h2>
            
            <div className={styles.orderList}>
              {finalOrder.map((player, index) => {
                const colorInfo = getColorInfo(player.color);
                
                return (
                  <div key={player.id} className={styles.orderItem}>
                    <div className={styles.orderNumber}>{index + 1}</div>
                    <div 
                      className={styles.orderColor}
                      style={{ backgroundColor: colorInfo.color }}
                    ></div>
                    <div className={styles.orderInfo}>
                      <span className={styles.orderName}>{player.name}</span>
                      <span className={styles.orderColorName}>({colorInfo.name})</span>
                      <span className={styles.orderDiceResult}>
                        Dado: {finalDiceResults[player.id]}
                      </span>
                    </div>
                    {index === 0 && (
                      <div className={styles.firstPlayerBadge}>
                        👑 Primer jugador
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            <p className={styles.orderExplanation}>
              {finalOrder.length > 0 && (
                <>
                  {finalOrder[0].name} ({getColorInfo(finalOrder[0].color).name}) obtuvo el valor más alto ({finalDiceResults[finalOrder[0].id]}) 
                  y comenzará el juego. Los demás seguirán el orden del tablero en sentido antihorario.
                </>
              )}
            </p>
            
            {isMultiplayer && !isHost && (
              <div style={{ 
                marginTop: '20px', 
                padding: '15px', 
                backgroundColor: '#f59e0b20',
                borderRadius: '8px',
                textAlign: 'center',
                color: '#f59e0b',
                fontWeight: 'bold'
              }}>
                ⏳ Esperando a que el host decida continuar...
              </div>
            )}
          </div>
        )}

        <div className={styles.actions}>
          
          {showResults && (
            <>
              <button
                className={`${styles.button} ${styles.rerollButton}`}
                onClick={handleReroll}
                disabled={isMultiplayer && !isHost}
                style={{
                  opacity: (isMultiplayer && !isHost) ? 0.5 : 1,
                  cursor: (isMultiplayer && !isHost) ? 'not-allowed' : 'pointer'
                }}
              >
                🎲 Volver a lanzar
                {isMultiplayer && !isHost && ' (Solo host)'}
              </button>
              
              <button
                className={`${styles.button} ${styles.continueButton}`}
                onClick={handleContinue}
                disabled={isMultiplayer && !isHost}
                style={{
                  opacity: (isMultiplayer && !isHost) ? 0.5 : 1,
                  cursor: (isMultiplayer && !isHost) ? 'not-allowed' : 'pointer'
                }}
              >
                Iniciar Juego
                {isMultiplayer && !isHost && ' (Solo host)'}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default TurnOrderDetermination;
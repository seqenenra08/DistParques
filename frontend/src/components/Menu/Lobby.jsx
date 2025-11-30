/**
 * Componente Lobby - Sala de espera multijugador
 */

import React, { useState, useEffect } from 'react';
import styles from './Lobby.module.css';
import audioService from '../../services/audioService';

const Lobby = ({ 
  roomCode, 
  roomState, 
  isHost, 
  onStartGame, 
  onLeaveLobby,
  socket 
}) => {
  const [copied, setCopied] = useState(false);
  const [players, setPlayers] = useState([]);
  const [readyCount, setReadyCount] = useState(0);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    if (roomState) {
      setPlayers(roomState.players || []);
      setReadyCount(roomState.ready_count || 0);
      
      // Encontrar el estado ready del jugador actual
      const currentPlayer = roomState.players?.find(p => p.socket_id === socket?.id);
      if (currentPlayer) {
        setIsReady(currentPlayer.is_ready);
      }
    }
  }, [roomState, socket]);

  const copyRoomCode = () => {
    navigator.clipboard.writeText(roomCode);
    audioService.playClick();
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const toggleReady = () => {
    if (socket) {
      const newReadyState = !isReady;
      socket.emit('set_ready', { ready: newReadyState });
      audioService.playClick();
    }
  };

  const handleStartGame = () => {
    audioService.playClick();
    onStartGame();
  };

  const handleLeave = () => {
    audioService.playClick();
    onLeaveLobby();
  };

  const canStart = isHost && readyCount === players.length - 1 && players.length >= 2;
  const allReady = readyCount === players.length - 1;

  return (
    <div className={styles.lobbyContainer}>
      <div className={styles.lobbyBox}>
        {/* Header con código de sala */}
        <div className={styles.header}>
          <div className={styles.titleSection}>
            <h1 className={styles.title}>Sala de Espera</h1>
            <p className={styles.subtitle}>Esperando jugadores...</p>
          </div>
          
          <div className={styles.roomCodeSection}>
            <label className={styles.roomCodeLabel}>Código de Sala</label>
            <div className={styles.roomCodeDisplay}>
              <span className={styles.roomCode}>{roomCode}</span>
              <button 
                className={styles.copyButton}
                onClick={copyRoomCode}
                title="Copiar código"
              >
                {copied ? '✓' : '📋'}
              </button>
            </div>
            {copied && <span className={styles.copiedMessage}>¡Copiado!</span>}
          </div>
        </div>

        {/* Lista de jugadores */}
        <div className={styles.playersSection}>
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>
              Jugadores ({players.length}/{roomState?.max_players || 4})
            </h2>
            <span className={styles.readyBadge}>
              {readyCount}/{players.length - 1} listos
            </span>
          </div>

          <div className={styles.playersList}>
            {players.map((player) => {
              // Determinar el emoji del color
              const colorEmojis = {
                red: '🔴',
                blue: '🔵',
                green: '🟢',
                yellow: '🟡'
              };
              const colorEmoji = player.color ? colorEmojis[player.color] : '';
              
              return (
                <div 
                  key={player.socket_id}
                  className={`${styles.playerCard} ${
                    player.is_ready ? styles.ready : styles.notReady
                  } ${player.is_host ? styles.host : ''}`}
                >
                  <div className={styles.playerInfo}>
                    <div className={styles.playerAvatar}>
                      {player.is_host ? '👑' : '👤'}
                    </div>
                    <div className={styles.playerDetails}>
                      <span className={styles.playerName}>
                        {colorEmoji && <span className={styles.colorIndicator}>{colorEmoji}</span>}
                        {player.name}
                        {player.is_host && <span className={styles.hostBadge}>Host</span>}
                      </span>
                      <span className={styles.playerStatus}>
                        {player.is_host ? 'Anfitrión' : player.is_ready ? '✓ Listo' : 'Esperando...'}
                      </span>
                    </div>
                  </div>
                  
                  {player.is_ready && !player.is_host && (
                    <div className={styles.readyIcon}>✓</div>
                  )}
                </div>
              );
            })}

            {/* Slots para bots */}
            {roomState?.num_bots > 0 && Array.from({ length: roomState.num_bots }).map((_, idx) => (
              <div key={`bot-${idx}`} className={`${styles.playerCard} ${styles.bot}`}>
                <div className={styles.playerInfo}>
                  <div className={styles.playerAvatar}>
                    🤖
                  </div>
                  <div className={styles.playerDetails}>
                    <span className={styles.playerName}>
                      Bot {idx + 1}
                      <span className={styles.botBadge}>BOT</span>
                    </span>
                    <span className={styles.playerStatus}>
                      Siempre listo
                    </span>
                  </div>
                </div>
                <div className={styles.readyIcon}>✓</div>
              </div>
            ))}

            {/* Slots vacíos */}
            {Array.from({ length: (roomState?.max_players || 4) - players.length - (roomState?.num_bots || 0) }).map((_, idx) => (
              <div key={`empty-${idx}`} className={styles.emptySlot}>
                <div className={styles.emptyIcon}>➕</div>
                <span className={styles.emptyText}>Esperando jugador...</span>
              </div>
            ))}
          </div>
        </div>

        {/* Instrucciones */}
        <div className={styles.instructions}>
          {isHost ? (
            <>
              <p className={styles.instructionText}>
                📢 Eres el anfitrión de la sala
              </p>
              {!allReady && players.length >= 2 && (
                <p className={styles.instructionText}>
                  Esperando a que todos los jugadores estén listos...
                </p>
              )}
              {players.length < 2 && (
                <p className={styles.instructionText}>
                  Comparte el código de sala con otros jugadores
                </p>
              )}
            </>
          ) : (
            <p className={styles.instructionText}>
              {isReady 
                ? '✓ Estás listo. Esperando al anfitrión...'
                : '👉 Haz clic en "Listo" cuando estés preparado'
              }
            </p>
          )}
        </div>

        {/* Botones de acción */}
        <div className={styles.actions}>
          {!isHost && (
            <button
              className={`${styles.readyButton} ${isReady ? styles.readyActive : ''}`}
              onClick={toggleReady}
            >
              <span className={styles.buttonIcon}>{isReady ? '✓' : '👍'}</span>
              {isReady ? 'Cancelar' : 'Listo'}
            </button>
          )}

          {isHost && (
            <button
              className={styles.startButton}
              onClick={handleStartGame}
              disabled={!canStart}
              title={!canStart ? 'Esperando jugadores listos' : 'Iniciar juego'}
            >
              <span className={styles.buttonIcon}>🎮</span>
              Iniciar Juego
            </button>
          )}

          <button
            className={styles.leaveButton}
            onClick={handleLeave}
          >
            <span className={styles.buttonIcon}>🚪</span>
            Salir
          </button>
        </div>

        {/* Info adicional */}
        <div className={styles.footer}>
          <p className={styles.footerText}>
            Mínimo 2 jugadores para iniciar
          </p>
        </div>
      </div>
    </div>
  );
};

export default Lobby;

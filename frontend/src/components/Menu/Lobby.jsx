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
      {/* Panel lateral izquierdo - Control de sala */}
      <div className={styles.commandCenter}>
        {/* Header de Estado del Sistema */}
        <div className={styles.systemHeader}>
          <div className={styles.systemStatus}>
            <div className={styles.statusIndicator}></div>
            <span className={styles.statusText}>SALA ACTIVA</span>
          </div>
          <div className={styles.serverInfo}>
            <span className={styles.serverLabel}>ID:</span>
            <span className={styles.serverId}>{roomCode}</span>
            <button 
              className={styles.cloneButton}
              onClick={copyRoomCode}
              title="Clonar identificador"
            >
              {copied ? '⚡' : '📡'}
            </button>
          </div>
          {copied && <div className={styles.cloneSuccess}>COPIADO</div>}
        </div>

        {/* Lista de conexiones */}
        <div className={styles.connectionsPanel}>
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle}>NODOS CONECTADOS</h2>
            <div className={styles.connectionStats}>
              <span className={styles.statLabel}>ACTIVOS:</span>
              <span className={styles.statValue}>{players.length}/{roomState?.max_players || 4}</span>
            </div>
          </div>

          <div className={styles.networkGrid}>
              {players.map((player) => {
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
                    className={`${styles.nodeCard} ${
                      player.is_ready ? styles.nodeReady : styles.nodePending
                    } ${player.is_host ? styles.nodeHost : ''}`}
                  >
                    <div className={styles.nodeHeader}>
                      <div className={styles.nodeId}>
                        NODE_{player.socket_id?.slice(-4) || 'XXXX'}
                      </div>
                      <div className={`${styles.nodeStatus} ${player.is_ready || player.is_host ? styles.online : styles.sync}`}>
                        {player.is_ready || player.is_host ? 'ONLINE' : 'SYNC'}
                      </div>
                    </div>
                    <div className={styles.nodeInfo}>
                      <div className={styles.nodeUser}>
                        <span className={styles.userIcon}>{player.is_host ? '⚡' : '👤'}</span>
                        <span className={styles.userName}>{player.name}</span>
                      </div>
                      <div className={styles.nodeMetadata}>
                        <span className={styles.colorCode}>{colorEmoji} {player.color?.toUpperCase() || 'N/A'}</span>
                        <span className={styles.accessLevel}>
                          {player.is_host ? 'ADMIN' : 'USER'}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* Nodos Bot */}
              {roomState?.num_bots > 0 && Array.from({ length: roomState.num_bots }).map((_, idx) => (
                <div key={`bot-${idx}`} className={`${styles.nodeCard} ${styles.nodeBot}`}>
                  <div className={styles.nodeHeader}>
                    <div className={styles.nodeId}>AI_BOT_{idx + 1}</div>
                    <div className={`${styles.nodeStatus} ${styles.online}`}>READY</div>
                  </div>
                  <div className={styles.nodeInfo}>
                    <div className={styles.nodeUser}>
                      <span className={styles.userIcon}>🤖</span>
                      <span className={styles.userName}>AUTONOMOUS_AGENT_{idx + 1}</span>
                    </div>
                    <div className={styles.nodeMetadata}>
                      <span className={styles.colorCode}>⚙️ AUTO</span>
                      <span className={styles.accessLevel}>BOT</span>
                    </div>
                  </div>
                </div>
              ))}

              {/* Nodos Vacíos */}
              {Array.from({ length: (roomState?.max_players || 4) - players.length - (roomState?.num_bots || 0) }).map((_, idx) => (
                <div key={`empty-${idx}`} className={styles.emptyNode}>
                  <div className={styles.emptyIcon}>📶</div>
                  <span className={styles.emptyLabel}>SLOT_DISPONIBLE</span>
                  <span className={styles.emptyDesc}>Esperando conexión...</span>
                </div>
              ))}
            </div>
          </div>

          {/* Panel de Acciones */}
          <div className={styles.actionMatrix}>
            {!isHost && (
              <button
                className={`${styles.readyToggle} ${isReady ? styles.toggleActive : ''}`}
                onClick={toggleReady}
              >
                <div className={styles.toggleIcon}>{isReady ? '⚡' : '🔋'}</div>
                <div className={styles.toggleLabel}>
                  {isReady ? 'CANCELAR' : 'CONFIRMAR'}
                </div>
              </button>
            )}

            {isHost && (
              <button
                className={`${styles.launchButton} ${!canStart ? styles.launchDisabled : ''}`}
                onClick={handleStartGame}
                disabled={!canStart}
              >
                <div className={styles.launchIcon}>🚀</div>
                <div className={styles.launchLabel}>INICIAR</div>
              </button>
            )}

            <button
              className={styles.disconnectButton}
              onClick={handleLeave}
            >
              <div className={styles.disconnectIcon}>🔌</div>
              <div className={styles.disconnectLabel}>SALIR</div>
            </button>
          </div>
        </div>

        {/* Panel lateral derecho - Terminal de información */}
        <div className={styles.infoPanel}>
          <div className={styles.terminalWindow}>
            <div className={styles.terminalHeader}>
              === ESTADO DE LA SALA ===
            </div>
            <div className={styles.terminalContent}>
              <div className={styles.glitchText}>
{`> Sala ${roomCode} activa...
> Monitoreando conexiones...
> Estado: [${allReady ? 'READY' : 'SYNC'}]
> 
> ESTADÍSTICAS:
>   • Nodos conectados: ${players.length}/${roomState?.max_players || 4}
>   • Bots activos: ${roomState?.num_bots || 0}
>   • Confirmaciones: ${readyCount}/${players.length - 1}
>   • Mínimo requerido: 2 usuarios
> 
> PERMISOS:
>   • Host: ${isHost ? 'TÚ' : players.find(p => p.is_host)?.name || 'N/A'}
>   • Tu estado: ${isHost ? 'ADMIN' : (isReady ? 'READY' : 'PENDING')}
> 
> ${isHost ? (
  !allReady && players.length >= 2 ? 'Esperando confirmaciones...' :
  players.length < 2 ? 'Compartir código de sala' :
  'Todos listos - Puedes iniciar'
) : (
  isReady ? 'Esperando al host...' : 'Confirma tu preparación'
)}
> 
> Sistema en espera...`}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Lobby;

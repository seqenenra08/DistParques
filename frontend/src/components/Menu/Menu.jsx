/**
 * Componente Menu - Pantalla de inicio del juego
 */

import React, { useState } from 'react';
import styles from './Menu.module.css';
import ColorSelection from './ColorSelection';
import TurnOrderDetermination from './TurnOrderDetermination';
import Settings from './Settings';
import RoomSelection from './RoomSelection';
import audioService from '../../services/audioService';

const Menu = ({ onStartGame, onShowRules, onCreateRoom, onJoinRoom, availableColors = [], showColorSelector = false, onRoomInfoReceived }) => {
  const [selectedPlayers, setSelectedPlayers] = useState(2);
  const [selectedBots, setSelectedBots] = useState(0);
  const [currentStep, setCurrentStep] = useState('menu'); // 'menu', 'players', 'bots', 'lobby', 'order', 'roomSelection'
  const [showSettings, setShowSettings] = useState(false); // Para mostrar/ocultar ajustes
  const [playersForOrder, setPlayersForOrder] = useState([]); // Jugadores para determinar orden

  const handleStartGame = () => {
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    setCurrentStep('players');
  };
  
  const handleContinueToBots = () => {
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    setCurrentStep('bots');
  };

  const handleContinueToLobby = () => {
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    setCurrentStep('lobby');
  };

  const handleMultiplayerGame = () => {
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    setCurrentStep('roomSelection');
  };

  const handleStartGameFromLobby = () => {
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    
    // Generar jugadores con colores aleatorios
    const allColors = ['red', 'blue', 'green', 'yellow'];
    const shuffledColors = [...allColors].sort(() => Math.random() - 0.5);
    
    const humanPlayers = selectedPlayers - selectedBots;
    const tempPlayers = [];
    
    // Crear jugadores humanos
    for (let i = 0; i < humanPlayers; i++) {
      tempPlayers.push({
        id: `player_${shuffledColors[i]}`,
        name: `Jugador ${i + 1}`,
        color: shuffledColors[i],
        isHuman: true
      });
    }
    
    // Crear bots
    for (let i = 0; i < selectedBots; i++) {
      const colorIndex = humanPlayers + i;
      tempPlayers.push({
        id: `player_${shuffledColors[colorIndex]}`,
        name: `Bot ${i + 1}`,
        color: shuffledColors[colorIndex],
        isHuman: false
      });
    }
    
    console.log('[MENU] Players created, going to order determination:', tempPlayers);
    setPlayersForOrder(tempPlayers);
    setCurrentStep('order');
  };

  const handleOrderDetermined = (orderedPlayers) => {
    console.log('[MENU] Order determined, starting game:', orderedPlayers);
    
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    
    // Pasar los jugadores ordenados al componente padre
    onStartGame({
      numberOfPlayers: orderedPlayers.length,
      players: orderedPlayers
    });
  };

  const handleBackToMenu = () => {
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    setCurrentStep('menu');
  };
  
  const handleBackToPlayers = () => {
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    setCurrentStep('players');
  };

  const handleBackToBots = () => {
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    setCurrentStep('bots');
  };

  const handleBackToLobby = () => {
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    setCurrentStep('lobby');
  };
  
  const handleSelectPlayers = (numPlayers) => {
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    setSelectedPlayers(numPlayers);
    setSelectedBots(0); // Reset bots al cambiar número de jugadores
  };

  const handleSelectBots = (numBots) => {
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    setSelectedBots(numBots);
  };

  const handleShowSettings = () => {
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    setShowSettings(true);
  };

  const handleCloseSettings = () => {
    setShowSettings(false);
  };

  const handleCreateRoom = (data) => {
    onCreateRoom(data);
  };

  const handleJoinRoom = (data) => {
    onJoinRoom(data);
  };

  // Renderizar según el paso actual
  if (currentStep === 'roomSelection') {
    return (
      <RoomSelection
        onCreateRoom={handleCreateRoom}
        onJoinRoom={handleJoinRoom}
        onBack={handleBackToMenu}
        availableColors={availableColors}
        showColorSelector={showColorSelector}
        onRoomInfoReceived={onRoomInfoReceived}
      />
    );
  }
  
  if (currentStep === 'players') {
    return (
      <div className={styles.menuContainer}>
        <div className={styles.menuBox}>
          <div className={styles.header}>
            <button className={styles.backButton} onClick={handleBackToMenu}>
              ← Atrás
            </button>
            <div className={styles.titleContainer}>
              <h1 className={styles.title}>Crear Partida</h1>
              <p className={styles.subtitle}>Selecciona el número de jugadores</p>
            </div>
          </div>

          <div className={styles.mainContent}>
            <div className={styles.playersSection}>
              <div className={styles.sectionHeader}>
                <div className={styles.sectionIcon}>👥</div>
                <h2 className={styles.sectionTitle}>Número de Jugadores</h2>
              </div>
              
              <div className={styles.playerCards}>
                {[2, 3, 4].map((num) => (
                  <div
                    key={num}
                    className={`${styles.playerCard} ${
                      selectedPlayers === num ? styles.selected : ''
                    }`}
                    onClick={() => handleSelectPlayers(num)}
                  >
                    <div className={styles.playerNumber}>{num}</div>
                    <div className={styles.playerLabel}>Jugadores</div>
                  </div>
                ))}
              </div>
            </div>

            <button
              className={styles.continueButton}
              onClick={handleContinueToBots}
            >
              <span className={styles.buttonIcon}>▶</span>
              Continuar
            </button>

            <div className={styles.instructionText}>
              Selecciona cuántos jugadores participarán en la partida
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (currentStep === 'bots') {
    // Máximo de bots: total de jugadores - 1 (debe quedar al menos 1 humano)
    const maxBots = selectedPlayers - 1;
    const botsOptions = Array.from({ length: maxBots + 1 }, (_, i) => i); // [0, 1, 2, ...maxBots]

    return (
      <div className={styles.menuContainer}>
        <div className={styles.menuBox}>
          <div className={styles.header}>
            <button className={styles.backButton} onClick={handleBackToPlayers}>
              ← Atrás
            </button>
            <div className={styles.titleContainer}>
              <h1 className={styles.title}>Crear Partida</h1>
              <p className={styles.subtitle}>Selecciona el número de bots</p>
            </div>
          </div>

          <div className={styles.mainContent}>
            <div className={styles.playersSection}>
              <div className={styles.sectionHeader}>
                <div className={styles.sectionIcon}>🤖</div>
                <h2 className={styles.sectionTitle}>Número de Bots</h2>
              </div>
              
              <div className={styles.playerCards}>
                {botsOptions.map((num) => (
                  <div
                    key={num}
                    className={`${styles.playerCard} ${
                      selectedBots === num ? styles.selected : ''
                    }`}
                    onClick={() => handleSelectBots(num)}
                  >
                    <div className={styles.playerNumber}>{num}</div>
                    <div className={styles.playerLabel}>
                      {num === 0 ? 'Sin Bots' : num === 1 ? 'Bot' : 'Bots'}
                    </div>
                  </div>
                ))}
              </div>

              <div className={styles.botsSummary}>
                <p className={styles.summaryText}>
                  Total de jugadores: <strong>{selectedPlayers}</strong>
                </p>
                <p className={styles.summaryDetail}>
                  {selectedPlayers - selectedBots} {selectedPlayers - selectedBots === 1 ? 'humano' : 'humanos'} 
                  {selectedBots > 0 && ` + ${selectedBots} ${selectedBots === 1 ? 'bot' : 'bots'}`}
                </p>
              </div>
            </div>

            <button
              className={styles.continueButton}
              onClick={handleContinueToLobby}
            >
              <span className={styles.buttonIcon}>▶</span>
              Continuar
            </button>

            <div className={styles.instructionText}>
              Los bots jugarán automáticamente
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (currentStep === 'lobby') {
    const humanPlayers = selectedPlayers - selectedBots;
    
    return (
      <div className={styles.menuContainer}>
        <div className={styles.menuBox}>
          <div className={styles.header}>
            <button className={styles.backButton} onClick={handleBackToBots}>
              ← Atrás
            </button>
            <div className={styles.titleContainer}>
              <h1 className={styles.title}>Sala de Espera</h1>
              <p className={styles.subtitle}>Todo listo para comenzar</p>
            </div>
          </div>

          <div className={styles.mainContent}>
            <div className={styles.playersSection}>
              <div className={styles.sectionHeader}>
                <div className={styles.sectionIcon}>👥</div>
                <h2 className={styles.sectionTitle}>Jugadores</h2>
              </div>
              
              <div className={styles.lobbyInfo}>
                <div className={styles.lobbyCard}>
                  <div className={styles.lobbyIcon}>🎮</div>
                  <div className={styles.lobbyLabel}>Jugadores Humanos</div>
                  <div className={styles.lobbyValue}>{humanPlayers}</div>
                </div>
                
                <div className={styles.lobbyCard}>
                  <div className={styles.lobbyIcon}>🤖</div>
                  <div className={styles.lobbyLabel}>Bots</div>
                  <div className={styles.lobbyValue}>{selectedBots}</div>
                </div>
                
                <div className={styles.lobbyCard}>
                  <div className={styles.lobbyIcon}>🎯</div>
                  <div className={styles.lobbyLabel}>Total</div>
                  <div className={styles.lobbyValue}>{selectedPlayers}</div>
                </div>
              </div>

              <div className={styles.lobbyNote}>
                <p className={styles.noteText}>
                  Los colores y el orden de turnos se asignarán aleatoriamente
                </p>
              </div>
            </div>

            <button
              className={styles.startButton}
              onClick={handleStartGameFromLobby}
            >
              <span className={styles.buttonIcon}>🚀</span>
              Iniciar Partida
            </button>

            <div className={styles.instructionText}>
              El anfitrión puede iniciar la partida cuando esté listo
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (currentStep === 'order') {
    return (
      <TurnOrderDetermination
        players={playersForOrder}
        onOrderDetermined={handleOrderDetermined}
        onBack={handleBackToLobby}
      />
    );
  }

  // Pantalla principal del menú
  return (
    <div className={styles.menuContainer}>
      {/* Modal de Ajustes */}
      {showSettings && <Settings onClose={handleCloseSettings} />}
      
      <div className={styles.menuBox}>
        <div className={styles.header}>
          <div className={styles.titleContainer}>
            <h1 className={styles.title}>Parchese</h1>
            <p className={styles.subtitle}>¡Bienvenido al juego clásico!</p>
          </div>
        </div>

        <div className={styles.mainContent}>
          <div className={styles.playersSection}>
            <div className={styles.sectionHeader}>
              <div className={styles.sectionIcon}>🎮</div>
              <h2 className={styles.sectionTitle}>¿Cómo quieres jugar?</h2>
            </div>
            
            <div className={styles.modeSelection}>
              <button
                className={styles.modeCard}
                onClick={handleStartGame}
              >
                <div className={styles.modeIcon}>👥</div>
                <h3 className={styles.modeTitle}>Crear Partida</h3>
                <p className={styles.modeDescription}>
                  Juega localmente en este dispositivo
                </p>
              </button>
              
              <button
                className={styles.modeCard}
                onClick={handleMultiplayerGame}
              >
                <div className={styles.modeIcon}>🌐</div>
                <h3 className={styles.modeTitle}>Unirse a Partida</h3>
                <p className={styles.modeDescription}>
                  Juega en línea con otros jugadores
                </p>
              </button>
            </div>
          </div>

          <div className={styles.bottomActions}>
            <button
              className={styles.rulesButton}
              onClick={onShowRules}
            >
              <span className={styles.buttonIcon}>📋</span>
              Ver Reglas
            </button>
            
            <button 
              className={styles.settingsButton}
              onClick={handleShowSettings}
            >
              <span className={styles.buttonIcon}>⚙️</span>
              Ajustes
            </button>
          </div>

          <div className={styles.instructionText}>
            Elige entre crear una partida local o unirte a una partida en línea
          </div>
        </div>
      </div>
    </div>
  );
};

export default Menu;

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
  const [currentStep, setCurrentStep] = useState('menu'); // 'menu', 'colors', 'order', 'roomSelection'
  const [playersWithColors, setPlayersWithColors] = useState([]);
  const [includeBot, setIncludeBot] = useState(false); // Para controlar si se agrega un bot
  const [showSettings, setShowSettings] = useState(false); // Para mostrar/ocultar ajustes

  const handleStartGame = () => {
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    setCurrentStep('colors');
  };

  const handleMultiplayerGame = () => {
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    setCurrentStep('roomSelection');
  };

  const handleColorsSelected = (players) => {
    console.log('[MENU] Colors selected, players:', players);
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    setPlayersWithColors(players);
    setCurrentStep('order');
  };

  const handleOrderDetermined = (orderedPlayers) => {
    console.log('[MENU] Order determined, passing players to game:', orderedPlayers);
    
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    
    // Si se seleccionó incluir un bot, agregar al final
    let finalPlayers = orderedPlayers;
    if (includeBot) {
      // Encontrar un color disponible para el bot
      const usedColors = orderedPlayers.map(p => p.color);
      const availableColors = ['red', 'blue', 'green', 'yellow'].filter(
        color => !usedColors.includes(color)
      );
      
      if (availableColors.length > 0) {
        const botColor = availableColors[0];
        const botPlayer = {
          id: `player_${botColor}`,
          name: `Bot ${botColor.charAt(0).toUpperCase() + botColor.slice(1)}`,
          color: botColor,
          isHuman: false,
          turnOrder: orderedPlayers.length // El bot va al final
        };
        
        finalPlayers = [...orderedPlayers, botPlayer];
        console.log('[MENU] Bot agregado:', botPlayer);
      }
    }
    
    // Pasar los jugadores ordenados al componente padre
    onStartGame({
      numberOfPlayers: finalPlayers.length,
      players: finalPlayers
    });
  };

  const handleBackToMenu = () => {
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    setCurrentStep('menu');
    setPlayersWithColors([]);
  };

  const handleBackToColors = () => {
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    setCurrentStep('colors');
  };
  
  const handleSelectPlayers = (numPlayers) => {
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    setSelectedPlayers(numPlayers);
    setIncludeBot(false);
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

  if (currentStep === 'colors') {
    return (
      <ColorSelection
        numberOfPlayers={selectedPlayers}
        onColorsSelected={handleColorsSelected}
        onBack={handleBackToMenu}
      />
    );
  }

  if (currentStep === 'order') {
    return (
      <TurnOrderDetermination
        players={playersWithColors}
        onOrderDetermined={handleOrderDetermined}
        onBack={handleBackToColors}
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
            <h1 className={styles.title}>Parcheesi</h1>
            <p className={styles.subtitle}>¡Bienvenido al juego clásico!</p>
          </div>
          <div className={styles.gameIcon}>
            <div className={styles.iconShape}>🎲</div>
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

          <div className={styles.actionSection}>
            <button
              className={styles.createGameButton}
              onClick={handleStartGame}
            >
              <span className={styles.buttonIcon}>👥</span>
              Partida Local
            </button>
            
            <button
              className={styles.multiplayerButton}
              onClick={handleMultiplayerGame}
            >
              <span className={styles.buttonIcon}>🌐</span>
              Multijugador
            </button>
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
            Selecciona el número de jugadores y continúa para elegir colores
          </div>
        </div>
      </div>
    </div>
  );
};

export default Menu;

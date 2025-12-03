/**
 * Componente ColorSelection - Selección de colores por jugador
 */

import React, { useState } from 'react';
import styles from './ColorSelection.module.css';
import audioService from '../../services/audioService';

const COLORS = [
  { id: 'red', name: 'Rojo', color: '#dc2626' },
  { id: 'green', name: 'Verde', color: '#16a34a' },
  { id: 'yellow', name: 'Amarillo', color: '#ca8a04' },
  { id: 'blue', name: 'Azul', color: '#2563eb' }
];

const ColorSelection = ({ numberOfPlayers, onColorsSelected, onBack }) => {
  const [currentPlayer, setCurrentPlayer] = useState(1);
  const [selectedColors, setSelectedColors] = useState([]);
  const [playerNames, setPlayerNames] = useState(
    Array.from({ length: numberOfPlayers }, (_, i) => `Jugador ${i + 1}`)
  );

  const handleColorSelect = (colorId) => {
    // 🔊 Reproducir sonido de selección
    audioService.playClick();
    
    const newSelectedColors = [...selectedColors];
    newSelectedColors[currentPlayer - 1] = colorId;
    setSelectedColors(newSelectedColors);

    if (currentPlayer < numberOfPlayers) {
      setCurrentPlayer(currentPlayer + 1);
    }
  };

  const handlePlayerNameChange = (index, name) => {
    const newNames = [...playerNames];
    newNames[index] = name || `Jugador ${index + 1}`;
    setPlayerNames(newNames);
  };

  const handleBack = () => {
    // 🔊 Reproducir sonido de click
    audioService.playClick();
    
    if (currentPlayer > 1) {
      setCurrentPlayer(currentPlayer - 1);
      const newSelectedColors = [...selectedColors];
      newSelectedColors[currentPlayer - 2] = null;
      setSelectedColors(newSelectedColors);
    } else {
      onBack();
    }
  };

  const handleFinish = () => {
    // 🔊 Reproducir sonido de confirmación
    audioService.playClick();
    
    const players = selectedColors.map((colorId, index) => ({
      id: `player_${colorId}`, // Usar el color como ID
      name: playerNames[index],
      color: colorId
    }));
    
    console.log('[COLOR SELECTION] Players selected:', players.map(p => `${p.name} (${p.color})`));
    console.log('[COLOR SELECTION] Number of players:', players.length);
    console.log('[COLOR SELECTION] Full player data:', players);
    onColorsSelected(players);
  };

  const getAvailableColors = () => {
    return COLORS.filter(color => !selectedColors.includes(color.id));
  };

  const isComplete = selectedColors.length === numberOfPlayers && selectedColors.every(color => color);

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.header}>
          <button onClick={handleBack} className={styles.backButton}>
            ← Atrás
          </button>
          <h1 className={styles.title}>Selección de Colores</h1>
        </div>
        
        {!isComplete ? (
          <>
            <div className={styles.currentPlayerInfo}>
              <h2 className={styles.playerTitle}>
                {playerNames[currentPlayer - 1]}
              </h2>
              <p className={styles.instruction}>Selecciona tu color:</p>
              
              <div className={styles.nameInput}>
                <label htmlFor={`player-name-${currentPlayer}`}>Nombre del jugador:</label>
                <input
                  id={`player-name-${currentPlayer}`}
                  type="text"
                  value={playerNames[currentPlayer - 1]}
                  onChange={(e) => handlePlayerNameChange(currentPlayer - 1, e.target.value)}
                  className={styles.input}
                  placeholder={`Jugador ${currentPlayer}`}
                />
              </div>
            </div>

            <div className={styles.colorsGrid}>
              {getAvailableColors().map((color) => (
                <button
                  key={color.id}
                  className={styles.colorButton}
                  style={{ 
                    backgroundColor: color.color,
                    border: `3px solid ${color.color}`
                  }}
                  onClick={() => handleColorSelect(color.id)}
                >
                  <span className={styles.colorName}>{color.name}</span>
                </button>
              ))}
            </div>

            {selectedColors.length === 0 && (
              <p className={styles.hint}>
                Los colores seleccionados no estarán disponibles para los siguientes jugadores
              </p>
            )}
          </>
        ) : (
          <div className={styles.summary}>
            <h2 className={styles.summaryTitle}>Resumen de Jugadores</h2>
            <div className={styles.playersList}>
              {selectedColors.map((colorId, index) => {
                const color = COLORS.find(c => c.id === colorId);
                return (
                  <div key={index} className={styles.playerSummary}>
                    <div 
                      className={styles.colorIndicator}
                      style={{ backgroundColor: color.color }}
                    ></div>
                    <span className={styles.playerName}>{playerNames[index]}</span>
                    <span className={styles.playerColor}>({color.name})</span>
                  </div>
                );
              })}
            </div>
            
            <p className={styles.nextStep}>
              A continuación, todos los jugadores lanzarán el dado para determinar el orden de juego.
            </p>
          </div>
        )}

        <div className={styles.selectedColors}>
          <h3>Colores ya seleccionados:</h3>
          <div className={styles.selectedColorsList}>
            {selectedColors.map((colorId, index) => {
              if (!colorId) return null;
              const color = COLORS.find(c => c.id === colorId);
              return (
                <div key={index} className={styles.selectedColor}>
                  <div 
                    className={styles.colorDot}
                    style={{ backgroundColor: color.color }}
                  ></div>
                  <span>{playerNames[index]} - {color.name}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className={styles.actions}>
          {isComplete && (
            <button
              className={`${styles.button} ${styles.continueButton}`}
              onClick={handleFinish}
            >
              Continuar al Juego
            </button>
          )}
        </div>

        <div className={styles.progress}>
          <div className={styles.progressBar}>
            <div 
              className={styles.progressFill}
              style={{ width: `${(selectedColors.filter(c => c).length / numberOfPlayers) * 100}%` }}
            ></div>
          </div>
          <span className={styles.progressText}>
            {selectedColors.filter(c => c).length} de {numberOfPlayers} jugadores
          </span>
        </div>
      </div>
    </div>
  );
};

export default ColorSelection;
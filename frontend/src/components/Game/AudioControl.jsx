/**
 * Componente de Control de Audio
 * Permite al usuario ajustar el volumen y silenciar los sonidos
 */

import React, { useState, useEffect } from 'react';
import styles from './AudioControl.module.css';
import audioService from '../../services/audioService';

const AudioControl = () => {
  const [volume, setVolume] = useState(0.5);
  const [isMuted, setIsMuted] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // Inicializar el servicio de audio
    audioService.initialize();
  }, []);

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    audioService.setVolume(newVolume);
    
    // Si estaba silenciado y cambiamos el volumen, quitar el silencio
    if (isMuted && newVolume > 0) {
      setIsMuted(false);
      audioService.toggleMute(); // Desactivar mute
    }
  };

  const handleToggleMute = () => {
    const newMutedState = audioService.toggleMute();
    setIsMuted(newMutedState);
    
    // Reproducir sonido de confirmación solo si se está desmuteando
    if (!newMutedState) {
      setTimeout(() => {
        audioService.playClick();
      }, 100);
    }
  };

  const handleTogglePanel = () => {
    setIsOpen(!isOpen);
    audioService.playClick();
  };

  const getVolumeIcon = () => {
    if (isMuted || volume === 0) return '🔇';
    if (volume < 0.3) return '🔈';
    if (volume < 0.7) return '🔉';
    return '🔊';
  };

  return (
    <div className={`${styles.audioControl} ${isOpen ? styles.open : ''}`}>
      <button 
        className={styles.toggleButton}
        onClick={handleTogglePanel}
        title="Controles de audio"
      >
        {getVolumeIcon()}
      </button>

      {isOpen && (
        <div className={styles.controlPanel}>
          <div className={styles.header}>
            <h3>Audio</h3>
          </div>

          <div className={styles.muteSection}>
            <button
              className={`${styles.muteButton} ${isMuted ? styles.muted : ''}`}
              onClick={handleToggleMute}
              title={isMuted ? 'Activar sonido' : 'Silenciar'}
            >
              {isMuted ? '🔇 Silenciado' : '🔊 Activo'}
            </button>
          </div>

          <div className={styles.volumeSection}>
            <label htmlFor="volume-slider">Volumen</label>
            <div className={styles.sliderContainer}>
              <span className={styles.volumeMin}>🔈</span>
              <input
                id="volume-slider"
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={volume}
                onChange={handleVolumeChange}
                className={styles.volumeSlider}
                disabled={isMuted}
              />
              <span className={styles.volumeMax}>🔊</span>
            </div>
            <div className={styles.volumeValue}>
              {Math.round(volume * 100)}%
            </div>
          </div>

          <div className={styles.soundList}>
            <p className={styles.soundListTitle}>Efectos de sonido:</p>
            <ul>
              <li>🎲 Lanzamiento de dados</li>
              <li>🎯 Movimiento de fichas</li>
              <li>💥 Captura de fichas</li>
              <li>🏁 Ficha en meta</li>
              <li>🏆 Victoria</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default AudioControl;

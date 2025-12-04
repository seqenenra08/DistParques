/**
 * Componente Dice - Dos dados con animación de lanzamiento
 */

import React, { useState, useEffect } from 'react';
import styles from './Dice.module.css';
import audioService from '../../services/audioService';

const Dice = ({ 
  value = null,  // Ahora puede ser un array [dice1, dice2] o null
  isRolling = false, 
  onRoll,
  disabled = false,
  playerColor = 'blue',
  noMovesAvailable = false,
  startPhaseAttempts = null  // { current: 1, max: 3 } para mostrar "1/3"
}) => {
  const [animating, setAnimating] = useState(false);
  const [displayedValues, setDisplayedValues] = useState([null, null]);
  const [showResults, setShowResults] = useState(false); // ✅ Nuevo estado para controlar cuándo mostrar resultados
  const [wasRolling, setWasRolling] = useState(false); // ✅ Rastrear si estaba rodando antes
  
  // Detectar cuando isRolling cambia de true a false (animación terminó)
  useEffect(() => {
    if (wasRolling && !isRolling && !animating) {
      // La animación del servidor terminó
      console.log('[DICE] ✅ Animación del servidor terminó - mostrando resultados');
      // Esperar un pequeño delay para asegurar que displayedValues esté actualizado
      setTimeout(() => {
        setShowResults(true);
      }, 100);
    }
    setWasRolling(isRolling);
  }, [isRolling, animating, wasRolling]);
  
  // Actualizar los valores mostrados cuando value cambia
  useEffect(() => {
    if (Array.isArray(value) && value.length === 2 && value[0] !== null && value[1] !== null) {
      console.log('[DICE] 🎲🎲 Actualizando displayedValues a:', value);
      setDisplayedValues(value);
      
      // 🔊 Reproducir sonido de dobles si los dados son iguales
      if (value[0] === value[1] && !animating) {
        setTimeout(() => {
          audioService.playDoubles();
        }, 300);
      }
      // NO limpiar showResults aquí - dejar que la animación lo maneje
    }
    // ✅ NO limpiar displayedValues cuando value es null
    // Los valores se mantendrán visibles hasta la próxima tirada
  }, [value, animating]);
  
  // Verificar si tenemos valores válidos
  const hasValues = displayedValues[0] !== null && displayedValues[1] !== null;
  const displayValue1 = displayedValues[0];
  const displayValue2 = displayedValues[1];
  const sum = hasValues ? displayedValues[0] + displayedValues[1] : 0;
  
  console.log('[DICE] Render - value:', value, ', displayedValues:', displayedValues, ', hasValues:', hasValues);
  console.log('[DICE] Props - disabled:', disabled, ', isRolling:', isRolling, ', animating:', animating, ', showResults:', showResults);

  const handleRoll = async () => {
    console.log('[DICE] handleRoll called - disabled:', disabled, ', animating:', animating, ', isRolling:', isRolling);
    if (disabled || animating || isRolling) {
      console.log('[DICE] Roll blocked - disabled:', disabled, ', animating:', animating, ', isRolling:', isRolling);
      return;
    }
    
    console.log('[DICE] Roll executing...');
    setAnimating(true);
    setShowResults(false); // Ocultar resultados durante la animación
    setDisplayedValues([null, null]); // ✅ Limpiar valores al iniciar nueva tirada
    
    // 🔊 Reproducir sonido de dados
    audioService.playDiceRoll();
    
    // Llamar al callback para enviar al servidor
    if (onRoll) {
      onRoll();
    }
    
    // Simular animación por 1 segundo (ajustado al audio)
    setTimeout(() => {
      setAnimating(false);
      // ✅ Mostrar resultados DESPUÉS de que termine la animación
      setShowResults(true);
      console.log('[DICE] ✅ Animación terminada - mostrando resultados');
    }, 1000);
  };

  // Función para generar los puntos del dado
  const renderDots = (number) => {
    const dots = [];
    const dotPositions = {
      1: ['center'],
      2: ['top-left', 'bottom-right'],
      3: ['top-left', 'center', 'bottom-right'],
      4: ['top-left', 'top-right', 'bottom-left', 'bottom-right'],
      5: ['top-left', 'top-right', 'center', 'bottom-left', 'bottom-right'],
      6: ['top-left', 'top-right', 'middle-left', 'middle-right', 'bottom-left', 'bottom-right']
    };

    const positions = dotPositions[number] || dotPositions[1];
    
    positions.forEach((position, index) => {
      dots.push(
        <div
          key={index}
          className={`${styles.dot} ${styles[position]}`}
        />
      );
    });

    return dots;
  };

  const diceClasses = [
    styles.dice,
    styles[`dice_${playerColor}`],
    (animating || isRolling) ? styles.rolling : '',
    disabled ? styles.disabled : ''
  ].filter(Boolean).join(' ');

  // Detectar si se sacaron dobles
  const isDoubles = hasValues && displayedValues[0] === displayedValues[1];

  return (
    <div className={styles.diceContainer}>
      {/* Banner de DOBLES - se muestra cuando hay dobles */}
      {isDoubles && (
        <div className={styles.doublesBanner}>
          <span className={styles.doublesEmoji}>🎲</span>
          <span className={styles.doublesText}>¡DOBLES!</span>
          <span className={styles.doublesEmoji}>🎲</span>
        </div>
      )}
      
      {/* Panel de control lateral izquierdo */}
      <div className={styles.controlPanel}>
        <div className={styles.diceHeader}>
          <h3 className={styles.headerTitle}>DICE SYSTEM</h3>
          <div className={styles.statusIndicator}>
            {disabled ? '⏳ WAITING' : 
             (animating || isRolling) ? '🎲 ROLLING' :
             noMovesAvailable ? '⚠️ NO MOVES' : 
             '✓ READY'}
          </div>
        </div>
        
        <div className={styles.diceInterface}>
          <div className={styles.diceWrapper}>
            {/* Primer dado */}
            <button
              className={diceClasses}
              onClick={handleRoll}
              disabled={disabled || animating || isRolling}
              aria-label={`Primer dado mostrando ${hasValues ? displayValue1 : 'vacío'}`}
            >
              <div className={styles.diceFace}>
                {(animating || isRolling) ? (
                  <div className={styles.rollingText}>🎲</div>
                ) : hasValues ? (
                  renderDots(displayValue1)
                ) : (
                  <div className={styles.emptyDice}></div>
                )}
              </div>
            </button>

            {/* Segundo dado */}
            <button
              className={diceClasses}
              onClick={handleRoll}
              disabled={disabled || animating || isRolling}
              aria-label={`Segundo dado mostrando ${hasValues ? displayValue2 : 'vacío'}`}
            >
              <div className={styles.diceFace}>
                {(animating || isRolling) ? (
                  <div className={styles.rollingText}>🎲</div>
                ) : hasValues ? (
                  renderDots(displayValue2)
                ) : (
                  <div className={styles.emptyDice}></div>
                )}
              </div>
            </button>
          </div>
          
          {/* Botón de lanzar */}
          {!disabled && (
            <div className={styles.rollButton}>
              <button
                onClick={handleRoll}
                disabled={disabled || animating || isRolling}
                className={styles.rollBtn}
              >
                {(animating || isRolling) ? 'ROLLING...' : 
                 noMovesAvailable ? 'SKIP TURN' : 
                 'ROLL DICE'}
              </button>
            </div>
          )}
        </div>
      </div>
      
      {/* Panel de información lateral derecho */}
      <div className={styles.infoPanel}>
        <div className={styles.terminalWindow}>
          <div className={styles.terminalHeader}>
            <span className={styles.glitchText}>DICE ANALYTICS</span>
          </div>
          <div className={styles.terminalContent}>
            {hasValues && showResults ? (
              `RESULT: SUCCESS
Dice 1: ${displayedValues[0]}
Dice 2: ${displayedValues[1]}
Sum: ${sum}

---[PATTERN ANALYSIS]---
Type: ${isDoubles ? 'DOUBLES' : 'NORMAL'}
Probability: ${((1/36) * 100).toFixed(1)}%
${isDoubles ? 'BONUS: Extra Turn!' : ''}

---[GAME STATUS]---
${startPhaseAttempts ? `Attempt: ${startPhaseAttempts.current}/${startPhaseAttempts.max}` : 'Phase: ACTIVE'}
Player: ${playerColor.toUpperCase()}
Status: ${disabled ? 'WAITING' : 'ACTIVE'}`
            ) : (animating || isRolling) ? (
              `PROCESSING ROLL...
Quantum RNG: ACTIVE
Entropy: HIGH
Status: CALCULATING

---[DICE PHYSICS]---
Rotation: ACTIVE
Velocity: RANDOM
Outcome: PENDING

---[SYSTEM STATE]---
${startPhaseAttempts ? `Attempt: ${startPhaseAttempts.current}/${startPhaseAttempts.max}` : 'Phase: ACTIVE'}
Ready: ${!disabled ? 'TRUE' : 'FALSE'}`
            ) : (
              `AWAITING INPUT...
Dice System: ONLINE
RNG Module: LOADED
Status: STANDBY

---[ROLL PARAMETERS]---
Dice Count: 2
Range: 1-6 each
Mode: ${noMovesAvailable ? 'SKIP' : 'STANDARD'}

---[PLAYER INFO]---
${startPhaseAttempts ? `Attempt: ${startPhaseAttempts.current}/${startPhaseAttempts.max}` : 'Phase: ACTIVE'}
Color: ${playerColor.toUpperCase()}
Status: ${disabled ? 'WAITING' : 'READY'}`
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dice;
/**
 * Componente Prison - Representa las cárceles (bases) de cada jugador
 */

import React from 'react';
import styles from './Prison.module.css';
import { COLOR_STYLES } from '../../utils/constants';

const Prison = ({ 
  color, 
  position, 
  pieces = [], 
  playerName,
  onClick 
}) => {

  const handleCellClick = (pieceIndex, piece) => {
    if (onClick && piece) {
      onClick(-1, [piece]); // -1 indica que está en la cárcel
    }
  };

  const colorStyles = COLOR_STYLES[color];

  return (
    <div 
      className={`${styles.prison} ${styles[`prison_${color}`]} ${styles[position.replace('-', '_')]}`}
      style={{
        backgroundColor: colorStyles?.background,
        borderColor: colorStyles?.primary
      }}
    >
      {/* Etiqueta del jugador */}
      <div 
        className={styles.prisonLabel}
        style={{ color: colorStyles?.primary }}
      >
        {playerName}
      </div>

      {/* Logo/Texto del color */}
      <div 
        className={styles.prisonTitle}
        style={{ 
          backgroundColor: colorStyles?.primary,
          color: 'white'
        }}
      >
        {color.toUpperCase()}
      </div>

      {/* Grid de 4 casillas para las fichas */}
      <div className={styles.prisonGrid}>
        {Array.from({ length: 4 }, (_, index) => {
          const piece = pieces.find(p => p.piece_id === index);
          
          return (
            <div
              key={index}
              className={`${styles.prisonCell} ${piece ? styles.hasPiece : styles.empty}`}
              onClick={() => handleCellClick(index, piece)}
              style={{
                borderColor: colorStyles?.primary + '80', // 80 = 50% opacity
              }}
            >
              {piece && (
                <div
                  className={`${styles.piece} ${styles[`piece_${color}`]}`}
                  style={{
                    backgroundColor: colorStyles?.primary,
                    color: 'white'
                  }}
                >
                  {piece.piece_id + 1}
                </div>
              )}
              
              {/* Placeholder para casilla vacía */}
              {!piece && (
                <div 
                  className={styles.emptySlot}
                  style={{
                    borderColor: colorStyles?.primary + '40'
                  }}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Contador de fichas */}
      <div 
        className={styles.pieceCount}
        style={{ color: colorStyles?.dark }}
      >
        {pieces.length}/4
      </div>
    </div>
  );
};

export default Prison;
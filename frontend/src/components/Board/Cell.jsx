/**
 * Componente Cell - Representa una casilla individual del tablero
 */

import React from 'react';
import styles from './Cell.module.css';
import { CELL_TYPES, PLAYER_COLORS, SPECIAL_POSITIONS } from '../../utils/constants';

const Cell = ({ 
  position, 
  pieces = [], 
  isHighlighted = false, 
  onClick,
  className = '',
  isSafe = false,
  isStart = false,
  showNumber = false,
  isColorStretch = false,
  colorStretch = null,
  stretchNumber = null
}) => {
  
  // Determinar el tipo de casilla
  const getCellType = () => {
    if (isColorStretch) return CELL_TYPES.GOAL;
    if (isSafe) return CELL_TYPES.SAFE;
    if (isStart) return CELL_TYPES.START;
    return CELL_TYPES.NORMAL;
  };

  const cellType = getCellType();

  const cellClasses = [
    styles.cell,
    styles[cellType],
    isColorStretch ? styles.colorStretch : '',
    colorStretch ? styles[`stretch_${colorStretch}`] : '',
    isHighlighted ? styles.highlighted : '',
    pieces.length > 0 ? styles.hasPieces : '',
    className
  ].filter(Boolean).join(' ');

  const handleClick = () => {
    if (onClick) {
      onClick(position, pieces);
    }
  };

  return (
    <div 
      className={cellClasses}
      onClick={handleClick}
      data-position={position}
    >
      {/* Mostrar número de casilla */}
      {showNumber && (
        <span className={styles.cellNumber}>
          {isColorStretch ? stretchNumber : position}
        </span>
      )}
      
      {/* Renderizar fichas en esta casilla */}
      <div className={styles.piecesContainer}>
        {pieces.map((piece, index) => (
          <div
            key={`${piece.color}-${piece.piece_id}`}
            className={`${styles.piece} ${styles[`piece_${piece.color}`]}`}
            style={{
              zIndex: index + 1,
              transform: `translate(${index * 3}px, ${index * 3}px)`
            }}
          >
            {piece.piece_id + 1}
          </div>
        ))}
      </div>

      {/* Indicador de casilla segura (círculo gris) */}
      {isSafe && !isStart && (
        <div className={styles.safeIndicator}></div>
      )}
      
      {/* Indicador de casilla de salida */}
      {isStart && (
        <div className={styles.startIndicator}></div>
      )}
    </div>
  );
};

export default Cell;
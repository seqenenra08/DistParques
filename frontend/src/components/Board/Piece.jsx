import React from 'react';
import styles from './Piece.module.css';

const Piece = ({ 
  id, 
  color, 
  position, 
  isSelected = false, 
  canMove = false,
  onClick, 
  boardSize = { width: 700, height: 700 } 
}) => {
  // Calcular posición absoluta basada en las coordenadas del tablero
  const getAbsolutePosition = () => {
    if (!position || !position.x || !position.y) {
      return { left: 0, top: 0 };
    }

    // Convertir porcentajes a píxeles
    const left = (position.x / 100) * boardSize.width;
    const top = (position.y / 100) * boardSize.height;

    return { 
      left: `${left}px`, 
      top: `${top}px` 
    };
  };

  const handleClick = () => {
    console.log('[PIECE] Click detectado en pieza:', id, ', canMove:', canMove);
    if (onClick) {
      console.log('[PIECE] Llamando a onClick callback');
      onClick(id);
    } else {
      console.log('[PIECE] ⚠️ No hay onClick callback');
    }
  };

  return (
    <div
      className={`${styles.piece} ${styles[color]} ${isSelected ? styles.selected : ''} ${canMove ? styles.canMove : ''}`}
      style={getAbsolutePosition()}
      onClick={handleClick}
      data-piece-id={id}
    >
      <div className={styles.innerPiece} />
    </div>
  );
};

export default Piece;
'use client';

import { useState, useEffect } from 'react';
import styles from './MoveSelector.module.css';

/**
 * Componente que permite al jugador seleccionar cuánto mover una ficha
 * Aparece cuando el usuario hace click en una ficha y hay múltiples opciones de movimiento
 */
export default function MoveSelector({ 
  availableMoves, 
  onSelectMove, 
  onCancel,
  selectedPiece 
}) {
  const [selectedMove, setSelectedMove] = useState(null);

  // Limpiar selección cuando cambien los movimientos disponibles
  useEffect(() => {
    setSelectedMove(null);
  }, [availableMoves]);

  if (!availableMoves || availableMoves.length === 0) {
    return null;
  }

  const handleMoveClick = (move) => {
    setSelectedMove(move);
    onSelectMove(move);
  };

  // Agrupar movimientos para mostrar mejor la UI
  // Si hay [6, 6, 12], mostrar "6 (x2)" y "12 (suma)"
  const moveGroups = {};
  availableMoves.forEach(move => {
    if (!moveGroups[move]) {
      moveGroups[move] = 0;
    }
    moveGroups[move]++;
  });

  const uniqueMoves = Object.keys(moveGroups).map(value => ({
    value: parseInt(value),
    count: moveGroups[value]
  }));

  // Detectar si algún valor es la suma de otros
  const halfValues = uniqueMoves.filter(m => m.count === 2).map(m => m.value);
  const sumValues = halfValues.map(v => v * 2);

  return (
    <div className={styles.overlay} onClick={onCancel}>
      <div className={styles.selector} onClick={(e) => e.stopPropagation()}>
        <h3 className={styles.title}>¿Cuánto quieres mover?</h3>
        
        {selectedPiece && (
          <p className={styles.subtitle}>
            Ficha seleccionada
          </p>
        )}
        
        <div className={styles.moveButtons}>
          {uniqueMoves.map((move) => {
            const isSum = sumValues.includes(move.value);
            
            return (
              <button
                key={move.value}
                className={`${styles.moveButton} ${selectedMove === move.value ? styles.selected : ''}`}
                onClick={() => handleMoveClick(move.value)}
              >
                <span className={styles.moveValue}>{move.value}</span>
                {move.count > 1 && !isSum && (
                  <span className={styles.moveCount}>x{move.count}</span>
                )}
                {isSum && (
                  <span className={styles.sumLabel}>suma</span>
                )}
                <span className={styles.moveLabel}>
                  {move.value === 1 ? 'casilla' : 'casillas'}
                </span>
              </button>
            );
          })}
        </div>
        
        <button className={styles.cancelButton} onClick={onCancel}>
          Cancelar
        </button>
      </div>
    </div>
  );
}

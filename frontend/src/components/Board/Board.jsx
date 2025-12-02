/**
 * Componente Board - Tablero principal del Parchese con imagen estática
 */

import React, { useState, useEffect } from 'react';
import Piece from './Piece';
import styles from './Board.module.css';
import { 
  BOARD_COORDINATES,
  PLAYER_COLORS
} from '../../utils/constants';
import audioService from '../../services/audioService';

const Board = ({ gameState, onPieceClick, onBoardClick, canMove = false, currentPlayer = null, currentPlayerColor = null, selectedPieceFromParent = null }) => {
  const [selectedPiece, setSelectedPiece] = useState(null);
  const [boardSize, setBoardSize] = useState({ width: 700, height: 700 });
  const [pieceOffset, setPieceOffset] = useState({ x: 2, y: 0 }); // Offset ajustable para fichas

  useEffect(() => {
    // Ajustar el tamaño del tablero responsivamente
    const updateBoardSize = () => {
      const container = document.querySelector(`.${styles.boardContainer}`);
      if (container) {
        const containerWidth = container.clientWidth;
        const size = Math.min(containerWidth, 700); // Máximo 700px
        setBoardSize({ width: size, height: size });
      }
    };

    updateBoardSize();
    window.addEventListener('resize', updateBoardSize);
    return () => window.removeEventListener('resize', updateBoardSize);
  }, []);

  const handlePieceClick = (pieceId) => {
    console.log('[BOARD] Pieza clickeada:', pieceId);
    console.log('[BOARD] canMove:', canMove, ', currentPlayer:', currentPlayer, ', currentPlayerColor:', currentPlayerColor);
    console.log('[BOARD] pendingPieceRelease:', gameState?.pendingPieceRelease);
    console.log('[BOARD] startPhase:', gameState?.startPhase);
    
    const [color] = pieceId.split('_');
    console.log('[BOARD] Color de la ficha:', color);
    
    // 🔊 Reproducir sonido de click al seleccionar ficha
    audioService.playClick();
    
    // Si está en modo de liberación de ficha, permitir click en fichas del jugador actual en la cárcel
    if (gameState?.pendingPieceRelease && gameState?.startPhase) {
      console.log('[BOARD] Modo de liberación de ficha activo');
      if (color === currentPlayerColor) {
        console.log('[BOARD] ✅ Ficha del jugador actual en modo liberación, permitiendo click');
        setSelectedPiece(pieceId);
        if (onPieceClick) {
          onPieceClick(pieceId);
        }
        return;
      } else {
        console.log('[BOARD] ❌ No es tu ficha');
        // 🔊 Reproducir sonido de error
        audioService.playError();
        return;
      }
    }
    
    // Solo permitir seleccionar fichas del jugador actual si se puede mover
    if (canMove && currentPlayerColor && color !== currentPlayerColor) {
      console.log(`[BOARD] ❌ No puedes mover fichas ${color}. Es turno de ${currentPlayer} (${currentPlayerColor})`);
      // 🔊 Reproducir sonido de error
      audioService.playError();
      return;
    }
    
    console.log('[BOARD] ✅ Validación pasada, llamando a onPieceClick');
    setSelectedPiece(pieceId);
    if (onPieceClick) {
      onPieceClick(pieceId);
    }
  };

  const handleBoardClick = (e) => {
    // Si se hace clic en el tablero (no en una ficha), deseleccionar
    if (e.target === e.currentTarget) {
      setSelectedPiece(null);
    }
    
    if (onBoardClick) {
      onBoardClick(e);
    }
  };

  // Obtener posición específica de una ficha en su cárcel
  const getPrisonPosition = (piece, pieceIndex) => {
    const prisonKey = `prison_${piece.color}`;
    const basePrison = BOARD_COORDINATES[prisonKey];
    
    console.log(`[PRISON] Buscando ${prisonKey} para pieza ${piece.id}`);
    console.log(`[PRISON] Coordenadas base encontradas:`, basePrison);
    
    if (!basePrison) {
      console.error(`[PRISON] ❌ No se encontraron coordenadas para ${prisonKey}`);
      return null;
    }

    // Organizar las fichas en una cuadrícula 2x2 dentro de cada cárcel
    const positions = [
      { x: -2, y: -2 }, // Superior izquierda
      { x: 2, y: -2 },  // Superior derecha  
      { x: -2, y: 2 },  // Inferior izquierda
      { x: 2, y: 2 }    // Inferior derecha
    ];

    const offset = positions[pieceIndex] || { x: 0, y: 0 };
    
    const finalPosition = {
      x: basePrison.x + offset.x,
      y: basePrison.y + offset.y
    };
    
    console.log(`[PRISON] Posición final para ${piece.id}:`, finalPosition);
    return finalPosition;
  };

  // Obtener coordenadas para una ficha basada en su posición
  const getPieceCoordinates = (piece, pieceIndex = 0) => {
    // Si la ficha está en la cárcel, usar posición específica
    let baseCoordinates = null;

    if (piece.position === 'prison') {
      return getPrisonPosition(piece, pieceIndex);
    } else if (piece.position === 'center') {
      // Centro: distribuir las fichas en círculo
      baseCoordinates = BOARD_COORDINATES['center'];
      const angle = (pieceIndex * Math.PI * 2) / 8; // Máximo 8 fichas alrededor
      const radius = 3; // Radio del círculo en porcentaje
      
      if (baseCoordinates) {
        return {
          x: baseCoordinates.x + Math.cos(angle) * radius,
          y: baseCoordinates.y + Math.sin(angle) * radius
        };
      }
    } else if (typeof piece.position === 'string' && piece.position.includes('_')) {
      // Camino final (ej: red_1, blue_2, etc.)
      baseCoordinates = BOARD_COORDINATES[piece.position];
    } else if (typeof piece.position === 'number') {
      // Posición numérica en el tablero (1-68)
      baseCoordinates = BOARD_COORDINATES[piece.position];
    }

    if (!baseCoordinates) return null;

    return {
      x: baseCoordinates.x + pieceOffset.x,
      y: baseCoordinates.y + pieceOffset.y
    };
  };

  // Obtener todas las fichas del estado actual
  const getAllPieces = () => {
    if (!gameState || !gameState.players) return [];
    
    console.log('[BOARD] getAllPieces - Total players:', gameState.players.length);
    console.log('[BOARD] Players:', gameState.players.map(p => `${p.name} (${p.color})`));
    
    const allPieces = [];
    gameState.players.forEach(player => {
      if (player.pieces) {
        console.log(`[BOARD] Player ${player.name} tiene ${player.pieces.length} fichas`);
        player.pieces.forEach(piece => {
          allPieces.push({
            id: `${player.color}_${piece.piece_id}`,
            color: player.color, // Usar el color del jugador, no de la ficha
            position: piece.position === -1 ? 'prison' : piece.position,
            pieceId: piece.piece_id,
            isInGoal: piece.is_in_goal
          });
        });
      }
    });
    
    console.log('[BOARD] Total pieces to render:', allPieces.length);
    return allPieces;
  };

  // Función para obtener coordenadas de ficha con manejo de apilamiento
  const getPieceCoordinatesWithStacking = (piece, allPieces) => {
    // Para fichas en la cárcel, manejar la cuadrícula especial
    if (piece.position === 'prison') {
      return getPieceCoordinates(piece, piece.pieceId);
    }

    // Para fichas en el centro, manejar círculo
    if (piece.position === 'center') {
      const centerPieces = allPieces.filter(p => p.position === 'center');
      const centerIndex = centerPieces.findIndex(p => p.id === piece.id);
      return getPieceCoordinates(piece, centerIndex);
    }

    // Para otras posiciones, aplicar offset basado en cantidad de fichas en la misma posición
    const baseCoords = getPieceCoordinates(piece);
    if (!baseCoords) return null;

    // Contar fichas en la misma posición
    const piecesInSamePosition = allPieces.filter(p => 
      p.position === piece.position && p.id !== piece.id
    );

    if (piecesInSamePosition.length > 0) {
      // Determinar dirección de apilamiento basada en la posición
      const pieceIndexInPosition = allPieces
        .filter(p => p.position === piece.position)
        .findIndex(p => p.id === piece.id);

      if (typeof piece.position === 'string' && piece.position.includes('_')) {
        // Caminos finales: apilar según orientación
        let gridPositions;
        
        if (piece.position.startsWith('red_') || piece.position.startsWith('yellow_')) {
          // Horizontal (lado a lado)
          gridPositions = [
            { x: 0, y: 0 },     // Primera ficha en posición base
            { x: 0, y: -2.5 },  // Segunda ficha arriba
            { x: 0, y: 2.5 },   // Tercera ficha abajo
            { x: 2.5, y: 0 }    // Cuarta ficha al lado
          ];
        } else {
          // Vertical (arriba/abajo)
          gridPositions = [
            { x: 0, y: 0 },     // Primera ficha en posición base
            { x: -2.5, y: 0 },  // Segunda ficha a la izquierda
            { x: 2.5, y: 0 },   // Tercera ficha a la derecha
            { x: 0, y: -2.5 }   // Cuarta ficha arriba
          ];
        }

        if (piece.position.endsWith('_8')) {
          // Casilla final: cuadrícula 2x2
          gridPositions = [
            { x: -1, y: -1 },   // Superior izquierda
            { x: 1, y: -1 },    // Superior derecha
            { x: -1, y: 1 },    // Inferior izquierda
            { x: 1, y: 1 }      // Inferior derecha
          ];
        }

        const offset = gridPositions[pieceIndexInPosition] || { x: 0, y: 0 };
        return {
          x: baseCoords.x + offset.x,
          y: baseCoords.y + offset.y
        };
      } else {
        // Casillas normales del tablero: disposición circular pequeña
        const angle = (pieceIndexInPosition * Math.PI * 2) / 4;
        const radius = 2;
        
        const gridPositions = [
          { x: 0, y: 0 },
          { x: Math.cos(angle) * radius, y: Math.sin(angle) * radius },
          { x: Math.cos(angle + Math.PI) * radius, y: Math.sin(angle + Math.PI) * radius },
          { x: Math.cos(angle + Math.PI/2) * radius, y: Math.sin(angle + Math.PI/2) * radius }
        ];

        const offset = gridPositions[pieceIndexInPosition] || { x: 0, y: 0 };
        return {
          x: baseCoords.x + offset.x,
          y: baseCoords.y + offset.y
        };
      }
    }

    return baseCoords;
  };

  return (
    <div className={styles.boardContainer}>
      <div 
        className={styles.board}
        style={{ 
          width: `${boardSize.width}px`, 
          height: `${boardSize.height}px` 
        }}
        onClick={handleBoardClick}
      >
        {/* Imagen de fondo del tablero */}
        <div 
          className={styles.boardBackground}
          style={{ 
            backgroundImage: 'url(/images/Parchís.svg.png)',
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        />

        {/* Renderizar todas las fichas */}
        {(() => {
          const allPieces = getAllPieces();
          console.log('[BOARD RENDER] Intentando renderizar fichas:', allPieces.length);
          console.log('[BOARD RENDER] Fichas por color:', {
            red: allPieces.filter(p => p.color === 'red').length,
            blue: allPieces.filter(p => p.color === 'blue').length,
            green: allPieces.filter(p => p.color === 'green').length,
            yellow: allPieces.filter(p => p.color === 'yellow').length
          });
          
          return allPieces.map(piece => {
            const coordinates = getPieceCoordinatesWithStacking(piece, allPieces);
            console.log(`[BOARD RENDER] Pieza ${piece.id} - position: ${piece.position}, coords:`, coordinates);
            
            if (!coordinates) {
              console.warn(`[BOARD RENDER] ⚠️ Sin coordenadas para pieza ${piece.id}`);
              return null;
            }

            return (
              <Piece
                key={piece.id}
                id={piece.id}
                color={piece.color}
                position={coordinates}
                isSelected={selectedPiece === piece.id || selectedPieceFromParent === piece.id}
                canMove={canMove && currentPlayerColor === piece.color}
                onClick={() => handlePieceClick(piece.id)}
              />
            );
          });
        })()}

        {/* Información de debug */}
        <div className={styles.debugInfo}>
          {gameState && (
            <div style={{ marginTop: '10px', fontSize: '12px', color: '#fff', backgroundColor: 'rgba(0,0,0,0.7)', padding: '5px', borderRadius: '3px' }}>
              Fichas: {gameState.pieces?.length || 0}
              {gameState.dice_values && Array.isArray(gameState.dice_values) && (
                <>
                  <br />
                  Dados: {gameState.dice_values[0]} + {gameState.dice_values[1]} = {gameState.dice_values[0] + gameState.dice_values[1]}
                </>
              )}
            </div>
          )}
        </div>

        {/* Información de jugadores */}
        <div className={styles.playersInfo}>
          {gameState?.players?.map(player => (
            <div 
              key={player.player_id} 
              className={`${styles.playerInfo} ${styles[player.color]}`}
            >
              <div className={styles.playerName}>
                {player.name}
                {player.name && player.name.toLowerCase().includes('bot') && (
                  <span style={{ marginLeft: '5px', fontSize: '14px' }}>🤖</span>
                )}
              </div>
              <div className={styles.playerStatus}>
                {player.pieces_in_home || 0} en casa
              </div>
            </div>
          )) || (
            // Fallback si no hay players definidos
            <div style={{ color: '#ccc', fontSize: '12px' }}>
              Esperando información de jugadores...
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Board;
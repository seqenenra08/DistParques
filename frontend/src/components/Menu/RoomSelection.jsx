/**
 * Componente RoomSelection - Crear o unirse a una sala
 */

import React, { useState } from 'react';
import styles from './RoomSelection.module.css';
import audioService from '../../services/audioService';

const RoomSelection = ({ onCreateRoom, onJoinRoom, onBack, availableColors = [], showColorSelector = false, onRoomInfoReceived }) => {
  const [mode, setMode] = useState('select'); // 'select', 'create', 'join', 'selectColor'
  const [playerName, setPlayerName] = useState('');
  const [roomCode, setRoomCode] = useState('');
  const [maxPlayers, setMaxPlayers] = useState(4);
  const [numBots, setNumBots] = useState(0);
  const [selectedColor, setSelectedColor] = useState('');
  const [error, setError] = useState('');
  const [joinedRoomCode, setJoinedRoomCode] = useState(''); // Código de la sala a la que se unió

  // Efecto para cambiar al modo selectColor cuando se recibe la información de la sala
  React.useEffect(() => {
    console.log('[RoomSelection] showColorSelector:', showColorSelector, 'mode:', mode, 'availableColors:', availableColors);
    if (showColorSelector && mode === 'join' && availableColors.length > 0) {
      console.log('[RoomSelection] Cambiando a modo selectColor con colores:', availableColors);
      setMode('selectColor');
      // Mantener el código de la sala si ya estaba guardado
      if (!joinedRoomCode && roomCode) {
        setJoinedRoomCode(roomCode.toUpperCase());
      }
      if (onRoomInfoReceived) {
        onRoomInfoReceived();
      }
    }
  }, [showColorSelector, mode, availableColors, onRoomInfoReceived, roomCode, joinedRoomCode]);

  // Colores disponibles para el juego
  const allColors = [
    { id: 'red', name: 'Rojo', emoji: '🔴' },
    { id: 'blue', name: 'Azul', emoji: '🔵' },
    { id: 'green', name: 'Verde', emoji: '🟢' },
    { id: 'yellow', name: 'Amarillo', emoji: '🟡' }
  ];

  const handleModeSelect = (selectedMode) => {
    audioService.playClick();
    setMode(selectedMode);
    setError('');
  };

  const handleBack = () => {
    audioService.playClick();
    if (mode === 'selectColor') {
      // Si está en selección de color, volver a join
      setMode('join');
      setSelectedColor('');
      setError('');
    } else if (mode !== 'select') {
      setMode('select');
      setError('');
    } else {
      onBack();
    }
  };

  const handleCreateRoom = () => {
    if (!playerName.trim()) {
      setError('Por favor ingresa tu nombre');
      audioService.playError();
      return;
    }

    if (!selectedColor) {
      setError('Por favor selecciona un color');
      audioService.playError();
      return;
    }

    // Validar que haya espacio para los bots
    if (numBots >= maxPlayers) {
      setError('Debe haber al menos 1 espacio para jugadores humanos');
      audioService.playError();
      return;
    }

    audioService.playClick();
    onCreateRoom({ playerName, maxPlayers, numBots, color: selectedColor });
  };

  const handleJoinRoom = () => {
    // Validar nombre primero
    if (!playerName.trim()) {
      setError('Por favor ingresa tu nombre');
      audioService.playError();
      return;
    }

    // Validar que el nombre no esté duplicado (esto se verificará en el backend)
    if (playerName.trim().length < 2) {
      setError('El nombre debe tener al menos 2 caracteres');
      audioService.playError();
      return;
    }

    if (!roomCode.trim() || roomCode.length !== 6) {
      setError('Por favor ingresa un código de sala válido (6 caracteres)');
      audioService.playError();
      return;
    }

    console.log('[RoomSelection] Validando sala y obteniendo colores disponibles');
    audioService.playClick();
    // Guardar el código de la sala y solicitar información al backend
    const upperRoomCode = roomCode.toUpperCase();
    setJoinedRoomCode(upperRoomCode);
    setError('');
    
    // Solicitar información de la sala sin color para obtener colores disponibles
    onJoinRoom({ playerName: playerName.trim(), roomCode: upperRoomCode, color: null });
  };

  const handleConfirmColor = () => {
    if (!selectedColor) {
      setError('Por favor selecciona un color');
      audioService.playError();
      return;
    }

    audioService.playClick();
    onJoinRoom({ playerName, roomCode: joinedRoomCode, color: selectedColor });
  };

  if (mode === 'create') {
    return (
      <div className={styles.container}>
        <div className={styles.box}>
          <div className={styles.header}>
            <button className={styles.backButton} onClick={handleBack}>
              ← Atrás
            </button>
            <h1 className={styles.title}>Crear Sala</h1>
            <div className={styles.icon}>🎮</div>
          </div>

          <div className={styles.form}>
            <div className={styles.inputGroup}>
              <label className={styles.label}>Tu Nombre</label>
              <input
                type="text"
                className={styles.input}
                placeholder="Ingresa tu nombre"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                maxLength={20}
              />
            </div>

            <div className={styles.inputGroup}>
              <label className={styles.label}>Número de Jugadores</label>
              <div className={styles.playerSelector}>
                {[2, 3, 4].map((num) => (
                  <button
                    key={num}
                    className={`${styles.playerOption} ${
                      maxPlayers === num ? styles.selected : ''
                    }`}
                    onClick={() => {
                      setMaxPlayers(num);
                      // Ajustar número de bots si excede el nuevo máximo
                      if (numBots >= num) {
                        setNumBots(Math.max(0, num - 1));
                      }
                      audioService.playClick();
                    }}
                  >
                    {num}
                  </button>
                ))}
              </div>
            </div>

            <div className={styles.inputGroup}>
              <label className={styles.label}>Número de Bots</label>
              <div className={styles.playerSelector}>
                {[0, 1, 2].map((num) => {
                  const isDisabled = num >= maxPlayers;
                  return (
                    <button
                      key={num}
                      className={`${styles.playerOption} ${
                        numBots === num ? styles.selected : ''
                      } ${isDisabled ? styles.disabled : ''}`}
                      onClick={() => {
                        if (!isDisabled) {
                          setNumBots(num);
                          audioService.playClick();
                        }
                      }}
                      disabled={isDisabled}
                    >
                      {num}
                    </button>
                  );
                })}
              </div>
              <p className={styles.helperText}>
                Los bots juegan automáticamente con las reglas del juego
              </p>
            </div>

            <div className={styles.inputGroup}>
              <label className={styles.label}>Tu Color</label>
              <div className={styles.colorSelector}>
                {allColors.map((color) => (
                  <button
                    key={color.id}
                    className={`${styles.colorOption} ${
                      selectedColor === color.id ? styles.selected : ''
                    } ${styles[color.id]}`}
                    onClick={() => {
                      setSelectedColor(color.id);
                      audioService.playClick();
                    }}
                    title={color.name}
                  >
                    <span className={styles.colorEmoji}>{color.emoji}</span>
                    <span className={styles.colorName}>{color.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {error && <div className={styles.error}>{error}</div>}

            <button className={styles.submitButton} onClick={handleCreateRoom}>
              <span className={styles.buttonIcon}>✨</span>
              Crear Sala
            </button>
          </div>

          <div className={styles.info}>
            <p>Se generará un código único que podrás compartir con otros jugadores</p>
          </div>
        </div>
      </div>
    );
  }

  if (mode === 'join') {
    return (
      <div className={styles.container}>
        <div className={styles.box}>
          <div className={styles.header}>
            <button className={styles.backButton} onClick={handleBack}>
              ← Atrás
            </button>
            <h1 className={styles.title}>Unirse a Sala</h1>
            <div className={styles.icon}>🚪</div>
          </div>

          <div className={styles.form}>
            <div className={styles.inputGroup}>
              <label className={styles.label}>Tu Nombre</label>
              <input
                type="text"
                className={styles.input}
                placeholder="Ingresa tu nombre"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                maxLength={20}
              />
            </div>

            <div className={styles.inputGroup}>
              <label className={styles.label}>Código de Sala</label>
              <input
                type="text"
                className={`${styles.input} ${styles.codeInput}`}
                placeholder="Ej: ABC123"
                value={roomCode}
                onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
                maxLength={6}
              />
            </div>

            {error && <div className={styles.error}>{error}</div>}

            <button className={styles.submitButton} onClick={handleJoinRoom}>
              <span className={styles.buttonIcon}>🎯</span>
              Continuar
            </button>
          </div>

          <div className={styles.info}>
            <p>Ingresa el código de 6 dígitos que te compartió el anfitrión</p>
          </div>
        </div>
      </div>
    );
  }

  if (mode === 'selectColor') {
    return (
      <div className={styles.container}>
        <div className={styles.box}>
          <div className={styles.header}>
            <button className={styles.backButton} onClick={handleBack}>
              ← Atrás
            </button>
            <h1 className={styles.title}>Selecciona tu Color</h1>
            <div className={styles.icon}>🎨</div>
          </div>

          <div className={styles.form}>
            <div className={styles.inputGroup}>
              <label className={styles.label}>
                Sala: <strong>{joinedRoomCode}</strong>
              </label>
              <p className={styles.helperText}>
                Hola <strong>{playerName}</strong>, selecciona el color de tus fichas
              </p>
            </div>

            <div className={styles.inputGroup}>
              <label className={styles.label}>Elige tu Color</label>
              <div className={styles.colorSelector}>
                {allColors.map((color) => {
                  const isAvailable = availableColors.length === 0 || availableColors.includes(color.id);
                  return (
                    <button
                      key={color.id}
                      className={`${styles.colorOption} ${
                        selectedColor === color.id ? styles.selected : ''
                      } ${styles[color.id]} ${!isAvailable ? styles.disabled : ''}`}
                      onClick={() => {
                        if (isAvailable) {
                          setSelectedColor(color.id);
                          audioService.playClick();
                        }
                      }}
                      disabled={!isAvailable}
                      title={isAvailable ? color.name : `${color.name} (ocupado)`}
                    >
                      <span className={styles.colorEmoji}>{color.emoji}</span>
                      <span className={styles.colorName}>{color.name}</span>
                      {!isAvailable && <span className={styles.takenBadge}>✗</span>}
                    </button>
                  );
                })}
              </div>
              {availableColors.length > 0 && (
                <p className={styles.helperText}>
                  Colores disponibles: {availableColors.length} de 4
                </p>
              )}
            </div>

            {error && <div className={styles.error}>{error}</div>}

            <button className={styles.submitButton} onClick={handleConfirmColor}>
              <span className={styles.buttonIcon}>✅</span>
              Confirmar y Unirse
            </button>
          </div>

          <div className={styles.info}>
            <p>Los colores ocupados no están disponibles</p>
          </div>
        </div>
      </div>
    );
  }

  // Mode select
  return (
    <div className={styles.container}>
      <div className={styles.box}>
        <div className={styles.header}>
          <button className={styles.backButton} onClick={handleBack}>
            ← Atrás
          </button>
          <h1 className={styles.title}>Modo Multijugador</h1>
          <div className={styles.icon}>🌐</div>
        </div>

        <div className={styles.modeSelection}>
          <button
            className={styles.modeCard}
            onClick={() => handleModeSelect('create')}
          >
            <div className={styles.modeIcon}>🎮</div>
            <h2 className={styles.modeTitle}>Crear Sala</h2>
            <p className={styles.modeDescription}>
              Crea una nueva sala y comparte el código con tus amigos
            </p>
          </button>

          <button
            className={styles.modeCard}
            onClick={() => handleModeSelect('join')}
          >
            <div className={styles.modeIcon}>🚪</div>
            <h2 className={styles.modeTitle}>Unirse a Sala</h2>
            <p className={styles.modeDescription}>
              Ingresa el código de una sala existente para unirte
            </p>
          </button>
        </div>

        <div className={styles.info}>
          <p>🎲 Juega con amigos en tiempo real</p>
        </div>
      </div>
    </div>
  );
};

export default RoomSelection;

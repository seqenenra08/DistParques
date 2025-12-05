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
  const maxPlayers = 4; // Fijo en 4 jugadores máximo
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

    // Validar que haya espacio para jugadores humanos (máximo 3 bots)
    if (numBots >= 4) {
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
        {/* Panel central - Wizard de creación */}
        <div className={styles.wizardBox}>
          <div className={styles.wizardHeader}>
            <button className={styles.backButton} onClick={handleBack}>
              ← PROTOCOLO DE RETORNO
            </button>
            <div className={styles.wizardProgress}>
              <div className={styles.progressBar}>
                <div className={styles.progressFill} style={{width: '75%'}}></div>
              </div>
              <span className={styles.progressText}>CONFIGURACIÓN AVANZADA</span>
            </div>
          </div>

          <div className={styles.wizardTitle}>
            <h1>INICIALIZAR SERVIDOR</h1>
            <p>Configuración de sala privada</p>
          </div>

          <div className={styles.wizardSteps}>
            {/* Paso 1 - Identidad */}
            <div className={styles.wizardStep}>
              <div className={styles.stepHeader}>
                <div className={styles.stepNumber}>01</div>
                <div className={styles.stepInfo}>
                  <h3>IDENTIDAD DEL HOST</h3>
                  <p>Configurar administrador de sala</p>
                </div>
              </div>
              <div className={styles.stepContent}>
                <input
                  type="text"
                  className={styles.wizardInput}
                  placeholder="NOMBRE DE USUARIO"
                  value={playerName}
                  onChange={(e) => setPlayerName(e.target.value)}
                  maxLength={20}
                />
              </div>
            </div>

            {/* Paso 2 - Configuración */}
            <div className={styles.wizardStep}>
              <div className={styles.stepHeader}>
                <div className={styles.stepNumber}>02</div>
                <div className={styles.stepInfo}>
                  <h3>PARÁMETROS DE SALA</h3>
                  <p>Jugadores y automatización</p>
                </div>
              </div>
              <div className={styles.stepContent}>
                <div className={styles.paramGrid}>
                  <div className={styles.paramSection}>
                    <label>BOTS ACTIVOS (Máximo 4 jugadores totales)</label>
                    <div className={styles.selectorGrid}>
                      {[0, 1, 2, 3].map((num) => {
                        // Asegurar que siempre haya al menos 1 espacio para jugador humano
                        const isDisabled = num >= 4; // Máximo 3 bots (4 total - 1 humano mínimo)
                        return (
                          <button
                            key={num}
                            className={`${styles.paramButton} ${
                              numBots === num ? styles.active : ''
                            } ${isDisabled ? styles.disabled : ''}`}
                            onClick={() => {
                              if (!isDisabled) {
                                setNumBots(num);
                                audioService.playClick();
                              }
                            }}
                            disabled={isDisabled}
                          >
                            <span className={styles.paramValue}>{num}</span>
                            <span className={styles.paramLabel}>AI</span>
                          </button>
                        );
                      })}
                    </div>
                    <div className={styles.paramInfo}>
                      <span>Jugadores humanos: {4 - numBots} | Bots: {numBots}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Paso 3 - Personalización */}
            <div className={styles.wizardStep}>
              <div className={styles.stepHeader}>
                <div className={styles.stepNumber}>03</div>
                <div className={styles.stepInfo}>
                  <h3>IDENTIDAD VISUAL</h3>
                  <p>Selección de avatar cromático</p>
                </div>
              </div>
              <div className={styles.stepContent}>
                <div className={styles.colorGrid}>
                  {allColors.map((color) => (
                    <button
                      key={color.id}
                      className={`${styles.colorCard} ${
                        selectedColor === color.id ? styles.selected : ''
                      } ${styles[color.id]}`}
                      onClick={() => {
                        setSelectedColor(color.id);
                        audioService.playClick();
                      }}
                    >
                      <div className={styles.colorIcon}>{color.emoji}</div>
                      <div className={styles.colorInfo}>
                        <span className={styles.colorTitle}>{color.name.toUpperCase()}</span>
                        <span className={styles.colorCode}>#{color.id.toUpperCase()}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {error && <div className={styles.wizardError}>{error}</div>}

          <div className={styles.wizardActions}>
            <button className={styles.deployButton} onClick={handleCreateRoom}>
              <span className={styles.deployIcon}>🚀</span>
              <span>DEPLOY SERVIDOR</span>
            </button>
          </div>
        </div>

        {/* Panel lateral derecho - Información sala */}
        <div className={styles.infoPanel}>
          <div className={styles.terminalWindow}>
            <div className={styles.terminalHeader}>
              === PROTOCOLO CREAR SALA ===
            </div>
            <div className={styles.terminalContent}>
              <div className={styles.glitchText}>
{`> Iniciando servidor privado...
> Generando código de acceso...
> Estado: [CONFIGURANDO]
> 
> CONFIGURACIÓN ACTUAL:
>   • Jugadores: ${maxPlayers}
>   • Bots: ${numBots}
>   • Espacios libres: ${maxPlayers - numBots - 1}
>   • Host: ${playerName || '[PENDIENTE]'}
>   • Color: ${selectedColor ? selectedColor.toUpperCase() : '[PENDIENTE]'}
> 
> PROTOCOLO:
> 1. Se genera código único (6 dígitos)
> 2. Tú eres el HOST de la sala
> 3. Comparte código con amigos
> 4. Solo tú puedes iniciar partida
> 5. Sala se elimina al terminar
> 
> Listo para crear servidor...`}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (mode === 'join') {
    return (
      <div className={styles.container}>
        {/* Panel de conexión tipo terminal */}
        <div className={styles.connectionBox}>
          <div className={styles.connectionHeader}>
            <button className={styles.backButton} onClick={handleBack}>
              ← DESCONECTAR
            </button>
            <div className={styles.statusBar}>
              <div className={styles.statusIndicator}></div>
              <span>PROTOCOLO DE ACCESO REMOTO</span>
            </div>
          </div>

          <div className={styles.connectionTerminal}>
            <div className={styles.terminalTitle}>
              <h1>ESTABLECER CONEXIÓN</h1>
              <p>Acceso a servidor distribuido</p>
            </div>

            <div className={styles.connectionFlow}>
              {/* Etapa 1 - Autenticación */}
              <div className={styles.flowStage}>
                <div className={styles.stageIcon}>🔐</div>
                <div className={styles.stageContent}>
                  <h3>AUTENTICACIÓN DE USUARIO</h3>
                  <div className={styles.authField}>
                    <div className={styles.fieldPrefix}>USER@SYSTEM:~$</div>
                    <input
                      type="text"
                      className={styles.terminalInput}
                      placeholder="IDENTIFICADOR_DE_USUARIO"
                      value={playerName}
                      onChange={(e) => setPlayerName(e.target.value)}
                      maxLength={20}
                    />
                  </div>
                </div>
              </div>

              {/* Etapa 2 - Código de acceso */}
              <div className={styles.flowStage}>
                <div className={styles.stageIcon}>🗝️</div>
                <div className={styles.stageContent}>
                  <h3>TOKEN DE ACCESO</h3>
                  <div className={styles.tokenField}>
                    <div className={styles.tokenPrefix}>ACCESS_CODE:</div>
                    <input
                      type="text"
                      className={styles.tokenInput}
                      placeholder="XXXXXX"
                      value={roomCode}
                      onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
                      maxLength={6}
                    />
                  </div>
                  <div className={styles.tokenStatus}>
                    <span className={`${styles.statusDot} ${roomCode.length === 6 ? styles.ready : styles.waiting}`}></span>
                    <span>{roomCode.length === 6 ? 'TOKEN VÁLIDO' : 'ESPERANDO TOKEN'}</span>
                  </div>
                </div>
              </div>

              {/* Etapa 3 - Estado de conexión */}
              <div className={styles.flowStage}>
                <div className={styles.stageIcon}>📡</div>
                <div className={styles.stageContent}>
                  <h3>ESTADO DE CONEXIÓN</h3>
                  <div className={styles.connectionStatus}>
                    <div className={styles.statusGrid}>
                      <div className={styles.statusItem}>
                        <span className={styles.statusLabel}>USUARIO:</span>
                        <span className={styles.statusValue}>{playerName || 'NO_SET'}</span>
                      </div>
                      <div className={styles.statusItem}>
                        <span className={styles.statusLabel}>TOKEN:</span>
                        <span className={styles.statusValue}>{roomCode || 'PENDING'}</span>
                      </div>
                      <div className={styles.statusItem}>
                        <span className={styles.statusLabel}>VALIDEZ:</span>
                        <span className={`${styles.statusValue} ${roomCode.length === 6 && playerName ? styles.valid : styles.invalid}`}>
                          {roomCode.length === 6 && playerName ? 'READY_TO_CONNECT' : 'INCOMPLETE_DATA'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {error && <div className={styles.connectionError}>{error}</div>}

            <div className={styles.connectionActions}>
              <button 
                className={`${styles.connectButton} ${!(roomCode.length === 6 && playerName) ? styles.disabled : ''}`} 
                onClick={handleJoinRoom}
                disabled={!(roomCode.length === 6 && playerName)}
              >
                <span className={styles.connectIcon}>⚡</span>
                <span>INICIAR HANDSHAKE</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (mode === 'selectColor') {
    return (
      <div className={styles.container}>
        {/* Panel lateral izquierdo - Selección color */}
        <div className={styles.box}>
          <div className={styles.header}>
            <button className={styles.backButton} onClick={handleBack}>
              ← ATRÁS
            </button>
            <h1 className={styles.title}>SELECCIÓN DE COLOR</h1>
            <div className={styles.icon}>🎨</div>
          </div>

          <div className={styles.form}>
            <div className={styles.inputGroup}>
              <label className={styles.label}>
                SALA: <strong>{joinedRoomCode}</strong>
              </label>
              <p className={styles.helperText}>
                USUARIO: <strong>{playerName}</strong>
              </p>
            </div>

            <div className={styles.inputGroup}>
              <label className={styles.label}>CONFIGURAR IDENTIDAD</label>
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
                  DISPONIBLES: {availableColors.length}/4 SLOTS
                </p>
              )}
            </div>

            {error && <div className={styles.error}>{error}</div>}

            <button className={styles.submitButton} onClick={handleConfirmColor}>
              <span className={styles.buttonIcon}>✅</span>
              CONFIRMAR CONEXIÓN
            </button>
          </div>

          <div className={styles.info}>
            <p>⚡ FINALIZANDO PROTOCOLO DE ACCESO</p>
          </div>
        </div>

        {/* Panel lateral derecho - Estado final */}
        <div className={styles.infoPanel}>
          <div className={styles.terminalWindow}>
            <div className={styles.terminalHeader}>
              === ASIGNACIÓN DE IDENTIDAD ===
            </div>
            <div className={styles.terminalContent}>
              <div className={styles.glitchText}>
{`> Conectado a sala ${joinedRoomCode}...
> Verificando espacios disponibles...
> Estado: [CONFIGURANDO PERFIL]
> 
> DATOS DE SESIÓN:
>   • Usuario: ${playerName}
>   • Sala: ${joinedRoomCode}
>   • Color: ${selectedColor ? selectedColor.toUpperCase() : '[SELECCIONA]'}
>   • Espacios libres: ${availableColors.length}
> 
> COLORES OCUPADOS:
${allColors.filter(c => !availableColors.includes(c.id) && availableColors.length > 0)
  .map(c => `>   ✗ ${c.name} [TOMADO]`).join('\n') || '>   [Analizando...]'}
> 
> ÚLTIMO PASO:
> Selecciona tu color de fichas
> para finalizar la conexión
> 
> Esperando confirmación...`}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Mode select - Selector principal con panel lateral
  return (
    <div className={styles.container}>
      {/* Panel lateral izquierdo - Menú */}
      <div className={styles.box}>
        <div className={styles.header}>
          <button className={styles.backButton} onClick={handleBack}>
            ← ATRÁS
          </button>
          <h1 className={styles.title}>MULTIJUGADOR</h1>
          <div className={styles.icon}>🌐</div>
        </div>

        <div className={styles.modeSelection}>
          <button
            className={styles.modeCard}
            onClick={() => handleModeSelect('create')}
          >
            <div className={styles.modeIcon}>🎮</div>
            <div>
              <h2 className={styles.modeTitle}>CREAR SALA</h2>
              <p className={styles.modeDescription}>
                Nueva sala privada con código único
              </p>
            </div>
          </button>

          <button
            className={styles.modeCard}
            onClick={() => handleModeSelect('join')}
          >
            <div className={styles.modeIcon}>🚪</div>
            <div>
              <h2 className={styles.modeTitle}>UNIRSE A SALA</h2>
              <p className={styles.modeDescription}>
                Conectar usando código de 6 dígitos
              </p>
            </div>
          </button>
        </div>

        <div className={styles.info}>
          <p>⚡ PROTOCOLO MULTIJUGADOR ACTIVO</p>
        </div>
      </div>

      {/* Panel lateral derecho - Información del sistema */}
      <div className={styles.infoPanel}>
        <div className={styles.terminalWindow}>
          <div className={styles.terminalHeader}>
            === SISTEMA MULTIJUGADOR v3.0 ===
          </div>
          <div className={styles.terminalContent}>
            <div className={styles.glitchText}>
{`> Modo multijugador activo...
> Verificando servidores...
> Estado: [CONECTADO]
> 
> CREAR SALA:
>   • Genera código único
>   • Soporte 2-4 jugadores
>   • Control de host
>   • Bots opcionales
> 
> UNIRSE A SALA:
>   • Ingresa código de 6 dígitos
>   • Selección de color automática
>   • Conexión inmediata
> 
> Tips:
> - Comparte el código con amigos
> - Solo el host puede iniciar
> - Salas se borran automáticamente
> 
> ¿Listo para jugar en red?`}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RoomSelection;

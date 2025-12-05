/**
 * Componente Settings - Configuración del juego
 */

import React, { useState, useEffect } from 'react';
import styles from './Settings.module.css';

const Settings = ({ onClose }) => {
  const [animationsEnabled, setAnimationsEnabled] = useState(true);
  const [showConfetti, setShowConfetti] = useState(true);
  const [gameSpeed, setGameSpeed] = useState('normal');
  const [theme, setTheme] = useState('default');
  const [language, setLanguage] = useState('es');
  const [showTutorial, setShowTutorial] = useState(true);

  useEffect(() => {
    // Cargar configuración guardada del localStorage
    const savedSettings = localStorage.getItem('parcheesiSettings');
    if (savedSettings) {
      const settings = JSON.parse(savedSettings);
      setAnimationsEnabled(settings.animationsEnabled ?? true);
      setShowConfetti(settings.showConfetti ?? true);
      setGameSpeed(settings.gameSpeed ?? 'normal');
      setTheme(settings.theme ?? 'default');
      setLanguage(settings.language ?? 'es');
      setShowTutorial(settings.showTutorial ?? true);
    }
  }, []);

  const saveSettings = () => {
    const settings = {
      animationsEnabled,
      showConfetti,
      gameSpeed,
      theme,
      language,
      showTutorial
    };
    localStorage.setItem('parcheesiSettings', JSON.stringify(settings));
  };



  const handleToggleAnimations = () => {
    const newState = !animationsEnabled;
    setAnimationsEnabled(newState);
    saveSettings();
  };

  const handleToggleConfetti = () => {
    const newState = !showConfetti;
    setShowConfetti(newState);
    saveSettings();
  };

  const handleGameSpeedChange = (speed) => {
    setGameSpeed(speed);
    saveSettings();
  };

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme);
    saveSettings();
  };

  const handleLanguageChange = (lang) => {
    setLanguage(lang);
    saveSettings();
  };

  const handleToggleTutorial = () => {
    const newState = !showTutorial;
    setShowTutorial(newState);
    saveSettings();
  };

  const handleResetSettings = () => {
    if (window.confirm('¿Estás seguro de que quieres restablecer todos los ajustes?')) {
      // Valores por defecto
      setAnimationsEnabled(true);
      setShowConfetti(true);
      setGameSpeed('normal');
      setTheme('default');
      setLanguage('es');
      setShowTutorial(true);

      // Limpiar localStorage
      localStorage.removeItem('parcheesiSettings');
    }
  };

  const handleClose = () => {
    onClose();
  };





  return (
    <div className={styles.overlay}>
      <div className={styles.settingsContainer}>
        <div className={styles.header}>
          <h1 className={styles.title}>⚙️ Ajustes</h1>
          <button className={styles.closeButton} onClick={handleClose}>
            ✕
          </button>
        </div>

        <div className={styles.content}>


          {/* SECCIÓN DE VISUALES */}
          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>
              <span className={styles.sectionIcon}>✨</span>
              Efectos Visuales
            </h2>

            <div className={styles.settingItem}>
              <div className={styles.settingLabel}>
                <span>Animaciones</span>
                <span className={styles.settingDescription}>
                  Activa o desactiva las animaciones del juego
                </span>
              </div>
              <button
                className={`${styles.toggleButton} ${animationsEnabled ? styles.toggleActive : ''}`}
                onClick={handleToggleAnimations}
              >
                {animationsEnabled ? 'Activadas' : 'Desactivadas'}
              </button>
            </div>

            <div className={styles.settingItem}>
              <div className={styles.settingLabel}>
                <span>Fuegos Artificiales</span>
                <span className={styles.settingDescription}>
                  Mostrar celebración al ganar
                </span>
              </div>
              <button
                className={`${styles.toggleButton} ${showConfetti ? styles.toggleActive : ''}`}
                onClick={handleToggleConfetti}
              >
                {showConfetti ? 'Activados' : 'Desactivados'}
              </button>
            </div>

            <div className={styles.settingItem}>
              <div className={styles.settingLabel}>
                <span>Tema Visual</span>
                <span className={styles.settingDescription}>
                  Selecciona el estilo del juego
                </span>
              </div>
              <div className={styles.buttonGroup}>
                <button
                  className={`${styles.optionButton} ${theme === 'default' ? styles.optionActive : ''}`}
                  onClick={() => handleThemeChange('default')}
                >
                  Clásico
                </button>
                <button
                  className={`${styles.optionButton} ${theme === 'dark' ? styles.optionActive : ''}`}
                  onClick={() => handleThemeChange('dark')}
                >
                  Oscuro
                </button>
                <button
                  className={`${styles.optionButton} ${theme === 'colorful' ? styles.optionActive : ''}`}
                  onClick={() => handleThemeChange('colorful')}
                >
                  Colorido
                </button>
              </div>
            </div>
          </div>

          {/* SECCIÓN DE JUGABILIDAD */}
          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>
              <span className={styles.sectionIcon}>🎮</span>
              Jugabilidad
            </h2>

            <div className={styles.settingItem}>
              <div className={styles.settingLabel}>
                <span>Velocidad del Juego</span>
                <span className={styles.settingDescription}>
                  Ajusta la velocidad de las animaciones
                </span>
              </div>
              <div className={styles.buttonGroup}>
                <button
                  className={`${styles.optionButton} ${gameSpeed === 'slow' ? styles.optionActive : ''}`}
                  onClick={() => handleGameSpeedChange('slow')}
                >
                  Lenta
                </button>
                <button
                  className={`${styles.optionButton} ${gameSpeed === 'normal' ? styles.optionActive : ''}`}
                  onClick={() => handleGameSpeedChange('normal')}
                >
                  Normal
                </button>
                <button
                  className={`${styles.optionButton} ${gameSpeed === 'fast' ? styles.optionActive : ''}`}
                  onClick={() => handleGameSpeedChange('fast')}
                >
                  Rápida
                </button>
              </div>
            </div>

            <div className={styles.settingItem}>
              <div className={styles.settingLabel}>
                <span>Mostrar Tutorial</span>
                <span className={styles.settingDescription}>
                  Muestra ayuda al iniciar el juego
                </span>
              </div>
              <button
                className={`${styles.toggleButton} ${showTutorial ? styles.toggleActive : ''}`}
                onClick={handleToggleTutorial}
              >
                {showTutorial ? 'Activado' : 'Desactivado'}
              </button>
            </div>

            <div className={styles.settingItem}>
              <div className={styles.settingLabel}>
                <span>Idioma</span>
                <span className={styles.settingDescription}>
                  Selecciona el idioma del juego
                </span>
              </div>
              <div className={styles.buttonGroup}>
                <button
                  className={`${styles.optionButton} ${language === 'es' ? styles.optionActive : ''}`}
                  onClick={() => handleLanguageChange('es')}
                >
                  🇪🇸 Español
                </button>
                <button
                  className={`${styles.optionButton} ${language === 'en' ? styles.optionActive : ''}`}
                  onClick={() => handleLanguageChange('en')}
                >
                  🇬🇧 English
                </button>
              </div>
            </div>
          </div>

          {/* SECCIÓN DE INFORMACIÓN */}
          <div className={styles.section}>
            <h2 className={styles.sectionTitle}>
              <span className={styles.sectionIcon}>ℹ️</span>
              Información
            </h2>

            <div className={styles.infoGrid}>
              <div className={styles.infoCard}>
                <div className={styles.infoIcon}>🎲</div>
                <div className={styles.infoLabel}>Versión</div>
                <div className={styles.infoValue}>1.0.0</div>
              </div>
              <div className={styles.infoCard}>
                <div className={styles.infoIcon}>👥</div>
                <div className={styles.infoLabel}>Jugadores</div>
                <div className={styles.infoValue}>2-4</div>
              </div>
              <div className={styles.infoCard}>
                <div className={styles.infoIcon}>🎵</div>
                <div className={styles.infoLabel}>Sonidos</div>
                <div className={styles.infoValue}>11</div>
              </div>
              <div className={styles.infoCard}>
                <div className={styles.infoIcon}>🎨</div>
                <div className={styles.infoLabel}>Colores</div>
                <div className={styles.infoValue}>4</div>
              </div>
            </div>
          </div>
        </div>

        <div className={styles.footer}>
          <button className={styles.resetButton} onClick={handleResetSettings}>
            🔄 Restablecer Ajustes
          </button>
          <button className={styles.saveButton} onClick={handleClose}>
            ✓ Guardar y Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;

/**
 * Servicio de Audio para el juego Parcheesi
 * Maneja todos los efectos de sonido del juego usando Web Audio API
 */

class AudioService {
  constructor() {
    this.audioContext = null;
    this.sounds = {};
    this.initialized = false;
    this.volume = 0.5; // Volumen por defecto (0 a 1)
    this.muted = false;
  }

  /**
   * Inicializar el contexto de audio
   * Debe llamarse después de una interacción del usuario (requisito del navegador)
   */
  async initialize() {
    if (this.initialized) return;

    try {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      this.initialized = true;
      console.log('[AudioService] Inicializado correctamente');

      // Cargar sonidos personalizados
      this.loadAudioFile('diceRoll', '/sounds/dice_sound.mp3');
      this.loadAudioFile('eating', '/sounds/eating.mp3');
    } catch (error) {
      console.error('[AudioService] Error al inicializar:', error);
    }
  }

  /**
   * Crear un sonido sintetizado usando osciladores
   */
  createTone(frequency, duration, type = 'sine', volume = 1) {
    if (!this.initialized || this.muted) return;

    const oscillator = this.audioContext.createOscillator();
    const gainNode = this.audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(this.audioContext.destination);

    oscillator.frequency.value = frequency;
    oscillator.type = type; // 'sine', 'square', 'sawtooth', 'triangle'

    const adjustedVolume = this.volume * volume;
    gainNode.gain.setValueAtTime(adjustedVolume, this.audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);

    oscillator.start(this.audioContext.currentTime);
    oscillator.stop(this.audioContext.currentTime + duration);

    return { oscillator, gainNode };
  }

  /**
   * Sonido de lanzamiento de dados
   * Simula el sonido de dados rodando con más realismo
   */
  playDiceRoll() {
    if (!this.initialized || this.muted) return;

    // Usar sonido personalizado si está cargado
    if (this.sounds['diceRoll']) {
      this.playLoadedSound('diceRoll');
      return;
    }

    // Sonido de agitación inicial (ruido)
    const shakeCount = 8;
    for (let i = 0; i < shakeCount; i++) {
      setTimeout(() => {
        // Crear múltiples tonos para simular dados chocando
        const freq1 = 180 + Math.random() * 100;
        const freq2 = 200 + Math.random() * 120;
        
        this.createTone(freq1, 0.04, 'square', 0.15);
        this.createTone(freq2, 0.04, 'square', 0.12);
      }, i * 60);
    }

    // Sonido de dados rodando (frecuencias medias rápidas)
    const rollStart = shakeCount * 60;
    const rollCount = 15;
    for (let i = 0; i < rollCount; i++) {
      setTimeout(() => {
        const freq = 220 + Math.random() * 200;
        this.createTone(freq, 0.03, 'sawtooth', 0.2);
      }, rollStart + i * 40);
    }

    // Sonidos de rebote (frecuencias descendentes)
    const bounceStart = rollStart + (rollCount * 40);
    const bounces = [
      { freq: 300, duration: 0.08, delay: 0 },
      { freq: 250, duration: 0.06, delay: 100 },
      { freq: 200, duration: 0.05, delay: 180 },
      { freq: 180, duration: 0.04, delay: 240 }
    ];

    bounces.forEach(bounce => {
      setTimeout(() => {
        this.createTone(bounce.freq, bounce.duration, 'sine', 0.3);
        // Añadir un segundo tono para dar más cuerpo
        this.createTone(bounce.freq * 1.5, bounce.duration * 0.8, 'triangle', 0.15);
      }, bounceStart + bounce.delay);
    });

    // Sonido final de "aterrizaje" (más sólido)
    setTimeout(() => {
      this.createTone(150, 0.15, 'sine', 0.4);
      this.createTone(180, 0.12, 'triangle', 0.25);
      
      // Click final
      setTimeout(() => {
        this.createTone(800, 0.02, 'sine', 0.15);
      }, 80);
    }, bounceStart + 300);
  }

  /**
   * Sonido de movimiento de ficha
   * Efecto suave de "deslizamiento"
   */
  playPieceMove() {
    if (!this.initialized || this.muted) return;

    // Tono ascendente rápido
    const oscillator = this.audioContext.createOscillator();
    const gainNode = this.audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(this.audioContext.destination);

    oscillator.frequency.setValueAtTime(300, this.audioContext.currentTime);
    oscillator.frequency.exponentialRampToValueAtTime(500, this.audioContext.currentTime + 0.15);
    oscillator.type = 'sine';

    gainNode.gain.setValueAtTime(this.volume * 0.3, this.audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.15);

    oscillator.start(this.audioContext.currentTime);
    oscillator.stop(this.audioContext.currentTime + 0.15);
  }

  /**
   * Sonido de captura de ficha
   * Efecto dramático cuando una ficha es comida
   */
  playPieceCapture() {
    if (!this.initialized || this.muted) return;

    // Usar sonido personalizado si está cargado
    if (this.sounds['eating']) {
      this.playLoadedSound('eating');
      return;
    }

    // Efecto de "golpe" dramático
    // Primer golpe bajo
    this.createTone(100, 0.1, 'sawtooth', 0.6);
    
    // Segundo golpe más alto
    setTimeout(() => {
      this.createTone(150, 0.15, 'sawtooth', 0.5);
    }, 80);

    // Efecto de "chispa"
    setTimeout(() => {
      for (let i = 0; i < 5; i++) {
        setTimeout(() => {
          this.createTone(800 + Math.random() * 400, 0.05, 'sine', 0.2);
        }, i * 30);
      }
    }, 150);
  }

  /**
   * Sonido de ficha llegando a la meta
   * Efecto de victoria menor
   */
  playPieceGoal() {
    if (!this.initialized || this.muted) return;

    // Secuencia ascendente triunfal
    const notes = [523, 659, 784, 1047]; // Do-Mi-Sol-Do (octava superior)
    notes.forEach((freq, index) => {
      setTimeout(() => {
        this.createTone(freq, 0.2, 'sine', 0.4);
      }, index * 100);
    });
  }

  /**
   * Sonido de victoria del juego
   * Melodía triunfal completa
   */
  playGameWin() {
    if (!this.initialized || this.muted) return;

    // Fanfarria de victoria
    const victoryMelody = [
      { freq: 523, duration: 0.2, delay: 0 },      // Do
      { freq: 659, duration: 0.2, delay: 200 },    // Mi
      { freq: 784, duration: 0.2, delay: 400 },    // Sol
      { freq: 1047, duration: 0.3, delay: 600 },   // Do alto
      { freq: 784, duration: 0.15, delay: 900 },   // Sol
      { freq: 1047, duration: 0.4, delay: 1050 },  // Do alto (sostenido)
    ];

    victoryMelody.forEach(note => {
      setTimeout(() => {
        this.createTone(note.freq, note.duration, 'triangle', 0.5);
        // Añadir armónicos
        this.createTone(note.freq * 2, note.duration, 'sine', 0.2);
      }, note.delay);
    });

    // Efecto de "campanitas" adicional
    setTimeout(() => {
      for (let i = 0; i < 8; i++) {
        setTimeout(() => {
          this.createTone(1500 + Math.random() * 500, 0.1, 'sine', 0.15);
        }, i * 80);
      }
    }, 1200);
  }

  /**
   * Sonido de dobles (bonus)
   * Efecto especial al sacar dobles
   */
  playDoubles() {
    if (!this.initialized || this.muted) return;

    // Dos tonos idénticos simultáneos (representando los dos dados iguales)
    this.createTone(600, 0.3, 'sine', 0.3);
    this.createTone(600, 0.3, 'triangle', 0.2);

    // Efecto de "brillo"
    setTimeout(() => {
      this.createTone(1200, 0.2, 'sine', 0.25);
    }, 150);
  }

  /**
   * Sonido de turno pasado
   * Efecto neutral/negativo
   */
  playTurnPass() {
    if (!this.initialized || this.muted) return;

    // Tono descendente
    const oscillator = this.audioContext.createOscillator();
    const gainNode = this.audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(this.audioContext.destination);

    oscillator.frequency.setValueAtTime(400, this.audioContext.currentTime);
    oscillator.frequency.exponentialRampToValueAtTime(200, this.audioContext.currentTime + 0.3);
    oscillator.type = 'sine';

    gainNode.gain.setValueAtTime(this.volume * 0.3, this.audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);

    oscillator.start(this.audioContext.currentTime);
    oscillator.stop(this.audioContext.currentTime + 0.3);
  }

  /**
   * Sonido de click/selección
   * Feedback suave para interacciones UI
   */
  playClick() {
    if (!this.initialized || this.muted) return;

    this.createTone(800, 0.05, 'sine', 0.15);
  }

  /**
   * Sonido de error/acción inválida
   */
  playError() {
    if (!this.initialized || this.muted) return;

    // Dos tonos bajos rápidos
    this.createTone(200, 0.1, 'square', 0.3);
    setTimeout(() => {
      this.createTone(180, 0.15, 'square', 0.3);
    }, 100);
  }

  /**
   * Sonido de inicio de partida
   */
  playGameStart() {
    if (!this.initialized || this.muted) return;

    // Secuencia ascendente emocionante
    const startSequence = [262, 330, 392, 523]; // Do-Mi-Sol-Do
    startSequence.forEach((freq, index) => {
      setTimeout(() => {
        this.createTone(freq, 0.25, 'triangle', 0.4);
      }, index * 150);
    });
  }

  /**
   * Sonido de determinación de orden (trompeta de anuncio)
   * Se reproduce cuando se muestra el orden final de turnos
   */
  playOrderDetermined() {
    if (!this.initialized || this.muted) return;

    // Fanfarria corta pero impactante
    const fanfare = [
      { freq: 392, duration: 0.15, delay: 0 },     // Sol
      { freq: 523, duration: 0.15, delay: 150 },   // Do
      { freq: 659, duration: 0.15, delay: 300 },   // Mi
      { freq: 784, duration: 0.3, delay: 450 },    // Sol (sostenido)
    ];

    fanfare.forEach(note => {
      setTimeout(() => {
        this.createTone(note.freq, note.duration, 'triangle', 0.45);
        // Añadir armónico para dar más brillo
        this.createTone(note.freq * 2, note.duration * 0.7, 'sine', 0.2);
      }, note.delay);
    });

    // Acorde final triunfal (Do mayor)
    setTimeout(() => {
      this.createTone(523, 0.4, 'triangle', 0.35);  // Do
      this.createTone(659, 0.4, 'sine', 0.25);      // Mi
      this.createTone(784, 0.4, 'sine', 0.25);      // Sol
    }, 750);
  }

  /**
   * Sonido de éxito (para creación de sala o acción exitosa)
   * Efecto positivo y satisfactorio
   */
  playSuccess() {
    if (!this.initialized || this.muted) return;

    // Secuencia ascendente brillante
    const successNotes = [
      { freq: 523, duration: 0.12, delay: 0 },    // Do
      { freq: 659, duration: 0.12, delay: 100 },  // Mi
      { freq: 784, duration: 0.2, delay: 200 },   // Sol
    ];

    successNotes.forEach(note => {
      setTimeout(() => {
        this.createTone(note.freq, note.duration, 'sine', 0.35);
        // Añadir brillo con armónico
        this.createTone(note.freq * 2, note.duration * 0.6, 'sine', 0.15);
      }, note.delay);
    });
  }

  /**
   * Sonido de jugador uniéndose al lobby
   * Efecto de notificación amigable
   */
  playPlayerJoin() {
    if (!this.initialized || this.muted) return;

    // Dos tonos ascendentes suaves
    this.createTone(440, 0.15, 'sine', 0.3);
    setTimeout(() => {
      this.createTone(554, 0.2, 'sine', 0.3);
      // Añadir campanita para dar calidez
      this.createTone(880, 0.15, 'sine', 0.15);
    }, 100);
  }

  /**
   * Establecer volumen general (0 a 1)
   */
  setVolume(volume) {
    this.volume = Math.max(0, Math.min(1, volume));
    console.log('[AudioService] Volumen ajustado a:', this.volume);
  }

  /**
   * Silenciar/Activar todos los sonidos
   */
  toggleMute() {
    this.muted = !this.muted;
    console.log('[AudioService] Silenciado:', this.muted);
    return this.muted;
  }

  /**
   * Cargar un archivo de audio externo (para sonidos más complejos)
   */
  async loadAudioFile(name, url) {
    if (!this.initialized) {
      await this.initialize();
    }

    try {
      const response = await fetch(url);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
      
      this.sounds[name] = audioBuffer;
      console.log(`[AudioService] Audio cargado: ${name}`);
    } catch (error) {
      console.error(`[AudioService] Error al cargar audio ${name}:`, error);
    }
  }

  /**
   * Reproducir un archivo de audio cargado previamente
   */
  playLoadedSound(name, volume = 1) {
    if (!this.initialized || this.muted || !this.sounds[name]) return;

    const source = this.audioContext.createBufferSource();
    const gainNode = this.audioContext.createGain();

    source.buffer = this.sounds[name];
    source.connect(gainNode);
    gainNode.connect(this.audioContext.destination);

    gainNode.gain.value = this.volume * volume;
    source.start(0);
  }
}

// Crear instancia singleton
const audioService = new AudioService();

export default audioService;

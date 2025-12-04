/**
 * Constantes del juego Parchese
 */

export const GAME_CONFIG = {
  BOARD_SIZE: 68, // 68 casillas principales como en la imagen
  MAX_PLAYERS: 4,
  PIECES_PER_PLAYER: 4,
  DICE_SIDES: 6,
  CELLS_PER_SIDE: 17, // 17 casillas por lado del perimetro
  ARM_LENGTH: 8, // 8 casillas en cada brazo de color hacia el centro
};

export const PLAYER_COLORS = {
  RED: 'red',
  BLUE: 'blue', 
  GREEN: 'green',
  YELLOW: 'yellow'
};

export const COLOR_STYLES = {
  [PLAYER_COLORS.RED]: {
    primary: '#dc2626',
    light: '#ef4444',
    dark: '#b91c1c',
    background: '#fef2f2'
  },
  [PLAYER_COLORS.BLUE]: {
    primary: '#2563eb',
    light: '#3b82f6',
    dark: '#1d4ed8',
    background: '#eff6ff'
  },
  [PLAYER_COLORS.GREEN]: {
    primary: '#16a34a',
    light: '#22c55e',
    dark: '#15803d',
    background: '#f0fdf4'
  },
  [PLAYER_COLORS.YELLOW]: {
    primary: '#ca8a04',
    light: '#eab308',
    dark: '#a16207',
    background: '#fefce8'
  }
};

// Posiciones especiales en el tablero de 68 casillas (basado en imagen real)
export const SPECIAL_POSITIONS = {
  // Posiciones de salida de cada color
  START_POSITIONS: {
    [PLAYER_COLORS.RED]: 39,   // Casilla 39 (salida roja)
    [PLAYER_COLORS.BLUE]: 22,  // Casilla 22 (salida azul)  
    [PLAYER_COLORS.GREEN]: 56, // Casilla 56 (salida verde)
    [PLAYER_COLORS.YELLOW]: 5  // Casilla 5 (salida amarilla)
  },
  
  // Casillas seguras (círculos grises en la imagen)
  SAFE_POSITIONS: [
    5,   // Salida amarilla
    12,  // Segura en lado derecho
    22,  // Salida azul
    29,  // Segura en lado superior
    39,  // Salida roja
    46,  // Segura en lado izquierdo
    56,  // Salida verde
    63   // Segura en lado inferior
  ],
  
  // Casillas de salida (también son seguras)
  EXIT_POSITIONS: [5, 22, 39, 56],  // Amarillo, Azul, Rojo, Verde
  
  // Entradas a las rectas finales (donde cada color entra a su pasillo final)
  GOAL_ENTRIES: {
    [PLAYER_COLORS.RED]: 34,   // Entra por casilla 34 hacia recta roja
    [PLAYER_COLORS.BLUE]: 17,  // Entra por casilla 17 hacia recta azul
    [PLAYER_COLORS.GREEN]: 51, // Entra por casilla 51 hacia recta verde  
    [PLAYER_COLORS.YELLOW]: 0  // Entra por casilla 0 (68) hacia recta amarilla
  },

  // Posiciones de las bases (cárceles) - círculos en las esquinas
  PRISON_POSITIONS: {
    [PLAYER_COLORS.RED]: 'top-left',
    [PLAYER_COLORS.BLUE]: 'top-right', 
    [PLAYER_COLORS.GREEN]: 'bottom-left',
    [PLAYER_COLORS.YELLOW]: 'bottom-right'
  }
};

// Estados del juego
export const GAME_STATUS = {
  WAITING: 'waiting',
  READY: 'ready',
  PLAYING: 'playing',
  FINISHED: 'finished'
};

// Tipos de casillas
export const CELL_TYPES = {
  NORMAL: 'normal',
  SAFE: 'safe',
  START: 'start',
  GOAL_ENTRY: 'goal_entry',
  GOAL: 'goal',
  CENTER: 'center'
};

// Coordenadas de las casillas en la imagen del tablero (en porcentajes)
// Basado en la imagen de 700x700px aproximadamente
export const BOARD_COORDINATES = {
  // Casillas del lado inferior (1-17) 
  1: { x: 58.15, y: 95.3 },  
  2: { x: 58.15, y: 90.7 },  
  3: { x: 58.15, y: 86.1 },  
  4: { x: 58.15, y: 81.4 },  
  5: { x: 58.15, y: 76.65 },  // Salida amarilla
  6: { x: 58.15, y: 72.2 },  
  7: { x: 58.15, y: 67.7 },  
  8: { x: 58.15, y: 63 },  
  9: { x: 61.0, y: 60.2 }, 
  10: { x: 65.6, y: 60 },
  11: { x: 70.0, y: 60 },
  12: { x: 74.73, y: 60 }, // Casilla segura
  13: { x: 79.4, y: 60 },
  14: { x: 84, y: 60 },
  15: { x: 88.7, y: 60 },
  16: { x: 93.2, y: 60 },
  17: { x: 93.2, y: 49.5 },

  // Casillas del lado derecho (18-34)
  18: { x: 93.2, y: 38.8 },  
  19: { x: 88.8, y: 38.8 },  
  20: { x: 84.2, y: 38.8 },  
  21: { x: 79.6, y: 38.8 },  
  22: { x: 74.8, y: 38.8 },  // Salida azul
  23: { x: 70.0, y: 38.8 },  
  24: { x: 65.6, y: 38.8 },  
  25: { x: 61.0, y: 38.8 },  
  26: { x: 58.15, y: 36.3 },
  27: { x: 58.15, y: 31.5 },
  28: { x: 58.15, y: 26.9 },
  29: { x: 58.15, y: 22.2 },  // Casilla segura
  30: { x: 58.15, y: 17.5 },
  31: { x: 58.15, y: 12.8 },
  32: { x: 58.15, y: 8.1 },
  33: { x: 58.15, y: 3.5 },
  34: { x: 47.5, y: 3.5 },

  // Casillas del lado superior (35-51)
  35: { x: 36.85, y: 3.5 },     
  36: { x: 36.85, y: 8.1 },     
  37: { x: 36.85, y: 12.8 },    
  38: { x: 36.85, y: 17.5 },    
  39: { x: 36.85, y: 22.2 },  // Salida roja
  40: { x: 36.85, y: 26.9 }, 
  41: { x: 36.85, y: 31.5 }, 
  42: { x: 36.85, y: 36.3 }, 
  43: { x: 34.2, y: 38.8 }, 
  44: { x: 29.4, y: 38.8 },
  45: { x: 24.9, y: 38.8 },
  46: { x: 20.15, y: 38.8 }, // Casilla segura
  47: { x: 15.6, y: 38.8 },
  48: { x: 10.9, y: 38.8 },
  49: { x: 6.35, y: 38.8 },
  50: { x: 1.7, y: 38.8 },
  51: { x: 1.7, y: 49.5 },

  // Casillas del lado izquierdo (52-68)
  52: { x: 1.7, y: 60.2 },  
  53: { x: 6.35, y: 60.2 },  
  54: { x: 10.9, y: 60.2 },
  55: { x: 15.6, y: 60.2 },
  56: { x: 20.15, y: 60.2 },  // Salida verde
  57: { x: 24.9, y: 60.2 },
  58: { x: 29.4, y: 60.2 },
  59: { x: 34.2, y: 60.2 },   
  60: { x: 36.85, y: 63 },   
  61: { x: 36.85, y: 67.7},
  62: { x: 36.85, y: 72.2 },
  63: { x: 36.85, y: 76.65 },   // Casilla segura
  64: { x: 36.85, y: 81.4 },
  65: { x: 36.85, y: 86.1 },
  66: { x: 36.85, y: 90.7 },
  67: { x: 36.85, y: 95.3 },
  68: { x: 47.5, y: 95.3 },

  // Rectas finales (coordenadas hacia el centro)
  // Recta roja (desde casilla 34 hacia el centro)
  'red_1': { x: 47.5, y: 8.1 },
  'red_2': { x: 47.5, y: 12.8},
  'red_3': { x: 47.5, y: 17.5 },
  'red_4': { x: 47.5, y: 22.2 },
  'red_5': { x: 47.5, y: 26.9 },
  'red_6': { x: 47.5, y: 31.3 },
  'red_7': { x: 47.5, y: 38.8 },
  'red_8': { x: 47.5, y: 42 },

  // Recta azul (desde casilla 17 hacia el centro)
  'blue_1': { x: 88.7, y: 49.5 },
  'blue_2': { x: 84, y: 49.5 },
  'blue_3': { x: 79.4, y: 49.5 },
  'blue_4': { x: 74.73, y: 49.5 },
  'blue_5': { x: 70, y: 49.5 },
  'blue_6': { x: 65.6, y: 49.5 },
  'blue_7': { x: 61.0, y: 49.5 },
  'blue_8': { x: 55, y: 49.5 },

  // Recta verde (desde casilla 51 hacia el centro)
  'green_1': { x: 6.35, y: 49.5 },
  'green_2': { x: 10.9, y: 49.5 },
  'green_3': { x: 15.6, y: 49.5 },
  'green_4': { x: 20.15, y: 49.5 },
  'green_5': { x: 24.9, y: 49.5 },
  'green_6': { x: 29.4, y: 49.5 },
  'green_7': { x: 34.2, y: 49.5 },
  'green_8': { x: 39.4, y: 49.5 },

  // Recta amarilla (desde casilla 0/68 hacia el centro)
  'yellow_1': { x: 47.5, y: 90.7 },
  'yellow_2': { x: 47.5, y: 86.1 },
  'yellow_3': { x: 47.5, y: 81.4 },
  'yellow_4': { x: 47.5, y: 76.65 },
  'yellow_5': { x: 47.5, y: 72.2 },
  'yellow_6': { x: 47.5, y: 67.7 },
  'yellow_7': { x: 47.5, y: 63 },
  'yellow_8': { x: 47.5, y: 57 },

  // Cárceles (bases de jugadores) - Centros de las áreas de cárcel
  'prison_red': { x: 18, y: 18 },      // Esquina superior izquierda
  'prison_blue': { x: 82, y: 18 },     // Esquina superior derecha
  'prison_green': { x: 18, y: 82 },    // Esquina inferior izquierda  
  'prison_yellow': { x: 82, y: 82 },   // Esquina inferior derecha

  // Centro (meta final)
  'center': { x: 50, y: 50 }
};
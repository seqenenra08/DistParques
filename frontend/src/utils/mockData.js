// Datos de prueba para el tablero
export const mockGameState = {
  currentPlayer: 'red',
  diceValue: 5,
  players: [
    {
      player_id: 1,
      name: 'Jugador Rojo',
      color: 'red',
      pieces_in_goal: 0,
      pieces: [
        { piece_id: 0, position: -1, is_in_goal: false }, // En casilla de salida ROJA (39)
        { piece_id: 1, position: -1, is_in_goal: false }, // En cárcel
        { piece_id: 2, position: -1, is_in_goal: false }, // En cárcel
        { piece_id: 3, position: -1, is_in_goal: false }  // En cárcel
      ]
    },
    {
      player_id: 2,
      name: 'Jugador Azul', 
      color: 'blue',
      pieces_in_goal: 0,
      pieces: [
        { piece_id: 0, position: -1, is_in_goal: false }, // En casilla de salida AZUL (22)
        { piece_id: 1, position: -1, is_in_goal: false }, // En cárcel
        { piece_id: 2, position: -1, is_in_goal: false }, // En cárcel
        { piece_id: 3, position: -1, is_in_goal: false }  // En cárcel
      ]
    },
    {
      player_id: 3,
      name: 'Jugador Verde',
      color: 'green', 
      pieces_in_goal: 0,
      pieces: [
        { piece_id: 0, position: -1, is_in_goal: false },  // En casilla de salida VERDE (5)
        { piece_id: 1, position: -1, is_in_goal: false }, // En cárcel
        { piece_id: 2, position: -1, is_in_goal: false }, // En cárcel
        { piece_id: 3, position: -1, is_in_goal: false }  // En cárcel
      ]
    },
    {
      player_id: 4,
      name: 'Jugador Amarillo',
      color: 'yellow',
      pieces_in_goal: 0,
      pieces: [
        { piece_id: 0, position: -1, is_in_goal: false }, // En casilla de salida AMARILLA (56)
        { piece_id: 1, position: -1, is_in_goal: false }, // En cárcel
        { piece_id: 2, position: -1, is_in_goal: false }, // En cárcel
        { piece_id: 3, position: -1, is_in_goal: false }  // En cárcel
      ]
    }
  ]
};

// Estado de prueba mixto (combinación de tablero y caminos finales)
export const testMixedState = {
  currentPlayer: 'blue',
  diceValue: 4,
  players: [
    {
      player_id: 1,
      name: 'Jugador Rojo',
      color: 'red',
      pieces_in_goal: 0,
      pieces: [
        { piece_id: 0, position: 39, is_in_goal: false },   // Casilla de salida
        { piece_id: 1, position: 45, is_in_goal: false },   // Casilla normal
        { piece_id: 2, position: 'red_4', is_in_goal: false },
        { piece_id: 3, position: -1, is_in_goal: false }
      ]
    },
    {
      player_id: 2,
      name: 'Jugador Azul',
      color: 'blue',
      pieces_in_goal: 0,
      pieces: [
        { piece_id: 0, position: 22, is_in_goal: false },
        { piece_id: 1, position: 'blue_2', is_in_goal: false },
        { piece_id: 2, position: 10, is_in_goal: false },
        { piece_id: 3, position: -1, is_in_goal: false }
      ]
    },
    {
      player_id: 3,
      name: 'Jugador Verde',
      color: 'green',
      pieces_in_goal: 0,
      pieces: [
        { piece_id: 0, position: 5, is_in_goal: false },
        { piece_id: 1, position: 'green_1', is_in_goal: false },
        { piece_id: 2, position: 65, is_in_goal: false },
        { piece_id: 3, position: -1, is_in_goal: false }
      ]
    },
    {
      player_id: 4,
      name: 'Jugador Amarillo',
      color: 'yellow',
      pieces_in_goal: 0,
      pieces: [
        { piece_id: 0, position: 56, is_in_goal: false },
        { piece_id: 1, position: 'yellow_5', is_in_goal: false },
        { piece_id: 2, position: 60, is_in_goal: false },
        { piece_id: 3, position: -1, is_in_goal: false }
      ]
    }
  ]
};

// Estado inicial del juego (todas las fichas en cárcel)
export const initialGameState = {
  currentPlayer: 'red',
  diceValue: null,
  players: [
    {
      player_id: 1,
      name: 'Jugador Rojo',
      color: 'red',
      pieces_in_goal: 0,
      pieces: [
        { piece_id: 0, position: -1, is_in_goal: false },
        { piece_id: 1, position: -1, is_in_goal: false },
        { piece_id: 2, position: -1, is_in_goal: false },
        { piece_id: 3, position: -1, is_in_goal: false }
      ]
    },
    {
      player_id: 2,
      name: 'Jugador Azul',
      color: 'blue',
      pieces_in_goal: 0,
      pieces: [
        { piece_id: 0, position: -1, is_in_goal: false },
        { piece_id: 1, position: -1, is_in_goal: false },
        { piece_id: 2, position: -1, is_in_goal: false },
        { piece_id: 3, position: -1, is_in_goal: false }
      ]
    },
    {
      player_id: 3,
      name: 'Jugador Verde',
      color: 'green',
      pieces_in_goal: 0,
      pieces: [
        { piece_id: 0, position: -1, is_in_goal: false },
        { piece_id: 1, position: -1, is_in_goal: false },
        { piece_id: 2, position: -1, is_in_goal: false },
        { piece_id: 3, position: -1, is_in_goal: false }
      ]
    },
    {
      player_id: 4,
      name: 'Jugador Amarillo',
      color: 'yellow',
      pieces_in_goal: 0,
      pieces: [
        { piece_id: 0, position: -1, is_in_goal: false },
        { piece_id: 1, position: -1, is_in_goal: false },
        { piece_id: 2, position: -1, is_in_goal: false },
        { piece_id: 3, position: -1, is_in_goal: false }
      ]
    }
  ]
};

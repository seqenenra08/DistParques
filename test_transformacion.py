#!/usr/bin/env python3
"""Script para probar la transformación de estado."""

import sys
sys.path.insert(0, '/home/seqenenra/Codes/DistParques/backend')
from models.partida import Partida
import json

def transformar_estado_para_frontend(estado):
    """Transforma el estado del backend al formato esperado por el frontend."""
    estado_frontend = estado.copy()
    
    # Transformar jugadores: 'fichas' -> 'pieces', 'nombre' -> 'name'
    if 'jugadores' in estado_frontend:
        jugadores_transformados = []
        for jugador in estado_frontend['jugadores']:
            jugador_frontend = {
                'player_id': jugador.get('id'),
                'name': jugador.get('nombre'),
                'color': jugador.get('color'),
                'es_su_turno': jugador.get('es_su_turno', False),
                'pieces_in_home': sum(1 for f in jugador.get('fichas', []) if f.get('estado') == 'meta'),
                'pieces': []
            }
            
            # Transformar fichas
            for ficha in jugador.get('fichas', []):
                # Mapear posición según el estado de la ficha
                posicion = -1  # Por defecto cárcel
                
                if ficha.get('estado') == 'carcel':
                    posicion = -1
                elif ficha.get('estado') == 'meta':
                    posicion = 'center'
                elif ficha.get('estado') == 'pasillo_final':
                    # Formato: color_posicion (ej: red_3)
                    posicion = f"{jugador.get('color')}_{ficha.get('posicion_pasillo', 0)}"
                else:
                    # Posición en tablero normal
                    posicion = ficha.get('posicion', -1)
                
                jugador_frontend['pieces'].append({
                    'piece_id': ficha.get('id'),
                    'color': ficha.get('color'),
                    'position': posicion,
                    'estado': ficha.get('estado'),
                    'is_in_goal': ficha.get('estado') == 'meta'
                })
            
            jugadores_transformados.append(jugador_frontend)
        
        estado_frontend['players'] = jugadores_transformados
        estado_frontend['jugadores'] = jugadores_transformados  # Mantener ambos por compatibilidad
    
    # Cambiar 'jugador_actual' -> 'currentPlayer'
    if 'jugador_actual' in estado_frontend:
        estado_frontend['currentPlayer'] = estado_frontend['jugador_actual']
    
    # Agregar currentPlayer también basado en turno
    if 'jugadores' in estado and estado.get('turno_actual') is not None:
        turno = estado.get('turno_actual', 0)
        if turno < len(estado['jugadores']):
            estado_frontend['currentPlayer'] = estado['jugadores'][turno].get('nombre')
    
    return estado_frontend

# Crear partida de prueba
partida = Partida(id_partida='TEST123')
partida.agregar_jugador('Jugador 1', 'player1', 'red')
partida.agregar_jugador('Bot 1', 'bot1', 'blue')
partida.agregar_jugador('Bot 2', 'bot2', 'yellow')
partida.agregar_jugador('Bot 3', 'bot3', 'green')
partida.iniciar_partida()

# Obtener estado backend
estado_backend = partida.obtener_estado()

# Transformar para frontend
estado_frontend = transformar_estado_para_frontend(estado_backend)

print('=== ESTADO TRANSFORMADO PARA FRONTEND ===')
print(f"Total players: {len(estado_frontend.get('players', []))}")
print(f"Current player: {estado_frontend.get('currentPlayer')}")
print()

for player in estado_frontend.get('players', []):
    print(f"Player: {player.get('name')} ({player.get('color')})")
    print(f"  - player_id: {player.get('player_id')}")
    print(f"  - pieces_in_home: {player.get('pieces_in_home')}")
    print(f"  - pieces: {len(player.get('pieces', []))}")
    for piece in player.get('pieces', []):
        print(f"    * piece_id={piece.get('piece_id')}, color={piece.get('color')}, position={piece.get('position')}, is_in_goal={piece.get('is_in_goal')}")
    print()

print('=== JSON COMPLETO ===')
print(json.dumps(estado_frontend, indent=2, default=str))

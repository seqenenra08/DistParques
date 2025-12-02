#!/usr/bin/env python3
"""Script de prueba para verificar transformación de estado."""

import sys
sys.path.insert(0, '/home/seqenenra/Codes/DistParques/backend')
from models.partida import Partida
import json

# Crear partida de prueba
partida = Partida(id_partida='TEST123')
partida.agregar_jugador('Jugador 1', 'player1', 'red')
partida.agregar_jugador('Bot 1', 'bot1', 'blue')
partida.agregar_jugador('Bot 2', 'bot2', 'yellow')
partida.agregar_jugador('Bot 3', 'bot3', 'green')
partida.iniciar_partida()

# Obtener estado
estado = partida.obtener_estado()

print('=== ESTADO DEL BACKEND ===')
print('Número de jugadores:', len(estado.get('jugadores', [])))
for j in estado.get('jugadores', []):
    print(f"  - {j.get('nombre')} ({j.get('color')}): {len(j.get('fichas', []))} fichas")
    for f in j.get('fichas', []):
        print(f"    * Ficha {f.get('id')}: estado={f.get('estado')}, pos={f.get('posicion')}")

print()
print('=== JUGADOR ACTUAL ===')
print('Turno:', estado.get('turno_actual'))
print('Jugador actual:', estado.get('jugador_actual'))

print()
print('=== ESTRUCTURA COMPLETA (JSON) ===')
print(json.dumps(estado, indent=2, default=str))

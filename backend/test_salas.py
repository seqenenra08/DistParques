#!/usr/bin/env python3
"""
Script de prueba para el servidor de salas.
Simula dos clientes conectándose: uno crea una sala y otro se une.
"""

import asyncio
import websockets
import json

async def cliente_host():
    """Simula el cliente que crea la sala (host)."""
    uri = "ws://localhost:5555"
    
    async with websockets.connect(uri) as websocket:
        print("[HOST] Conectado al servidor")
        
        # Recibir mensaje de bienvenida
        mensaje = await websocket.recv()
        print(f"[HOST] Recibido: {mensaje}")
        
        # Crear sala
        print("[HOST] Creando sala...")
        await websocket.send(json.dumps({
            "tipo": "CREAR_SALA",
            "playerName": "Jugador Host",
            "maxPlayers": 4,
            "numBots": 0,
            "color": "red"
        }))
        
        # Recibir respuesta
        respuesta = await websocket.recv()
        data = json.loads(respuesta)
        print(f"[HOST] Sala creada: {data.get('codigo_sala')}")
        
        # Esperar mensajes
        print("[HOST] Esperando jugadores...")
        while True:
            mensaje = await websocket.recv()
            data = json.loads(mensaje)
            print(f"[HOST] Evento: {data.get('tipo')}")
            
            # Si se unió un jugador, iniciar la partida
            if data.get('tipo') == 'JUGADOR_UNIDO':
                print("[HOST] ¡Jugador unido! Iniciando partida en 2 segundos...")
                await asyncio.sleep(2)
                
                await websocket.send(json.dumps({
                    "tipo": "INICIAR_PARTIDA"
                }))
                print("[HOST] Solicitud de inicio enviada")


async def cliente_invitado(codigo_sala):
    """Simula el cliente que se une a la sala."""
    uri = "ws://localhost:5555"
    
    # Esperar un poco para que el host cree la sala
    await asyncio.sleep(1)
    
    async with websockets.connect(uri) as websocket:
        print("[GUEST] Conectado al servidor")
        
        # Recibir mensaje de bienvenida
        mensaje = await websocket.recv()
        print(f"[GUEST] Recibido: {mensaje}")
        
        # Unirse a sala
        print(f"[GUEST] Uniéndose a sala {codigo_sala}...")
        await websocket.send(json.dumps({
            "tipo": "UNIRSE_SALA",
            "roomCode": codigo_sala,
            "playerName": "Jugador Invitado",
            "color": "blue"
        }))
        
        # Recibir respuesta
        respuesta = await websocket.recv()
        data = json.loads(respuesta)
        print(f"[GUEST] Respuesta: {data.get('tipo')}")
        
        # Esperar mensajes
        print("[GUEST] Esperando eventos...")
        while True:
            mensaje = await websocket.recv()
            data = json.loads(mensaje)
            print(f"[GUEST] Evento: {data.get('tipo')}")


async def prueba_completa():
    """Ejecuta una prueba completa del sistema."""
    print("=" * 60)
    print("🧪 PRUEBA DEL SERVIDOR DE SALAS")
    print("=" * 60)
    print()
    
    # Código de sala que usará el invitado (el host lo generará)
    # En una prueba real, necesitaríamos comunicación entre los clientes
    # Para simplificar, usaremos uno fijo
    
    print("⚠️  Asegúrate de que el servidor esté corriendo!")
    print("   Ejecuta: python3 backend/iniciar_servidor.py")
    print()
    
    try:
        # Crear tareas para ambos clientes
        # Nota: En este ejemplo simplificado, el código de sala se pasa manualmente
        # En producción, el invitado lo obtendría del host
        
        host_task = asyncio.create_task(cliente_host())
        
        # Dar tiempo al host para crear la sala
        await asyncio.sleep(2)
        
        # El invitado necesitaría el código real de la sala
        # Por ahora, esta prueba es más conceptual
        
        # Esperar a que termine (nunca termina en este ejemplo)
        await host_task
        
    except ConnectionRefusedError:
        print("\n❌ ERROR: No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté corriendo")
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba interrumpida por el usuario")


if __name__ == "__main__":
    print(__doc__)
    asyncio.run(prueba_completa())

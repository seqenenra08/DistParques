#!/usr/bin/env python3
"""Test rápido para verificar que el bot funciona correctamente"""

import time
import sys
import threading
from cliente.bot_jugador import BotJugador

def main():
    """Ejecuta dos bots para probar la partida"""
    print("=== Iniciando prueba del bot ===\n")
    
    # Crear dos bots
    bot1 = BotJugador("Bot-Rojo", host="127.0.0.1", puerto=5555)
    bot2 = BotJugador("Bot-Azul", host="127.0.0.1", puerto=5555)
    
    try:
        # Conectar ambos bots
        print("Conectando Bot-Rojo...")
        if not bot1.conectar():
            print("❌ Error al conectar bot1")
            return
        
        # Iniciar hilo de recepción para bot1
        hilo1 = threading.Thread(target=bot1.recibir_mensajes, daemon=True)
        hilo1.start()
        
        time.sleep(1.5)
        
        print("Conectando Bot-Azul...")
        if not bot2.conectar():
            print("❌ Error al conectar bot2")
            return
        
        # Iniciar hilo de recepción para bot2
        hilo2 = threading.Thread(target=bot2.recibir_mensajes, daemon=True)
        hilo2.start()
        
        print("\nBots conectados. Esperando 3 segundos antes de iniciar partida...")
        time.sleep(3)
        
        # Enviar START desde el primer bot
        print("\n🎮 Bot-Rojo enviando START...\n")
        bot1.enviar_mensaje({"tipo": "START"})
        
        # Dejar que los bots jueguen por 30 segundos
        print("=" * 60)
        print("PARTIDA EN CURSO - Los bots jugarán por 30 segundos")
        print("=" * 60)
        print()
        
        time.sleep(30)
        
        print("\n" + "=" * 60)
        print("=== Prueba completada ===")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⚠️  Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Desconectar bots
        print("\nDesconectando bots...")
        bot1.desconectar()
        bot2.desconectar()
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Prueba interrumpida")
        sys.exit(0)

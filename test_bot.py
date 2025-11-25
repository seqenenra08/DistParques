#!/usr/bin/env python3
"""
Test rápido del bot - Verifica que pueda conectarse y jugar
"""

import sys
import time
import subprocess
import signal

def test_bot():
    print("\n🧪 TEST: Bot Jugador Automático")
    print("="*60)
    
    # Iniciar servidor
    print("\n1️⃣ Iniciando servidor...")
    servidor = subprocess.Popen(
        ["python3", "backend/servidor.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2)
    
    # Iniciar bot
    print("2️⃣ Iniciando bot...")
    bot = subprocess.Popen(
        ["python3", "cliente/bot_jugador.py", "TestBot"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Esperar y verificar output del bot
    print("3️⃣ Verificando funcionamiento del bot...")
    time.sleep(3)
    
    # Verificar que el bot sigue corriendo
    if bot.poll() is None:
        print("   ✅ Bot conectado y activo")
        resultado = True
    else:
        print("   ❌ Bot se detuvo inesperadamente")
        resultado = False
    
    # Cleanup
    print("\n4️⃣ Limpiando procesos...")
    bot.send_signal(signal.SIGTERM)
    servidor.send_signal(signal.SIGTERM)
    
    time.sleep(1)
    bot.kill()
    servidor.kill()
    
    print("\n" + "="*60)
    if resultado:
        print("✅ TEST EXITOSO: El bot funciona correctamente")
        print("\n💡 Para probarlo en una partida real, ejecuta:")
        print("   ./demo_bot.sh")
    else:
        print("❌ TEST FALLIDO: Revisar implementación")
    print("="*60 + "\n")
    
    return resultado

if __name__ == "__main__":
    try:
        exito = test_bot()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrumpido")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

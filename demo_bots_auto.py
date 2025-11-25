#!/usr/bin/env python3
"""
Demo completa: Bot jugando automáticamente
Muestra 2 bots jugando entre sí para demostrar funcionamiento
"""

import subprocess
import time
import sys

def main():
    print("\n" + "🤖"*30)
    print("   DEMO: DOS BOTS JUGANDO ENTRE SÍ")
    print("🤖"*30 + "\n")
    
    print("Esta demo mostrará dos bots jugando automáticamente")
    print("Presiona Ctrl+C para detener\n")
    print("-"*60 + "\n")
    
    # Iniciar servidor
    print("1️⃣ Iniciando servidor...")
    servidor = subprocess.Popen(
        ["python3", "backend/servidor.py"],
        cwd="/home/seqenenra/Codes/DistParques"
    )
    time.sleep(2)
    
    # Iniciar Bot 1
    print("2️⃣ Iniciando Bot-1...")
    bot1 = subprocess.Popen(
        ["python3", "cliente/bot_jugador.py", "Bot-1"],
        cwd="/home/seqenenra/Codes/DistParques"
    )
    time.sleep(1)
    
    # Iniciar Bot 2
    print("3️⃣ Iniciando Bot-2...")
    bot2 = subprocess.Popen(
        ["python3", "cliente/bot_jugador.py", "Bot-2"],
        cwd="/home/seqenenra/Codes/DistParques"
    )
    time.sleep(1)
    
    print("\n" + "="*60)
    print("✅ DEMO EN EJECUCIÓN - Los bots están jugando")
    print("="*60)
    print("\n💡 Tip: Abre otra terminal y ejecuta:")
    print("   python3 cliente/cliente_simple.py")
    print("   para unirte como jugador humano\n")
    print("Presiona Ctrl+C para detener la demo\n")
    
    try:
        # Mantener corriendo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo demo...")
        bot1.terminate()
        bot2.terminate()
        servidor.terminate()
        time.sleep(1)
        bot1.kill()
        bot2.kill()
        servidor.kill()
        print("✅ Demo detenida\n")

if __name__ == "__main__":
    main()

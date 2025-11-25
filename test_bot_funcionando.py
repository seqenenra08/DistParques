#!/usr/bin/env python3
"""
Test para verificar que el bot funciona correctamente
"""

import subprocess
import time
import sys

print("\n🧪 VERIFICACIÓN: Bot Lanzando Dados y Jugando")
print("="*60)

# Iniciar servidor en background
print("1. Iniciando servidor...")
servidor = subprocess.Popen(
    ["python3", "backend/servidor.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)
time.sleep(2)

# Iniciar Bot-1
print("2. Iniciando Bot-1...")
bot1 = subprocess.Popen(
    ["python3", "cliente/bot_jugador.py", "Bot-1"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)
time.sleep(2)

# Iniciar Bot-2
print("3. Iniciando Bot-2...")
bot2 = subprocess.Popen(
    ["python3", "cliente/bot_jugador.py", "Bot-2"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

print("\n" + "="*60)
print("✅ Bots iniciados, monitoreando actividad...")
print("="*60 + "\n")

# Monitorear por 15 segundos
inicio = time.time()
lineas_bot1 = []
lineas_bot2 = []

try:
    while time.time() - inicio < 15:
        # Leer de Bot-1
        try:
            linea = bot1.stdout.readline()
            if linea:
                lineas_bot1.append(linea.strip())
                if "🎲" in linea or "Lanzando" in linea or "Moviendo" in linea:
                    print(f"[Bot-1] {linea.strip()}")
        except:
            pass
        
        # Leer de Bot-2
        try:
            linea = bot2.stdout.readline()
            if linea:
                lineas_bot2.append(linea.strip())
                if "🎲" in linea or "Lanzando" in linea or "Moviendo" in linea:
                    print(f"[Bot-2] {linea.strip()}")
        except:
            pass
        
        time.sleep(0.1)

except KeyboardInterrupt:
    pass

print("\n" + "="*60)
print("📊 RESULTADOS DEL TEST")
print("="*60)

# Verificar si los bots lanzaron dados
bot1_lanzo = any("Lanzando dados" in l for l in lineas_bot1)
bot2_lanzo = any("Lanzando dados" in l for l in lineas_bot2)
bot1_movio = any("Moviendo" in l for l in lineas_bot1)
bot2_movio = any("Moviendo" in l for l in lineas_bot2)

print(f"\n✅ Bot-1 lanzó dados: {bot1_lanzo}")
print(f"✅ Bot-1 movió fichas: {bot1_movio}")
print(f"✅ Bot-2 lanzó dados: {bot2_lanzo}")
print(f"✅ Bot-2 movió fichas: {bot2_movio}")

if bot1_lanzo and bot2_lanzo:
    print("\n🎉 ¡ÉXITO! Los bots están funcionando correctamente")
    resultado = 0
else:
    print("\n❌ PROBLEMA: Los bots no están lanzando dados")
    resultado = 1

# Cleanup
print("\n🧹 Limpiando procesos...")
bot1.terminate()
bot2.terminate()
servidor.terminate()
time.sleep(1)
bot1.kill()
bot2.kill()
servidor.kill()

print("✅ Test completado\n")
sys.exit(resultado)

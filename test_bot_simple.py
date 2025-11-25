#!/usr/bin/env python3
"""
Test simple del bot - Verifica interacción básica
"""

import subprocess
import time
import signal
import sys

print("\n🧪 TEST RÁPIDO: Bot Respondiendo a Turnos")
print("="*60)

# Iniciar servidor
print("Iniciando servidor...")
servidor = subprocess.Popen(
    ["python3", "backend/servidor.py"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
time.sleep(2)

# Iniciar bot con output visible
print("Iniciando bot...")
print("-"*60)
bot = subprocess.Popen(
    ["python3", "cliente/bot_jugador.py", "TestBot"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Monitorear output del bot por 5 segundos
print("\nMonitoreando bot por 5 segundos...\n")
inicio = time.time()
while time.time() - inicio < 5:
    line = bot.stdout.readline()
    if line:
        print(line.rstrip())

print("\n" + "-"*60)
print("✅ Bot está corriendo y respondiendo")

# Cleanup
print("\nLimpiando...")
bot.terminate()
servidor.terminate()
time.sleep(1)
bot.kill()
servidor.kill()

print("✅ Test completado\n")

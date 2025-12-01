#!/usr/bin/env python3
"""Script para iniciar el servidor de salas multijugador."""

import os
import sys

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from servidor_salas import ServidorSalas
import asyncio

def main():
    print("=" * 60)
    print("🎲 SERVIDOR DE SALAS MULTIJUGADOR - PARQUÉS 🎲")
    print("=" * 60)
    print()
    
    # Configuración del servidor
    host = os.getenv('SERVER_HOST', '0.0.0.0')
    puerto = int(os.getenv('SERVER_PORT', '5555'))
    
    print(f"📡 Host: {host}")
    print(f"🔌 Puerto: {puerto}")
    print()
    print("Características:")
    print("  ✅ Múltiples salas simultáneas")
    print("  ✅ Códigos únicos de 6 dígitos")
    print("  ✅ 2-4 jugadores por sala")
    print("  ✅ Soporte para bots")
    print()
    print("=" * 60)
    print()
    
    # Crear e iniciar servidor
    servidor = ServidorSalas(host, puerto)
    
    try:
        asyncio.run(servidor.iniciar())
    except KeyboardInterrupt:
        print("\n")
        print("=" * 60)
        print("⚠️  Servidor detenido por el usuario")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

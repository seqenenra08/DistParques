#!/usr/bin/env bash
# Script para ejecutar cliente de consola

cd "$(dirname "$0")"

if [ -f env/bin/activate ]; then
    source env/bin/activate
else
    echo "⚠️  Entorno virtual no encontrado."
    exit 1
fi

echo "🎮 Iniciando cliente de consola..."
python3 cliente/cliente_consola.py "$@"

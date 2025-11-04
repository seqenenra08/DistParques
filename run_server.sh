#!/usr/bin/env bash
# Script para ejecutar el servidor de Parqués

cd "$(dirname "$0")"

# Activar entorno virtual
if [ -f env/bin/activate ]; then
    source env/bin/activate
else
    echo "⚠️  Entorno virtual no encontrado. Ejecuta: python3 -m venv env"
    exit 1
fi

# Ejecutar servidor
echo "🚀 Iniciando servidor de Parqués..."
python3 backend/servidor.py "$@"

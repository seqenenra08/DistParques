#!/bin/bash

# Script para iniciar servidor y frontend automáticamente
# Uso: ./iniciar_juego.sh

echo "🎮 DistParques - Iniciando Sistema"
echo "===================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "backend/servidor_salas.py" ]; then
    echo "❌ Error: Ejecuta este script desde la raíz del proyecto"
    exit 1
fi

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo servicios..."
    kill $SERVER_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
    wait $FRONTEND_PID 2>/dev/null
    echo "✅ Servicios detenidos"
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "1️⃣  Iniciando servidor backend (puerto 5555)..."
/home/seqenenra/Codes/DistParques/env/bin/python backend/servidor_salas.py &
SERVER_PID=$!
sleep 2

# Verificar que el servidor inició
if ! ps -p $SERVER_PID > /dev/null; then
    echo "❌ Error: No se pudo iniciar el servidor"
    echo "   Verifica que no haya otro servidor corriendo en el puerto 5555"
    exit 1
fi

echo "✅ Servidor backend iniciado (PID: $SERVER_PID)"
echo ""

echo "2️⃣  Iniciando frontend (puerto 3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ Frontend iniciando... (PID: $FRONTEND_PID)"
echo ""

echo "===================================="
echo "✨ Sistema iniciado correctamente"
echo "===================================="
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend:  ws://localhost:5555"
echo ""
echo "📝 Logs:"
echo "   - Backend:  Ver arriba"
echo "   - Frontend: Ver en el navegador (F12)"
echo ""
echo "⏹️  Para detener: Presiona Ctrl+C"
echo ""

# Esperar indefinidamente
wait

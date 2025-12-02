#!/bin/bash

echo "========================================="
echo "🧪 SCRIPT DE PRUEBA - DistParques"
echo "========================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "backend/servidor_salas.py" ]; then
    echo "❌ Error: Ejecuta este script desde la raíz del proyecto"
    exit 1
fi

echo "1️⃣  Verificando estructura de archivos..."
echo ""

# Verificar archivos críticos
archivos=(
    "backend/servidor_salas.py"
    "backend/servidor.py"
    "backend/models/partida.py"
    "frontend/src/app/page.js"
    "cliente/cliente_simple.py"
    "cliente/bot_jugador.py"
)

for archivo in "${archivos[@]}"; do
    if [ -f "$archivo" ]; then
        echo "   ✅ $archivo"
    else
        echo "   ❌ $archivo (FALTA)"
    fi
done

echo ""
echo "2️⃣  Verificando dependencias Python..."
echo ""

# Verificar Python
if command -v python3 &> /dev/null; then
    echo "   ✅ Python3 instalado: $(python3 --version)"
else
    echo "   ❌ Python3 no encontrado"
fi

# Verificar módulos Python
python3 -c "import websockets" 2>/dev/null && echo "   ✅ websockets" || echo "   ⚠️  websockets no instalado (pip install websockets)"
python3 -c "import asyncio" 2>/dev/null && echo "   ✅ asyncio" || echo "   ❌ asyncio no disponible"

echo ""
echo "3️⃣  Verificando dependencias Node.js..."
echo ""

# Verificar Node
if command -v node &> /dev/null; then
    echo "   ✅ Node.js instalado: $(node --version)"
else
    echo "   ❌ Node.js no encontrado"
fi

# Verificar npm
if command -v npm &> /dev/null; then
    echo "   ✅ npm instalado: $(npm --version)"
else
    echo "   ❌ npm no encontrado"
fi

# Verificar package.json
if [ -f "frontend/package.json" ]; then
    echo "   ✅ package.json existe"
    if [ -d "frontend/node_modules" ]; then
        echo "   ✅ node_modules instalado"
    else
        echo "   ⚠️  node_modules no encontrado - ejecuta: cd frontend && npm install"
    fi
else
    echo "   ❌ package.json no encontrado"
fi

echo ""
echo "========================================="
echo "📋 INSTRUCCIONES DE USO"
echo "========================================="
echo ""
echo "Para iniciar el servidor:"
echo "  $ python3 backend/servidor_salas.py"
echo ""
echo "Para iniciar el frontend:"
echo "  $ cd frontend && npm run dev"
echo ""
echo "Para probar con cliente terminal:"
echo "  $ python3 cliente/cliente_simple.py"
echo ""
echo "Para probar con bot:"
echo "  $ python3 cliente/bot_jugador.py"
echo ""
echo "========================================="
echo "✨ Verificación completada"
echo "========================================="

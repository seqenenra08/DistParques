@echo off
REM Script para iniciar un cliente de Parqués

echo.
echo ================================================
echo     CLIENTE DE PARQUES
echo ================================================
echo.

cd /d "%~dp0"

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado
    echo Por favor instala Python 3.7 o superior
    pause
    exit /b 1
)

REM Iniciar cliente
echo Conectando al servidor localhost:5555...
echo.

python cliente\cliente_consola.py

pause

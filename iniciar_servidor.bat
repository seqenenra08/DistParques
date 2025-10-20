@echo off
REM Script para iniciar el servidor de Parqués

echo.
echo ================================================
echo     SERVIDOR DE PARQUES - Iniciando...
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

REM Iniciar servidor
echo Iniciando servidor en puerto 5555...
echo.
echo Para detener el servidor, presiona Ctrl+C
echo.

python backend\servidor.py

pause

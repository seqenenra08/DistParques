@echo off
echo ============================================
echo   PRUEBA RAPIDA - INICIO MANUAL
echo ============================================
echo.
echo Este script prueba el nuevo sistema de inicio manual
echo.
echo Se abriran 3 ventanas:
echo   1. Servidor
echo   2. Cliente (Anfitrion)
echo   3. Cliente (Jugador 2)
echo.
echo INSTRUCCIONES:
echo   1. Ingresa nombres en cada cliente
echo   2. El primer cliente es el ANFITRION
echo   3. El anfitrion debe escribir: iniciar
echo   4. La partida comenzara!
echo.
pause

echo.
echo [1/3] Iniciando servidor...
start "Servidor Parques" cmd /k "cd /d %~dp0 && py backend\servidor.py"
timeout /t 2 /nobreak >nul

echo [2/3] Iniciando Cliente 1 (Anfitrion)...
start "Cliente 1 - Anfitrion" cmd /k "cd /d %~dp0 && py cliente\cliente_consola.py"
timeout /t 1 /nobreak >nul

echo [3/3] Iniciando Cliente 2...
start "Cliente 2 - Jugador" cmd /k "cd /d %~dp0 && py cliente\cliente_consola.py"

echo.
echo ============================================
echo   LISTO! Ventanas abiertas
echo ============================================
echo.
echo Recuerda:
echo   - El Cliente 1 es el ANFITRION
echo   - Debe escribir 'iniciar' cuando esten listos
echo.
pause

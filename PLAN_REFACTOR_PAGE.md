# Plan de Refactorización: page.js

## Problema Actual
El `page.js` tiene lógica duplicada/local que intenta manejar el juego en modo test/offline, causando inconsistencias con la lógica del servidor.

## Objetivo
Hacer que `page.js` funcione como `cliente_simple.py` y `bot_jugador.py`:
- **Solo enviar comandos al servidor**
- **Solo recibir y mostrar el estado del servidor**
- **NO calcular movimientos ni validar reglas localmente**

## Cambios Necesarios

### 1. Eliminar Lógica Local
- ❌ Eliminar función `nextTurn()` local
- ❌ Eliminar lógica de movimiento de fichas en modo test
- ❌ Eliminar validaciones locales de reglas
- ❌ Eliminar `isTestMode`

### 2. Simplificar Estados
- Mantener solo estados UI (visuales)
- Confiar en `gameState` del servidor para toda la lógica

### 3. Seguir Protocolo del Servidor
Mensajes que envía el servidor (según `servidor.py`):
- `ASSIGN_COLOR` - Asignación de color al jugador
- `GAME_START` - Partida iniciada
- `SELECCION_TURNO` - Fase de lanzar dados para determinar orden
- `DADO_INICIO_RESULT` - Resultado del dado de inicio
- `TURNO_DETERMINADO` - Orden de turnos determinado
- `DICE_RESULT` - Resultado de lanzamiento de dados
- `FICHAS_INFO` - Información de fichas del jugador
- `MOVE_RESULT` - Resultado de movimiento
- `UPDATE` - Estado actualizado del juego

### 4. Comandos a Enviar
- `JOIN` - Unirse a la partida
- `START` - Iniciar partida
- `ROLL_INICIO` - Lanzar dado para determinar orden
- `ROLL` - Lanzar dados en turno normal
- `MOVE` - Mover ficha con suma de dados
- `MOVE_DIVIDIDO` - Mover fichas con dados divididos
- `SACAR_FICHA_JUEGO` - Sacar ficha del juego (3 pares)
- `GET_FICHAS` - Obtener info de fichas
- `GET_STATE` - Obtener estado actual

### 5. Flujo Simplificado

```
Usuario conecta → JOIN
                ↓
Servidor asigna color → ASSIGN_COLOR
                ↓
Usuario/Host inicia → START
                ↓
Servidor pide dados inicio → SELECCION_TURNO
                ↓
Todos lanzan → ROLL_INICIO
                ↓
Servidor determina orden → TURNO_DETERMINADO
                ↓
Jugador lanza dados → ROLL
                ↓
Servidor responde → DICE_RESULT
                ↓
Jugador mueve ficha → MOVE
                ↓
Servidor valida y ejecuta → MOVE_RESULT + UPDATE
                ↓
(Repetir)
```

## Implementación

### Paso 1: Adaptar useSocket/socketService
Asegurar que el protocolo WebSocket use los mismos nombres de eventos que el TCP del servidor.

### Paso 2: Refactorizar page.js
- Eliminar toda la lógica local de juego
- Mantener solo handlers que envíen eventos al servidor
- Procesar respuestas del servidor y actualizar UI

### Paso 3: Testing
- Probar con cliente_simple.py y page.js juntos
- Probar con bot_jugador.py
- Verificar que todas las reglas funcionen igual

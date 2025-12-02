# Solución: Unificar Lógica del Servidor

## Problema Identificado

Tienes **DOS** servidores con lógicas diferentes:

### 1. `backend/servidor.py` (TCP) ✅ COMPLETO
- Usado por `cliente_simple.py` y `bot_jugador.py`
- Tiene TODA la lógica del juego implementada correctamente:
  - Fase de inicio con 3 intentos para sacar par
  - Lanzamiento de dados para determinar orden inicial
  - Movimientos con suma o divididos
  - Regla de 3 pares consecutivos
  - Captura de fichas
  - Entrada a pasillo final y meta
  - Validaciones completas

### 2. `backend/servidor_salas.py` (WebSocket) ❌ INCOMPLETO
- Usado por el frontend Next.js (`page.js`)
- Tiene sistema de salas y manejo de bots
- PERO le falta la lógica completa de juego de `servidor.py`

## Solución: 2 Opciones

### Opción A: Migrar `page.js` a usar `servidor.py` (TCP)
**Pros:**
- La lógica ya está completa y probada
- No necesitas modificar backend
- Solo adaptas el frontend

**Contras:**
- Pierdes el sistema de salas de `servidor_salas.py`
- WebSocket es mejor para web que TCP

### Opción B: Portar lógica de `servidor.py` a `servidor_salas.py` ⭐ RECOMENDADO
**Pros:**
- Mantienes WebSocket (mejor para web)
- Mantienes sistema de salas
- Unifica toda la lógica en un solo servidor

**Contras:**
- Requiere trabajo de portar código
- Más complejo inicialmente

## Plan de Implementación (Opción B)

### Paso 1: Copiar Handlers de `servidor.py` a `servidor_salas.py`

Copiar estos métodos completos:
```python
- procesar_roll_inicio()
- procesar_roll()
- procesar_move()
- procesar_move_dividido()
- procesar_sacar_ficha_juego()
- procesar_get_fichas()
```

### Paso 2: Adaptar Eventos WebSocket

Cambiar nombres de eventos del frontend para que coincidan con el servidor TCP:

**Frontend (`page.js`):**
```javascript
// ANTES
emit('roll_dice', {})

// DESPUÉS
emit('ROLL', { jugador: myPlayerName })
```

**Servidor (`servidor_salas.py`):**
```python
# Agregar handlers para:
- ROLL_INICIO
- ROLL
- MOVE
- MOVE_DIVIDIDO
- SACAR_FICHA_JUEGO
- GET_FICHAS
```

### Paso 3: Unificar Respuestas

Usar los mismos formatos de respuesta:
```python
# DADO_INICIO_RESULT
# DICE_RESULT
# MOVE_RESULT
# FICHAS_INFO
# etc.
```

### Paso 4: Adaptar `page.js`

Simplificar para que solo:
1. Envíe comandos al servidor
2. Reciba y muestre respuestas
3. NO calcule lógica localmente

## Archivos a Modificar

### Backend
1. `backend/servidor_salas.py` 
   - Agregar métodos de `servidor.py`
   - Adaptar para WebSocket
   - Mantener sistema de salas

### Frontend
1. `frontend/src/app/page.js`
   - Eliminar lógica local
   - Usar eventos del protocolo TCP
   - Simplificar estados

2. `frontend/src/services/socketService.js`
   - Actualizar nombres de eventos
   - Agregar nuevos eventos

## Implementación Paso a Paso

### 1. Crear `servidor_unificado.py`

Combinar lo mejor de ambos:
- Sistema de salas de `servidor_salas.py`
- Lógica completa de `servidor.py`
- WebSocket

### 2. Actualizar Frontend

Adaptar `page.js` para usar el nuevo protocolo unificado.

### 3. Testing

Probar con:
- Multijugador humano vs humano
- Humano vs bots
- Todos los casos edge (3 pares, captura, etc.)

## Siguiente Paso Inmediato

¿Quieres que:
1. **Cree el servidor unificado** (`servidor_unificado.py`)
2. **Actualice `servidor_salas.py`** para agregar la lógica faltante
3. **Simplifique `page.js`** para que solo comunique con el servidor

**Recomendación:** Opción 2 (actualizar `servidor_salas.py`) es la más práctica.

# 🔄 Fix: Cambio Automático de Turno

## 🐛 Problema Encontrado

Cuando un jugador lanzaba los dados y **no tenía fichas movibles**, el turno NO cambiaba automáticamente. El mismo jugador podía seguir lanzando dados indefinidamente.

### Ejemplo del Bug:
```
> lanzar
🎲 Dados: 1 + 2 = 3
   ⚠️ No hay fichas movibles. Turno perdido.

> lanzar  ← ¡No debería poder hacer esto!
🎲 Dados: 1 + 3 = 4
   ⚠️ No hay fichas movibles. Turno perdido.

> lanzar  ← ¡Sigue siendo su turno!
🎲 Dados: 2 + 6 = 8
   ⚠️ No hay fichas movibles. Turno perdido.
```

---

## ✅ Solución Implementada

### Cambios en el Servidor (`servidor.py`):

1. **En `lanzar_dados()`**:
   - Agregado flag `turno_perdido` cuando no hay fichas movibles
   - Agregado flag `cambiar_turno` en la respuesta
   - Se pasa el parámetro `es_par` a `obtener_fichas_movibles()`

2. **En `manejar_roll()`**:
   - Detecta cuando `cambiar_turno == True`
   - Limpia el lanzamiento guardado
   - Llama a `cambiar_turno()` automáticamente
   - Notifica el cambio a todos los jugadores

### Cambios en el Cliente (`cliente_consola.py`):

1. **En procesamiento de `ROLL_RESULT`**:
   - Detecta el flag `turno_perdido`
   - Actualiza `es_mi_turno = False`
   - Limpia `ultimo_dado` y `fichas_movibles`

2. **En procesamiento de `PLAYER_ROLLED`**:
   - Muestra mensaje cuando otro jugador pierde turno

---

## 🎮 Comportamiento Correcto Ahora

### Caso 1: Sin Fichas Movibles
```
> lanzar
🎲 Dados: 1 + 2 = 3
   ⚠️ No hay fichas movibles. Turno perdido.

➡️ Es el turno de Maria

> lanzar  ← Ya no funciona
❌ No es tu turno
```

### Caso 2: Con Fichas Movibles
```
> lanzar
🎲 Dados: 3 + 3 = 6
   ¡PAR! Puedes sacar ficha de la cárcel

📍 Fichas movibles: [0, 1, 2, 3]
   Escribe 'mover <num_ficha>' para mover una ficha

> mover 0
✅ Ficha salió de la cárcel
   🎉 ¡Turno extra!
```

---

## 🔧 Detalles Técnicos

### Flujo del Cambio de Turno:

1. **Jugador lanza dados**
   ```
   Cliente → Servidor: ROLL
   ```

2. **Servidor calcula fichas movibles**
   ```python
   fichas_movibles = jugador.obtener_fichas_movibles(total, es_par)
   turno_perdido = len(fichas_movibles) == 0
   ```

3. **Si no hay fichas movibles**:
   ```python
   if turno_perdido:
       # Limpiar lanzamiento
       del partida.ultimo_lanzamiento[id_jugador]
       
       # Cambiar turno
       servidor.cambiar_turno(id_partida)
       
       # Notificar a todos
       broadcast("TURN_CHANGE", {...})
   ```

4. **Cliente recibe notificación**
   ```python
   if turno_perdido:
       self.es_mi_turno = False
   ```

5. **Mensaje de cambio de turno**
   ```
   Servidor → Todos: TURN_CHANGE
   ```

---

## 📊 Casos de Prueba

### ✅ Test 1: Turno Perdido (Sin Fichas en Juego)
- **Situación**: Todas las fichas en cárcel, se lanza sin par
- **Resultado Esperado**: Turno cambia automáticamente
- **Estado**: ✅ Funciona

### ✅ Test 2: Turno Perdido (Fichas Bloqueadas)
- **Situación**: Fichas en juego pero no pueden moverse con el número
- **Resultado Esperado**: Turno cambia automáticamente
- **Estado**: ✅ Funciona

### ✅ Test 3: Con Fichas Movibles
- **Situación**: Hay al menos una ficha que puede moverse
- **Resultado Esperado**: Jugador puede elegir qué ficha mover
- **Estado**: ✅ Funciona

### ✅ Test 4: Par sin Fichas en Cárcel
- **Situación**: Saca par pero no tiene fichas en cárcel
- **Resultado Esperado**: Si no hay fichas movibles, turno cambia
- **Estado**: ✅ Funciona

---

## 🚀 Cómo Probar

1. **Reinicia el servidor**:
   ```powershell
   py backend\servidor.py
   ```

2. **Conecta 2 jugadores**

3. **Inicia la partida**:
   ```
   > iniciar
   ```

4. **Lanza dados sin par** (para no poder sacar fichas):
   ```
   > lanzar
   ```

5. **Verifica que el turno cambie automáticamente**:
   ```
   ➡️ Es el turno de [otro jugador]
   ```

---

## 📝 Archivos Modificados

- ✏️ `backend/servidor.py`:
  - Método `lanzar_dados()` - Agregado detección de turno perdido
  - Método `manejar_roll()` - Agregado cambio automático de turno

- ✏️ `cliente/cliente_consola.py`:
  - Procesamiento de `ROLL_RESULT` - Actualiza estado del turno
  - Procesamiento de `PLAYER_ROLLED` - Muestra mensaje de turno perdido

---

## 🎯 Impacto

- ✅ Mejora la jugabilidad
- ✅ Previene el abuso de lanzar dados indefinidamente
- ✅ Más justo y realista
- ✅ Alineado con las reglas del juego original

---

**Fecha**: 19 de octubre de 2025  
**Tipo**: Bugfix  
**Prioridad**: Alta  
**Estado**: ✅ Resuelto

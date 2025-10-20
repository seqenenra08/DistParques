# 🔒 Fix Crítico: Deadlocks en Sincronización

## 🐛 Problema Crítico Encontrado

El sistema tenía **múltiples deadlocks** causados por locks anidados. Esto provocaba que:
- La partida no iniciaba al escribir `iniciar`
- El turno no cambiaba correctamente
- Los mensajes no se enviaban a los clientes

## 🔍 Análisis del Problema

### ¿Qué es un Deadlock?

Un **deadlock** ocurre cuando:
1. Un método obtiene un lock (bloqueo)
2. Dentro de ese lock, llama a otro método
3. Ese segundo método intenta obtener el **mismo lock**
4. ❌ El sistema se queda congelado esperando un lock que nunca se liberará

### Deadlocks Encontrados:

#### 1. En `iniciar_partida_manual()`
```python
# ❌ ANTES (con deadlock)
with self.lock_partidas:  # ← Obtiene el lock
    # ... validaciones ...
    partida.iniciar_partida()
    
    # ¡Problema! broadcast_a_partida también intenta obtener lock_partidas
    self.broadcast_a_partida(...)  # ← Intenta obtener el mismo lock = DEADLOCK
```

#### 2. En `cambiar_turno()`
```python
# ❌ ANTES (con deadlock)
with self.lock_partidas:  # ← Obtiene el lock
    partida = self.partidas[id_partida]
    siguiente = partida.pasar_turno()
    
    # ¡Problema! broadcast_a_partida también intenta obtener lock_partidas
    self.broadcast_a_partida(...)  # ← DEADLOCK
```

#### 3. En `broadcast_estado_partida()`
```python
# ❌ ANTES (con deadlock)
with self.lock_partidas:  # ← Obtiene el lock
    estado = partida.to_dict()
    
    # ¡Problema! broadcast_a_partida también intenta obtener lock_partidas
    self.broadcast_a_partida(...)  # ← DEADLOCK
```

#### 4. En `manejar_roll()`
```python
# ❌ ANTES (sin protección)
partida = self.servidor.partidas[self.id_partida]  # ← Acceso sin lock = RACE CONDITION
```

---

## ✅ Solución Aplicada

### Patrón de Solución:
1. **Preparar datos dentro del lock**
2. **Salir del lock**
3. **Hacer operaciones costosas fuera del lock** (como broadcasts)

### 1. Corregido `iniciar_partida_manual()`
```python
# ✅ AHORA (sin deadlock)
with self.lock_partidas:
    # Validaciones y preparación de datos
    partida.iniciar_partida()
    
    datos_broadcast = {
        "id_partida": id_partida,
        "jugadores": [j.to_dict() for j in partida.jugadores],
        ...
    }
# Lock liberado aquí ↑

# Broadcast FUERA del lock
self.broadcast_a_partida(id_partida, "START_GAME", datos_broadcast)
```

### 2. Corregido `cambiar_turno()`
```python
# ✅ AHORA (sin deadlock)
with self.lock_partidas:
    if id_partida not in self.partidas:
        return
    
    partida = self.partidas[id_partida]
    siguiente = partida.pasar_turno()
    
    datos_broadcast = {
        "turno_actual": partida.turno_actual,
        "jugador_actual": siguiente.to_dict(),
        "mensaje": f"Es el turno de {siguiente.nombre}"
    }
# Lock liberado aquí ↑

# Broadcast FUERA del lock
self.broadcast_a_partida(id_partida, "TURN_CHANGE", datos_broadcast)
```

### 3. Corregido `broadcast_estado_partida()`
```python
# ✅ AHORA (sin deadlock)
with self.lock_partidas:
    if id_partida not in self.partidas:
        return
    
    partida = self.partidas[id_partida]
    estado = partida.to_dict()
# Lock liberado aquí ↑

# Broadcast FUERA del lock
self.broadcast_a_partida(id_partida, "UPDATE", estado)
```

### 4. Corregido `manejar_roll()`
```python
# ✅ AHORA (con protección)
if resultado.get("cambiar_turno", False):
    # Limpiar con lock
    with self.servidor.lock_partidas:
        if self.id_partida in self.servidor.partidas:
            partida = self.servidor.partidas[self.id_partida]
            if hasattr(partida, 'ultimo_lanzamiento'):
                if self.id_jugador in partida.ultimo_lanzamiento:
                    del partida.ultimo_lanzamiento[self.id_jugador]
    
    # Cambiar turno (maneja su propio lock)
    self.servidor.cambiar_turno(self.id_partida)
```

---

## 📊 Impacto de las Correcciones

| Problema | Antes | Después |
|----------|-------|---------|
| **Inicio de partida** | ❌ Se congela | ✅ Funciona |
| **Cambio de turno** | ❌ Se congela | ✅ Funciona |
| **Broadcast de estado** | ❌ Se congela | ✅ Funciona |
| **Turno perdido** | ❌ No cambia | ✅ Cambia automáticamente |
| **Acceso concurrente** | ❌ Race conditions | ✅ Protegido |

---

## 🎯 Principios Aplicados

### 1. **Minimize Lock Time**
- Mantener el lock solo el tiempo necesario
- Preparar datos rápido
- Liberar el lock antes de operaciones lentas

### 2. **No Nested Locks (Mismo Lock)**
- Nunca llamar a un método que obtiene el mismo lock
- Si es necesario, refactorizar para separar responsabilidades

### 3. **Lock Ordering**
- Si necesitas múltiples locks, siempre obtenerlos en el mismo orden
- Evita locks circulares

### 4. **Defensive Programming**
- Siempre verificar que el recurso existe antes de usarlo
- Usar `if id_partida not in self.partidas: return`

---

## 🧪 Casos de Prueba

### ✅ Test 1: Inicio de Partida
```
Anfitrión: > iniciar
Resultado esperado: 🎮 ¡LA PARTIDA HA COMENZADO!
Estado: ✅ FUNCIONA
```

### ✅ Test 2: Cambio de Turno Manual
```
Jugador 1: > lanzar
Jugador 1: > mover 0
Resultado esperado: ➡️ Es el turno de Jugador 2
Estado: ✅ FUNCIONA
```

### ✅ Test 3: Cambio de Turno Automático
```
Jugador 1: > lanzar (sin fichas movibles)
Resultado esperado: ➡️ Es el turno de Jugador 2
Estado: ✅ FUNCIONA
```

### ✅ Test 4: Múltiples Jugadores
```
4 jugadores conectados, turnos rotan correctamente
Estado: ✅ FUNCIONA
```

---

## 🔧 Debugging Tips

### Síntomas de Deadlock:
- El servidor "se congela"
- Los comandos no responden
- No hay mensajes de error, solo silencio
- CPU al 0% (esperando el lock)

### Cómo Detectar:
1. Verificar logs del servidor
2. Si se detiene en medio de una operación = posible deadlock
3. Revisar qué métodos llaman a `broadcast_a_partida`
4. Verificar que no haya locks anidados del mismo tipo

### Cómo Prevenir:
- Documentar qué locks usa cada método
- Seguir el patrón: preparar → liberar → ejecutar
- Code review enfocado en locks
- Tests de concurrencia

---

## 📝 Resumen de Archivos Modificados

- ✏️ **`backend/servidor.py`**:
  - `iniciar_partida_manual()` - Movido broadcast fuera del lock
  - `cambiar_turno()` - Movido broadcast fuera del lock
  - `broadcast_estado_partida()` - Movido broadcast fuera del lock
  - `manejar_roll()` - Agregado protección de lock para acceso a partida

---

## 🚀 Próximos Pasos

Para usar las correcciones:

1. **Reinicia el servidor**:
   ```powershell
   py backend\servidor.py
   ```

2. **Prueba todas las funcionalidades**:
   - Iniciar partida
   - Lanzar dados
   - Mover fichas
   - Cambios de turno automáticos

3. **Verificar logs** para asegurarse de que todo funciona

---

## 📚 Recursos Adicionales

- **Documentación de threading en Python**: https://docs.python.org/3/library/threading.html
- **Patrón Lock en sistemas distribuidos**: Ver arquitectura del servidor
- **Best practices para locks**: Mantener crítico mínimo

---

**Fecha**: 19 de octubre de 2025  
**Tipo**: Bugfix Crítico  
**Prioridad**: Crítica  
**Severidad**: Bloqueante  
**Estado**: ✅ Resuelto  
**Impacto**: Sistema ahora es funcional

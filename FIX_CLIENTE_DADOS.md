# ✅ CORRECCIÓN: Cliente actualizado para soportar dados iniciales

## 🐛 Problema Identificado

El cliente (`cliente_simple.py`) no estaba manejando la nueva funcionalidad de selección de turno con dados. Cuando el usuario escribía `lanzar` después de `iniciar`, el comando enviaba `ROLL` en lugar de `ROLL_INICIO`, causando que no funcionara correctamente.

## 🔧 Cambios Realizados

### `cliente/cliente_simple.py`

1. **Nuevos atributos:**
   - `esperando_dados_inicio`: Indica si está en fase de selección
   - `ya_lance_inicio`: Evita que el jugador lance múltiples veces

2. **Nuevos manejadores de mensajes:**
   - `SELECCION_TURNO`: Notifica que debe lanzar para selección
   - `DADO_INICIO_RESULT`: Confirma el valor lanzado
   - `DADO_INICIO`: Muestra valores de otros jugadores
   - `TURNO_DETERMINADO`: Muestra resultados y ganador

3. **Lógica mejorada del comando `lanzar`:**
   ```python
   if self.esperando_dados_inicio:
       # Envía ROLL_INICIO durante la selección
       self.enviar({"tipo": "ROLL_INICIO"})
   else:
       # Envía ROLL durante el juego normal
       self.enviar({"tipo": "ROLL"})
   ```

## 🎮 Flujo de Uso

### Terminal 1 - Servidor:
```bash
cd backend
python3 servidor.py
```

### Terminales 2-5 - Clientes:
```bash
python3 cliente/cliente_simple.py
# Ingresa tu nombre: juan, david, mejia, alvarez
```

### Secuencia de comandos:

1. **Todos los jugadores:** Esperan a que se conecten
   
2. **Cualquier jugador:** `iniciar`
   ```
   ============================================================
   🎮 Partida iniciada. Todos deben lanzar el dado para determinar el orden
   ============================================================
   
   🎲 Todos los jugadores deben lanzar el dado. El mayor número comienza.
   💡 Escribe 'lanzar' para lanzar tu dado
   ```

3. **Cada jugador:** `lanzar`
   ```
   🎲 Tu resultado: 5
      Sacaste 5. Esperando a los demás jugadores...
   
   🎲 david (azul) sacó: 3
   🎲 mejia (amarillo) sacó: 6
   🎲 alvarez (verde) sacó: 2
   ```

4. **Sistema muestra resultados:**
   ```
   ============================================================
   🏆 RESULTADOS DE LA SELECCIÓN
   ============================================================
   
   👑 1. mejia (amarillo): 6
      2. juan (rojo): 5
      3. david (azul): 3
      4. alvarez (verde): 2
   
   🎯 ¡mejia tiene el mayor número y comienza!
   ============================================================
   ```

5. **El jugador ganador:** `lanzar` (ahora es el turno real)
   ```
   🎲 Dados: (4, 5) → Suma: 9
   ```

## ✨ Características Implementadas

✅ Detección automática de fase de selección
✅ Envío correcto de `ROLL_INICIO` vs `ROLL`
✅ Visualización de resultados de todos los jugadores
✅ Prevención de lanzamientos múltiples
✅ Tabla ordenada de resultados
✅ Notificación clara del ganador
✅ Transición suave al juego normal

## 🧪 Prueba Rápida

Para probar la funcionalidad completa:

```bash
# Terminal 1
cd backend && python3 servidor.py

# Terminales 2-5
python3 cliente/cliente_simple.py

# En cada cliente:
# 1. Ingresa nombre
# 2. Cuando todos estén conectados, uno escribe: iniciar
# 3. Todos escriben: lanzar
# 4. Ver resultados y quién comienza
# 5. El ganador escribe: lanzar (para su primer turno real)
```

## 📋 Comandos Disponibles

Durante la fase de selección:
- `lanzar` - Lanza un dado para la selección

Durante el juego:
- `lanzar` - Lanza dos dados para tu turno
- `mover N` - Mueve la ficha N
- `dividir N1 D1 N2 D2` - Divide los dados entre dos fichas
- `fichas` - Ver estado de tus fichas
- `jugadores` - Ver todos los jugadores

## 🎯 Resultado Esperado

Ahora cuando escribas `lanzar` después de `iniciar`, el sistema:
1. Enviará `ROLL_INICIO` correctamente
2. Mostrará tu resultado
3. Mostrará los resultados de los demás
4. Determinará y anunciará el ganador
5. Solo el ganador podrá jugar primero
6. Los demás estarán bloqueados hasta su turno

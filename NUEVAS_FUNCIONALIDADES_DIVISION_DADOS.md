# Nuevas Funcionalidades Implementadas

## 📋 Resumen

Se implementaron dos funcionalidades importantes solicitadas:

1. **División de dados**: Poder usar cada dado por separado para mover diferentes fichas
2. **Salto automático de turno**: Si no hay movimientos válidos posibles, el turno se salta automáticamente

## ✨ Funcionalidad 1: División de Dados

### Descripción
Cuando un jugador tiene **2 o más fichas fuera de la cárcel** y los dados son **diferentes** (no par), puede dividir los dados para:
- Usar un dado para mover una ficha
- Usar el otro dado para mover otra ficha diferente

### Reglas Implementadas
✅ Solo se puede dividir si los dados son diferentes (ej: 3-5, no 4-4)
✅ Solo se puede dividir si hay al menos 2 fichas fuera de la cárcel
✅ **No se puede mover la misma ficha dos veces** en un turno
✅ Cada dado debe usarse exactamente una vez
✅ Si se divide, cada valor debe corresponder a un dado individual

### Ejemplo de Uso

```python
# Escenario: Fichas 0 y 1 en el tablero, dados (3, 5)

# Opción 1: Usar suma completa con una ficha
movimientos = [{"id_ficha": 0, "valor_dado": 8}]  # 3 + 5 = 8

# Opción 2: Dividir dados entre dos fichas
movimientos = [
    {"id_ficha": 0, "valor_dado": 3},  # Ficha 0 se mueve 3
    {"id_ficha": 1, "valor_dado": 5}   # Ficha 1 se mueve 5
]

# ❌ INVÁLIDO: Mover la misma ficha dos veces
movimientos = [
    {"id_ficha": 0, "valor_dado": 3},
    {"id_ficha": 0, "valor_dado": 5}  # Error!
]
```

### Respuesta del Servidor

Cuando se lanzan dados, el servidor ahora incluye:

```json
{
  "tipo": "DICE_RESULT",
  "dados": [3, 5],
  "suma": 8,
  "puede_dividir_dados": true,
  "opciones_division": [
    {
      "tipo": "suma",
      "valor": 8,
      "fichas": [0, 1]
    },
    {
      "tipo": "dado1",
      "valor": 3,
      "fichas": [0, 1]
    },
    {
      "tipo": "dado2",
      "valor": 5,
      "fichas": [0, 1]
    }
  ],
  "fichas_movibles": [0, 1],
  "mensaje": "Puedes dividir los dados entre diferentes fichas"
}
```

## ✨ Funcionalidad 2: Salto Automático de Turno

### Descripción
Si un jugador **no tiene ningún movimiento válido** con los dados que sacó, el turno se **salta automáticamente** sin requerir acción del jugador.

### Casos que Activan el Salto Automático

1. **Ficha cerca de la meta con dados altos**
   - Ejemplo: Ficha a 2 casillas de meta, saca 5-6
   - Ningún dado permite llegar exacto → Turno saltado

2. **Todas las fichas bloqueadas**
   - Todas las fichas en cárcel sin par
   - Todas las fichas en meta
   - Ninguna ficha puede moverse con los valores

3. **Par pero con ficha en cárcel que no puede salir**
   - Si saca par pero ya tiene fichas en cárcel que deben salir

### Comportamiento

#### Sin Par
```
🎲 Dados: (5, 6) - Sin movimientos válidos
⏭️  Turno saltado automáticamente
→ Pasa al siguiente jugador
```

#### Con Par
```
🎲 Dados: (5, 5) - Sin movimientos válidos
✨ Sacaste par - Puedes lanzar de nuevo
→ NO se salta el turno, puede lanzar otra vez
```

### Respuesta del Servidor

Cuando no hay movimientos válidos:

```json
{
  "tipo": "DICE_RESULT",
  "dados": [5, 6],
  "suma": 11,
  "es_par": false,
  "sin_movimientos": true,
  "cambio_turno": true,
  "mensaje": "Sin movimientos válidos. No hay fichas disponibles para mover - Turno saltado"
}
```

## 🔧 Archivos Modificados

### 1. `/backend/models/partida.py`

#### Método Nuevo: `tiene_movimientos_validos()`
```python
def tiene_movimientos_validos(self, jugador: Jugador, dados: tuple) -> Dict:
    """Verifica si el jugador tiene algún movimiento válido con los dados."""
```

**Retorna:**
- `tiene_movimientos`: bool - Si hay movimientos posibles
- `fichas_movibles`: List[int] - IDs de fichas que pueden moverse
- `puede_dividir`: bool - Si puede dividir los dados
- `opciones_division`: List - Opciones detalladas para dividir

#### Mejoras en: `procesar_turno_dividido()`
- ✅ Validación de que no se use la misma ficha dos veces
- ✅ Validación de que cada dado se use exactamente una vez
- ✅ Mejor manejo de errores con mensajes claros

### 2. `/backend/servidor.py`

#### Mejoras en: `procesar_roll()`
- ✅ Llama a `tiene_movimientos_validos()` después de lanzar dados
- ✅ Salta turno automáticamente si no hay movimientos
- ✅ Retorna información sobre división de dados
- ✅ Indica qué fichas pueden moverse

## 🧪 Tests Creados

### `test_dividir_dados.py`
- ✅ Test 1: Dividir dados entre dos fichas diferentes
- ✅ Test 2: No permitir mover la misma ficha dos veces
- ✅ Test 3: Saltar turno sin movimientos (ajustado)
- ✅ Test 4: Par de dados no permite división

### `test_saltar_turno.py`
- ✅ Test 1: Escenario real - Ficha a 3 de meta, saca 6
- ✅ Test 2: Integración servidor detecta y salta turno

## 📊 Resultados de Tests

```
======================================================================
RESUMEN DE TESTS
======================================================================
Test 1 (Dividir dados): ✅ EXITOSO
Test 2 (No repetir ficha): ✅ EXITOSO
Test 3 (Saltar turno sin movimientos): ✅ EXITOSO
Test 4 (Par no divide): ✅ EXITOSO

✅ TODOS LOS TESTS PASARON
======================================================================
```

## 🎯 Casos de Uso Detallados

### Caso 1: División de Dados
```
Jugador tiene fichas 0 y 1 en juego
🎲 Dados: (3, 5)

Opción A: Mover ficha 0 con suma (8 casillas)
Opción B: Dividir:
  - Ficha 0 → 3 casillas
  - Ficha 1 → 5 casillas
```

### Caso 2: Salto Automático
```
Jugador tiene 1 ficha a 3 casillas de meta
🎲 Dados: (5, 6) suma = 11

❌ Con 5: 3 + 5 = 8 (se pasa)
❌ Con 6: 3 + 6 = 9 (se pasa)
❌ Con 11: 3 + 11 = 14 (se pasa)

⏭️  Turno saltado automáticamente
```

### Caso 3: Salto con Par
```
Jugador tiene 1 ficha a 2 casillas de meta
🎲 Dados: (6, 6) suma = 12

❌ No puede mover pero sacó PAR
✨ Puede lanzar de nuevo
```

## 🚀 Cómo Usar en el Cliente

### Para Frontend/Cliente

```javascript
// 1. Lanzar dados
socket.send({
  tipo: "ROLL"
});

// 2. Recibir respuesta
{
  tipo: "DICE_RESULT",
  dados: [3, 5],
  puede_dividir_dados: true,
  fichas_movibles: [0, 1],
  sin_movimientos: false
}

// 3a. Si puede dividir, mostrar opciones al jugador
if (respuesta.puede_dividir_dados) {
  // Mostrar UI para seleccionar:
  // - Mover 1 ficha con suma
  // - Mover 2 fichas diferentes con dados separados
}

// 3b. Si sin_movimientos es true, no hacer nada
if (respuesta.sin_movimientos) {
  // Mostrar mensaje: "Turno saltado automáticamente"
  // El servidor ya cambió el turno
}

// 4. Enviar movimiento dividido
socket.send({
  tipo: "MOVE_DIVIDIDO",
  dados: [3, 5],
  movimientos: [
    {id_ficha: 0, valor_dado: 3},
    {id_ficha: 1, valor_dado: 5}
  ]
});
```

## 📝 Notas Importantes

1. **División solo con dados diferentes**: No se puede dividir un par (4-4)
2. **Cada ficha una vez**: Una ficha solo puede moverse una vez por turno
3. **Salto automático transparente**: El jugador no necesita hacer nada
4. **Par permite relanzar**: Incluso sin movimientos válidos, si saca par puede lanzar de nuevo
5. **Compatible con modo clásico**: El modo de suma completa sigue funcionando

## ✅ Estado

**FUNCIONALIDADES IMPLEMENTADAS Y VERIFICADAS** ✅

Fecha: 2 de diciembre de 2025

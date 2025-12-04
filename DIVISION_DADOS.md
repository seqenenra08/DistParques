# División de Dados - Funcionalidad Implementada

## 📋 Descripción

Ahora puedes **dividir los dados entre diferentes fichas** en lugar de usar la suma completa en una sola ficha.

## 🎲 Ejemplo

Si sacas **2 y 4**:
- **Opción 1 (Clásica)**: Mover una ficha **6 casillas** (suma completa)
- **Opción 2 (División)**: Mover una ficha **2 casillas** y otra ficha **4 casillas**

## ✅ Reglas de División

1. ✔️ Puedes usar cada dado en una ficha diferente
2. ✔️ Cada dado debe usarse exactamente una vez
3. ✔️ **NO puedes mover la misma ficha dos veces** en un turno
4. ✔️ Solo puedes dividir si **NO sacaste par** (con par debes usar la suma)
5. ✔️ Solo puedes dividir si **NO todas tus fichas están en la cárcel**

## 🚫 Restricciones

- ❌ No puedes dividir pares (ej: 3-3 debe usarse como 6)
- ❌ No puedes mover la misma ficha con ambos dados
- ❌ Los valores deben corresponder exactamente a los dados lanzados

## 📡 Protocolo del Servidor

### Respuesta al lanzar dados

Cuando lanzas los dados, el servidor ahora envía:

```json
{
  "tipo": "DICE_RESULT",
  "dados": [2, 4],
  "suma": 6,
  "es_par": false,
  "puede_dividir_dados": true,
  "opciones_division": [
    {
      "tipo": "suma",
      "valor": 6,
      "fichas": [0, 1, 2]
    },
    {
      "tipo": "dado1",
      "valor": 2,
      "fichas": [0, 1, 2, 3]
    },
    {
      "tipo": "dado2",
      "valor": 4,
      "fichas": [0, 1, 2]
    }
  ],
  "fichas_movibles": [0, 1, 2, 3]
}
```

### Enviar movimiento dividido

Para usar la división de dados, envía un mensaje `MOVE_DIVIDIDO`:

```json
{
  "tipo": "MOVE_DIVIDIDO",
  "dados": [2, 4],
  "movimientos": [
    {
      "id_ficha": 0,
      "valor_dado": 2
    },
    {
      "id_ficha": 1,
      "valor_dado": 4
    }
  ]
}
```

### Respuesta del servidor

```json
{
  "tipo": "MOVE_RESULT",
  "exito": true,
  "dados": [2, 4],
  "es_par": false,
  "movimientos_realizados": [
    {
      "id_ficha": 0,
      "casillas": 2,
      "capturadas": 0
    },
    {
      "id_ficha": 1,
      "casillas": 4,
      "capturadas": 1
    }
  ],
  "fichas_capturadas": [...],
  "cambio_turno": true
}
```

## 🎮 Implementación en el Frontend

El frontend debe:

1. **Detectar** cuando `puede_dividir_dados` es `true`
2. **Mostrar opciones** al usuario:
   - Usar suma completa en una ficha
   - Dividir dados entre dos fichas
3. **Validar** que el usuario no seleccione la misma ficha dos veces
4. **Enviar** mensaje `MOVE_DIVIDIDO` con los movimientos

## 🤖 Comportamiento de los Bots

Los bots **actualmente usan solo la suma completa**. Se puede mejorar para que usen división en casos estratégicos.

## 💡 Ventajas Estratégicas

- 🎯 **Capturas múltiples**: Puedes capturar en dos posiciones diferentes
- 🛡️ **Protección**: Avanzar una ficha importante y mover otra a seguro
- 🏃 **Velocidad**: Sacar fichas de zonas peligrosas más rápido
- 📍 **Posicionamiento**: Mejor control del tablero

## 📝 Ejemplo de Uso

```javascript
// Frontend detecta que puede dividir
if (diceResult.puede_dividir_dados) {
  // Mostrar UI para dividir dados
  showSplitDiceOptions(diceResult.opciones_division);
}

// Usuario selecciona dividir: ficha 0 con dado 2, ficha 1 con dado 4
const moveDividido = {
  tipo: "MOVE_DIVIDIDO",
  dados: [2, 4],
  movimientos: [
    { id_ficha: 0, valor_dado: 2 },
    { id_ficha: 1, valor_dado: 4 }
  ]
};

socket.send(JSON.stringify(moveDividido));
```

## ✅ Estado Actual

- ✅ Backend implementado en `servidor_salas.py`
- ✅ Lógica de validación en `partida.py`
- ✅ Información de división incluida en respuesta de dados
- ✅ Endpoint `MOVE_DIVIDIDO` funcionando
- ⏳ Frontend pendiente de implementar UI para división

---

**Fecha de implementación**: 4 de diciembre de 2025

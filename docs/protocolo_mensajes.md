# 📡 Protocolo de Comunicación Cliente-Servidor

## Diagrama de flujo de mensajes JSON

Este documento describe el protocolo de comunicación entre el cliente y el servidor para el juego de Parqués.

---

## 🔹 Tipos de Mensajes

### 1. `JOIN` - Unirse a una partida

**Dirección:** Cliente → Servidor

**Descripción:** El cliente envía su nombre para unirse a una partida.

**Mensaje del Cliente:**
```json
{
  "type": "JOIN",
  "data": {
    "nombre": "Juan",
    "id_partida": "partida_123"  // Opcional: si quiere unirse a una partida específica
  }
}
```

**Respuesta del Servidor (Éxito):**
```json
{
  "type": "JOIN_SUCCESS",
  "data": {
    "id_jugador": "abc123",
    "id_partida": "partida_123",
    "mensaje": "Te has unido a la partida",
    "es_anfitrion": true  // true si es el primer jugador (anfitrión)
  }
}
```

**Respuesta del Servidor (Error):**
```json
{
  "type": "JOIN_ERROR",
  "data": {
    "mensaje": "La partida está llena",
    "codigo_error": "PARTIDA_LLENA"
  }
}
```

---

### 2. `ASSIGN_COLOR` - Asignación de color

**Dirección:** Servidor → Cliente

**Descripción:** El servidor asigna un color al jugador después de unirse.

**Mensaje del Servidor:**
```json
{
  "type": "ASSIGN_COLOR",
  "data": {
    "id_jugador": "abc123",
    "color": "rojo",
    "posicion_orden": 1,
    "jugadores_en_partida": 2,
    "max_jugadores": 4
  }
}
```

---

### 3. `START` - Solicitar inicio de partida (NUEVO)

**Dirección:** Cliente → Servidor

**Descripción:** El cliente anfitrión solicita iniciar la partida manualmente.

**Mensaje del Cliente:**
```json
{
  "type": "START",
  "data": {}
}
```

**Respuesta (implícita):** 
- Si es exitoso: Se envía `START_GAME` a todos los clientes
- Si hay error: Se envía `START_ERROR` al cliente que lo solicitó

**Respuesta del Servidor (Error):**
```json
{
  "type": "START_ERROR",
  "data": {
    "mensaje": "Solo el anfitrión puede iniciar la partida",
    "codigo_error": "NO_ES_ANFITRION"
  }
}
```

**Códigos de Error:**
- `PARTIDA_NO_ENCONTRADA`: La partida no existe
- `NO_ES_ANFITRION`: El jugador no es el anfitrión
- `PARTIDA_YA_INICIADA`: La partida ya está en curso
- `JUGADORES_INSUFICIENTES`: No hay suficientes jugadores (mínimo 2)
- `ERROR_INICIAR`: Error interno al iniciar

---

### 4. `START_GAME` - Inicio de partida

**Dirección:** Servidor → Todos los Clientes

**Descripción:** La partida ha comenzado (enviado después de que el anfitrión ejecuta START).

**Mensaje del Servidor:**
```json
{
  "type": "START_GAME",
  "data": {
    "id_partida": "partida_123",
    "jugadores": [
      {
        "id": "abc123",
        "nombre": "Juan",
        "color": "rojo",
        "posicion_orden": 1
      },
      {
        "id": "def456",
        "nombre": "María",
        "color": "azul",
        "posicion_orden": 2
      }
    ],
    "turno_actual": 0,
    "jugador_actual": {
      "id": "abc123",
      "nombre": "Juan",
      "color": "rojo"
    },
    "mensaje": "¡La partida ha comenzado!"
  }
}
```

---

### 5. `ROLL` - Lanzar dados

**Dirección:** Cliente → Servidor

**Descripción:** El jugador solicita lanzar el dado.

**Mensaje del Cliente:**
```json
{
  "type": "ROLL",
  "data": {
    "id_jugador": "abc123",
    "id_partida": "partida_123"
  }
}
```

**Respuesta del Servidor:**
```json
{
  "type": "ROLL_RESULT",
  "data": {
    "id_jugador": "abc123",
    "resultado": 5,
    "puede_sacar": true,
    "fichas_movibles": [0, 1, 2, 3],  // IDs de fichas que pueden moverse
    "mensaje": "Has sacado un 5. Puedes sacar una ficha de la cárcel."
  }
}
```

---

### 5. `MOVE` - Mover ficha

**Dirección:** Cliente → Servidor

**Descripción:** El jugador solicita mover una ficha específica.

**Mensaje del Cliente:**
```json
{
  "type": "MOVE",
  "data": {
    "id_jugador": "abc123",
    "id_partida": "partida_123",
    "id_ficha": 0,
    "pasos": 5
  }
}
```

**Respuesta del Servidor (Éxito):**
```json
{
  "type": "MOVE_SUCCESS",
  "data": {
    "id_jugador": "abc123",
    "id_ficha": 0,
    "posicion_anterior": -1,
    "posicion_nueva": 5,
    "ficha_comida": null,  // o datos de la ficha comida si aplica
    "turno_extra": true,
    "llego_a_meta": false,
    "mensaje": "Ficha salió de la cárcel"
  }
}
```

**Respuesta del Servidor (Error):**
```json
{
  "type": "MOVE_ERROR",
  "data": {
    "mensaje": "No es tu turno",
    "codigo_error": "TURNO_INVALIDO"
  }
}
```

---

### 6. `UPDATE` - Actualización del estado del tablero

**Dirección:** Servidor → Todos los Clientes

**Descripción:** El servidor envía el estado actualizado del tablero después de cada movimiento.

**Mensaje del Servidor:**
```json
{
  "type": "UPDATE",
  "data": {
    "id_partida": "partida_123",
    "turno_actual": 0,
    "jugador_actual": {
      "id": "abc123",
      "nombre": "Juan",
      "color": "rojo"
    },
    "ultimo_dado": 5,
    "jugadores": [
      {
        "id": "abc123",
        "nombre": "Juan",
        "color": "rojo",
        "turno": true,
        "fichas": [
          {
            "id": 0,
            "posicion": 5,
            "estado": "activa"
          },
          {
            "id": 1,
            "posicion": -1,
            "estado": "carcel"
          },
          {
            "id": 2,
            "posicion": -1,
            "estado": "carcel"
          },
          {
            "id": 3,
            "posicion": -1,
            "estado": "carcel"
          }
        ],
        "fichas_en_meta": 0
      },
      {
        "id": "def456",
        "nombre": "María",
        "color": "azul",
        "turno": false,
        "fichas": [
          {
            "id": 0,
            "posicion": -1,
            "estado": "carcel"
          },
          {
            "id": 1,
            "posicion": -1,
            "estado": "carcel"
          },
          {
            "id": 2,
            "posicion": -1,
            "estado": "carcel"
          },
          {
            "id": 3,
            "posicion": -1,
            "estado": "carcel"
          }
        ],
        "fichas_en_meta": 0
      }
    ],
    "evento": "FICHA_MOVIDA"
  }
}
```

---

### 7. `EATEN` - Ficha comida

**Dirección:** Servidor → Todos los Clientes

**Descripción:** Una ficha ha sido comida por otra.

**Mensaje del Servidor:**
```json
{
  "type": "EATEN",
  "data": {
    "id_jugador_comedor": "abc123",
    "nombre_comedor": "Juan",
    "color_comedor": "rojo",
    "id_ficha_comida": 0,
    "id_jugador_comido": "def456",
    "nombre_comido": "María",
    "color_comido": "azul",
    "posicion": 22,
    "mensaje": "Juan ha comido una ficha de María"
  }
}
```

---

### 8. `TURN_CHANGE` - Cambio de turno

**Dirección:** Servidor → Todos los Clientes

**Descripción:** El turno ha pasado al siguiente jugador.

**Mensaje del Servidor:**
```json
{
  "type": "TURN_CHANGE",
  "data": {
    "turno_actual": 1,
    "jugador_actual": {
      "id": "def456",
      "nombre": "María",
      "color": "azul"
    },
    "mensaje": "Es el turno de María"
  }
}
```

---

### 9. `WIN` - Jugador ganador

**Dirección:** Servidor → Todos los Clientes

**Descripción:** Un jugador ha ganado la partida.

**Mensaje del Servidor:**
```json
{
  "type": "WIN",
  "data": {
    "id_partida": "partida_123",
    "ganador": {
      "id": "abc123",
      "nombre": "Juan",
      "color": "rojo",
      "fichas_en_meta": 4
    },
    "duracion_partida": "00:15:32",
    "fecha_fin": "2025-10-19T14:30:00",
    "mensaje": "¡Juan ha ganado la partida!"
  }
}
```

---

### 10. `PLAYER_DISCONNECT` - Desconexión de jugador

**Dirección:** Servidor → Todos los Clientes

**Descripción:** Un jugador se ha desconectado.

**Mensaje del Servidor:**
```json
{
  "type": "PLAYER_DISCONNECT",
  "data": {
    "id_jugador": "def456",
    "nombre": "María",
    "color": "azul",
    "mensaje": "María se ha desconectado"
  }
}
```

---

### 11. `ERROR` - Error general

**Dirección:** Servidor → Cliente

**Descripción:** Ha ocurrido un error.

**Mensaje del Servidor:**
```json
{
  "type": "ERROR",
  "data": {
    "codigo_error": "MOVIMIENTO_INVALIDO",
    "mensaje": "No puedes mover esa ficha",
    "detalles": "La ficha está en la cárcel y necesitas un 5 o un número par para sacarla"
  }
}
```

---

## 🔄 Flujo Típico de una Partida

```
1. Cliente A → JOIN → Servidor
2. Servidor → ASSIGN_COLOR → Cliente A (color: rojo)

3. Cliente B → JOIN → Servidor
4. Servidor → ASSIGN_COLOR → Cliente B (color: azul)

5. Servidor → START_GAME → Todos los clientes

6. Cliente A → ROLL → Servidor
7. Servidor → ROLL_RESULT → Cliente A (resultado: 5)
8. Cliente A → MOVE → Servidor (ficha: 0)
9. Servidor → MOVE_SUCCESS → Cliente A
10. Servidor → UPDATE → Todos los clientes

11. Cliente B → ROLL → Servidor
12. Servidor → ROLL_RESULT → Cliente B (resultado: 3)
13. Servidor → TURN_CHANGE → Todos los clientes (turno de A)

... (continúa el juego) ...

N. Servidor → WIN → Todos los clientes (ganador: Juan)
```

---

## 📋 Códigos de Error

| Código | Descripción |
|--------|-------------|
| `PARTIDA_LLENA` | La partida ya tiene el máximo de jugadores |
| `PARTIDA_NO_ENCONTRADA` | La partida solicitada no existe |
| `TURNO_INVALIDO` | No es el turno del jugador |
| `MOVIMIENTO_INVALIDO` | El movimiento solicitado no es válido |
| `FICHA_NO_ENCONTRADA` | La ficha especificada no existe |
| `DADO_NO_LANZADO` | Debes lanzar el dado antes de mover |
| `JUGADOR_NO_ENCONTRADO` | El jugador no existe en la partida |
| `PARTIDA_YA_INICIADA` | La partida ya ha comenzado |
| `PARTIDA_FINALIZADA` | La partida ya ha terminado |

---

## 🎯 Eventos Especiales

### Turno Extra

Cuando un jugador:
- Saca una ficha de la cárcel (lanza 5 o par)
- Come una ficha enemiga
- Mete una ficha en la meta

El servidor no envía `TURN_CHANGE` y el jugador mantiene el turno.

### Pares Consecutivos

Si un jugador saca 3 pares consecutivos, puede haber reglas especiales (según variante del juego).

---

## 🔐 Autenticación

Cada mensaje debe incluir el `id_jugador` para validar que el cliente tiene permiso para realizar la acción.

---

## 📝 Notas de Implementación

1. **WebSockets**: Se recomienda usar WebSockets para comunicación en tiempo real
2. **Serialización**: Todos los mensajes deben ser JSON válido
3. **Validación**: El servidor debe validar todos los movimientos antes de aplicarlos
4. **Broadcast**: Los mensajes `UPDATE`, `TURN_CHANGE`, `WIN` se envían a todos los clientes conectados
5. **Timeout**: Implementar timeout para jugadores inactivos (ej: 30 segundos por turno)

# Protocolo de Comunicación Parqués

## 📡 Formato
- **Transporte**: TCP Socket
- **Formato**: JSON + `\n` (cada mensaje termina en salto de línea)
- **Encoding**: UTF-8

---

## 📨 Mensajes Cliente → Servidor

### 1. JOIN - Unirse a la partida
```json
{
  "tipo": "JOIN",
  "nombre": "Juan"
}
```
**Respuesta**:
```json
{
  "tipo": "ASSIGN_COLOR",
  "exito": true,
  "color": "rojo",
  "nombre": "Juan",
  "mensaje": "Bienvenido Juan, eres rojo"
}
```

### 2. START - Iniciar partida
```json
{
  "tipo": "START"
}
```

### 3. ROLL - Lanzar dados
```json
{
  "tipo": "ROLL"
}
```
**Respuesta**:
```json
{
  "tipo": "DICE_RESULT",
  "dados": [3, 5],
  "suma": 8,
  "es_par": false
}
```

### 4. MOVE - Mover ficha
```json
{
  "tipo": "MOVE",
  "id_ficha": 0,
  "dados": [3, 5]
}
```

### 5. GET_STATE - Obtener estado actual
```json
{
  "tipo": "GET_STATE"
}
```

---

## 📩 Mensajes Servidor → Cliente

### UPDATE - Estado de la partida (broadcast)
```json
{
  "tipo": "UPDATE",
  "estado": {
    "iniciada": true,
    "turno_actual": 0,
    "jugador_actual": "Juan",
    "jugadores": [
      {
        "nombre": "Juan",
        "color": "rojo",
        "es_su_turno": true,
        "fichas": [
          {"id": 0, "posicion": 12, "estado": "tablero"},
          {"id": 1, "posicion": null, "estado": "carcel"}
        ]
      }
    ],
    "tablero": {
      "12": [{"color": "rojo", "id": 0}]
    }
  }
}
```

### MOVE_RESULT - Resultado de movimiento
```json
{
  "tipo": "MOVE_RESULT",
  "dados": [4, 4],
  "es_par": true,
  "accion": "mover",
  "fichas_capturadas": [],
  "cambio_turno": false
}
```

---

## 🎮 Flujo típico para Unity

1. **Conexión y Login**
   - Unity conecta TCP → `127.0.0.1:5555`
   - Envía `JOIN` con nombre del jugador
   - Recibe `ASSIGN_COLOR` con su color

2. **Espera e Inicio**
   - Cuando hay 2+ jugadores, cualquiera envía `START`
   - Todos reciben `GAME_START` y `UPDATE` inicial

3. **Turno del Jugador**
   - Si `estado.jugador_actual == mi_nombre`:
     - Usuario clickea botón "Lanzar Dados"
     - Unity envía `ROLL`
     - Recibe `DICE_RESULT`
     - Usuario selecciona ficha y clickea "Mover"
     - Unity envía `MOVE`
     - Recibe `MOVE_RESULT` y `UPDATE` (broadcast)

4. **Escuchar Actualizaciones**
   - Unity mantiene thread escuchando mensajes `UPDATE`
   - Actualiza UI y tablero en cada `UPDATE`

---

## 🔧 Implementación en Unity (C#)

```csharp
using System.Net.Sockets;
using System.Text;
using Newtonsoft.Json;

TcpClient client = new TcpClient("127.0.0.1", 5555);
NetworkStream stream = client.GetStream();

// Enviar
void Enviar(object mensaje) {
    string json = JsonConvert.SerializeObject(mensaje) + "\n";
    byte[] data = Encoding.UTF8.GetBytes(json);
    stream.Write(data, 0, data.Length);
}

// Recibir (en thread separado)
void Recibir() {
    byte[] buffer = new byte[4096];
    while (true) {
        int bytes = stream.Read(buffer, 0, buffer.Length);
        string json = Encoding.UTF8.GetString(buffer, 0, bytes);
        // Parsear JSON y procesar...
    }
}
```

---

## ⚠️ Manejo de Errores

- Si servidor responde `{"error": "..."}` → mostrar mensaje al usuario
- Si `stream.Read()` retorna 0 → conexión cerrada
- Validar `exito: true/false` en respuestas importantes

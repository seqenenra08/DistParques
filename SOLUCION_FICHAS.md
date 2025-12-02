# Solución: Fichas no se ven en el tablero

## Problema identificado
Las fichas no aparecían en el tablero porque había un desajuste entre:
1. **Colores del backend**: usaba español (`rojo`, `azul`, `amarillo`, `verde`)
2. **Colores del frontend**: esperaba inglés (`red`, `blue`, `yellow`, `green`)
3. **Estructura de datos**: el backend enviaba `jugadores.fichas` pero el frontend esperaba `players.pieces`

## Cambios realizados ✅

### 1. Actualización de colores en el backend
- **Archivo**: `backend/models/jugador.py`
  ```python
  COLORES_DISPONIBLES = ["red", "blue", "yellow", "green"]  # Antes: rojo, azul, amarillo, verde
  salidas = {"red": 5, "blue": 22, "yellow": 39, "green": 56}
  ```

- **Archivo**: `backend/models/tablero.py`
  ```python
  SALIDAS = {"red": 5, "blue": 22, "yellow": 39, "green": 56}
  ENTRADAS_PASILLO = {"red": 63, "blue": 12, "yellow": 29, "green": 46}
  ```

### 2. Transformación de estado para el frontend
- **Archivo**: `backend/servidor_salas.py`
- **Nueva función**: `_transformar_estado_para_frontend()`
  
  Transforma automáticamente:
  - `jugadores` → `players`
  - `nombre` → `name`
  - `fichas` → `pieces`
  - `posicion: None` con `estado: 'carcel'` → `position: -1`
  - `estado: 'meta'` → `position: 'center'`
  - `estado: 'pasillo_final'` → `position: 'color_N'` (ej: `red_3`)

### 3. Aplicación de transformación
Se aplicó la transformación en **todos** los eventos que envían estado:
- `PARTIDA_INICIADA`
- `UPDATE`
- `ESTADO_ACTUALIZADO`
- `DADOS_LANZADOS`
- `DICE_RESULT`
- `MOVE_RESULT`

## Cómo verificar que funciona

### 1. Reiniciar el servidor backend (si no está corriendo)
```bash
cd ~/Codes/DistParques
/home/seqenenra/Codes/DistParques/env/bin/python backend/servidor_salas.py
```

### 2. Reiniciar el frontend
```bash
cd ~/Codes/DistParques/frontend
npm run dev
```

### 3. Abrir el navegador
```
http://localhost:3000
```

### 4. Verificar en consola del navegador
Deberías ver logs como:
```
[PARTIDA_INICIADA] {
  estado: {
    players: [
      {
        name: "Jugador 1",
        color: "red",
        pieces: [
          { piece_id: 0, position: -1, color: "red" },  // -1 = cárcel
          { piece_id: 1, position: -1, color: "red" },
          ...
        ]
      },
      ...
    ]
  }
}

[BOARD RENDER] Intentando renderizar fichas: 16  // ¡Ahora debería mostrar 16!
[BOARD RENDER] Fichas por color: {red: 4, blue: 4, yellow: 4, green: 4}
```

## Estructura de datos esperada

### Estado del backend (antes de transformación)
```json
{
  "jugadores": [
    {
      "nombre": "Jugador 1",
      "color": "red",
      "fichas": [
        {
          "id": 0,
          "color": "red",
          "posicion": null,
          "estado": "carcel"
        }
      ]
    }
  ]
}
```

### Estado transformado para frontend
```json
{
  "players": [
    {
      "name": "Jugador 1",
      "color": "red",
      "pieces": [
        {
          "piece_id": 0,
          "color": "red",
          "position": -1,
          "estado": "carcel",
          "is_in_goal": false
        }
      ]
    }
  ]
}
```

## Posiciones de fichas

| Estado backend | Position frontend | Ubicación en tablero |
|----------------|-------------------|----------------------|
| `estado: "carcel"`, `posicion: null` | `-1` | Cárcel (convertido a `'prison'`) |
| `estado: "tablero"`, `posicion: 15` | `15` | Casilla 15 del tablero |
| `estado: "pasillo_final"`, `posicion_pasillo: 3` | `"red_3"` | Pasillo final posición 3 |
| `estado: "meta"` | `"center"` | Centro (meta) |

## Troubleshooting

### Si las fichas aún no aparecen:
1. Abre las Dev Tools del navegador (F12)
2. Ve a la pestaña Console
3. Busca `[PARTIDA_INICIADA]` y expande el objeto `estado`
4. Verifica que tenga:
   - ✅ `players` (no `jugadores`)
   - ✅ Cada player tiene `pieces` (no `fichas`)
   - ✅ Cada piece tiene `position: -1` (no `null`)
   - ✅ Colores en inglés (`red`, no `rojo`)

### Si ves errores de colores inválidos:
- Asegúrate de que el servidor backend se reinició después de los cambios
- Los colores deben ser: `red`, `blue`, `yellow`, `green`

### Si el tablero se ve vacío:
- Verifica en consola: `[BOARD RENDER] Intentando renderizar fichas: X`
- Si X es 0, el problema está en `gameState.players`
- Si X es 16, el problema está en las coordenadas o renderizado

## Próximos pasos
Una vez que veas las fichas en la cárcel:
1. Lanza los dados (botón "Roll Dice")
2. Si sacas par, podrás sacar una ficha de la cárcel
3. Los bots jugarán automáticamente su turno

¡Disfruta del juego! 🎲🎮

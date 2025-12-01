# Sistema de Salas Multijugador

## Descripción

El servidor ahora soporta **múltiples salas de juego simultáneas**, permitiendo que varios grupos de jugadores jueguen partidas independientes al mismo tiempo.

## Características

- ✅ **Múltiples salas**: Crea y únete a diferentes salas de juego
- ✅ **Códigos únicos**: Cada sala tiene un código de 6 caracteres (ej: ABC123)
- ✅ **2-4 jugadores**: Configurable por sala
- ✅ **Soporte para bots**: Agrega bots para completar la partida
- ✅ **Host controls**: El creador de la sala puede iniciar el juego
- ✅ **Gestión automática**: Las salas vacías se eliminan automáticamente

## Cómo Funciona

### Flujo de Juego

1. **Crear Partida** (desde el menú frontend):
   - El jugador selecciona "Crear Partida"
   - Se genera un código único de sala (ej: "XYZ789")
   - El jugador se convierte en el "host" de la sala

2. **Unirse a Partida**:
   - Otros jugadores seleccionan "Unirse a Partida"
   - Ingresan el código de 6 dígitos
   - Se unen a la sala existente

3. **Iniciar Juego**:
   - Solo el host puede iniciar la partida
   - Mínimo 2 jugadores requeridos
   - Se pueden agregar bots para completar

## Iniciar el Servidor

### Opción 1: Script Python
```bash
cd backend
python3 iniciar_servidor.py
```

### Opción 2: Directo con Python
```bash
cd backend
python3 servidor_salas.py
```

### Opción 3: Con Variables de Entorno
```bash
SERVER_HOST=0.0.0.0 SERVER_PORT=5555 python3 backend/iniciar_servidor.py
```

## Protocolo de Mensajes

### Cliente → Servidor

#### Crear Sala
```json
{
  "tipo": "CREAR_SALA",
  "playerName": "Nombre del jugador",
  "maxPlayers": 4,
  "numBots": 0,
  "color": "red"
}
```

#### Unirse a Sala
```json
{
  "tipo": "UNIRSE_SALA",
  "roomCode": "ABC123",
  "playerName": "Nombre del jugador",
  "color": "blue"
}
```

#### Iniciar Partida
```json
{
  "tipo": "INICIAR_PARTIDA"
}
```

#### Lanzar Dados
```json
{
  "tipo": "LANZAR_DADOS"
}
```

#### Mover Ficha
```json
{
  "tipo": "MOVER_FICHA",
  "id_ficha": 0,
  "dados": [3, 4]
}
```

### Servidor → Cliente

#### Sala Creada
```json
{
  "tipo": "SALA_CREADA",
  "exito": true,
  "codigo_sala": "ABC123",
  "jugador": {
    "nombre": "Jugador 1",
    "color": "red",
    "es_host": true
  },
  "estado_sala": {
    "codigo": "ABC123",
    "jugadores": [...],
    "max_jugadores": 4,
    "jugadores_conectados": 1,
    "iniciada": false
  }
}
```

#### Unido a Sala
```json
{
  "tipo": "UNIDO_A_SALA",
  "exito": true,
  "codigo_sala": "ABC123",
  "jugador": {
    "nombre": "Jugador 2",
    "color": "blue",
    "es_host": false
  },
  "estado_sala": {...}
}
```

#### Partida Iniciada
```json
{
  "tipo": "PARTIDA_INICIADA",
  "mensaje": "¡La partida ha comenzado!",
  "estado": {
    "id": "ABC123",
    "iniciada": true,
    "jugadores": [...],
    "turno_actual": 0,
    "jugador_actual": "Jugador 1"
  }
}
```

## Integración con Frontend

El frontend ya tiene la estructura para manejar salas. Solo necesitas actualizar `socketService.js` para usar WebSockets en lugar de Socket.IO:

### Cambios Necesarios en Frontend:

1. **Actualizar la conexión** en `src/services/socketService.js`
2. **Adaptar eventos** para usar el protocolo WebSocket nativo
3. **Actualizar URL** del servidor (ws://localhost:5555)

## Estructura de Archivos

```
backend/
├── servidor_salas.py         # Servidor con múltiples salas
├── iniciar_servidor.py        # Script para iniciar servidor
├── servidor.py                # Servidor antiguo (single room)
└── models/
    ├── partida.py             # Lógica de partida
    ├── jugador.py             # Modelo de jugador
    ├── tablero.py             # Modelo de tablero
    └── ficha.py               # Modelo de ficha
```

## Ventajas del Sistema de Salas

1. **Escalabilidad**: Múltiples partidas simultáneas
2. **Privacidad**: Cada sala es independiente con su código
3. **Flexibilidad**: Diferentes configuraciones por sala
4. **Eficiencia**: Las salas vacías se eliminan automáticamente
5. **Simple**: Fácil de usar para los jugadores (código de 6 dígitos)

## Próximos Pasos

1. ✅ Servidor con múltiples salas creado
2. ⏳ Actualizar frontend para usar WebSockets nativos
3. ⏳ Implementar persistencia de salas (opcional)
4. ⏳ Agregar sistema de reconexión
5. ⏳ Implementar chat de sala (opcional)

## Comandos Útiles

```bash
# Iniciar servidor
python3 backend/iniciar_servidor.py

# Iniciar con puerto personalizado
SERVER_PORT=8080 python3 backend/iniciar_servidor.py

# Ver logs en tiempo real
python3 backend/iniciar_servidor.py 2>&1 | tee server.log
```

## Troubleshooting

### El servidor no inicia
- Verifica que el puerto 5555 esté disponible
- Ejecuta: `netstat -tuln | grep 5555`
- Si está ocupado, usa otro puerto con `SERVER_PORT=8080`

### No se pueden conectar clientes
- Verifica que el firewall permita conexiones en el puerto
- Si estás en producción, usa `0.0.0.0` como host
- Si es local, puedes usar `localhost` o `127.0.0.1`

### Las salas no se crean
- Verifica los logs del servidor
- Asegúrate de que el mensaje tenga el formato correcto
- Revisa que el frontend esté enviando todos los campos requeridos

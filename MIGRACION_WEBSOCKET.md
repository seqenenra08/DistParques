# Migración de Socket.IO a WebSocket Nativo

## ✅ Cambios Realizados

### 1. Servicio WebSocket Actualizado
- **Archivo**: `src/services/socketService.js`
- Reemplazado Socket.IO con WebSocket nativo
- Agregado mapeo de eventos entre frontend y backend
- Implementada reconexión automática
- Sistema de cola de mensajes para envíos pendientes

### 2. Hook useSocket Actualizado
- **Archivo**: `src/hooks/useSocket.js`
- Adaptado para usar WebSocket nativo
- Mantenida la misma API para compatibilidad
- Conservada funcionalidad de reconexión

### 3. Variables de Entorno
- **Archivos**: `.env.local`, `.env.local.example`
- Nueva variable: `NEXT_PUBLIC_WS_URL=ws://localhost:5555`
- Configurable para desarrollo y producción

## 🔄 Mapeo de Eventos

### Backend → Frontend
```
CONECTADO           → connection_success
SALA_CREADA         → room_created
UNIDO_A_SALA        → room_joined
JUGADOR_UNIDO       → player_joined_room
PARTIDA_INICIADA    → game_started
DADOS_LANZADOS      → dice_rolled
RESULTADO_MOVIMIENTO → piece_moved
ESTADO_ACTUALIZADO  → game_state_updated
ERROR               → error
```

### Frontend → Backend
```
create_room              → CREAR_SALA
join_room                → UNIRSE_SALA
start_game_from_lobby    → INICIAR_PARTIDA
roll_dice                → LANZAR_DADOS
move_piece               → MOVER_FICHA
release_piece            → LIBERAR_FICHA
```

## 🚀 Cómo Usar

### 1. Iniciar el Servidor Backend
```bash
cd backend
python3 iniciar_servidor.py
```

Deberías ver:
```
============================================================
🎲 SERVIDOR DE SALAS MULTIJUGADOR - PARQUÉS 🎲
============================================================
✅ Servidor escuchando en ws://0.0.0.0:5555
```

### 2. Iniciar el Frontend
```bash
cd frontend
npm run dev
```

El frontend se conectará automáticamente a `ws://localhost:5555`

### 3. Verificar Conexión
Abre la consola del navegador, deberías ver:
```
✅ Conectado al servidor WebSocket
[WS] Mensaje recibido: {tipo: "CONECTADO", ...}
```

## 🔧 Configuración

### Desarrollo Local
El archivo `.env.local` ya está configurado:
```env
NEXT_PUBLIC_WS_URL=ws://localhost:5555
```

### Producción
Crea un archivo `.env.production`:
```env
NEXT_PUBLIC_WS_URL=ws://tu-servidor.com:5555
```

## 📝 Compatibilidad

El código mantiene **100% de compatibilidad** con el código existente:

```javascript
// El código existente sigue funcionando sin cambios
const { socket, connected, emit } = useSocket();

emit('create_room', { 
  playerName: 'Jugador 1',
  maxPlayers: 4 
});

socket.on('room_created', (data) => {
  console.log('Sala creada:', data);
});
```

## 🧪 Probar la Conexión

### Desde la Consola del Navegador
```javascript
// Verificar estado
console.log('Conectado:', socketService.isConnected());

// Enviar mensaje de prueba
socketService.emit('ping', {});
```

### Desde el Backend
El servidor mostrará:
```
🔌 Nueva conexión desde ('127.0.0.1', 54321)
```

## ⚠️ Diferencias con Socket.IO

| Característica | Socket.IO | WebSocket Nativo |
|---------------|-----------|------------------|
| Reconexión automática | ✅ Sí | ✅ Sí (implementado) |
| Rooms | ✅ Sí | ⚠️ Manual (implementado en backend) |
| Fallback a HTTP | ✅ Sí | ❌ No |
| Tamaño librería | ~200KB | ~0KB (nativo) |
| Performance | Buena | Excelente |

## 🐛 Troubleshooting

### Error: "WebSocket connection failed"
- Verifica que el backend esté corriendo
- Confirma el puerto (5555) esté abierto
- Revisa la URL en `.env.local`

### Error: "No conectado, encolando mensaje"
- El mensaje se guardará en cola
- Se enviará automáticamente al reconectar
- Normal durante reconexiones

### No recibo eventos
- Verifica el mapeo de eventos en `socketService.js`
- Revisa la consola del navegador y del servidor
- Asegúrate de que el evento esté registrado con `.on()`

## 📊 Ventajas de WebSocket Nativo

1. **Rendimiento**: Más rápido y ligero
2. **Sin dependencias**: No requiere librerías externas
3. **Simplicidad**: Más fácil de entender y mantener
4. **Compatibilidad**: Funciona en todos los navegadores modernos
5. **Tamaño**: 0 KB adicionales en el bundle

## 🔄 Reversión (Si es Necesario)

Si necesitas volver a Socket.IO:

1. Restaura el archivo anterior:
   ```bash
   git checkout HEAD -- src/services/socketService.js
   ```

2. Reinstala Socket.IO:
   ```bash
   npm install socket.io-client
   ```

3. Actualiza `.env.local`:
   ```env
   NEXT_PUBLIC_SOCKET_URL=http://localhost:5000
   ```

## ✨ Próximos Pasos

1. ✅ WebSocket nativo implementado
2. ✅ Mapeo de eventos completado
3. ✅ Reconexión automática funcionando
4. ⏳ Probar flujo completo de creación/unión de salas
5. ⏳ Implementar heartbeat/ping-pong (opcional)
6. ⏳ Agregar compresión de mensajes (opcional)

## 📞 Ayuda

Si algo no funciona:
1. Revisa los logs del servidor
2. Abre la consola del navegador
3. Verifica que ambos estén usando el mismo puerto
4. Confirma que el formato de mensajes sea correcto

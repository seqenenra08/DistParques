# 🎮 Cómo Crear Diferentes Salas - Guía Completa

## ✅ ¿Qué se ha implementado?

He creado un **servidor de salas multijugador** que permite:

- **Múltiples partidas simultáneas**: Varios grupos pueden jugar al mismo tiempo
- **Salas privadas**: Cada sala tiene un código único de 6 dígitos
- **Control por host**: El creador de la sala puede configurar e iniciar el juego
- **Soporte para bots**: Agrega jugadores automáticos
- **Gestión automática**: Las salas vacías se eliminan solas

## 📁 Archivos Creados

```
backend/
├── servidor_salas.py          # ⭐ Nuevo servidor con múltiples salas
├── iniciar_servidor.py         # Script para iniciar el servidor fácilmente
├── test_salas.py              # Script de prueba
└── servidor.py                # Servidor antiguo (mantener por compatibilidad)

docs/
└── SERVIDOR_SALAS.md          # Documentación técnica completa
└── GUIA_SALAS.md              # Esta guía (para usuarios)
```

## 🚀 Cómo Usar

### 1. Iniciar el Servidor

Abre una terminal y ejecuta:

```bash
cd /home/seqenenra/Codes/DistParques
python3 backend/iniciar_servidor.py
```

Verás algo como:
```
============================================================
🎲 SERVIDOR DE SALAS MULTIJUGADOR - PARQUÉS 🎲
============================================================

📡 Host: 0.0.0.0
🔌 Puerto: 5555

Características:
  ✅ Múltiples salas simultáneas
  ✅ Códigos únicos de 6 dígitos
  ✅ 2-4 jugadores por sala
  ✅ Soporte para bots

============================================================

🚀 Servidor de salas iniciando en 0.0.0.0:5555
✅ Servidor escuchando en ws://0.0.0.0:5555
Esperando conexiones...
```

### 2. Flujo del Juego

#### Para el jugador que CREA la partida:

1. Click en **"Crear Partida"** en el menú
2. Selecciona:
   - Número de jugadores (2-4)
   - Número de bots (opcional)
3. Se genera un **código de sala** (ej: "XYZ789")
4. Comparte ese código con tus amigos
5. Espera a que se unan
6. Click en **"Iniciar Partida"**

#### Para jugadores que se UNEN:

1. Click en **"Unirse a Partida"** en el menú
2. Ingresa el **código de 6 dígitos** que te compartieron
3. Ingresa tu nombre
4. Selecciona tu color
5. Espera a que el host inicie el juego

## 🔧 Integración con el Frontend

Tu frontend ya tiene la estructura para salas. Solo necesitas actualizar el protocolo:

### Cambios Necesarios

El frontend actualmente usa Socket.IO, pero el nuevo servidor usa **WebSockets nativos**.

**Opción 1: Actualizar para usar WebSockets nativos** (recomendado)
```javascript
// En src/services/socketService.js
const ws = new WebSocket('ws://localhost:5555');

ws.onopen = () => {
  console.log('Conectado');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Procesar mensajes
};

// Crear sala
ws.send(JSON.stringify({
  tipo: 'CREAR_SALA',
  playerName: 'Mi Nombre',
  maxPlayers: 4,
  numBots: 0,
  color: 'red'
}));
```

**Opción 2: Mantener Socket.IO** (requiere wrapper en el backend)

Si prefieres mantener Socket.IO, puedo crear un wrapper que convierta entre Socket.IO y WebSockets.

## 📊 Ejemplo de Flujo Completo

```
Jugador 1 (Host):                  Servidor:                    Jugador 2:
     |                                 |                              |
     |---> CREAR_SALA                  |                              |
     |                                 |                              |
     |<--- SALA_CREADA (ABC123)        |                              |
     |     "Comparte el código"        |                              |
     |                                 |                              |
     |                                 |   <--- UNIRSE_SALA (ABC123)  |
     |                                 |                              |
     |<--- JUGADOR_UNIDO               |---> UNIDO_A_SALA            |
     |     "Juan se unió"              |                              |
     |                                 |                              |
     |---> INICIAR_PARTIDA             |                              |
     |                                 |                              |
     |<--- PARTIDA_INICIADA            |---> PARTIDA_INICIADA         |
     |                                 |                              |
     |<--------------- ¡JUEGO COMIENZA! --------------------------->|
```

## 🎯 Ventajas del Sistema

1. **Privacidad**: Cada sala es independiente con su código
2. **Flexibilidad**: Diferentes configuraciones por sala
3. **Escalabilidad**: Múltiples partidas al mismo tiempo
4. **Simplicidad**: Código de 6 dígitos fácil de compartir
5. **Eficiencia**: Las salas vacías se limpian automáticamente

## 🧪 Probar el Servidor

### Prueba Manual

1. Inicia el servidor:
   ```bash
   python3 backend/iniciar_servidor.py
   ```

2. En otra terminal, prueba con un cliente simple:
   ```bash
   python3 backend/test_salas.py
   ```

### Prueba con el Frontend

1. Inicia el servidor:
   ```bash
   python3 backend/iniciar_servidor.py
   ```

2. Inicia el frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Abre dos navegadores diferentes
4. En el primero, crea una sala
5. En el segundo, únete con el código

## 🔍 Debugging

Si algo no funciona, revisa:

1. **¿El servidor está corriendo?**
   ```bash
   ps aux | grep servidor_salas
   ```

2. **¿El puerto está libre?**
   ```bash
   netstat -tuln | grep 5555
   ```

3. **¿Hay errores en el log?**
   Mira la terminal donde iniciaste el servidor

## 📝 Protocolo de Mensajes

### Mensajes que envía el Cliente

| Mensaje | Descripción | Campos |
|---------|-------------|--------|
| `CREAR_SALA` | Crea una nueva sala | playerName, maxPlayers, numBots, color |
| `UNIRSE_SALA` | Únete a una sala existente | roomCode, playerName, color |
| `INICIAR_PARTIDA` | Inicia el juego (solo host) | - |
| `LANZAR_DADOS` | Lanza los dados | - |
| `MOVER_FICHA` | Mueve una ficha | id_ficha, dados |

### Mensajes que envía el Servidor

| Mensaje | Descripción | Cuándo |
|---------|-------------|--------|
| `SALA_CREADA` | Confirmación de creación | Después de CREAR_SALA |
| `UNIDO_A_SALA` | Confirmación de unión | Después de UNIRSE_SALA |
| `JUGADOR_UNIDO` | Notificación a todos | Cuando alguien se une |
| `PARTIDA_INICIADA` | El juego comienza | Después de INICIAR_PARTIDA |
| `DADOS_LANZADOS` | Resultado de dados | Después de LANZAR_DADOS |
| `ESTADO_ACTUALIZADO` | Estado del juego | Después de cada movimiento |

## 🎓 Próximos Pasos

1. ✅ Servidor implementado
2. ⏳ Actualizar frontend para WebSockets nativos
3. ⏳ Agregar sistema de chat (opcional)
4. ⏳ Implementar reconexión automática
5. ⏳ Añadir persistencia de salas (opcional)

## 💡 Tips

- **Códigos de sala**: Son de 6 caracteres (letras mayúsculas y números)
- **Jugadores mínimos**: 2 (puedes usar bots para completar)
- **Timeout**: Las salas sin actividad se eliminan automáticamente
- **Reconexión**: Si te desconectas, la sala permanece activa por un tiempo

## 🆘 Ayuda

Si necesitas ayuda:
1. Revisa `SERVIDOR_SALAS.md` para documentación técnica
2. Ejecuta `python3 backend/test_salas.py` para probar
3. Mira los logs del servidor para errores
4. Verifica que el puerto 5555 esté libre

## 📞 Contacto

Para más información o problemas, revisa:
- `SERVIDOR_SALAS.md` - Documentación técnica completa
- `backend/servidor_salas.py` - Código fuente del servidor
- Logs del servidor - Para debugging

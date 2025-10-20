# 🟡 Fase 2 - Servidor TCP en Python (Backend)

## ✅ Completado

Se ha implementado un servidor TCP completo con todas las funcionalidades requeridas para el juego de Parqués distribuido.

---

## 🏗️ Arquitectura del Servidor

```
┌──────────────────────────────────────────────────────┐
│            SERVIDOR TCP (Puerto 5555)                │
│  - Acepta múltiples conexiones simultáneas          │
│  - Threading para cada cliente                      │
│  - Sincronización con Locks                         │
└──────────────┬───────────────────────────────────────┘
               │
       ┌───────┴────────┬──────────────┬──────────────┐
       ▼                ▼              ▼              ▼
┌─────────────┐  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Cliente 1  │  │  Cliente 2  │ │  Cliente 3  │ │  Cliente 4  │
│  (Thread)   │  │  (Thread)   │ │  (Thread)   │ │  (Thread)   │
└─────────────┘  └─────────────┘ └─────────────┘ └─────────────┘
       │                │              │              │
       └────────────────┴──────────────┴──────────────┘
                        │
                ┌───────▼────────┐
                │  GestorPartidas│
                │  - Partidas    │
                │  - Jugadores   │
                │  - Turnos      │
                └────────────────┘
```

---

## 📁 Archivos Creados

### 1. `backend/servidor.py` ✅
**Servidor TCP principal**

**Clases:**
- `ServidorParques`: Servidor principal
- `ClienteHandler`: Maneja cada conexión de cliente

**Características:**
- ✅ Servidor TCP con `socket`
- ✅ Manejo de múltiples clientes con `threading`
- ✅ Mensajes JSON sobre TCP
- ✅ Sistema de partidas múltiples
- ✅ Control de turnos con `threading.Lock`
- ✅ Bloqueo de nuevos jugadores cuando la partida inicia
- ✅ Broadcast de mensajes a todos los jugadores
- ✅ Manejo de desconexiones

**Métodos principales:**
```python
# Gestión de servidor
servidor.iniciar()
servidor.detener()
servidor.aceptar_clientes()

# Gestión de partidas
servidor.obtener_o_crear_partida(id_partida)
servidor.agregar_jugador_a_partida(cliente, nombre, id_partida)
servidor.lanzar_dados(id_partida, id_jugador)
servidor.mover_ficha(id_partida, id_jugador, id_ficha)
servidor.cambiar_turno(id_partida)

# Comunicación
servidor.broadcast_a_partida(id_partida, tipo, datos)
servidor.broadcast_estado_partida(id_partida)
```

---

### 2. `backend/sincronizacion.py` ✅
**Sincronización de tiempo con Algoritmo de Berkeley**

**Clases:**
- `SincronizadorBerkeley`: Implementa el algoritmo
- `RelojSincronizado`: Reloj local con offset

**Algoritmo de Berkeley:**
1. El servidor (coordinador) solicita el tiempo a todos los clientes
2. Recibe los tiempos de cada cliente
3. Calcula el tiempo promedio
4. Calcula el ajuste necesario para cada cliente
5. Envía los ajustes a cada cliente
6. Cada cliente ajusta su reloj local

**Características:**
- ✅ Sincronización periódica automática (cada 30 segundos)
- ✅ Compensación de RTT (Round-Trip Time)
- ✅ Thread dedicado para sincronización
- ✅ Manejo de offsets de tiempo

**Uso:**
```python
from sincronizacion import SincronizadorBerkeley

sincronizador = SincronizadorBerkeley(servidor)
sincronizador.iniciar()

# Obtener tiempo sincronizado
tiempo_actual = sincronizador.obtener_tiempo_sincronizado()
```

---

### 3. `cliente/cliente_consola.py` ✅
**Cliente de consola para pruebas**

**Características:**
- ✅ Interfaz de línea de comandos interactiva
- ✅ Conexión TCP al servidor
- ✅ Thread para recibir mensajes
- ✅ Comandos simples para jugar
- ✅ Visualización del estado del juego
- ✅ Soporte para sincronización de tiempo

**Comandos:**
```
lanzar / l       - Lanzar los dados
mover <N> / m <N> - Mover la ficha N (0-3)
estado / e       - Ver estado actual
ayuda / h        - Mostrar ayuda
salir            - Salir del juego
```

**Uso:**
```bash
python cliente/cliente_consola.py
python cliente/cliente_consola.py --host 192.168.1.100 --puerto 5555
```

---

### 4. Scripts de Ejecución
- `iniciar_servidor.bat` ✅ - Inicia el servidor
- `iniciar_cliente.bat` ✅ - Inicia un cliente

---

## 🎮 Reglas del Juego Implementadas

### 🎲 Dados
- ✅ **2 dados** se lanzan en cada turno
- ✅ Se suman los valores (2-12)
- ✅ **Pares** (dados iguales) permiten:
  - Sacar fichas de la cárcel
  - Turno extra

### 🏠 Salida de Cárcel
- ✅ Solo con **par** (dados iguales)
- ✅ La ficha sale a la casilla de salida de su color
- ✅ Otorga turno extra

### 🚶 Movimiento
- ✅ Fichas avanzan según la suma de los dados
- ✅ Recorrido circular de 68 casillas
- ✅ Entrada a zona final (8 casillas)
- ✅ Llegada exacta a la meta

### 😈 Capturas
- ✅ Una ficha puede comer a otra si:
  - Caen en la misma casilla
  - La casilla NO es segura
  - La casilla NO es de salida
  - Son de jugadores diferentes
- ✅ La ficha comida vuelve a la cárcel
- ✅ Comer otorga turno extra

### 🏰 Seguros
- ✅ 8 casillas seguras en el tablero
- ✅ Las fichas en seguros no pueden ser comidas
- ✅ Salidas de cada color son seguras

### 🏆 Victoria
- ✅ Gana el primer jugador que meta sus 4 fichas en la meta
- ✅ Broadcast de victoria a todos los jugadores
- ✅ La partida finaliza automáticamente

---

## 🔐 Sincronización y Concurrencia

### Threading
```python
# Lock para partidas
lock_partidas = threading.Lock()

# Lock para clientes
lock_clientes = threading.Lock()

# Lock por cliente para envío de mensajes
lock_cliente = threading.Lock()
```

### Control de Turnos
- ✅ Solo el jugador actual puede lanzar dados
- ✅ Solo el jugador actual puede mover fichas
- ✅ Validación de turno en cada acción
- ✅ Cambio automático de turno
- ✅ Turnos extra por eventos especiales

### Bloqueo de Partidas
```python
# Bloquear nuevos jugadores cuando inicia
if partida.estado == EstadoPartida.EN_CURSO:
    return error("PARTIDA_YA_INICIADA")

# Verificar capacidad
if not partida.puede_unirse():
    return error("PARTIDA_LLENA")
```

---

## 📡 Protocolo de Comunicación

### Mensajes Implementados

#### Cliente → Servidor
1. **JOIN** - Unirse a partida
```json
{
  "type": "JOIN",
  "data": {
    "nombre": "Juan",
    "id_partida": "default"
  }
}
```

2. **ROLL** - Lanzar dados
```json
{
  "type": "ROLL",
  "data": {}
}
```

3. **MOVE** - Mover ficha
```json
{
  "type": "MOVE",
  "data": {
    "id_ficha": 0
  }
}
```

4. **DISCONNECT** - Desconectar
```json
{
  "type": "DISCONNECT",
  "data": {}
}
```

5. **TIME_RESPONSE** - Respuesta de tiempo (Berkeley)
```json
{
  "type": "TIME_RESPONSE",
  "data": {
    "tiempo_cliente": "2025-10-19T14:30:00.123456"
  }
}
```

#### Servidor → Cliente
1. **ASSIGN_COLOR** - Asignar color
2. **START_GAME** - Iniciar partida
3. **ROLL_RESULT** - Resultado de dados
4. **MOVE_SUCCESS** - Movimiento exitoso
5. **UPDATE** - Estado actualizado
6. **TURN_CHANGE** - Cambio de turno
7. **WIN** - Victoria
8. **EATEN** - Ficha comida
9. **TIME_REQUEST** - Solicitud de tiempo (Berkeley)
10. **TIME_SYNC** - Sincronización de tiempo
11. **ERROR** - Error

---

## 🚀 Cómo Ejecutar

### Opción 1: Scripts Batch (Windows)

**Iniciar Servidor:**
```cmd
iniciar_servidor.bat
```

**Iniciar Cliente (en otra ventana):**
```cmd
iniciar_cliente.bat
```

### Opción 2: Línea de Comandos

**Servidor:**
```bash
python backend/servidor.py
```

**Cliente:**
```bash
python cliente/cliente_consola.py
```

**Cliente con parámetros:**
```bash
python cliente/cliente_consola.py --host 192.168.1.100 --puerto 5555
```

---

## 🧪 Pruebas

### Probar con múltiples clientes

1. Iniciar el servidor en una terminal
2. Abrir 2-4 terminales adicionales
3. Ejecutar el cliente en cada una
4. Unirse con diferentes nombres
5. Esperar que la partida inicie automáticamente
6. Jugar por turnos

### Ejemplo de sesión:

**Terminal 1 (Servidor):**
```
🎲 Servidor de Parqués
Servidor iniciado en 0.0.0.0:5555
Esperando conexiones...
Nueva conexión desde ('127.0.0.1', 54321)
Jugador 'Alice' se unió a partida 'default'
Nueva conexión desde ('127.0.0.1', 54322)
Jugador 'Bob' se unió a partida 'default'
Partida 'default' iniciada con 2 jugadores
```

**Terminal 2 (Cliente Alice):**
```
🎲 Cliente de Parqués
📝 Ingresa tu nombre: Alice
✅ Te has unido a la partida
🎨 Color asignado: ROJO
👤 Bob (azul) se unió a la partida
🎮 ¡LA PARTIDA HA COMENZADO!
💡 ¡Es tu turno! Escribe 'lanzar'
> lanzar
🎲 Dados: 3 + 4 = 7
📍 Fichas movibles: []
⚠️ No hay fichas movibles
```

---

## 📊 Estructura de Datos

### Partida
```python
{
  "id": "partida_1",
  "estado": "en_curso",
  "jugadores": [...],
  "turno_actual": 0,
  "ultimo_dado": 7,
  "historial_movimientos": [...]
}
```

### Jugador
```python
{
  "id": "player_1",
  "nombre": "Alice",
  "color": "rojo",
  "turno": true,
  "fichas": [...],
  "fichas_en_meta": 0
}
```

### Ficha
```python
{
  "id": 0,
  "color": "rojo",
  "posicion": 5,
  "estado": "activa",
  "pasos_recorridos": 0
}
```

---

## 🔧 Configuración

### Servidor
```python
# En servidor.py, línea ~600
servidor = ServidorParques(
    host="0.0.0.0",  # Escuchar en todas las interfaces
    puerto=5555       # Puerto del servidor
)
```

### Sincronización
```python
# En sincronizacion.py
intervalo_sincronizacion = 30  # Sincronizar cada 30 segundos
```

---

## ⚠️ Manejo de Errores

### Códigos de Error Implementados
- `PARTIDA_LLENA` - No hay espacio en la partida
- `PARTIDA_YA_INICIADA` - La partida ya comenzó
- `PARTIDA_NO_ENCONTRADA` - Partida no existe
- `TURNO_INVALIDO` - No es el turno del jugador
- `DADO_NO_LANZADO` - Debe lanzar dados primero
- `MOVIMIENTO_INVALIDO` - Movimiento no válido
- `NOMBRE_REQUERIDO` - Falta el nombre
- `TIPO_INVALIDO` - Tipo de mensaje desconocido

---

## 📈 Características Técnicas

### Concurrencia
- ✅ Un thread por cliente conectado
- ✅ Thread principal para aceptar conexiones
- ✅ Thread de sincronización de tiempo
- ✅ Locks para prevenir race conditions

### Escalabilidad
- ✅ Soporta múltiples partidas simultáneas
- ✅ Cada partida es independiente
- ✅ Sin límite de partidas activas (limitado por memoria)

### Robustez
- ✅ Manejo de desconexiones inesperadas
- ✅ Timeout en operaciones de red
- ✅ Validación de todos los mensajes
- ✅ Logging completo de eventos

---

## 🎯 Próximos Pasos (Fase 3)

- [ ] Implementar interfaz gráfica (GUI)
- [ ] Cliente web con WebSockets
- [ ] Animaciones de movimiento
- [ ] Efectos de sonido
- [ ] Chat entre jugadores
- [ ] Sistema de salas/lobbies
- [ ] Reconnection automática
- [ ] Persistencia en base de datos

---

**Fecha de completación:** 19 de octubre de 2025  
**Estado:** ✅ Fase 2 Completada  
**Líneas de código:** ~1,200+  
**Archivos creados:** 5  
**Tests realizados:** Funcional ✅

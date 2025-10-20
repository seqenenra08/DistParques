# 🎮 Guía de Uso - Servidor y Cliente de Parqués

## ⚠️ IMPORTANTE: Sistema de Inicio Manual

**La partida ahora usa INICIO MANUAL**:
- El **primer jugador** es el **anfitrión** 👑
- El anfitrión debe escribir **`iniciar`** para comenzar
- Se necesitan **mínimo 2 jugadores**
- Ver guía detallada: [`INICIO_MANUAL.md`](INICIO_MANUAL.md)

---

## 📋 Requisitos Previos

- **Python 3.7+** instalado en el sistema
- **Windows** (los scripts .bat son para Windows, pero el código funciona en Linux/Mac)
- **Conexión de red** (localhost para pruebas locales, o red local/internet para juego distribuido)

---

## 🚀 Inicio Rápido

### 1. Verificar Python

Abre una terminal y ejecuta:
```cmd
python --version
```

Deberías ver algo como: `Python 3.11.0` o superior.

### 2. Navegar al directorio del proyecto
```cmd
cd C:\Users\Seqen\OneDrive\Desktop\DistParques
```

### 3. Iniciar el Servidor

**Opción A: Usando el script (recomendado)**
```cmd
iniciar_servidor.bat
```

**Opción B: Manualmente**
```cmd
python backend\servidor.py
```

Deberías ver:
```
Servidor iniciado en 0.0.0.0:5555
Esperando conexiones en 0.0.0.0:5555...
```

### 4. Iniciar Cliente(s)

**Abre OTRA terminal** y ejecuta:

**Opción A: Usando el script**
```cmd
iniciar_cliente.bat
```

**Opción B: Manualmente**
```cmd
python cliente\cliente_consola.py
```

### 5. Jugar

Sigue las instrucciones en la consola del cliente.

---

## 🎯 Tutorial Paso a Paso

### Ejemplo con 2 Jugadores

#### Terminal 1 - Servidor
```cmd
C:\> cd DistParques
C:\DistParques> python backend\servidor.py

================================================
     SERVIDOR DE PARQUES
================================================

Servidor iniciado en 0.0.0.0:5555
Esperando conexiones en 0.0.0.0:5555...
```

#### Terminal 2 - Cliente 1 (Alice)
```cmd
C:\> cd DistParques
C:\DistParques> python cliente\cliente_consola.py

================================================
🎲 PARQUÉS - CLIENTE DE CONSOLA
================================================

📝 Ingresa tu nombre: Alice
🎮 ID de partida (Enter para 'default'): [Enter]

✅ Te has unido a la partida
   Tu ID: player_1
🎨 Color asignado: ROJO
   Jugadores en partida: 1/4

💡 Comandos disponibles:
   lanzar      - Lanzar los dados
   mover <N>   - Mover la ficha N (0-3)
   estado      - Ver estado actual
   ayuda       - Mostrar comandos
   salir       - Salir del juego

> _
```

#### Terminal 3 - Cliente 2 (Bob)
```cmd
C:\> cd DistParques
C:\DistParques> python cliente\cliente_consola.py

📝 Ingresa tu nombre: Bob
🎮 ID de partida (Enter para 'default'): [Enter]

✅ Te has unido a la partida
🎨 Color asignado: AZUL
   Jugadores en partida: 2/4
```

#### En Terminal 2 (Alice)
```
👤 Bob (azul) se unió a la partida
   Jugadores: 2

============================================================
🎮 ¡LA PARTIDA HA COMENZADO!
============================================================

👥 Jugadores:
   - Alice (rojo)
   - Bob (azul)

🎯 Turno inicial: Alice

💡 ¡Es tu turno! Escribe 'lanzar' para tirar los dados

> lanzar

🎲 Dados: 3 + 3 = 6
   ¡PAR! Puedes sacar ficha de la cárcel

📍 Fichas movibles: [0, 1, 2, 3]
   Escribe 'mover <num_ficha>' para mover una ficha

> mover 0

✅ Ficha salió de la cárcel
   🎉 ¡Turno extra!

> lanzar

🎲 Dados: 2 + 5 = 7

📍 Fichas movibles: [0]
   Escribe 'mover <num_ficha>' para mover una ficha

> mover 0

✅ Ficha movida correctamente

➡️ Es el turno de Bob
```

#### En Terminal 3 (Bob)
```
🎲 Alice lanzó: 3 + 3 = 6
✅ Alice movió una ficha
🎲 Alice lanzó: 2 + 5 = 7
✅ Alice movió una ficha

➡️ Es el turno de Bob

💡 Es tu turno. Escribe 'lanzar' para tirar los dados

> lanzar
...
```

---

## 📝 Comandos del Cliente

### Comandos Básicos

| Comando | Alias | Descripción |
|---------|-------|-------------|
| `lanzar` | `l` | Lanza los 2 dados |
| `mover <N>` | `m <N>` | Mueve la ficha N (0-3) |
| `estado` | `e` | Muestra tu estado actual |
| `ayuda` | `h` | Muestra la lista de comandos |
| `salir` | - | Sale del juego |

### Ejemplos

```
> lanzar
> l

> mover 0
> m 0

> estado
> e

> ayuda
> h

> salir
```

---

## 🎲 Reglas del Juego

### Objetivo
Ser el primero en meter las **4 fichas** en la meta.

### Inicio
1. Todas las fichas empiezan en la **cárcel**
2. Para sacar una ficha, debes sacar un **PAR** (dados iguales)
3. Ejemplos de pares: 1-1, 2-2, 3-3, 4-4, 5-5, 6-6

### Movimiento
1. Lanza 2 dados
2. Suma el resultado (ej: 3+4=7)
3. Mueve una ficha ese número de casillas
4. Si la ficha está en cárcel, solo sale con PAR

### Casillas Especiales

#### 🏠 Salidas (Seguras)
- Cada color tiene su salida
- Rojo: casilla 5
- Azul: casilla 22
- Amarillo: casilla 39
- Verde: casilla 56
- No se puede comer en salidas

#### 🏰 Seguros
- Casillas: 5, 12, 22, 29, 39, 46, 56, 63
- No se puede comer en seguros

### Comer Fichas
- Si caes en una casilla con una ficha enemiga
- Y la casilla NO es segura
- La ficha enemiga vuelve a la cárcel
- Obtienes turno extra

### Turnos Extra
Obtienes turno extra cuando:
- Sacas un PAR (para sacar de cárcel)
- Comes una ficha enemiga
- Metes una ficha en la meta

### Victoria
- Mete las 4 fichas en la meta
- Debes llegar EXACTAMENTE
- ¡El primero en lograrlo gana!

---

## 🔧 Configuración Avanzada

### Servidor en Otra Máquina

Si quieres conectarte a un servidor en otra computadora:

**En el servidor:**
1. Anota la dirección IP (ej: 192.168.1.100)
2. Asegúrate que el puerto 5555 esté abierto en el firewall

**En el cliente:**
```cmd
python cliente\cliente_consola.py --host 192.168.1.100 --puerto 5555
```

### Cambiar Puerto del Servidor

Edita `backend/servidor.py` línea ~600:
```python
servidor = ServidorParques(host="0.0.0.0", puerto=6666)  # Cambiar puerto
```

### Máximo de Jugadores

Edita al crear la partida o en `backend/servidor.py`:
```python
partida = Partida(id_partida, max_jugadores=4)  # Cambiar a 2, 3 o 4
```

---

## ❓ Solución de Problemas

### "Python no está instalado"

**Solución:**
1. Descarga Python desde [python.org](https://python.org)
2. Durante la instalación, marca "Add Python to PATH"
3. Reinicia la terminal

### "No se puede conectar al servidor"

**Verifica:**
1. ¿El servidor está ejecutándose?
2. ¿La dirección IP es correcta?
3. ¿El puerto es el correcto?
4. ¿El firewall permite la conexión?

**Prueba:**
```cmd
# Ver si el servidor está escuchando
netstat -an | findstr :5555
```

### "Conexión cerrada por el servidor"

**Posibles causas:**
1. El servidor se detuvo
2. Conexión de red interrumpida
3. El servidor está sobrecargado

**Solución:**
- Reinicia el servidor
- Reconecta el cliente

### "No es tu turno"

Debes esperar a que sea tu turno para jugar.

**Verifica:**
```
> estado
```

Verás si es tu turno o no.

---

## 📊 Logs y Debug

### Ver Logs del Servidor

El servidor muestra logs en la consola:
```
2025-10-19 14:30:00 - INFO - Servidor iniciado en 0.0.0.0:5555
2025-10-19 14:30:05 - INFO - Nueva conexión desde ('127.0.0.1', 54321)
2025-10-19 14:30:06 - INFO - Nueva partida creada: default
2025-10-19 14:30:10 - INFO - Partida default iniciada con 2 jugadores
```

### Habilitar Debug Detallado

Edita `backend/servidor.py` línea ~18:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Cambiar de INFO a DEBUG
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

---

## 🎮 Consejos de Juego

### Estrategia Básica
1. **Prioridad**: Saca todas tus fichas de la cárcel primero
2. **Agrupación**: Mantén fichas juntas para protegerte
3. **Seguros**: Usa los seguros estratégicamente
4. **Pares**: Los pares son oro, ¡úsalos bien!

### Orden de Movimiento
1. Si tienes fichas en cárcel y sacas par → Saca ficha
2. Si tienes fichas activas → Mueve la más avanzada
3. Si puedes comer → ¡Hazlo! (turno extra)
4. Protege fichas cerca de la meta

---

## 🧪 Pruebas

### Test Rápido (1 jugador + bot)
Para probar rápidamente:
1. Inicia servidor
2. Inicia un cliente
3. El servidor esperará a otro jugador (mínimo 2)

### Test Completo (4 jugadores)
1. Inicia servidor
2. Abre 4 terminales
3. Inicia un cliente en cada una
4. Todos se unen a la misma partida
5. El juego inicia automáticamente

---

## 📚 Referencia de Mensajes

### Cliente → Servidor
- `JOIN` - Unirse a partida
- `ROLL` - Lanzar dados
- `MOVE` - Mover ficha
- `DISCONNECT` - Desconectar

### Servidor → Cliente
- `JOIN_SUCCESS` / `JOIN_ERROR` - Resultado de unirse
- `ASSIGN_COLOR` - Color asignado
- `START_GAME` - Partida iniciada
- `ROLL_RESULT` - Resultado de dados
- `MOVE_SUCCESS` / `MOVE_ERROR` - Resultado de movimiento
- `UPDATE` - Estado actualizado
- `TURN_CHANGE` - Cambio de turno
- `WIN` - Victoria
- `EATEN` - Ficha comida
- `PLAYER_DISCONNECT` - Jugador desconectado
- `ERROR` - Error general

---

## 🛠️ Mantenimiento

### Detener el Servidor
- Presiona `Ctrl+C` en la terminal del servidor
- El servidor se detendrá gracefully

### Limpiar Partidas
Las partidas se eliminan automáticamente cuando:
- Todos los jugadores se desconectan
- La partida termina

### Reiniciar
1. Detén el servidor (`Ctrl+C`)
2. Espera 2-3 segundos
3. Inicia el servidor de nuevo

---

**¿Necesitas ayuda?**
Consulta `FASE2_README.md` para detalles técnicos o revisa los logs del servidor.

¡Disfruta jugando Parqués! 🎲🎉

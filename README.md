# 🎲 Parqués Distribuido

Juego multijugador de Parqués con servidor Python y cliente Unity (actualmente con cliente de consola funcional).

---

## 🚀 Inicio Rápido

### 1️⃣ Crear y activar entorno virtual

```bash
cd /home/seqenenra/Codes/DistParques
python3 -m venv env
source env/bin/activate  # En Windows: .\env\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ Iniciar el servidor

**Opción A - Script rápido:**
```bash
chmod +x run_server.sh
./run_server.sh
```

**Opción B - Manual:**
```bash
source env/bin/activate
python3 backend/servidor.py
```

Verás:
```
✅ Servidor escuchando en 0.0.0.0:5555
Esperando jugadores... (mínimo 2, máximo 4)
```

### 3️⃣ Conectar clientes (mínimo 2, máximo 4)

**En terminales diferentes:**

```bash
# Terminal 2 - Jugador 1
source env/bin/activate
python3 cliente/cliente_simple.py
# Ingresa tu nombre: Ana

# Terminal 3 - Jugador 2  
source env/bin/activate
python3 cliente/cliente_simple.py
# Ingresa tu nombre: Luis

# (Opcional) Terminal 4 y 5 para más jugadores...
```

### 4️⃣ Iniciar y jugar

**En cualquier terminal de cliente:**
```bash
> iniciar        # Inicia la partida (requiere 2+ jugadores)
```

**Cuando sea tu turno:**
```bash
> lanzar         # Lanza los dados
🎲 Dados: (4, 5) → Suma: 9

> fichas         # Ver tus fichas disponibles
📋 TUS FICHAS:
   ❌ Ficha 0: 🔒 En cárcel (necesita par)
   ✅ Ficha 1: 🎲 En posición 12
   ✅ Ficha 2: 🎲 En posición 25
   ❌ Ficha 3: 🏁 En la meta

# OPCIÓN 1: Mover con suma total
> mover 1        # Mueve ficha 1 con 9 casillas (4+5)

# OPCIÓN 2: Dividir dados en dos fichas
> dividir 1 4 2 5   # Ficha 1 con 4, ficha 2 con 5
```

---

## 🎮 Comandos del Cliente

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `iniciar` | Iniciar la partida (2-4 jugadores) | `> iniciar` |
| `lanzar` | Lanzar los dados | `> lanzar` |
| `mover N` | Mover ficha N con suma total | `> mover 0` |
| `dividir N1 D1 N2 D2` | Dividir dados en 2 fichas | `> dividir 0 3 1 5` |
| `fichas` | Ver estado de tus fichas | `> fichas` |
| `jugadores` | Ver jugadores conectados | `> jugadores` |
| `ayuda` | Mostrar ayuda | `> ayuda` |
| `salir` | Desconectar del servidor | `> salir` |

---

## 📋 Reglas del Juego (Implementadas)

### ✅ Reglas Básicas
- **2-4 jugadores** con 4 fichas cada uno
- **Lanzar 2 dados** en cada turno
- **Ganar:** Llevar las 4 fichas a la meta

### 🎲 Mecánicas de Dados
- **Par (ej: 3,3):** Lanzas de nuevo después de mover
- **Suma o División:** Puedes usar la suma (6) o dividir (3+3 en dos fichas)
- **3 pares consecutivos:** Penalización - tu ficha más adelantada vuelve a la cárcel

### 🔒 Salir de la Cárcel
- **Necesitas PAR** para sacar una ficha (ej: 4,4 o 6,6)
- Comando: `> mover N` donde N es la ficha en cárcel

### 🛡️ Seguros y Capturas
- **Seguros (12 casillas):** No puedes ser capturado
- **Captura:** Si caes en casilla con ficha rival (no seguro), la envías a su cárcel
- **Casilla de salida:** Es segura para tu color

### 🏁 Pasillo Final y Meta
- Al completar la vuelta, entras al **pasillo final** (8 casillas)
- Llegas a la **meta** y esa ficha queda inmóvil

---

## 📂 Estructura del Proyecto

```
DistParques/
├── backend/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ficha.py          # Clase Ficha con estados
│   │   ├── jugador.py        # Clase Jugador con fichas
│   │   ├── tablero.py        # Tablero con 68 casillas
│   │   └── partida.py        # Lógica del juego y turnos
│   ├── servidor.py            # Servidor TCP multi-cliente
│   └── cliente_consola.py     # Cliente de prueba (alternativo)
├── cliente/
│   ├── cliente_simple.py      # Cliente principal (RECOMENDADO)
│   └── cliente_consola.py     # Cliente alternativo
├── docs/
│   └── PROTOCOLO.md           # Protocolo JSON para Unity
├── requirements.txt           # Dependencias Python
├── run_server.sh             # Script para iniciar servidor
├── run_cliente.sh            # Script para iniciar cliente
└── README.md                 # Este archivo
```

---

## 🎯 Ejemplo de Partida Completa

```bash
# ========== TERMINAL 1 - SERVIDOR ==========
$ python3 backend/servidor.py
✅ Servidor escuchando en 0.0.0.0:5555
🔌 Nueva conexión desde ('127.0.0.1', 45678)
✅ Ana se unió como rojo
🔌 Nueva conexión desde ('127.0.0.1', 45679)
✅ Luis se unió como azul
🎮 Partida iniciada! Turno de Ana
🎲 Ana lanzó (4, 4)
🚶 Ana movió ficha 0: sacar_carcel
🎲 Ana lanzó (3, 5)
🚶 Ana movió ficha 0: mover
🎲 Luis lanzó (6, 6)
...

# ========== TERMINAL 2 - ANA ==========
$ python3 cliente/cliente_simple.py
📝 Tu nombre: Ana
✅ Conectado a 127.0.0.1:5555
🎨 Bienvenido Ana, eres rojo

────────────────────────────────────────────────────────────
👥 JUGADORES (2/4):
👉 rojo     - Ana              (TÚ)
     🏁0 🔒4 🎲0
   azul     - Luis            
     🏁0 🔒4 🎲0
⏳ Esperando inicio (mín. 2 jugadores)
────────────────────────────────────────────────────────────

> iniciar
============================================================
🎮 Partida iniciada. Turno de Ana
============================================================

⏰ ES TU TURNO, Ana! Escribe 'lanzar'

> lanzar
🎲 Dados: (4, 4) → Suma: 8
   ✨ ¡PAR! Puedes tirar de nuevo después de mover
   🔓 ¡Puedes SACAR DE LA CÁRCEL! Usa: mover N

📋 TUS FICHAS:
   ❌ Ficha 0: 🔒 En cárcel (necesita par)
   ❌ Ficha 1: 🔒 En cárcel (necesita par)
   ❌ Ficha 2: 🔒 En cárcel (necesita par)
   ❌ Ficha 3: 🔒 En cárcel (necesita par)

> mover 0
✅ Ficha sacada de la cárcel
   🎲 Sacaste PAR, lanza de nuevo!

> lanzar
🎲 Dados: (3, 5) → Suma: 8

📋 TUS FICHAS:
   ✅ Ficha 0: 🎲 En posición 5
   ❌ Ficha 1: 🔒 En cárcel (necesita par)
   ❌ Ficha 2: 🔒 En cárcel (necesita par)
   ❌ Ficha 3: 🔒 En cárcel (necesita par)

> mover 0
✅ Ficha movida
   ⏭️  Fin de turno

────────────────────────────────────────────────────────────
👥 JUGADORES (2/4):
   rojo     - Ana              (TÚ)
     🏁0 🔒3 🎲1
👉 azul     - Luis            
     🏁0 🔒4 🎲0
────────────────────────────────────────────────────────────

# ========== TERMINAL 3 - LUIS ==========
$ python3 cliente/cliente_simple.py
📝 Tu nombre: Luis
✅ Conectado a 127.0.0.1:5555
🎨 Bienvenido Luis, eres azul
...
⏰ ES TU TURNO, Luis! Escribe 'lanzar'

> lanzar
🎲 Dados: (2, 6) → Suma: 8
💡 Opciones:
   1. 'mover N'        - Mover ficha N con suma (8)
   2. 'dividir N1 D1 N2 D2' - Mover dos fichas separadas
      Ejemplo: dividir 0 2 1 6

> fichas
📋 TUS FICHAS:
   ❌ Ficha 0: 🔒 En cárcel (necesita par)
   ❌ Ficha 1: 🔒 En cárcel (necesita par)
   ❌ Ficha 2: 🔒 En cárcel (necesita par)
   ❌ Ficha 3: 🔒 En cárcel (necesita par)

> mover 0
❌ La ficha 0 está en la cárcel. Necesitas sacar PAR para liberarla.
💡 Intenta con otra ficha. Escribe 'fichas' para ver opciones

# (No tiene fichas fuera, turno pasa)
```

---

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'models'"
```bash
cd backend
python3 servidor.py
```

### Error: "Address already in use" (Puerto ocupado)
```bash
# Usar otro puerto
python3 servidor.py 0.0.0.0 5556
python3 cliente/cliente_simple.py 127.0.0.1 5556
```

### Error: "No se puede conectar al servidor"
- Verifica que el servidor esté corriendo primero
- Comprueba el puerto (por defecto 5555)
- Si es en otra máquina, usa su IP en lugar de 127.0.0.1

### El turno no cambia / No salen fichas de la cárcel
- **Para salir de cárcel:** DEBES sacar PAR (ej: 3,3 o 6,6)
- **Para cambiar turno:** DEBES ejecutar `mover N` después de `lanzar`
- Si no es par, el turno cambia automáticamente después de mover

---

## 🔌 Conexión desde Unity (Próxima Fase)

Ver `docs/PROTOCOLO.md` para detalles del protocolo JSON.

**Conexión básica en C#:**
```csharp
using System.Net.Sockets;
using System.Text;
using Newtonsoft.Json;

TcpClient client = new TcpClient("127.0.0.1", 5555);
NetworkStream stream = client.GetStream();

// Unirse
string joinMsg = "{\"tipo\":\"JOIN\",\"nombre\":\"Player1\"}\n";
byte[] data = Encoding.UTF8.GetBytes(joinMsg);
stream.Write(data, 0, data.Length);

// Leer respuesta
byte[] buffer = new byte[4096];
int bytes = stream.Read(buffer, 0, buffer.Length);
string response = Encoding.UTF8.GetString(buffer, 0, bytes);
```

---

## 🧪 Testing

```bash
# Ejecutar tests
pytest tests/

# Con cobertura
pytest --cov=backend tests/
```

---

## 📊 Checklist de Desarrollo

- [x] **Fase 1:** Diseño y planeación
- [x] **Fase 2:** Servidor Python completo
  - [x] Servidor TCP multi-cliente
  - [x] Lógica de turnos con sincronización
  - [x] Reglas del juego (dados, capturas, seguros)
  - [x] División de dados y movimientos flexibles
  - [x] Información de fichas disponibles
  - [x] Reintentos en caso de error
- [ ] **Fase 3:** Cliente Unity
- [ ] **Fase 4:** Integración y pruebas
- [ ] **Fase 5:** Extras (DB, bots, móvil)

---

## 🆕 Funcionalidades Nuevas (v2.0)

### ✨ División de Dados
Ahora puedes dividir el resultado de los dados en dos fichas diferentes:
```bash
> lanzar
🎲 Dados: (3, 5) → Suma: 8

# Opción 1: Mover una ficha con la suma
> mover 0        # Ficha 0 avanza 8 casillas

# Opción 2: Dividir entre dos fichas
> dividir 0 3 1 5   # Ficha 0 con 3, ficha 1 con 5
```

### 📊 Información de Fichas
Comando `fichas` muestra el estado detallado:
```bash
> fichas
📋 TUS FICHAS:
   ✅ Ficha 0: 🎲 En posición 12
   ❌ Ficha 1: 🔒 En cárcel (necesita par)
   ✅ Ficha 2: 🎲 En posición 34
   ❌ Ficha 3: 🏁 En la meta
```

### 🔄 Reintentos Inteligentes
Si eliges una ficha incorrecta, puedes intentar con otra:
```bash
> mover 0
❌ La ficha 0 está en la cárcel. Necesitas sacar PAR para liberarla.
💡 Intenta con otra ficha. Escribe 'fichas' para ver opciones

> mover 2        # Intentar con otra ficha
✅ Ficha movida
```

---

## 📞 Soporte

- **Protocolo JSON:** Ver `docs/PROTOCOLO.md`
- **Arquitectura:** Ver código en `backend/models/`
- **Ejemplos:** Ejecutar `python3 cliente/cliente_simple.py`

---

## 📝 Notas

- El servidor maneja hasta **4 jugadores simultáneos**
- Mínimo **2 jugadores** para iniciar
- Los dados se mantienen disponibles hasta que muevas, permitiendo reintentos
- Compatible con Unity mediante sockets TCP y protocolo JSON

---

**¡Disfruta el juego! 🎲🎉**

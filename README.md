# 🎲 Parqués - Sistema Distribuido

## ✅ Fases Completadas

### ✅ Fase 1: Diseño y Planeación
### ✅ Fase 2: Servidor TCP con Threading

---

## 🎮 Inicio Manual de Partida

**IMPORTANTE**: La partida ahora usa **inicio manual** por parte del anfitrión.

- El **primer jugador** que se conecta es el **anfitrión** 👑
- El anfitrión debe escribir **`iniciar`** cuando todos estén listos
- Se necesitan **mínimo 2 jugadores** para iniciar
- Ver guía completa en: [`INICIO_MANUAL.md`](INICIO_MANUAL.md)

---

## 🚀 Inicio Rápido

### 1. Iniciar Servidor
```powershell
py backend\servidor.py
```

### 2. Iniciar Clientes (2-4 jugadores)
```powershell
py cliente\cliente_consola.py
```

### 3. El Anfitrión Inicia
```
> iniciar
```

---

## 📦 Backend - Python

Se han implementado todas las clases principales del sistema:

#### 📦 Módulos Creados

```
backend/
└── models/
    ├── __init__.py          # Módulo de exportación
    ├── jugador.py           # Clase Jugador
    ├── ficha.py             # Clase Ficha
    ├── tablero.py           # Clase Tablero
    └── partida.py           # Clase Partida
```

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                         PARTIDA                              │
│  - Gestiona el juego completo                                │
│  - Control de turnos                                         │
│  - Validación de movimientos                                 │
│  - Detección de ganador                                      │
└────────────┬────────────────────────────────────────────────┘
             │
             ├──────────┬──────────┬──────────┬──────────┐
             ▼          ▼          ▼          ▼          ▼
        ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
        │JUGADOR 1│ │JUGADOR 2│ │JUGADOR 3│ │JUGADOR 4│
        │ (Rojo)  │ │ (Azul)  │ │(Amarillo│ │ (Verde) │
        └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
             │           │           │           │
        ┌────┴────┐ ┌────┴────┐ ┌────┴────┐ ┌────┴────┐
        │ Fichas  │ │ Fichas  │ │ Fichas  │ │ Fichas  │
        │(4 unid.)│ │(4 unid.)│ │(4 unid.)│ │(4 unid.)│
        └─────────┘ └─────────┘ └─────────┘ └─────────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │   TABLERO     │
                         │ - 68 casillas │
                         │ - Seguros     │
                         │ - Salidas     │
                         │ - Zonas final │
                         └───────────────┘
```

---

## 📋 Clases Implementadas

### 1. 🎮 `Jugador`
**Archivo:** `backend/models/jugador.py`

**Atributos:**
- `nombre` (str): Nombre del jugador
- `color` (ColorJugador): Color asignado (ROJO, AZUL, AMARILLO, VERDE)
- `fichas` (List[Ficha]): Lista de 4 fichas
- `turno` (bool): Indica si es su turno
- `id` (str): Identificador único

**Métodos principales:**
- `asignar_color()`: Asigna color y crea fichas
- `activar_turno()` / `desactivar_turno()`: Control de turnos
- `tiene_fichas_en_carcel()`: Verifica fichas en cárcel
- `todas_fichas_en_meta()`: Verifica condición de victoria
- `obtener_fichas_movibles()`: Obtiene fichas que pueden moverse
- `to_dict()`: Serialización a JSON

---

### 2. 🎯 `Ficha`
**Archivo:** `backend/models/ficha.py`

**Atributos:**
- `id` (int): Identificador (0-3)
- `color` (ColorJugador): Color de la ficha
- `posicion` (int): Posición en el tablero (-1 = cárcel)
- `estado` (EstadoFicha): CARCEL, ACTIVA, SEGURO, FINAL
- `pasos_recorridos` (int): Contador de pasos
- `en_recta_final` (bool): Si está en zona de llegada

**Métodos principales:**
- `esta_en_carcel()`, `esta_activa()`, `esta_en_seguro()`, `esta_en_final()`
- `sacar_de_carcel()`: Saca ficha al tablero
- `mover()`: Mueve a nueva posición
- `enviar_a_carcel()`: Devuelve a cárcel (cuando es comida)
- `marcar_como_final()`: Llega a meta
- `puede_moverse()`: Valida si puede moverse
- `puede_comer()`: Verifica si puede comer otra ficha

---

### 3. 🎲 `Tablero`
**Archivo:** `backend/models/tablero.py`

**Atributos:**
- `num_casillas` (int): 68 casillas en circuito principal
- `casillas` (List[dict]): Configuración de cada casilla
- `seguros` (List[int]): Posiciones seguras [5, 12, 22, 29, 39, 46, 56, 63]
- `salidas` (Dict): Posiciones de salida por color
- `entradas_finales` (Dict): Donde cada color entra a su zona final

**Configuración del tablero:**
- **Total de casillas:** 68 en circuito + 8 por cada zona final
- **Salidas:**
  - Rojo: casilla 5
  - Azul: casilla 22
  - Amarillo: casilla 39
  - Verde: casilla 56
- **Seguros:** Cada 17 casillas aproximadamente + salidas

**Métodos principales:**
- `obtener_posicion_salida()`: Obtiene salida por color
- `es_casilla_segura()`: Verifica si es seguro
- `calcular_nueva_posicion()`: Calcula movimiento
- `puede_llegar_a_meta()`: Verifica llegada exacta
- `verificar_colision()`: Detecta fichas enemigas
- `agregar_ficha_a_casilla()` / `remover_ficha_de_casilla()`

---

### 4. 🏆 `Partida`
**Archivo:** `backend/models/partida.py`

**Atributos:**
- `id` (str): Identificador de la partida
- `jugadores` (List[Jugador]): 2-4 jugadores
- `tablero` (Tablero): Tablero de juego
- `estado` (EstadoPartida): ESPERANDO, EN_CURSO, PAUSADA, FINALIZADA
- `turno_actual` (int): Índice del jugador actual
- `ganador` (Jugador): Jugador ganador
- `ultimo_dado` (int): Último valor lanzado
- `historial_movimientos` (List): Log de jugadas

**Métodos principales:**
- `agregar_jugador()`: Añade jugador y asigna color
- `iniciar_partida()`: Comienza el juego
- `lanzar_dado()`: Simula dado (1-6)
- `puede_sacar_de_carcel()`: Valida salida (5 o pares)
- `mover_ficha()`: Ejecuta movimiento con validaciones
- `pasar_turno()`: Cambia de jugador
- `otorgar_turno_extra()`: Por sacar 5, comer, etc.
- `finalizar_partida()`: Declara ganador

---

## 📡 Protocolo de Comunicación

**Archivo:** `docs/protocolo_mensajes.md`

Se ha documentado el flujo completo de mensajes JSON entre cliente y servidor:

### Mensajes Implementados:

1. **`JOIN`** → Cliente envía nombre
2. **`ASSIGN_COLOR`** → Servidor asigna color
3. **`START_GAME`** → Partida iniciada
4. **`ROLL`** → Lanzar dados
5. **`ROLL_RESULT`** → Resultado del dado
6. **`MOVE`** → Mover ficha
7. **`MOVE_SUCCESS`** / **`MOVE_ERROR`** → Resultado del movimiento
8. **`UPDATE`** → Estado del tablero actualizado
9. **`EATEN`** → Ficha comida
10. **`TURN_CHANGE`** → Cambio de turno
11. **`WIN`** → Jugador ganador
12. **`PLAYER_DISCONNECT`** → Desconexión
13. **`ERROR`** → Errores generales

### Códigos de Error Definidos:
- `PARTIDA_LLENA`
- `PARTIDA_NO_ENCONTRADA`
- `TURNO_INVALIDO`
- `MOVIMIENTO_INVALIDO`
- `FICHA_NO_ENCONTRADA`
- `DADO_NO_LANZADO`
- Y más...

---

## 🎯 Reglas del Juego Implementadas

### Salir de la Cárcel
- Se necesita sacar **5** o un **número par** (2, 4, 6, 8, 10, 12)
- Al sacar, la ficha va a la casilla de salida

### Movimiento
- Las fichas avanzan según el número del dado
- Al completar 68 casillas, entran a su zona final (8 casillas)
- Deben llegar **exactamente** a la meta

### Comer Fichas
- Una ficha puede comer fichas enemigas en la misma casilla
- **No se puede comer** en casillas seguras
- La ficha comida regresa a la cárcel
- Comer otorga **turno extra**

### Turnos Extra
Se otorga turno extra al:
- Sacar ficha de la cárcel (5 o par)
- Comer una ficha enemiga
- Meter una ficha en la meta

### Victoria
El primer jugador que meta sus **4 fichas** en la meta gana

---

## 🔄 Flujo de Ejemplo

```python
# Crear partida
partida = Partida("partida_1")

# Agregar jugadores
j1 = partida.agregar_jugador("Juan", "abc123")
j2 = partida.agregar_jugador("María", "def456")

# Iniciar partida
partida.iniciar_partida()

# Turno de Juan
dado = partida.lanzar_dado()  # Resultado: 5
resultado = partida.mover_ficha("abc123", 0, 5)  # Saca ficha 0

# Actualizar estado
estado = partida.to_dict()  # Para enviar a clientes
```

---

## 📊 Diagrama de Estados de una Ficha

```
    ┌─────────┐
    │  CARCEL │ (posición: -1)
    └────┬────┘
         │ (Lanzar 5 o par)
         ▼
    ┌─────────┐
    │  ACTIVA │ (en tablero)
    └────┬────┘
         │
         ├─────────────┐
         │             │
         ▼             ▼
    ┌─────────┐  ┌─────────┐
    │  SEGURO │  │ (comida)│
    └────┬────┘  └────┬────┘
         │            │
         │            └──────► CARCEL
         │
         ▼
    ┌───────────────┐
    │ RECTA FINAL   │ (8 casillas)
    └───────┬───────┘
            │
            ▼
    ┌─────────┐
    │  FINAL  │ (meta alcanzada)
    └─────────┘
```

---

## 🧪 Próximos Pasos (Fase 2)

- [ ] Implementar servidor WebSocket
- [ ] Crear gestor de partidas múltiples
- [ ] Implementar persistencia (base de datos)
- [ ] Crear API REST para consultas
- [ ] Implementar sistema de autenticación
- [ ] Agregar logging y monitoreo

---

## 📝 Uso de las Clases

### Importar módulos
```python
from backend.models import Jugador, Ficha, Tablero, Partida
from backend.models import ColorJugador, EstadoFicha, EstadoPartida
```

### Crear y gestionar partida
```python
# Crear nueva partida
partida = Partida("game_001", max_jugadores=4)

# Agregar jugadores
jugador1 = partida.agregar_jugador("Alice", "player_1")
jugador2 = partida.agregar_jugador("Bob", "player_2")

# Iniciar juego
if partida.iniciar_partida():
    print("¡Partida iniciada!")
    
# Jugar
dado = partida.lanzar_dado()
print(f"Resultado del dado: {dado}")

# Mover ficha
resultado = partida.mover_ficha("player_1", 0, dado)
if resultado["exito"]:
    print(resultado["mensaje"])
    
# Serializar estado
estado_json = partida.to_dict()
```

---

## 🎨 Enumeraciones Definidas

### `ColorJugador`
- `ROJO`
- `AZUL`
- `AMARILLO`
- `VERDE`

### `EstadoFicha`
- `CARCEL`
- `ACTIVA`
- `SEGURO`
- `FINAL`

### `EstadoPartida`
- `ESPERANDO`
- `EN_CURSO`
- `PAUSADA`
- `FINALIZADA`

---

## ✨ Características Implementadas

✅ Sistema completo de clases orientadas a objetos  
✅ Validación de movimientos  
✅ Detección de colisiones y "comer fichas"  
✅ Sistema de turnos con turnos extra  
✅ Seguimiento de estado completo  
✅ Serialización a JSON  
✅ Protocolo de comunicación documentado  
✅ Reglas completas del Parqués  
✅ Soporte para 2-4 jugadores  
✅ Historial de movimientos  

---

**Fecha de completación:** 19 de octubre de 2025  
**Estado:** ✅ Fase 1 Completada

# 🚀 Guía de Inicio Rápido - Parqués

## 📋 Requisitos Previos

### Instalar Python

Si Python no está instalado en tu sistema, descárgalo desde:
- **Windows/Mac/Linux:** https://www.python.org/downloads/
- Versión recomendada: Python 3.9 o superior

### Verificar instalación

Abre una terminal (PowerShell, CMD, o Terminal) y ejecuta:

```bash
python --version
```

o en algunos sistemas:

```bash
python3 --version
```

Deberías ver algo como: `Python 3.x.x`

---

## 📂 Estructura del Proyecto

```
DistParques/
│
├── backend/                    # Backend en Python
│   └── models/                # Clases principales
│       ├── __init__.py        # Módulo de exportación
│       ├── jugador.py         # Clase Jugador
│       ├── ficha.py           # Clase Ficha
│       ├── tablero.py         # Clase Tablero
│       └── partida.py         # Clase Partida
│
├── tests/                     # Tests unitarios
│   ├── __init__.py
│   └── test_models.py         # Tests de las clases
│
├── ejemplos/                  # Ejemplos de uso
│   └── ejemplo_uso.py         # Demostración completa
│
├── docs/                      # Documentación
│   └── protocolo_mensajes.md  # Protocolo cliente-servidor
│
├── .gitignore                 # Archivos ignorados por git
├── README.md                  # Documentación principal
└── requirements.txt           # Dependencias (vacío en Fase 1)
```

---

## 🏃 Ejecución Rápida

### 1. Navegar al directorio del proyecto

```bash
cd c:\Users\Seqen\OneDrive\Desktop\DistParques
```

### 2. Ejecutar el ejemplo de uso

```bash
python ejemplos/ejemplo_uso.py
```

Este script mostrará:
- ✅ Creación de una partida
- ✅ Agregado de jugadores
- ✅ Inicio de la partida
- ✅ Lanzamiento de dados
- ✅ Movimiento de fichas
- ✅ Serialización a JSON
- ✅ Simulación de varios turnos

### 3. Ejecutar los tests

```bash
python tests/test_models.py
```

Los tests verificarán:
- ✅ Creación de jugadores, fichas y tablero
- ✅ Asignación de colores
- ✅ Movimiento de fichas
- ✅ Reglas del juego (salir de cárcel, comer fichas, etc.)
- ✅ Gestión de turnos
- ✅ Serialización a JSON

---

## 💻 Uso Básico en Código

### Importar las clases

```python
from backend.models import Jugador, Ficha, Tablero, Partida
from backend.models import ColorJugador, EstadoFicha, EstadoPartida
```

### Crear una partida

```python
# Crear partida con ID único
partida = Partida("mi_partida_001", max_jugadores=4)

# Agregar jugadores
jugador1 = partida.agregar_jugador("Alice", "player_1")
jugador2 = partida.agregar_jugador("Bob", "player_2")

print(f"{jugador1.nombre} tiene el color {jugador1.color.value}")
# Salida: Alice tiene el color rojo
```

### Iniciar y jugar

```python
# Iniciar la partida (requiere mínimo 2 jugadores)
if partida.iniciar_partida():
    print("¡Partida iniciada!")
    
    # Obtener jugador actual
    jugador_actual = partida.obtener_jugador_actual()
    print(f"Turno de: {jugador_actual.nombre}")
    
    # Lanzar dado
    resultado_dado = partida.lanzar_dado()
    print(f"Dado: {resultado_dado}")
    
    # Verificar si puede sacar de la cárcel
    if partida.puede_sacar_de_carcel(resultado_dado):
        print("¡Puedes sacar una ficha de la cárcel!")
    
    # Mover ficha (ejemplo: ficha 0)
    resultado = partida.mover_ficha(
        id_jugador=jugador_actual.id,
        id_ficha=0,
        pasos=resultado_dado
    )
    
    if resultado["exito"]:
        print(f"✅ {resultado['mensaje']}")
        
        if resultado["turno_extra"]:
            print("¡Tienes un turno extra!")
    else:
        print(f"❌ {resultado['mensaje']}")
```

### Obtener estado en JSON

```python
# Convertir estado completo a diccionario
estado = partida.to_dict()

# Convertir a JSON
import json
estado_json = json.dumps(estado, indent=2, ensure_ascii=False)
print(estado_json)
```

---

## 🎮 Reglas del Juego Implementadas

### 🔓 Salir de la Cárcel
- Necesitas sacar **5** o un **número par** (2, 4, 6)
- Al sacar, la ficha va a tu casilla de salida
- Obtienes un turno extra

### 🎯 Movimiento
- Avanza según el número del dado
- Recorre 68 casillas en el circuito principal
- Luego entra a tu zona final (8 casillas más)
- Debes llegar **exactamente** a la meta

### 🏰 Casillas Seguras
- Posiciones: 5, 12, 22, 29, 39, 46, 56, 63
- Las fichas en seguros **no pueden ser comidas**
- Las salidas de cada color también son seguros

### 😈 Comer Fichas
- Si caes en la misma casilla que una ficha enemiga, la "comes"
- La ficha comida regresa a la cárcel
- Obtienes un turno extra
- No puedes comer fichas en seguros

### 🏆 Ganar
- El primer jugador que meta sus **4 fichas** en la meta gana
- Debes llegar exactamente (no puedes pasarte)

### 🔄 Turnos Extra
Se otorgan en estos casos:
- Sacar ficha de la cárcel (5 o par)
- Comer una ficha enemiga
- Meter una ficha en la meta

---

## 📊 Atributos Principales

### Jugador
- `nombre`: Nombre del jugador
- `color`: ColorJugador (ROJO, AZUL, AMARILLO, VERDE)
- `fichas`: Lista de 4 fichas
- `turno`: True si es su turno
- `id`: Identificador único

### Ficha
- `id`: 0-3 (identificador de la ficha)
- `posicion`: Posición en el tablero (-1 = cárcel)
- `estado`: EstadoFicha (CARCEL, ACTIVA, SEGURO, FINAL)
- `color`: ColorJugador
- `pasos_recorridos`: Contador de pasos

### Tablero
- `num_casillas`: 68 casillas
- `seguros`: Lista de posiciones seguras
- `salidas`: Posiciones de salida por color
- `casillas`: Lista de todas las casillas

### Partida
- `id`: Identificador único
- `jugadores`: Lista de 2-4 jugadores
- `tablero`: Tablero de juego
- `estado`: EstadoPartida (ESPERANDO, EN_CURSO, PAUSADA, FINALIZADA)
- `turno_actual`: Índice del jugador actual
- `ganador`: Jugador ganador (si aplica)

---

## 🔍 Métodos Útiles

### Partida
```python
partida.agregar_jugador(nombre, id)         # Agregar jugador
partida.iniciar_partida()                    # Iniciar juego
partida.lanzar_dado()                        # Lanzar dado
partida.mover_ficha(id_jugador, id_ficha, pasos)  # Mover
partida.pasar_turno()                        # Siguiente jugador
partida.obtener_jugador_actual()             # Jugador con turno
partida.to_dict()                            # Serializar a dict
```

### Jugador
```python
jugador.asignar_color(color)                 # Asignar color
jugador.activar_turno()                      # Activar turno
jugador.desactivar_turno()                   # Desactivar turno
jugador.tiene_fichas_en_carcel()             # Verificar fichas en cárcel
jugador.todas_fichas_en_meta()               # Verificar victoria
jugador.obtener_fichas_movibles(pasos)       # Fichas que pueden moverse
```

### Ficha
```python
ficha.sacar_de_carcel(posicion)              # Sacar de cárcel
ficha.mover(nueva_pos, es_seguro)            # Mover ficha
ficha.enviar_a_carcel()                      # Devolver a cárcel
ficha.marcar_como_final()                    # Llegar a meta
ficha.esta_en_carcel()                       # Verificar si está en cárcel
ficha.esta_activa()                          # Verificar si está activa
```

### Tablero
```python
tablero.obtener_posicion_salida(color)       # Obtener salida por color
tablero.es_casilla_segura(posicion)          # Verificar si es seguro
tablero.calcular_nueva_posicion(pos, pasos, color)  # Calcular movimiento
tablero.verificar_colision(pos, color)       # Detectar fichas enemigas
```

---

## 📖 Documentación Adicional

- **Protocolo de mensajes:** Ver `docs/protocolo_mensajes.md`
- **README principal:** Ver `README.md`
- **Ejemplos:** Ver `ejemplos/ejemplo_uso.py`

---

## 🐛 Solución de Problemas

### Python no encontrado
1. Instala Python desde https://www.python.org/downloads/
2. Durante la instalación, marca "Add Python to PATH"
3. Reinicia la terminal

### Errores de importación
Asegúrate de ejecutar los scripts desde el directorio raíz:
```bash
cd c:\Users\Seqen\OneDrive\Desktop\DistParques
python ejemplos/ejemplo_uso.py
```

### Tests fallan
Verifica que todos los archivos estén en su lugar:
```bash
backend/models/__init__.py
backend/models/jugador.py
backend/models/ficha.py
backend/models/tablero.py
backend/models/partida.py
```

---

## 🎯 Próximos Pasos

### Fase 2: Servidor y Comunicación
- [ ] Implementar servidor WebSocket
- [ ] Crear sistema de salas/partidas múltiples
- [ ] Implementar el protocolo de mensajes
- [ ] Agregar autenticación básica

### Fase 3: Frontend
- [ ] Crear interfaz gráfica
- [ ] Implementar cliente WebSocket
- [ ] Diseñar tablero visual
- [ ] Agregar animaciones

### Fase 4: Características Avanzadas
- [ ] Sistema de rankings
- [ ] Persistencia de partidas
- [ ] Replay de partidas
- [ ] Chat entre jugadores

---

## 📞 Soporte

Si encuentras algún problema o tienes preguntas:
1. Revisa la documentación en `README.md`
2. Consulta el protocolo en `docs/protocolo_mensajes.md`
3. Ejecuta los tests para verificar el funcionamiento

---

**¡Disfruta jugando Parqués! 🎲**

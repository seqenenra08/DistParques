# 🎲 Tablero de Parqués - Diseño y Estructura

## 📐 Disposición del Tablero

El tablero de Parqués tradicional tiene **68 casillas** en el circuito principal, distribuidas en forma de cruz. Cada color tiene:
- 1 casilla de salida
- 8 casillas en su zona final (recta a la meta)
- Varias casillas seguras

---

## 🎨 Distribución de Colores

```
         [AMARILLO]
              ↓
              39
         
    [VERDE] ← 56  →  22 → [AZUL]
              
              5
              ↑
           [ROJO]
```

### Posiciones de Salida (casillas seguras)
- 🔴 **Rojo:** Casilla 5
- 🔵 **Azul:** Casilla 22  
- 🟡 **Amarillo:** Casilla 39
- 🟢 **Verde:** Casilla 56

---

## 🏰 Casillas Seguras

Las casillas seguras son posiciones donde las fichas **no pueden ser comidas**:

```
Posiciones seguras: [5, 12, 22, 29, 39, 46, 56, 63]
```

### Distribución (cada ~8-9 casillas)
- Casilla 5: Salida Roja 🔴
- Casilla 12: Seguro intermedio
- Casilla 22: Salida Azul 🔵
- Casilla 29: Seguro intermedio
- Casilla 39: Salida Amarilla 🟡
- Casilla 46: Seguro intermedio
- Casilla 56: Salida Verde 🟢
- Casilla 63: Seguro intermedio

---

## 🔄 Recorrido de las Fichas

### Ejemplo: Ficha Roja 🔴

1. **Inicio:** Cárcel (posición -1)
2. **Salida:** Casilla 5 (al sacar 5 o par)
3. **Recorrido:** 5 → 6 → 7 → ... → 67 → 0 → 1 → 2 → 3 → 4
4. **Total en circuito:** 68 casillas (de 5 hasta dar la vuelta y llegar a 4)
5. **Entrada a zona final:** Después de 68 pasos
6. **Zona final:** 8 casillas adicionales
7. **Meta:** Casilla final #8 de la zona

### Representación Visual del Recorrido

```
                    ┌─────────────────┐
                    │   ZONA FINAL    │
                    │  (8 casillas)   │
                    │                 │
                    │   1→2→3→4→5     │
                    │         ↓       │
                    │     META 8←7←6  │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
         ┌──────────┤   CIRCUITO      │
         │          │   PRINCIPAL     │
    SALIDA (pos 5)  │  (68 casillas)  │
         │          │                 │
         └──────────┤                 │
                    └─────────────────┘
```

---

## 📊 Mapa Completo de Casillas

### Segmento 1: Casillas 0-16 (Zona Roja)
```
0   1   2   3   4   [5]  6   7   8   9   10  11  [12] 13  14  15  16
                    🔴                               🏰
```
- Casilla 5: Salida Roja + Seguro
- Casilla 12: Seguro

### Segmento 2: Casillas 17-33 (Zona Azul)
```
17  18  19  20  21  [22] 23  24  25  26  27  28  [29] 30  31  32  33
                    🔵                               🏰
```
- Casilla 22: Salida Azul + Seguro
- Casilla 29: Seguro

### Segmento 3: Casillas 34-50 (Zona Amarilla)
```
34  35  36  37  38  [39] 40  41  42  43  44  45  [46] 47  48  49  50
                    🟡                               🏰
```
- Casilla 39: Salida Amarilla + Seguro
- Casilla 46: Seguro

### Segmento 4: Casillas 51-67 (Zona Verde)
```
51  52  53  54  55  [56] 57  58  59  60  61  62  [63] 64  65  66  67
                    🟢                               🏰
```
- Casilla 56: Salida Verde + Seguro
- Casilla 63: Seguro

---

## 🎯 Zonas Finales (Rectas a la Meta)

Cada color tiene su propia zona final de **8 casillas** que lleva a la meta:

### 🔴 Zona Final Roja
```
Entrada (después de 68 pasos desde casilla 5)
↓
[1] → [2] → [3] → [4] → [5] → [6] → [7] → [8] META 🏆
```

### 🔵 Zona Final Azul
```
Entrada (después de 68 pasos desde casilla 22)
↓
[1] → [2] → [3] → [4] → [5] → [6] → [7] → [8] META 🏆
```

### 🟡 Zona Final Amarilla
```
Entrada (después de 68 pasos desde casilla 39)
↓
[1] → [2] → [3] → [4] → [5] → [6] → [7] → [8] META 🏆
```

### 🟢 Zona Final Verde
```
Entrada (después de 68 pasos desde casilla 56)
↓
[1] → [2] → [3] → [4] → [5] → [6] → [7] → [8] META 🏆
```

---

## 📏 Cálculos de Movimiento

### Fórmula para calcular nueva posición
```python
# En el circuito principal (antes de entrar a zona final)
nueva_posicion = (posicion_actual + pasos) % 68

# Pasos totales desde la salida
pasos_desde_salida = calcular_pasos_desde_salida(posicion_actual, color)

# Entrar a zona final cuando pasos_desde_salida >= 68
if pasos_desde_salida >= 68:
    entrar_zona_final = True
    pasos_en_final = pasos_desde_salida - 68
```

### Ejemplo de Recorrido Completo (Ficha Roja)

```
Pasos  | Posición | Estado
-------|----------|------------------
0      | -1       | En cárcel
+5     | 5        | Salida (casilla 5)
+3     | 8        | Activa
+6     | 14       | Activa
+4     | 18       | Activa
...    | ...      | ...
68     | 4        | Última casilla del circuito
+1     | Final 1  | En zona final
+7     | Final 8  | META 🏆
```

---

## 🎮 Características Especiales del Tablero

### 1. Casillas de Salida
- Son **seguras** (no se puede comer)
- Punto de entrada desde la cárcel
- Se accede con 5 o número par

### 2. Casillas Seguras Intermedias
- Distribuidas estratégicamente cada ~8-9 casillas
- Protegen las fichas de ser comidas
- Permiten estrategias defensivas

### 3. Circuito Circular
- 68 casillas en total
- Modular: después de la 67 viene la 0
- Cada jugador da la vuelta completa antes de su zona final

### 4. Zona Final (Recta)
- 8 casillas exclusivas por color
- No circular (del 1 al 8)
- Se debe llegar **exactamente** a la meta
- No se puede ser comido aquí

---

## 🔢 Tabla de Referencia Rápida

| Elemento | Cantidad | Descripción |
|----------|----------|-------------|
| Casillas circuito | 68 | Casillas compartidas |
| Casillas zona final | 8 × 4 = 32 | 8 por cada color |
| Casillas seguras | 8 | En circuito principal |
| Salidas | 4 | Una por color |
| Fichas por jugador | 4 | Total de 16 fichas |
| Jugadores | 2-4 | Mínimo 2, máximo 4 |

---

## 📍 Matriz de Posiciones Críticas

### Para Jugador Rojo 🔴
- **Salida:** 5
- **Última casilla circuito:** 4
- **Entrada zona final:** Después de pasar por casilla 4
- **Casillas seguras en ruta:** 5, 12, 22, 29, 39, 46, 56, 63

### Para Jugador Azul 🔵
- **Salida:** 22
- **Última casilla circuito:** 21
- **Entrada zona final:** Después de pasar por casilla 21
- **Casillas seguras en ruta:** 22, 29, 39, 46, 56, 63, 5, 12

### Para Jugador Amarillo 🟡
- **Salida:** 39
- **Última casilla circuito:** 38
- **Entrada zona final:** Después de pasar por casilla 38
- **Casillas seguras en ruta:** 39, 46, 56, 63, 5, 12, 22, 29

### Para Jugador Verde 🟢
- **Salida:** 56
- **Última casilla circuito:** 55
- **Entrada zona final:** Después de pasar por casilla 55
- **Casillas seguras en ruta:** 56, 63, 5, 12, 22, 29, 39, 46

---

## 🎲 Diagrama de Estados del Tablero

```
┌─────────────────────────────────────────────────────────┐
│                    TABLERO DE PARQUÉS                   │
│                                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │ Cárcel  │  │ Cárcel  │  │ Cárcel  │  │ Cárcel  │   │
│  │  Roja   │  │  Azul   │  │Amarilla │  │  Verde  │   │
│  │  (4)    │  │  (4)    │  │  (4)    │  │  (4)    │   │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │
│       │            │            │            │         │
│       ↓            ↓            ↓            ↓         │
│  ┌────────────────────────────────────────────────┐    │
│  │       CIRCUITO PRINCIPAL (68 casillas)        │    │
│  │  ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐    │    │
│  │  │0 │1 │2 │..│67│                      │    │    │
│  │  └──┴──┴──┴──┴──┘  Casillas compartidas│    │    │
│  │          ↓                              │    │    │
│  │     [Seguros: 5, 12, 22, 29,           │    │    │
│  │               39, 46, 56, 63]          │    │    │
│  └────────────────────────────────────────────────┘    │
│       │            │            │            │         │
│       ↓            ↓            ↓            ↓         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │  Final  │  │  Final  │  │  Final  │  │  Final  │   │
│  │  Rojo   │  │  Azul   │  │Amarillo │  │  Verde  │   │
│  │  (8)    │  │  (8)    │  │  (8)    │  │  (8)    │   │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │
│       │            │            │            │         │
│       ↓            ↓            ↓            ↓         │
│     META 🏆      META 🏆      META 🏆      META 🏆    │
└─────────────────────────────────────────────────────────┘
```

---

## 🧮 Código de Ejemplo: Navegando el Tablero

```python
from backend.models import Tablero, ColorJugador

# Crear tablero
tablero = Tablero()

# Obtener posición de salida para rojo
salida_roja = tablero.obtener_posicion_salida(ColorJugador.ROJO)
print(f"Salida roja: {salida_roja}")  # 5

# Verificar si una casilla es segura
es_seguro = tablero.es_casilla_segura(12)
print(f"Casilla 12 es segura: {es_seguro}")  # True

# Calcular nueva posición
# Ficha roja en casilla 60, avanza 8 pasos
nueva_pos, entro_final = tablero.calcular_nueva_posicion(
    posicion_actual=60,
    pasos=8,
    color=ColorJugador.ROJO,
    en_recta_final=False
)
print(f"Nueva posición: {nueva_pos}")  # 0 (60 + 8 = 68, 68 % 68 = 0)
```

---

**Implementado en:** `backend/models/tablero.py`

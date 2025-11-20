# 🔍 ANÁLISIS DEL JUEGO - Problemas y Guía de Uso

## 🐛 PROBLEMAS ENCONTRADOS

### ❌ PROBLEMA 1: Las capturas NO funcionan correctamente

**Ubicación**: `backend/models/partida.py` - método `_mover_ficha()`

**El problema**:
```python
# Línea ~380 en partida.py
if not es_seguro:
    capturadas = self.tablero.verificar_captura(ficha.posicion, ficha)
    for capturada in capturadas:
        capturada.capturar()
        self.tablero.remover_ficha(ficha.posicion, capturada)
    
    return capturadas
```

**¿Por qué NO funciona?**
La lógica de captura solo se ejecuta si la casilla NO es segura. Sin embargo, hay varios problemas:

1. **La ficha que se mueve se agrega ANTES de verificar capturas**:
   ```python
   self.tablero.agregar_ficha(ficha.posicion, ficha)  # Se agrega primero
   
   # Luego verifica capturas
   if not es_seguro:
       capturadas = self.tablero.verificar_captura(ficha.posicion, ficha)
   ```
   
   Pero en `tablero.verificar_captura()`:
   ```python
   def verificar_captura(self, posicion: int, ficha_movida) -> List:
       fichas_en_casilla = self.obtener_fichas_en(posicion)  # ¡Ya incluye la que recién se movió!
       capturadas = []
       
       for ficha in fichas_en_casilla:
           if ficha.color != ficha_movida.color and ficha.id != ficha_movida.id:
               capturadas.append(ficha)
   ```

2. **El problema es el orden**: La ficha se agrega al tablero ANTES de buscar capturas, entonces cuando busca fichas en esa casilla, la ficha que acaba de llegar YA está ahí.

3. **La verificación por ID no es suficiente**: Compara `ficha.id != ficha_movida.id`, pero dos fichas de diferentes jugadores pueden tener el mismo ID (0, 1, 2, 3).

### ❌ PROBLEMA 2: Fichas en META pueden seguir moviéndose

**Ubicación**: `backend/models/partida.py` - método `obtener_fichas_disponibles()`

**El código dice**:
```python
elif ficha.esta_en_meta():
    info["descripcion"] = "🏁 En la meta"
    info["puede_mover"] = False  # ✅ Dice que NO puede moverse
```

**Pero en `procesar_turno()`**:
```python
if id_ficha is not None:
    ficha = jugador.fichas[id_ficha]
    
    # Solo verifica si está en cárcel
    if ficha.esta_en_carcel():
        return {"error": "..."}
    
    # ❌ NO verifica si está en META antes de mover
    if not jugador.puede_mover(id_ficha, suma_dados):
        return {"error": "..."}
```

Y en `jugador.puede_mover()`:
```python
def puede_mover(self, id_ficha: int, dados: int) -> bool:
    ficha = self.fichas[id_ficha]
    
    if ficha.esta_en_carcel():
        return False
    
    # ✅ Verifica si está en meta
    if ficha.esta_en_meta():
        return False
    
    return True
```

**Entonces debería funcionar... pero**:
El problema es que `puede_mover()` SÍ lo valida, pero el mensaje de error es genérico y no dice "La ficha ya está en la meta".

### ❌ PROBLEMA 3: No hay validación de fichas en meta en movimiento dividido

**Ubicación**: `backend/models/partida.py` - método `procesar_turno_dividido()`

```python
for mov in movimientos:
    id_ficha = mov["id_ficha"]
    valor = mov["valor_dado"]
    
    ficha = jugador.fichas[id_ficha]
    if ficha.esta_en_carcel():
        # ✅ Valida cárcel
        ...
    else:
        # ❌ NO valida si está en META
        if not jugador.puede_mover(id_ficha, valor):
            return {"error": f"No puedes mover la ficha {id_ficha}"}
```

Aunque llama a `puede_mover()` que sí valida, el mensaje es confuso.

### ⚠️ PROBLEMA 4: Lógica de entrada al pasillo final confusa

**En `tablero.py`**:
```python
ENTRADAS_PASILLO = {"rojo": 63, "azul": 12, "amarillo": 29, "verde": 46}
```

**Pero en `partida.py`** el código que maneja esto está en `_mover_ficha()`:
```python
# Verificar si debe entrar al pasillo final
casillas_totales = ficha.casillas_recorridas + casillas

if casillas_totales >= 68:
    # Entra al pasillo final
    ...
```

Usa `casillas_recorridas >= 68` en lugar de verificar si llegó a la casilla de entrada del pasillo.

---

## 📋 CÓMO FUNCIONA EL JUEGO ACTUALMENTE

### 🎮 Paso a Paso para Jugar

#### 1️⃣ **Iniciar el Servidor**
```bash
cd /home/seqenenra/Codes/DistParques
python3 backend/servidor.py
```

Verás:
```
✅ Servidor escuchando en 0.0.0.0:5555
Esperando jugadores... (mínimo 2, máximo 4)
```

#### 2️⃣ **Conectar Jugadores** (mínimo 2, máximo 4)

**Terminal 2 - Jugador 1:**
```bash
cd /home/seqenenra/Codes/DistParques
python3 cliente/cliente_simple.py
```
- Ingresa nombre: `Ana`
- Te asigna color: `ROJO`
- Todas las fichas empiezan en la **cárcel** (🔒)

**Terminal 3 - Jugador 2:**
```bash
python3 cliente/cliente_simple.py
```
- Ingresa nombre: `Luis`
- Te asigna color: `AZUL`

**Terminal 4 y 5 (opcional) - Jugadores 3 y 4:**
```bash
python3 cliente/cliente_simple.py
```

#### 3️⃣ **Iniciar la Partida**

En **cualquier terminal de cliente**:
```
> iniciar
```

Verás:
```
============================================================
🎮 Partida iniciada. Turno de Ana
============================================================
```

#### 4️⃣ **Turno de Juego** (cuando sea tu turno)

##### **A. Lanzar Dados**
```
> lanzar
```

Posibles resultados:

**Si sacas PAR (ej: 4, 4) y tienes fichas en cárcel:**
```
🎲 Dados: (4, 4) → Suma: 8
   ✨ ¡PAR! Puedes tirar de nuevo después de mover
   🔓 ¡Puedes SACAR DE LA CÁRCEL! Usa: mover N
```

**Si sacas NO-PAR (ej: 3, 5) y todas en cárcel:**
```
🎲 Dados: (3, 5) → Suma: 8
   🔒 Todas tus fichas están en la cárcel - necesitas PAR
   ⏭️  Turno perdido automáticamente
```
*(El turno pasa automáticamente al siguiente jugador)*

**Si sacas dados normales (tienes fichas fuera):**
```
🎲 Dados: (2, 5) → Suma: 7
   💡 Opciones:
   1. 'mover N'        - Mover ficha N con suma (7)
   2. 'dividir N1 D1 N2 D2' - Mover dos fichas separadas
```

##### **B. Ver Tus Fichas**
```
> fichas
```

Verás:
```
📋 TUS FICHAS:
   ❌ Ficha 0: 🔒 En cárcel (necesita par para salir)
   ✅ Ficha 1: 🎲 En posición 12
   ✅ Ficha 2: 🎲 En posición 34
   ❌ Ficha 3: 🏁 En la meta
```

- ✅ = Puede moverse
- ❌ = No puede moverse

##### **C. Mover una Ficha**

**Opción 1: Mover con la suma total**
```
> mover 1
```
Mueve la ficha 1 con la suma de los dados (ej: 7 casillas).

**Opción 2: Dividir dados entre dos fichas**
```
> dividir 1 2 2 5
```
- Ficha 1 se mueve 2 casillas
- Ficha 2 se mueve 5 casillas

##### **D. Estados de las Fichas**

1. **🔒 CÁRCEL**: 
   - Empieza aquí
   - Solo sale con PAR (ej: 3,3 o 5,5)
   - Al salir va a su casilla de salida

2. **🎲 EN TABLERO**:
   - Moviéndose por las 68 casillas
   - Puede ser capturada (si no está en seguro)

3. **🏃 PASILLO FINAL**:
   - Últimas 8 casillas antes de la meta
   - Después de completar 68 casillas del tablero

4. **🏁 META**:
   - Ficha terminó
   - No puede moverse más

##### **E. Reglas Importantes**

**PAR (dados iguales):**
- ✨ Sacas PAR (ej: 4,4) → Puedes lanzar de nuevo después de mover
- Si todas tus fichas están en cárcel y NO sacas PAR → Pierdes turno automáticamente

**TRES PARES CONSECUTIVOS:**
- Si sacas 3 pares seguidos → Penalización
- Tu ficha más adelantada regresa a la cárcel
- Pierdes el turno

**CAPTURA** (⚠️ Actualmente tiene BUG):
- Si caes en una casilla con ficha enemiga (no seguro)
- La ficha enemiga regresa a su cárcel
- Actualmente NO funciona correctamente

**CASILLAS SEGURAS** (🛡️):
- No puedes ser capturado aquí
- Casillas: 5, 12, 17, 22, 29, 34, 39, 46, 51, 56, 63, 0

**LLEGAR EXACTO A LA META:**
- Debes caer EXACTO en la casilla 8 del pasillo final
- Si te pasas, NO puedes mover esa ficha

#### 5️⃣ **Ganar el Juego**

El primer jugador que lleve **las 4 fichas a la META** gana:
```
🏆 ¡Ana GANÓ!
```

---

## 🎯 EJEMPLO DE PARTIDA COMPLETA

```
[SERVIDOR TERMINAL]
✅ Servidor escuchando en 0.0.0.0:5555
🔌 Nueva conexión desde ('127.0.0.1', 45678)
✅ Ana se unió como rojo
🔌 Nueva conexión desde ('127.0.0.1', 45679)
✅ Luis se unió como azul
🎮 Partida iniciada! Turno de Ana
🎲 Ana lanzó (5, 5)
🚶 Ana movió ficha 0: sacar_carcel
🎲 Ana lanzó (3, 4)
🚶 Ana movió ficha 0: mover
⏭️  Turno de Luis
🎲 Luis lanzó (2, 2)
🚶 Luis movió ficha 1: sacar_carcel
...
```

```
[CLIENTE ANA TERMINAL]
📝 Tu nombre: Ana
✅ Conectado a 127.0.0.1:5555
🎨 Bienvenido Ana, eres rojo

────────────────────────────────────────────────────────────
👥 JUGADORES (2/4):
   rojo     - Ana              (TÚ)
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

🎲 Dados: (5, 5) → Suma: 10
   ✨ ¡PAR! Puedes tirar de nuevo después de mover
   🔓 ¡Puedes SACAR DE LA CÁRCEL!

📋 TUS FICHAS:
   ❌ Ficha 0: 🔒 En cárcel (necesita par)
   ❌ Ficha 1: 🔒 En cárcel (necesita par)
   ❌ Ficha 2: 🔒 En cárcel (necesita par)
   ❌ Ficha 3: 🔒 En cárcel (necesita par)

> mover 0

✅ Ficha sacada de la cárcel
   🎲 Sacaste PAR, lanza de nuevo!

> lanzar

🎲 Dados: (3, 4) → Suma: 7

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
```

---

## 🔧 RESUMEN DE COMANDOS DEL CLIENTE

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `iniciar` | Inicia la partida | `> iniciar` |
| `lanzar` | Lanza los dados | `> lanzar` |
| `mover N` | Mueve ficha N (0-3) | `> mover 0` |
| `dividir N1 D1 N2 D2` | Divide dados | `> dividir 0 3 1 5` |
| `fichas` | Ve tus fichas | `> fichas` |
| `jugadores` | Ve jugadores | `> jugadores` |
| `ayuda` | Muestra ayuda | `> ayuda` |
| `salir` | Desconectar | `> salir` |

---

## 🚨 BUGS QUE NECESITAN CORRECCIÓN

### 1. Corregir Sistema de Capturas
- **Prioridad**: ALTA 🔴
- **Problema**: Las fichas no se capturan cuando caen en la misma casilla
- **Archivos afectados**: `backend/models/partida.py`, `backend/models/tablero.py`

### 2. Mensajes más claros para fichas en META
- **Prioridad**: MEDIA 🟡
- **Problema**: El mensaje de error es genérico
- **Solución**: Agregar validación explícita antes de `puede_mover()`

### 3. Validar META en movimiento dividido
- **Prioridad**: MEDIA 🟡
- **Problema**: No valida si la ficha ya está en meta al dividir dados
- **Archivo afectado**: `backend/models/partida.py`

### 4. Clarificar lógica de entrada al pasillo
- **Prioridad**: BAJA 🟢
- **Problema**: Código confuso sobre cuándo entrar al pasillo final
- **Funciona**: Sí, pero es difícil de mantener

---

## 📝 NOTAS PARA TU AMIGO

- **El juego funciona** pero tiene bugs en las capturas
- **La lógica principal está en** `backend/models/partida.py`
- **Las fichas se manejan en** `backend/models/ficha.py`
- **El tablero se gestiona en** `backend/models/tablero.py`
- **Los clientes se conectan vía TCP** y hablan con JSON
- **No hay base de datos**, todo está en memoria

### Estructura del Proyecto:
```
backend/
├── servidor.py          # Servidor TCP (maneja conexiones)
└── models/
    ├── partida.py      # Lógica del juego (IMPORTANTE)
    ├── ficha.py        # Estados de las fichas
    ├── tablero.py      # Tablero 68 casillas
    └── jugador.py      # Datos del jugador

cliente/
├── cliente_simple.py   # Cliente de consola (texto)
└── cliente_dashboard.py # Cliente visual (curses)
```

### Protocolo de Mensajes (JSON):
- `JOIN` → Unirse a partida
- `START` → Iniciar partida
- `ROLL` → Lanzar dados
- `MOVE` → Mover ficha
- `GET_STATE` → Obtener estado

¡Espero que esto ayude! 🎲✨

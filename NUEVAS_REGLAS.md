# 🎲 Nuevas Reglas Implementadas - Parqués Distribuido

## 📋 Resumen

Este documento describe las nuevas reglas tradicionales del Parqués que se han implementado en el juego distribuido.

---

## 🎯 1. Selección de Turno por Dados

### Descripción
Al inicio de la partida, todos los jugadores lanzan **un solo dado** para determinar quién comienza.

### Mecánica
- Cada jugador lanza automáticamente un dado al iniciarse la partida
- **El jugador con el número más alto** comienza el juego
- En caso de **empate**, los jugadores empatados vuelven a lanzar hasta desempatar
- Los resultados se muestran en tiempo real a todos los jugadores

### Implementación
```python
# Servidor determina automáticamente el orden
partida.lanzar_dado_inicio(jugador)
# Cuando todos lanzaron:
partida._determinar_primer_turno()
```

### Mensajes del Cliente
```
🎲 SELECCIÓN DE TURNO:
   Ana lanzó: 6
   Luis lanzó: 4
   Pedro lanzó: 6
   
🔄 Empate entre Ana y Pedro, lanzando de nuevo...
   Ana lanzó: 3
   Pedro lanzó: 5
   
✅ Pedro comienza el juego!
```

---

## 🎯 2. Primer Turno con 3 Oportunidades

### Descripción
Cuando un jugador gana el turno inicial, tiene **3 oportunidades** para sacar sus fichas de la cárcel.

### Mecánica
- El jugador puede lanzar los dados **hasta 3 veces**
- En cada lanzamiento busca sacar **PAR** (dados iguales)
- Si saca par, puede sacar una ficha de la cárcel
- Si no saca par en las 3 oportunidades, **pierde el turno**
- Esta regla solo aplica en el **primer turno** de cada jugador

### Comandos
```bash
> lanzar          # Intento 1
🎲 (3, 5) - No es par. Te quedan 2 intentos.

> lanzar          # Intento 2
🎲 (2, 4) - No es par. Te queda 1 intento.

> lanzar          # Intento 3
🎲 (1, 6) - Se agotaron las oportunidades. Turno perdido.
```

```bash
> lanzar          # Con suerte
🎲 (4, 4) - ¡PAR! Saca una ficha.

> mover 0         # Sacar ficha 0 de la cárcel
✅ Ficha sacada. Puedes lanzar de nuevo.
```

### Implementación
```python
# En jugador.py
jugador.es_primer_turno = True
jugador.intentos_primer_turno = 0
jugador.max_intentos_primer_turno = 3

# En partida.py
if jugador.es_primer_turno:
    jugador.incrementar_intento_primer_turno()
    if not es_par and jugador.agotar_intentos_primer_turno():
        # Cambiar turno
```

---

## ⚡ 3. Regla de 3 Pares Consecutivos

### Descripción
Si un jugador saca **3 pares consecutivos** en sus lanzamientos, puede sacar una ficha del juego directamente a la meta.

### Mecánica
- Cada vez que sacas **par**, se incrementa un contador
- Al llegar a **3 pares seguidos**, se activa la regla especial
- Puedes **elegir una ficha** para enviarla directamente a la meta
- Es una **bonificación** por tu suerte con los dados
- El contador se resetea si no sacas par

### Comandos
```bash
> lanzar
🎲 (5, 5) - PAR! Puedes lanzar de nuevo. Pares consecutivos: 1

> lanzar
🎲 (3, 3) - PAR! Puedes lanzar de nuevo. Pares consecutivos: 2

> lanzar
🎲 (6, 6) - ¡3 PARES CONSECUTIVOS!
   Puedes sacar una ficha del juego directamente a la meta.

> sacar 2         # Sacar ficha 2 del juego
✅ Ficha 2 enviada directamente a la meta!
```

### Implementación
```python
# En jugador.py
jugador.pares_consecutivos = 0

def incrementar_pares(self):
    self.pares_consecutivos += 1

def tiene_tres_pares(self) -> bool:
    return self.pares_consecutivos >= 3

# En partida.py
if es_par(dados):
    jugador.incrementar_pares()
    if jugador.tiene_tres_pares():
        # Permitir sacar ficha del juego
        self.jugador_puede_sacar_ficha = jugador
        return {"accion": "tres_pares_sacar_ficha"}
```

---

## 🔐 4. Control de Lanzamientos

### Descripción
Sistema para prevenir que un jugador lance los dados múltiples veces sin mover fichas.

### Mecánica
- Solo puedes lanzar **una vez por turno** (excepto con pares)
- Si sacas **par**, puedes lanzar de nuevo después de mover
- No puedes lanzar múltiples veces sin mover
- En el **primer turno** puedes lanzar hasta 3 veces

### Validaciones
```python
# En servidor.py
if not jugador.es_su_turno:
    return {"error": "No es tu turno"}

if not jugador.puede_lanzar():
    return {"error": "Ya lanzaste los dados. Debes mover primero."}
```

### Flags de Control
```python
# En jugador.py
jugador.ya_lanzo_dados = False          # Marca si lanzó este turno
jugador.puede_lanzar_de_nuevo = False   # Permite relanzar por par

def marcar_lanzamiento(self):
    """Marca que lanzó los dados."""
    if self.puede_lanzar_de_nuevo:
        self.puede_lanzar_de_nuevo = False  # Consumir permiso
    self.ya_lanzo_dados = True

def permitir_lanzar_de_nuevo(self):
    """Permite lanzar por sacar par."""
    self.puede_lanzar_de_nuevo = True
```

### Escenarios
```bash
# Escenario 1: Sin par
> lanzar
🎲 (3, 5)
> lanzar
❌ Ya lanzaste los dados. Debes mover primero.

# Escenario 2: Con par
> lanzar
🎲 (4, 4) - PAR!
> mover 0
✅ Ficha movida
> lanzar          # Permitido por el par
🎲 (2, 6)
> lanzar          # NO permitido
❌ Ya lanzaste los dados. Debes mover primero.
```

---

## 📊 Casos de Prueba

### Test 1: Selección de Turno
```bash
cd /home/seqenenra/Codes/DistParques
python3 test_dados_inicio.py
```
- ✅ 4 jugadores lanzan dado de inicio
- ✅ Se selecciona el de mayor número
- ✅ Manejo de empates

### Test 2: Primer Turno
```bash
python3 test_nuevas_reglas.py
```
- ✅ 3 oportunidades para sacar par
- ✅ Pérdida de turno si no saca par
- ✅ Sacar ficha con par en primer turno

### Test 3: 3 Pares Consecutivos
```bash
python3 test_nuevas_reglas.py
```
- ✅ Contador de pares consecutivos
- ✅ Sacar ficha del juego con 3 pares
- ✅ Reseteo del contador sin par

### Test 4: Control de Lanzamientos
```bash
python3 test_control_lanzamientos.py
python3 test_servidor_lanzamientos.py
```
- ✅ Bloqueo de lanzamientos múltiples
- ✅ Permiso de relanzar con pares
- ✅ Validación en servidor

---

## 🔧 Archivos Modificados

### Backend
- `backend/models/jugador.py`
  - Añadidos atributos: `es_primer_turno`, `intentos_primer_turno`, `ya_lanzo_dados`, `puede_lanzar_de_nuevo`
  - Nuevos métodos: `puede_lanzar()`, `marcar_lanzamiento()`, `permitir_lanzar_de_nuevo()`, `resetear_lanzamiento()`

- `backend/models/partida.py`
  - Método `lanzar_dado_inicio()` para selección de turno
  - Método `_determinar_primer_turno()` con manejo de empates
  - Lógica de primer turno en `procesar_turno()`
  - Regla de 3 pares consecutivos
  - Control de lanzamientos integrado

- `backend/servidor.py`
  - Endpoint `ROLL_INICIO` para dados de inicio
  - Validación `puede_lanzar()` en `procesar_roll()`
  - Endpoint `SACAR_FICHA_JUEGO` para 3 pares
  - Broadcast de mensajes `SELECCION_TURNO`, `DADO_INICIO`, `TURNO_DETERMINADO`

### Cliente
- `cliente/cliente_simple.py`
  - Manejo de mensajes de selección de turno
  - Comando `sacar N` para 3 pares
  - Visualización de intentos restantes en primer turno

---

## 📝 Mensajes del Protocolo

### SELECCION_TURNO
```json
{
  "tipo": "SELECCION_TURNO",
  "mensaje": "Lanzando dados para determinar el orden..."
}
```

### DADO_INICIO
```json
{
  "tipo": "DADO_INICIO",
  "jugador": "Ana",
  "dado": 6,
  "mensaje": "Ana lanzó 6"
}
```

### TURNO_DETERMINADO
```json
{
  "tipo": "TURNO_DETERMINADO",
  "jugador": "Ana",
  "mensaje": "Ana comienza el juego!",
  "dados_inicio": {"ana": 6, "luis": 4}
}
```

### TRES_PARES_SACAR_FICHA
```json
{
  "tipo": "DICE_RESULT",
  "dados": [6, 6],
  "es_par": true,
  "accion": "tres_pares_sacar_ficha",
  "mensaje": "¡3 pares consecutivos! Elige una ficha para sacar del juego."
}
```

---

## 🎮 Guía Rápida para Usuarios

### 1. Inicio del Juego
1. Conectar al menos 2 jugadores
2. Escribir `iniciar` en cualquier cliente
3. Todos lanzan automáticamente un dado
4. El jugador con mayor número comienza

### 2. Primer Turno
1. El jugador inicial tiene 3 intentos
2. Escribir `lanzar` hasta sacar par
3. Con par, escribir `mover N` para sacar ficha
4. Si no saca par en 3 intentos, pierde turno

### 3. Pares Consecutivos
1. Sacar par 3 veces seguidas
2. Aparece mensaje: "¡3 pares consecutivos!"
3. Escribir `sacar N` para enviar ficha a meta
4. La ficha llega directamente sin pasar por el tablero

### 4. Lanzamientos Controlados
1. Solo puedes lanzar una vez por turno
2. Con par, puedes lanzar de nuevo después de mover
3. No puedes lanzar sin mover primero
4. El servidor valida automáticamente

---

## ✅ Estado de Implementación

| Regla | Estado | Test |
|-------|--------|------|
| Selección de turno por dados | ✅ Completo | ✅ Passing |
| Manejo de empates | ✅ Completo | ✅ Passing |
| Primer turno 3 oportunidades | ✅ Completo | ✅ Passing |
| 3 pares consecutivos | ✅ Completo | ✅ Passing |
| Control de lanzamientos | ✅ Completo | ✅ Passing |
| Validación en servidor | ✅ Completo | ✅ Passing |
| Mensajes al cliente | ✅ Completo | ✅ Passing |

---

## 🐛 Bugs Solucionados

### Bug #1: Lanzamientos Múltiples
**Problema:** El jugador podía escribir "lanzar" múltiples veces sin mover fichas.

**Solución:** Sistema de flags `ya_lanzo_dados` y `puede_lanzar_de_nuevo` con validación en servidor.

**Test:** `test_servidor_lanzamientos.py` - ✅ Passing

---

## 📚 Referencias

- **Reglas tradicionales del Parqués:** Basado en reglas colombianas estándar
- **Protocolo de comunicación:** Ver `docs/protocolo_mensajes.md`
- **Tests:** Ver `test_*` en directorio raíz

---

**Última actualización:** Diciembre 2024  
**Versión:** 2.1.0

# Bug Corregido: Par no detectado en último intento con todas las fichas en cárcel

## 📋 Descripción del Bug

Cuando un jugador tenía todas sus fichas en la cárcel y sacaba un **par en el tercer (último) intento**, el juego **NO detectaba el par** y el jugador perdía su turno injustamente.

### Síntomas
- ✅ Intentos 1 y 2 sin par: funcionaban correctamente
- ❌ Intento 3 CON par: se procesaba como "intentos agotados"
- ❌ El jugador perdía el turno aunque había sacado par
- ❌ No se permitía sacar una ficha de la cárcel

## 🔍 Causa del Bug

El bug estaba en el archivo `/backend/servidor.py`, líneas 246-254:

```python
# CÓDIGO ANTIGUO (CON BUG)
if todas_en_carcel and not es_par:
    resultado = self.partida.procesar_turno(jugador, dados, None)
    resultado["tipo"] = "DICE_RESULT"
    
    if resultado.get('cambio_turno'):
        print(f"⏭️  {jugador.nombre} perdió el turno (intentos agotados)")
        self.broadcast_estado()
    
    return resultado

# Verificar si puede sacar de cárcel con par
puede_sacar = es_par and jugador.tiene_fichas_en_carcel()

return {
    "tipo": "DICE_RESULT",
    ...
}
```

### Problema
El servidor solo llamaba a `procesar_turno()` cuando **NO** se sacaba par. Cuando SÍ se sacaba par, simplemente retornaba sin procesar, lo que causaba:

1. ❌ El contador `intentos_carcel` **NO se incrementaba**
2. ❌ El contador **NO se reseteaba** al sacar par
3. ❌ El estado del jugador quedaba inconsistente

## ✅ Solución

Se modificó el código para que **SIEMPRE** llame a `procesar_turno()` cuando todas las fichas están en cárcel:

```python
# CÓDIGO CORREGIDO
if todas_en_carcel:
    # Procesar el turno para que se actualice el contador de intentos
    resultado = self.partida.procesar_turno(jugador, dados, None)
    resultado["tipo"] = "DICE_RESULT"
    
    if resultado.get('cambio_turno'):
        print(f"⏭️  {jugador.nombre} perdió el turno (intentos agotados)")
        self.broadcast_estado()
    
    return resultado
```

### Ventajas de la solución
✅ La lógica de intentos se maneja consistentemente en `partida.py`
✅ El contador se incrementa correctamente en cada intento
✅ El contador se resetea cuando se saca par
✅ El par se detecta correctamente en cualquier intento (1, 2 o 3)

## 🧪 Tests de Verificación

Se crearon múltiples tests para verificar la corrección:

### Test 1: `test_bug_par_ultimo_intento.py`
Verifica el escenario básico: 3 intentos y par en el tercero.

### Test 2: `test_bug_servidor.py`
Simula el flujo completo del servidor con la lógica actualizada.

### Test 3: `test_caso_limite_intentos.py`
Verifica dos casos límite:
- **Caso 1**: Par exactamente cuando `intentos_carcel = 2`
- **Caso 2**: NO par cuando `intentos_carcel = 2` (debe agotar intentos)

## 📊 Flujo Correcto Después de la Corrección

### Escenario: Todas las fichas en cárcel

```
Intento 1: Dados (3, 5) - NO par
  └─> incrementar_intento_carcel() → intentos = 1
  └─> Mensaje: "Te quedan 2 intentos"
  └─> NO cambiar turno

Intento 2: Dados (2, 4) - NO par
  └─> incrementar_intento_carcel() → intentos = 2
  └─> Mensaje: "Te quedan 1 intento"
  └─> NO cambiar turno

Intento 3: Dados (5, 5) - ¡PAR!
  └─> incrementar_intento_carcel() → intentos = 3
  └─> Detectar par → resetear_intentos_carcel() → intentos = 0
  └─> Mensaje: "¡Sacaste par! Ahora saca una ficha"
  └─> permitir_lanzar_de_nuevo()
  └─> NO cambiar turno
  
  Usuario: "mover 0"
  └─> Sacar ficha 0 de la cárcel
  └─> ¡Puede lanzar de nuevo!
```

### Escenario alternativo: NO par en el tercer intento

```
Intento 3: Dados (3, 5) - NO par
  └─> incrementar_intento_carcel() → intentos = 3
  └─> agotar_intentos_carcel() → True
  └─> Mensaje: "No sacaste par en 3 intentos. Turno perdido."
  └─> resetear_intentos_carcel() → intentos = 0
  └─> cambiar_turno()
```

## 🎯 Archivos Modificados

- **`/backend/servidor.py`** (líneas 246-254)
  - Cambio: Procesar turno SIEMPRE cuando todas las fichas están en cárcel

## ✅ Estado

**BUG CORREGIDO Y VERIFICADO** ✅

Fecha de corrección: 2 de diciembre de 2025

# Fix: Par en Tercer Intento - Cliente No Detectaba la Acción

## 📋 Problema Reportado

Cuando un jugador tiene todas sus fichas en la cárcel y saca un **par en el tercer (último) intento**, el cliente (bot) **no permitía sacar la ficha**.

## 🔍 Diagnóstico

### Backend (Servidor) ✅
El backend **funcionaba correctamente**:
- Detectaba el par en el tercer intento
- Reseteaba el contador de intentos
- Retornaba `accion: "par_sacar_carcel"` correctamente
- Permitía sacar la ficha cuando se enviaba MOVE

### Cliente (Bot) ❌
El bot **no manejaba correctamente** la respuesta `"par_sacar_carcel"`:
- Recibía el mensaje `DICE_RESULT` con `accion="par_sacar_carcel"`
- Pero no tenía lógica específica para manejar esta acción
- Trataba de procesar como un turno normal
- No enviaba el comando MOVE para sacar la ficha

## ✅ Solución Implementada

Se modificó el archivo `/cliente/bot_jugador.py` para manejar correctamente las acciones cuando todas las fichas están en cárcel.

### Cambios en el Manejo de `DICE_RESULT`

**ANTES:**
```python
elif tipo == "DADOS" or tipo == "DICE_RESULT":
    # ...
    if msg.get("accion") == "sin_movimiento":
        print(f"   ⏭️  Turno perdido automáticamente")
        self.es_mi_turno = False
        return
    
    # Tomar decisión de movimiento
    threading.Timer(self.retraso_decision, self.decidir_movimiento).start()
```

**DESPUÉS:**
```python
elif tipo == "DADOS" or tipo == "DICE_RESULT":
    # ...
    accion = msg.get("accion")
    
    # Manejo específico para fichas en cárcel
    if accion == "sin_par_carcel":
        print(f"   🔒 Sin par - {msg.get('mensaje', 'Intenta de nuevo')}")
        return  # El turno continúa, puede lanzar de nuevo
    
    elif accion == "intentos_agotados":
        print(f"   ❌ {msg.get('mensaje', 'Se agotaron los intentos')}")
        self.es_mi_turno = False
        return
    
    elif accion == "par_sacar_carcel":
        print(f"   🎉 {msg.get('mensaje', '¡Sacaste par! Sacando ficha...')}")
        # ✅ NUEVA LÓGICA: Decidir qué ficha sacar y enviar MOVE
        threading.Timer(self.retraso_decision, self.decidir_movimiento).start()
        return
    
    # Si sin movimientos válidos, saltar turno
    if msg.get("sin_movimientos") or accion == "sin_movimiento":
        print(f"   ⏭️  Sin movimientos válidos - Turno perdido")
        self.es_mi_turno = False
        return
    
    # Decisión de movimiento normal
    threading.Timer(self.retraso_decision, self.decidir_movimiento).start()
```

### Mejoras en el Manejo de `MOVE_RESULT`

Se mejoró el manejo de errores y la detección de cuándo puede lanzar de nuevo:

```python
elif tipo == "RESULTADO" or tipo == "MOVE_RESULT":
    accion = msg.get("accion")
    
    if accion == "sacar_carcel":
        print(f"   🔓 Ficha sacada de la cárcel")
        if msg.get("mensaje"):
            print(f"   💬 {msg.get('mensaje')}")
    
    # ✅ MEJORADO: Mejor detección de error
    elif msg.get("error"):
        print(f"   ⚠️  Error: {msg.get('error')}")
        if self.es_mi_turno:
            print(f"   🔄 Intentando acción alternativa...")
            threading.Timer(self.retraso_decision, self.decidir_movimiento).start()
        return
    
    # ✅ MEJORADO: Detección más robusta de poder lanzar de nuevo
    es_par = msg.get("es_par", False)
    cambio_turno = msg.get("cambio_turno", False)
    puede_lanzar = ("lanzar de nuevo" in msg.get("mensaje", "").lower() or 
                    "puedes lanzar" in msg.get("mensaje", "").lower())
    
    if (es_par and not cambio_turno) or puede_lanzar:
        print(f"   🔄 Sacamos PAR, lanzando de nuevo...")
        self.lanzamiento_pendiente = True
        self.dados_actuales = None
        threading.Timer(self.retraso_entre_acciones, self.lanzar_dados).start()
    else:
        self.es_mi_turno = False
        self.lanzamiento_pendiente = False
```

## 📊 Flujo Correcto Ahora

### Escenario: Todas las fichas en cárcel, tercer intento es par

```
┌─────────────────────────────────────────────────────────────────┐
│ INTENTO 1: Dados (2, 5) - NO par                               │
└─────────────────────────────────────────────────────────────────┘
  Servidor → Bot: {tipo: "DICE_RESULT", accion: "sin_par_carcel"}
  Bot procesa: "Sin par, esperando siguiente intento"
  Bot NO envía MOVE ✅

┌─────────────────────────────────────────────────────────────────┐
│ INTENTO 2: Dados (3, 6) - NO par                               │
└─────────────────────────────────────────────────────────────────┘
  Servidor → Bot: {tipo: "DICE_RESULT", accion: "sin_par_carcel"}
  Bot procesa: "Sin par, esperando siguiente intento"
  Bot NO envía MOVE ✅

┌─────────────────────────────────────────────────────────────────┐
│ INTENTO 3: Dados (5, 5) - ¡PAR!                                │
└─────────────────────────────────────────────────────────────────┘
  Servidor → Bot: {tipo: "DICE_RESULT", accion: "par_sacar_carcel"}
  Bot procesa: "¡Sacaste par! Debo sacar una ficha"
  Bot llama a decidir_movimiento() ✅
  Bot identifica ficha en cárcel (ej: ficha 0) ✅
  
  Bot → Servidor: {tipo: "MOVE", id_ficha: 0, dados: [5, 5]}
  Servidor procesa: sacar_ficha_carcel(jugador, 0) ✅
  
  Servidor → Bot: {tipo: "MOVE_RESULT", accion: "sacar_carcel", 
                   mensaje: "Puedes lanzar de nuevo"}
  Bot procesa: "Ficha sacada, detecta 'lanzar de nuevo'" ✅
  Bot → Servidor: {tipo: "ROLL"} para lanzar de nuevo ✅
```

## 🧪 Tests Creados

### `test_bug_tercer_intento_par.py`
Verifica que:
- ✅ El servidor detecta el par en el tercer intento
- ✅ El contador se resetea correctamente
- ✅ Se retorna `accion="par_sacar_carcel"`
- ✅ Se puede sacar la ficha con MOVE

### `test_integracion_bot_tercer_par.py`
Simula el flujo completo bot-servidor:
- ✅ Bot recibe 3 mensajes DICE_RESULT
- ✅ Bot solo responde al tercer mensaje (par)
- ✅ Bot envía MOVE correctamente
- ✅ Bot recibe confirmación y puede lanzar de nuevo

## 📁 Archivos Modificados

1. **`/cliente/bot_jugador.py`**
   - Líneas 148-175: Manejo mejorado de `DICE_RESULT`
   - Líneas 177-212: Manejo mejorado de `MOVE_RESULT`
   - Nueva lógica para detectar `"par_sacar_carcel"`
   - Mejor manejo de errores con reintentos

## ✅ Verificación

Todos los tests pasan exitosamente:
```
✅ test_bug_par_ultimo_intento.py - Backend correcto
✅ test_bug_servidor.py - Servidor correcto  
✅ test_bug_tercer_intento_par.py - Flujo servidor correcto
✅ test_integracion_bot_tercer_par.py - Integración bot completa
```

## 🎯 Estado Final

**PROBLEMA RESUELTO** ✅

- Backend: Funcionaba correctamente (sin cambios)
- Cliente/Bot: Ahora maneja correctamente `"par_sacar_carcel"`
- Integración: Flujo completo funciona como se espera

Fecha: 2 de diciembre de 2025

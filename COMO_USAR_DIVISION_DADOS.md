# Cómo usar la División de Dados

## ✅ Implementación Completa

La funcionalidad de división de dados ya está **completamente implementada** tanto en el backend como en el frontend.

## 🎮 Cómo Funciona

### 1. Cuando Puedes Dividir Dados

Puedes dividir los dados cuando:
- ✅ Sacas dados **diferentes** (por ejemplo: 2 y 4, no 3 y 3)
- ✅ Tienes **al menos 2 fichas** fuera de la cárcel
- ✅ Ambos dados pueden mover fichas diferentes

### 2. Cómo Activar el Modo División

Cuando lanzas los dados y cumples las condiciones, verás:

```
Dados: 2 y 4. Puedes dividirlos o usar la suma (6)
```

Y aparecerá un botón: **✂️ Dividir dados**

### 3. Proceso de División

1. **Haz clic en "✂️ Dividir dados"**
   - Se activa el modo división
   - Aparece un indicador: "🎯 Modo división activo"

2. **Selecciona la primera ficha**
   - El mensaje te dirá: "Selecciona una ficha para moverla X casillas"
   - Haz clic en la ficha que quieres mover

3. **Selecciona la segunda ficha**
   - El mensaje cambia: "Ahora selecciona otra ficha para moverla Y casillas"
   - Haz clic en una **ficha diferente**
   - ⚠️ No puedes usar la misma ficha dos veces

4. **Automático**
   - El movimiento se envía automáticamente al servidor
   - Ambas fichas se mueven simultáneamente

### 4. Cancelar División

Si cambias de opinión:
- Haz clic en **❌ Cancelar**
- Vuelves al modo normal
- Puedes seleccionar una ficha y elegir entre los valores individuales o la suma

## 📋 Ejemplo Práctico

### Escenario
Tienes 2 fichas rojas fuera de la cárcel:
- Ficha 0 en posición 10
- Ficha 1 en posición 20

Lanzas los dados: **2 y 5**

### Opción A: Usar la suma (modo normal)
- Haz clic en una ficha
- Selecciona "7" en el menú
- La ficha se mueve 7 casillas

### Opción B: Dividir dados (modo nuevo)
1. Haz clic en "✂️ Dividir dados"
2. Haz clic en Ficha 0 → se mueve 2 casillas (posición 12)
3. Haz clic en Ficha 1 → se mueve 5 casillas (posición 25)

**Ventaja**: Puedes posicionar dos fichas estratégicamente en lugar de mover solo una.

## 🛡️ Validaciones

El sistema previene errores:
- ❌ No puedes mover la misma ficha dos veces
- ❌ No puedes usar valores que no corresponden a los dados
- ❌ No puedes dividir pares (3 y 3)
- ❌ Solo funciona si tienes fichas disponibles para ambos valores

## 🔧 Detalles Técnicos

### Backend
- Endpoint: `MOVE_DIVIDIDO`
- Función: `procesar_turno_dividido()`
- Validaciones automáticas de reglas

### Frontend
- Nuevos estados: `splitMode`, `splitMovements`, `canSplitDice`
- Botón de activación con estilos CSS
- Indicador visual de progreso
- Manejo automático de mensajes

## 📝 Notas

- La división de dados es **opcional**
- Si prefieres el modo clásico, simplemente ignora el botón "✂️ Dividir dados"
- El modo división se cancela automáticamente si hay un error
- Los bots aún no usan división estratégica (próxima mejora)

## 🎯 Estado Actual

✅ Backend: Completamente funcional
✅ Frontend: UI implementada y funcional
✅ Validaciones: Todas las reglas implementadas
✅ Tests: `test_division_dados.py` verifica correctamente

**¡La funcionalidad está lista para usar!** 🎉

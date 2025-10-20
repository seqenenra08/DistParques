# ⚡ REINICIAR Y PROBAR - Guía Rápida

## 🔴 IMPORTANTE: Debes Reiniciar el Servidor

Todos los problemas están corregidos, pero **DEBES reiniciar el servidor** para que los cambios surtan efecto.

---

## 🚀 Pasos para Reiniciar

### 1. Cerrar Todo lo Anterior

En cada terminal que tengas abierto:
- Presiona **Ctrl + C** para detener el proceso
- O simplemente **cierra la ventana**

### 2. Iniciar Servidor Nuevo

**Opción A - Terminal PowerShell:**
```powershell
cd C:\Users\Seqen\OneDrive\Desktop\DistParques
py backend\servidor.py
```

**Opción B - Script .bat:**
```
Doble clic en: iniciar_servidor.bat
```

Deberías ver:
```
INFO - Servidor inicializado en 0.0.0.0:5555
INFO - Servidor iniciado en 0.0.0.0:5555
Esperando conexiones en 0.0.0.0:5555...
```

### 3. Iniciar Cliente 1 (Anfitrión)

**Nueva terminal PowerShell:**
```powershell
cd C:\Users\Seqen\OneDrive\Desktop\DistParques
py cliente\cliente_consola.py
```

**Ingresar:**
```
📝 Ingresa tu nombre: Juan
🎮 ID de partida: [Enter]
```

**Verás:**
```
👑 ERES EL ANFITRIÓN DE ESTA PARTIDA
   💡 Cuando todos los jugadores estén listos, escribe 'iniciar' para comenzar
```

### 4. Iniciar Cliente 2

**Nueva terminal PowerShell:**
```powershell
cd C:\Users\Seqen\OneDrive\Desktop\DistParques
py cliente\cliente_consola.py
```

**Ingresar:**
```
📝 Ingresa tu nombre: Maria
🎮 ID de partida: [Enter]
```

### 5. Iniciar Partida

**En el terminal de Juan (Cliente 1):**
```
> iniciar
```

**Deberías ver en AMBOS clientes:**
```
============================================================
🎮 ¡LA PARTIDA HA COMENZADO!
============================================================

👥 Jugadores:
   - Juan (rojo)
   - Maria (azul)

🎯 Turno inicial: Juan

💡 ¡Es tu turno! Escribe 'lanzar' para tirar los dados
```

✅ **Si ves esto, todo funciona correctamente!**

---

## 🎮 Pruebas a Realizar

### Prueba 1: Turno Perdido (Sin Fichas Movibles)

**Quien tenga el turno:**
```
> lanzar
```

**Si NO sale par (no puedes sacar fichas):**
```
🎲 Dados: 1 + 2 = 3
   ⚠️ No hay fichas movibles. Turno perdido.

➡️ Es el turno de Maria
```

✅ **Verificar:** El turno cambió automáticamente

### Prueba 2: Turno con Par (Puedes Sacar)

```
> lanzar
🎲 Dados: 4 + 4 = 8
   ¡PAR! Puedes sacar ficha de la cárcel

📍 Fichas movibles: [0, 1, 2, 3]

> mover 0
✅ Ficha salió de la cárcel
   🎉 ¡Turno extra!
```

✅ **Verificar:** Puedes lanzar de nuevo (turno extra)

### Prueba 3: Turno Normal

```
> lanzar
🎲 Dados: 3 + 5 = 8

📍 Fichas movibles: [0]

> mover 0
✅ Ficha movida correctamente

➡️ Es el turno de Juan
```

✅ **Verificar:** El turno cambió al otro jugador

---

## ❓ Preguntas de Verificación

### ✅ ¿La partida inicia al escribir `iniciar`?
- **Sí** → ✅ Fix del deadlock funciona
- **No** → ❌ Reinicia el servidor

### ✅ ¿El turno cambia cuando no hay fichas movibles?
- **Sí** → ✅ Fix del cambio automático funciona
- **No** → ❌ Reinicia el servidor

### ✅ ¿Aparece el mensaje "Es el turno de..."?
- **Sí** → ✅ Broadcast de TURN_CHANGE funciona
- **No** → ❌ Reinicia el servidor

### ✅ ¿Puedes lanzar cuando NO es tu turno?
- **No (muestra error)** → ✅ Validación funciona
- **Sí** → ❌ Hay un problema

---

## 🐛 Si Algo Falla

### Síntoma: "La partida aún no ha comenzado" después de `iniciar`
**Solución:**
1. Cierra el servidor (Ctrl+C)
2. Cierra todos los clientes
3. Inicia servidor de nuevo
4. Inicia clientes de nuevo
5. Intenta de nuevo

### Síntoma: "No es turno de nadie"
**Solución:**
1. **Asegúrate de que reiniciaste el servidor**
2. Si persiste, revisa los logs del servidor

### Síntoma: El mismo jugador puede lanzar múltiples veces
**Solución:**
1. **Asegúrate de que reiniciaste el servidor**
2. El código actualizado previene esto

---

## 📋 Checklist Final

Antes de contactar soporte, verifica:

- [ ] Cerraste todos los terminales anteriores
- [ ] Reiniciaste el servidor con el código actualizado
- [ ] Usaste `py backend\servidor.py` (no otro comando)
- [ ] El servidor muestra "Esperando conexiones..."
- [ ] Los clientes se conectan sin error
- [ ] El anfitrión ve el mensaje de "ERES EL ANFITRIÓN"

---

## 🎉 Todo Funciona

Si todas las pruebas pasan:
- ✅ Sistema funcional al 100%
- ✅ Puedes jugar partidas completas
- ✅ Todos los problemas corregidos

---

## 📞 Comandos de Referencia Rápida

```powershell
# Servidor
cd C:\Users\Seqen\OneDrive\Desktop\DistParques
py backend\servidor.py

# Cliente (ejecutar 2-4 veces)
cd C:\Users\Seqen\OneDrive\Desktop\DistParques
py cliente\cliente_consola.py
```

---

**¡Listo para jugar! 🎲**

# 🎮 Guía de Inicio Manual de Partida

## 📋 Cambio Importante

La partida **ya NO inicia automáticamente**. Ahora el **jugador anfitrión** (el primero que se conecta) debe iniciarla manualmente usando el comando `iniciar`.

---

## 🚀 Cómo Funciona Ahora

### 1️⃣ Primer Jugador (Anfitrión)

El primer jugador en conectarse se convierte en el **anfitrión** de la partida.

**Al conectarse verá:**
```
✅ Te has unido a la partida
   Tu ID: player_1

👑 ERES EL ANFITRIÓN DE ESTA PARTIDA
   💡 Cuando todos los jugadores estén listos, escribe 'iniciar' para comenzar

🎨 Color asignado: ROJO
   Jugadores en partida: 1/4

💡 Comandos disponibles:
   iniciar     - Iniciar la partida (solo anfitrión)
   lanzar      - Lanzar los dados
   mover <N>   - Mover la ficha N (0-3)
   estado      - Ver estado actual
   ayuda       - Mostrar comandos
   salir       - Salir del juego
```

### 2️⃣ Otros Jugadores

Los jugadores que se conectan después verán:
```
✅ Te has unido a la partida
   Tu ID: player_2

🎨 Color asignado: AZUL
   Jugadores en partida: 2/4

💡 Comandos disponibles:
   lanzar      - Lanzar los dados
   mover <N>   - Mover la ficha N (0-3)
   estado      - Ver estado actual
   ayuda       - Mostrar comandos
   salir       - Salir del juego
```

**Todos los jugadores verán cuando alguien más se une:**
```
👤 Bob (azul) se unió a la partida
   Jugadores: 2
   💡 Escribe 'iniciar' cuando estés listo para comenzar  ← (solo el anfitrión ve esto)
```

### 3️⃣ Iniciar la Partida

**Solo el anfitrión puede escribir:**
```
> iniciar
```

O la forma corta:
```
> i
```

**Requisitos para iniciar:**
- ✅ Mínimo **2 jugadores** conectados
- ✅ Solo el **anfitrión** puede iniciar
- ✅ La partida debe estar en estado **ESPERANDO**

---

## 📝 Ejemplo Completo Paso a Paso

### Terminal 1 (Servidor)
```powershell
PS C:\Users\Seqen\OneDrive\Desktop\DistParques> py backend\servidor.py

2025-10-19 22:00:00 - INFO - Servidor inicializado en 0.0.0.0:5555
2025-10-19 22:00:00 - INFO - Servidor iniciado en 0.0.0.0:5555
Esperando conexiones en 0.0.0.0:5555...
```

### Terminal 2 (Cliente 1 - Anfitrión)
```powershell
PS C:\Users\Seqen\OneDrive\Desktop\DistParques> py cliente\cliente_consola.py

🎲 Cliente de Parqués - Conectando a localhost:5555...
✅ Conectado al servidor

================================================
🎲 PARQUÉS - CLIENTE DE CONSOLA
================================================

📝 Ingresa tu nombre: Alice
🎮 ID de partida (Enter para 'default'): 

✅ Te has unido a la partida
   Tu ID: player_1

👑 ERES EL ANFITRIÓN DE ESTA PARTIDA
   💡 Cuando todos los jugadores estén listos, escribe 'iniciar' para comenzar

🎨 Color asignado: ROJO
   Jugadores en partida: 1/4

💡 Comandos disponibles:
   iniciar     - Iniciar la partida (solo anfitrión)
   lanzar      - Lanzar los dados
   mover <N>   - Mover la ficha N (0-3)
   estado      - Ver estado actual
   ayuda       - Mostrar comandos
   salir       - Salir del juego

> 
```

Alice espera a que lleguen más jugadores...

### Terminal 3 (Cliente 2)
```powershell
PS C:\Users\Seqen\OneDrive\Desktop\DistParques> py cliente\cliente_consola.py

🎲 Cliente de Parqués - Conectando a localhost:5555...
✅ Conectado al servidor

📝 Ingresa tu nombre: Bob
🎮 ID de partida (Enter para 'default'): 

✅ Te has unido a la partida
   Tu ID: player_2

🎨 Color asignado: AZUL
   Jugadores en partida: 2/4

> 
```

### En Terminal 2 (Alice) aparece:
```
👤 Bob (azul) se unió a la partida
   Jugadores: 2
   💡 Escribe 'iniciar' cuando estés listo para comenzar

> 
```

### Alice inicia la partida:
```
> iniciar
🎮 Iniciando partida...
```

### Ambos clientes ven:
```
============================================================
🎮 ¡LA PARTIDA HA COMENZADO!
============================================================

👥 Jugadores:
   - Alice (rojo)
   - Bob (azul)

🎯 Turno inicial: Alice

💡 ¡Es tu turno! Escribe 'lanzar' para tirar los dados

> 
```

---

## ⚠️ Mensajes de Error

### Si no eres anfitrión:
```
> iniciar
❌ Solo el anfitrión puede iniciar la partida
```

### Si no hay suficientes jugadores:
```
> iniciar
🎮 Iniciando partida...
❌ Error al iniciar: Se necesitan al menos 2 jugadores
```

### Si la partida ya inició:
```
> iniciar
❌ La partida ya ha sido iniciada
```

### Si intentas jugar antes de iniciar:
```
> lanzar
❌ La partida aún no ha comenzado
   💡 Escribe 'iniciar' para comenzar
```

---

## 🎯 Comandos del Anfitrión

El anfitrión tiene un comando adicional:

| Comando | Descripción | Cuándo usar |
|---------|-------------|-------------|
| `iniciar` o `i` | Inicia la partida | Cuando haya al menos 2 jugadores |
| `lanzar` o `l` | Lanza los dados | Durante su turno (después de iniciar) |
| `mover <N>` o `m <N>` | Mueve la ficha N | Después de lanzar dados |
| `estado` o `e` | Ver estado | En cualquier momento |
| `ayuda` o `h` | Ver comandos | En cualquier momento |
| `salir` | Salir del juego | En cualquier momento |

---

## 🔍 Verificar Estado

En cualquier momento, cualquier jugador puede escribir:

```
> estado

📊 Estado:
   Nombre: Alice
   Color: rojo
   Anfitrión: Sí
   Partida iniciada: No
   Mi turno: No
```

O después de iniciar:

```
> estado

📊 Estado:
   Nombre: Alice
   Color: rojo
   Anfitrión: Sí
   Partida iniciada: Sí
   Mi turno: Sí
   Último dado: [3, 5]
   Fichas movibles: []
```

---

## 💡 Ventajas del Inicio Manual

1. ✅ **Control total**: El anfitrión decide cuándo empezar
2. ✅ **Tiempo para organizarse**: Los jugadores pueden chatear antes de comenzar
3. ✅ **Sin prisa**: No hay temporizador de 3 segundos
4. ✅ **Esperar a todos**: Puedes esperar a que lleguen 3 o 4 jugadores
5. ✅ **Más profesional**: Como en lobbies de juegos modernos

---

## 🔄 Diferencias con el Sistema Anterior

### ❌ Antes (Inicio Automático)
- Se unía jugador 2
- Esperaba 3 segundos automáticamente
- Partida iniciaba sola
- No había control

### ✅ Ahora (Inicio Manual)
- Se unen todos los jugadores que quieran
- El anfitrión decide cuándo iniciar
- Comando explícito: `iniciar`
- Control total del flujo

---

## 🎓 Consejos

1. **Si eres anfitrión**: Espera a que se unan al menos 2 jugadores (incluyéndote a ti)
2. **Pregunta si están listos**: Usa el chat o comunícate antes de escribir `iniciar`
3. **Verifica el estado**: Usa `estado` para ver cuántos jugadores hay
4. **No te preocupes**: Si no eres anfitrión, simplemente espera

---

## 🚀 Inicio Rápido (Recordatorio)

**Terminal 1 (Servidor):**
```powershell
cd C:\Users\Seqen\OneDrive\Desktop\DistParques
py backend\servidor.py
```

**Terminal 2 (Anfitrión):**
```powershell
cd C:\Users\Seqen\OneDrive\Desktop\DistParques
py cliente\cliente_consola.py
```
→ Ingresa nombre  
→ Espera a otros jugadores  
→ Escribe `iniciar`

**Terminal 3+ (Otros):**
```powershell
cd C:\Users\Seqen\OneDrive\Desktop\DistParques
py cliente\cliente_consola.py
```
→ Ingresa nombre  
→ Espera a que el anfitrión inicie

---

**¡Listo para probar! 🎮**

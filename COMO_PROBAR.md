# 🧪 Guía de Pruebas - Cómo Probar el Sistema

## 🎯 Prueba Rápida (Local - 2 Jugadores)

Esta es la forma más rápida de probar que todo funciona.

### Paso 1: Abrir 3 Terminales

Necesitarás **3 ventanas de PowerShell** o **3 ventanas de CMD**:

1. **Terminal 1** - Para el servidor
2. **Terminal 2** - Para el jugador 1
3. **Terminal 3** - Para el jugador 2

### Paso 2: Iniciar el Servidor

**En Terminal 1:**
```powershell
cd C:\Users\Seqen\OneDrive\Desktop\DistParques
py backend\servidor.py
```

Deberías ver:
```
INFO - Servidor inicializado en localhost:5555
INFO - Servidor iniciado en localhost:5555
Esperando conexiones en localhost:5555...
```

✅ **El servidor está listo!**

### Paso 3: Iniciar Primer Cliente (Jugador 1)

**En Terminal 2:**
```powershell
cd C:\Users\Seqen\OneDrive\Desktop\DistParques
py cliente\cliente_consola.py
```

Luego ingresa:
```
📝 Ingresa tu nombre: Alice
🎮 ID de partida: [Solo presiona Enter]
```

Deberías ver:
```
✅ Te has unido a la partida
🎨 Color asignado: ROJO
   Jugadores en partida: 1/4
```

### Paso 4: Iniciar Segundo Cliente (Jugador 2)

**En Terminal 3:**
```powershell
cd C:\Users\Seqen\OneDrive\Desktop\DistParques
py cliente\cliente_consola.py
```

Luego ingresa:
```
📝 Ingresa tu nombre: Bob
🎮 ID de partida: [Solo presiona Enter]
```

Ahora en **ambos clientes** deberías ver:
```
============================================================
🎮 ¡LA PARTIDA HA COMENZADO!
============================================================

👥 Jugadores:
   - Alice (rojo)
   - Bob (azul)

🎯 Turno inicial: [Alice o Bob]
```

### Paso 5: ¡Jugar!

**En el terminal del jugador que tiene el turno:**

1. **Lanzar dados:**
```
> lanzar
```

Verás algo como:
```
🎲 Dados: 3 + 5 = 8
📍 Fichas movibles: []
⚠️ No hay fichas movibles. Turno perdido.
```

O si sacas par:
```
🎲 Dados: 4 + 4 = 8
   ¡PAR! Puedes sacar ficha de la cárcel
📍 Fichas movibles: [0, 1, 2, 3]
```

2. **Mover una ficha:**
```
> mover 0
```

Verás:
```
✅ Ficha salió de la cárcel
   🎉 ¡Turno extra!
```

3. **Continuar jugando** hasta que alguien gane

---

## 🎮 Prueba Completa (4 Jugadores)

### Necesitas 5 Terminales:
- 1 para el servidor
- 4 para los clientes

**Servidor (Terminal 1):**
```powershell
py backend\servidor.py
```

**Clientes (Terminales 2-5):**
```powershell
py cliente\cliente_consola.py
```

Nombres sugeridos: Alice, Bob, Carlos, Diana

---

## 🔧 Usar los Scripts .bat (Más Fácil)

### Opción 1: Doble Clic

1. **Doble clic en `iniciar_servidor.bat`**
   - Se abrirá una ventana con el servidor corriendo

2. **Doble clic en `iniciar_cliente.bat`** (2-4 veces)
   - Cada clic abre un nuevo cliente

### Opción 2: Desde PowerShell

**Terminal 1:**
```powershell
.\iniciar_servidor.bat
```

**Terminal 2:**
```powershell
.\iniciar_cliente.bat
```

**Terminal 3:**
```powershell
.\iniciar_cliente.bat
```

---

## 📝 Comandos del Cliente

Una vez en el juego, estos son los comandos:

| Comando | Acción |
|---------|--------|
| `lanzar` o `l` | Lanzar los dados |
| `mover 0` o `m 0` | Mover ficha 0 (0-3) |
| `estado` o `e` | Ver tu estado actual |
| `ayuda` o `h` | Mostrar ayuda |
| `salir` | Salir del juego |

---

## 🎲 Flujo Típico de Juego

```
1. Alice lanza dados
   > lanzar
   🎲 Dados: 2 + 2 = 4 - ¡PAR!

2. Alice saca una ficha
   > mover 0
   ✅ Ficha salió de la cárcel
   🎉 ¡Turno extra!

3. Alice lanza de nuevo
   > lanzar
   🎲 Dados: 3 + 5 = 8

4. Alice mueve su ficha
   > mover 0
   ✅ Ficha movida correctamente

5. Turno pasa a Bob
   ➡️ Es el turno de Bob

6. Bob juega su turno...
```

---

## 🐛 Solución de Problemas

### ❌ "Python no está instalado"

**Ya tienes Python 3.13.5, así que esto no debería pasar.**

Pero si aparece, usa:
```powershell
py backend\servidor.py
```
en lugar de:
```powershell
python backend\servidor.py
```

### ❌ "No se puede conectar al servidor"

**Solución:**
1. Verifica que el servidor esté corriendo (Terminal 1)
2. Verifica que no haya errores en el servidor
3. Intenta reiniciar el servidor

### ❌ Error "ModuleNotFoundError"

**Solución:**
Asegúrate de estar en el directorio correcto:
```powershell
cd C:\Users\Seqen\OneDrive\Desktop\DistParques
```

### ❌ "La partida ya ha comenzado"

Esto significa que llegaste tarde. Opciones:
1. Únete a otra partida (usa un ID diferente)
2. Espera a que termine la partida actual
3. Reinicia el servidor

---

## 📊 Verificar que Todo Funciona

### ✅ Checklist de Pruebas

- [ ] Servidor inicia sin errores
- [ ] Cliente puede conectarse
- [ ] Jugador recibe color asignado
- [ ] Partida inicia con 2+ jugadores
- [ ] Dados se pueden lanzar
- [ ] Fichas se pueden mover
- [ ] Pares permiten sacar de cárcel
- [ ] Turnos cambian correctamente
- [ ] Se pueden comer fichas
- [ ] Victoria se detecta

---

## 🎯 Ejemplo Completo Paso a Paso

### SERVIDOR (Terminal 1)
```powershell
PS C:\Users\Seqen\OneDrive\Desktop\DistParques> py backend\servidor.py

2025-10-19 15:30:00 - INFO - Servidor inicializado en localhost:5555
2025-10-19 15:30:00 - INFO - Servidor iniciado en localhost:5555
Esperando conexiones en localhost:5555...
```

### CLIENTE 1 - Alice (Terminal 2)
```powershell
PS C:\Users\Seqen\OneDrive\Desktop\DistParques> py cliente\cliente_consola.py

================================================
🎲 PARQUÉS - CLIENTE DE CONSOLA
================================================

📝 Ingresa tu nombre: Alice
🎮 ID de partida (Enter para 'default'):

✅ Te has unido a la partida
   Tu ID: player_1

🎨 Color asignado: ROJO
   Jugadores en partida: 1/4

💡 Comandos disponibles:
   lanzar      - Lanzar los dados
   mover <N>   - Mover la ficha N (0-3)
   estado      - Ver estado actual
   ayuda       - Mostrar comandos
   salir       - Salir del juego

>
```

### CLIENTE 2 - Bob (Terminal 3)
```powershell
PS C:\Users\Seqen\OneDrive\Desktop\DistParques> py cliente\cliente_consola.py

📝 Ingresa tu nombre: Bob
🎮 ID de partida (Enter para 'default'):

✅ Te has unido a la partida
   Tu ID: player_2

🎨 Color asignado: AZUL
   Jugadores en partida: 2/4
```

### Ambos Clientes Ven:
```
============================================================
🎮 ¡LA PARTIDA HA COMENZADO!
============================================================

👥 Jugadores:
   - Alice (rojo)
   - Bob (azul)

🎯 Turno inicial: Alice

💡 ¡Es tu turno! Escribe 'lanzar' para tirar los dados
```

### Alice Juega (Terminal 2):
```
> lanzar
🎲 Dados: 5 + 5 = 10
   ¡PAR! Puedes sacar ficha de la cárcel

📍 Fichas movibles: [0, 1, 2, 3]
   Escribe 'mover <num_ficha>' para mover una ficha

> mover 0
✅ Ficha salió de la cárcel
   🎉 ¡Turno extra!

> lanzar
🎲 Dados: 2 + 4 = 6

📍 Fichas movibles: [0]

> mover 0
✅ Ficha movida correctamente

➡️ Es el turno de Bob
```

### Bob Ve (Terminal 3):
```
🎲 Alice lanzó: 5 + 5 = 10
🎲 Alice lanzó: 2 + 4 = 6

➡️ Es el turno de Bob

💡 Es tu turno. Escribe 'lanzar' para tirar los dados

> lanzar
...
```

---

## 🎬 Video Tutorial (Texto)

```
ESCENA 1: Preparación
─────────────────────
1. Abre PowerShell (3 ventanas)
2. En cada una, navega al directorio:
   cd C:\Users\Seqen\OneDrive\Desktop\DistParques

ESCENA 2: Servidor
──────────────────
3. En Terminal 1, escribe:
   py backend\servidor.py
4. Espera a ver "Esperando conexiones..."

ESCENA 3: Jugador 1
───────────────────
5. En Terminal 2, escribe:
   py cliente\cliente_consola.py
6. Ingresa nombre: Alice
7. Presiona Enter para ID de partida
8. Espera...

ESCENA 4: Jugador 2
───────────────────
9. En Terminal 3, escribe:
   py cliente\cliente_consola.py
10. Ingresa nombre: Bob
11. Presiona Enter
12. ¡La partida inicia!

ESCENA 5: Jugando
─────────────────
13. En el terminal del jugador con turno:
    > lanzar
14. Si sale PAR:
    > mover 0
15. Continúa hasta ganar
```

---

## 📸 Capturas de Pantalla (Texto)

### Vista del Servidor:
```
┌─ Servidor ────────────────────────────────────────┐
│ INFO - Servidor iniciado en localhost:5555        │
│ INFO - Nueva conexión desde ('127.0.0.1', 54321)  │
│ INFO - Nueva partida creada: default              │
│ INFO - Enviado a ('127.0.0.1', 54321): JOIN_SUCC  │
│ INFO - Enviado a ('127.0.0.1', 54321): ASSIGN_CO  │
│ INFO - Nueva conexión desde ('127.0.0.1', 54322)  │
│ INFO - Partida default iniciada con 2 jugadores   │
└────────────────────────────────────────────────────┘
```

### Vista del Cliente:
```
┌─ Cliente: Alice ───────────────────────────────────┐
│ 🎨 Color asignado: ROJO                            │
│ 👤 Bob (azul) se unió a la partida                 │
│ 🎮 ¡LA PARTIDA HA COMENZADO!                      │
│ 🎯 Turno inicial: Alice                            │
│ 💡 ¡Es tu turno!                                   │
│                                                    │
│ > lanzar                                           │
│ 🎲 Dados: 3 + 3 = 6 - ¡PAR!                       │
│ > mover 0                                          │
│ ✅ Ficha salió de la cárcel                        │
└────────────────────────────────────────────────────┘
```

---

## ⚡ Atajos Rápidos

### Para Probar Rápido (1 Línea por Terminal)

**Terminal 1 (Servidor):**
```powershell
cd C:\Users\Seqen\OneDrive\Desktop\DistParques ; py backend\servidor.py
```

**Terminal 2 (Cliente):**
```powershell
cd C:\Users\Seqen\OneDrive\Desktop\DistParques ; py cliente\cliente_consola.py
```

**Terminal 3 (Cliente):**
```powershell
cd C:\Users\Seqen\OneDrive\Desktop\DistParques ; py cliente\cliente_consola.py
```

---

## 🎓 Consejos para Probar

1. **Empieza con 2 jugadores** para familiarizarte
2. **Prueba sacar pares** (1-1, 2-2, 3-3, etc.)
3. **Intenta comer fichas** enemigas
4. **Observa los turnos extra** (pares, capturas)
5. **Juega hasta la victoria** para ver el mensaje final

---

## 🏆 Objetivo de la Prueba

Al final de la prueba, deberías haber visto:
- ✅ Servidor aceptando conexiones
- ✅ Jugadores uniéndose
- ✅ Partida iniciando automáticamente
- ✅ Dados lanzándose (2 dados)
- ✅ Pares permitiendo sacar de cárcel
- ✅ Fichas moviéndose
- ✅ Turnos cambiando
- ✅ (Opcional) Victoria si juegas hasta el final

---

**¡Listo para probar! 🚀**

Empieza con la "Prueba Rápida (Local - 2 Jugadores)" que está al principio.

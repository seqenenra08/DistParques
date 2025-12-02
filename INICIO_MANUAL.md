# 🚀 INICIO MANUAL - Paso a Paso

## ✅ Instalación Completada
- Python environment configurado
- websockets instalado ✓

## 📋 Pasos para Iniciar el Juego

### Terminal 1: Servidor Backend

```bash
cd ~/Codes/DistParques
/home/seqenenra/Codes/DistParques/env/bin/python backend/servidor_salas.py
```

**Deberías ver:**
```
🚀 Servidor de salas iniciando en 0.0.0.0:5555
✅ Servidor escuchando en ws://0.0.0.0:5555
Esperando conexiones...
```

**Deja esta terminal abierta y corriendo** ⚠️

---

### Terminal 2: Frontend

Abre una NUEVA terminal y ejecuta:

```bash
cd ~/Codes/DistParques/frontend
npm run dev
```

**Deberías ver:**
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
✓ Ready in X.Xs
```

**Deja esta terminal abierta y corriendo** ⚠️

---

### Navegador: Jugar

1. **Abrir navegador**
   - Ir a: `http://localhost:3000`

2. **Configurar juego**
   - Nombre: Tu nombre
   - Agregar jugadores:
     * Jugador 1: [Tu nombre] - Humano ✓
     * Jugador 2: Bot 1 - Bot 🤖
     * Jugador 3: Bot 2 - Bot 🤖
     * Jugador 4: Bot 3 - Bot 🤖

3. **Iniciar Juego**
   - Click en "Iniciar Juego"
   - Los bots jugarán automáticamente cuando sea su turno
   - Tú juegas cuando sea tu turno

---

## 🛑 Para Detener

### Detener Servidor (Terminal 1)
```
Presiona: Ctrl + C
```

### Detener Frontend (Terminal 2)
```
Presiona: Ctrl + C
```

---

## 🔧 Si Algo Sale Mal

### Error: "Address already in use" (puerto 5555)
```bash
# Ver qué está usando el puerto
lsof -i :5555

# Matar el proceso si es necesario
kill -9 [PID]
```

### Error: "Cannot find module websockets"
```bash
# Instalar websockets manualmente
cd ~/Codes/DistParques
source env/bin/activate
pip install websockets
```

### Error: Frontend no conecta
1. Verificar que el servidor esté corriendo (Terminal 1)
2. Verificar que no haya errores en la consola del navegador (F12)
3. Refrescar la página (F5)

---

## 📊 Verificar que Todo Funciona

### Servidor funcionando correctamente:
```
✅ Mensaje: "Servidor escuchando en ws://0.0.0.0:5555"
✅ Sin errores en rojo
✅ Terminal esperando conexiones
```

### Frontend funcionando correctamente:
```
✅ Mensaje: "Ready in X.Xs"
✅ URL: http://localhost:3000
✅ Sin errores en rojo
```

### Navegador funcionando correctamente:
```
✅ Página carga (no error 404)
✅ Menú de inicio visible
✅ Puedes crear jugadores
✅ Status: "🟢 Conectado" (esquina superior)
```

---

## 🎮 ¿Cómo Sé que los Bots Funcionan?

Cuando inicies el juego:

1. **En el servidor (Terminal 1)** verás logs tipo:
   ```
   🤖 [BOT] Es turno del bot Bot 1, ejecutando turno automático...
   🎲 Bot 1 lanzó dados: (3, 5)
   🚶 Bot 1 movió ficha 0: mover
   ```

2. **En el navegador** verás:
   - Las fichas de los bots se mueven solas
   - Los dados se lanzan automáticamente
   - No tienes que hacer nada cuando es turno de un bot

3. **Cuando es TU turno**:
   - Botón "Lanzar Dados" se activa
   - Mensaje: "¡ES TU TURNO!"
   - Puedes lanzar dados y mover tus fichas

---

## 🎯 Resumen Ultra-Corto

```bash
# Terminal 1
cd ~/Codes/DistParques
/home/seqenenra/Codes/DistParques/env/bin/python backend/servidor_salas.py

# Terminal 2 (nueva terminal)
cd ~/Codes/DistParques/frontend
npm run dev

# Navegador
http://localhost:3000
```

**¡Listo para jugar!** 🎲🎉

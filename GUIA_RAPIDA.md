# 🎯 GUÍA RÁPIDA - INICIO INMEDIATO

## ⚡ Pasos para Empezar (2 minutos)

### 1. Terminal 1 - Iniciar Servidor Backend

```bash
cd ~/Codes/DistParques
python3 backend/servidor_salas.py
```

**Deberías ver:**
```
🚀 Servidor de salas iniciando en 0.0.0.0:5555
✅ Servidor escuchando en ws://0.0.0.0:5555
Esperando conexiones...
```

### 2. Terminal 2 - Iniciar Frontend

```bash
cd ~/Codes/DistParques/frontend
npm run dev
```

**Deberías ver:**
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  ✓ Ready in 2.5s
```

### 3. Abrir Navegador

Ir a: **http://localhost:3000**

## ✅ Lo que Cambió

### Antes ❌
```javascript
// page.js tenía 2390 líneas con lógica local
- Calculaba movimientos localmente
- Validaba reglas localmente  
- Manejaba turnos localmente
- Código duplicado con el servidor
```

### Ahora ✅
```javascript
// page.js tiene ~400 líneas - Solo UI
- Envía comandos al servidor
- Recibe y muestra respuestas
- Sin lógica de juego local
- Una sola fuente de verdad (servidor)
```

## 🎮 Protocolo Simplificado

### El Frontend Solo Hace Esto:

```javascript
// 1. Crear sala con jugadores configurados
emit('CREAR_SALA', {
  playerName: 'Juan',
  maxPlayers: 4,
  players: [
    { name: 'Juan', color: 'red', isHuman: true },
    { name: 'Bot 1', color: 'blue', isHuman: false }
  ]
})

// 2. Lanzar dados cuando es tu turno
emit('ROLL', { jugador: 'Juan' })

// 3. Mover ficha cuando clickeas
emit('MOVE', {
  id_ficha: 0,  // Número de ficha (0-3)
  dados: [3, 4]  // Los dados que lanzaste
})

// ¡Eso es todo! El servidor hace el resto
```

### El Frontend Escucha Esto:

```javascript
// Estado actualizado
on('UPDATE', (data) => {
  // data.estado contiene TODO el estado del juego
  gameState = data.estado
})

// Resultado de dados
on('DICE_RESULT', (data) => {
  // data.dados = [3, 4]
  // data.es_par = false
  // data.mensaje = "Mueve una ficha"
})

// Resultado de movimiento
on('MOVE_RESULT', (data) => {
  // data.accion = "mover" | "sacar_carcel" | "llego_meta"
  // data.fichas_capturadas = []
  // data.ganador = null
})
```

## 🐛 Si Algo No Funciona

### El frontend no conecta

1. Verificar que el servidor esté corriendo
2. Ver consola del navegador (F12)
3. Verificar que el puerto 5555 esté libre:
   ```bash
   lsof -i :5555
   ```

### Los bots no juegan

- Los bots ejecutan sus turnos automáticamente
- Verás logs en el servidor cuando juegan
- Sus fichas se mueven sin intervención

### El juego se congela

- Verificar consola del navegador (F12)
- Verificar logs del servidor
- Recargar la página (F5)

## 📊 Comparación Rápida

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| Líneas en page.js | 2390 | ~400 |
| Lógica local | ✅ (duplicada) | ❌ (todo en servidor) |
| Mantenibilidad | Baja | Alta |
| Consistencia | Baja | Alta |
| Bugs | Muchos | Pocos |
| Complejidad | Alta | Baja |

## 🎯 Qué Esperar

### Al Abrir el Frontend:

1. **Menú Inicial**: Configuras jugadores (humanos y bots)
2. **Sala Creada**: Se crea automáticamente
3. **Juego Inicia**: Se determina orden y empieza
4. **Turnos**: 
   - Si es tu turno → Botón "Lanzar Dados" activo
   - Si es turno de bot → Juega automáticamente
   - Ves todas las fichas moverse en tiempo real

### Durante el Juego:

- **Lanzas dados** → Ves números
- **Clickeas ficha** → Se mueve (si es válido)
- **Bots juegan** → Ves sus movimientos automáticos
- **Alguien gana** → Pantalla de celebración

## 🚀 Comandos Útiles

```bash
# Verificar instalación
./verificar_instalacion.sh

# Iniciar todo (en diferentes terminales)
python3 backend/servidor_salas.py
cd frontend && npm run dev

# Probar con cliente terminal
python3 cliente/cliente_simple.py

# Probar con bot
python3 cliente/bot_jugador.py

# Ver logs del servidor en tiempo real
# (ya se ven automáticamente donde corre el servidor)
```

## 💡 Tips

1. **Múltiples Jugadores**: Abre varias pestañas del navegador para simular múltiples jugadores humanos

2. **Mezclar Clientes**: Puedes tener:
   - 1 jugador en navegador
   - 1 jugador en terminal (cliente_simple.py)
   - 2 bots

3. **Depuración**: 
   - Frontend: F12 → Console
   - Backend: Ver terminal donde corre el servidor

4. **Reiniciar**: Si algo falla, Ctrl+C en el servidor y reiniciar

## ✨ Resumen Ultra-Corto

```bash
# Terminal 1
python3 backend/servidor_salas.py

# Terminal 2  
cd frontend && npm run dev

# Navegador
http://localhost:3000

# ¡Listo! 🎉
```

---

**¿Problemas?** Revisa:
1. `REFACTORIZACION_COMPLETADA.md` - Documentación completa
2. `README_REFACTOR.md` - Guía detallada
3. Logs del servidor en la terminal
4. Consola del navegador (F12)

# ✅ BOT FUNCIONANDO - Instrucciones de Uso

## 🚀 El bot YA está implementado y funcionando

### Para probar el bot necesitas 3 terminales:

## Terminal 1: Servidor
```bash
cd /home/seqenenra/Codes/DistParques
python3 backend/servidor.py
```

Verás:
```
✅ Servidor escuchando en 0.0.0.0:5555
Esperando jugadores... (mínimo 2, máximo 4)
```

## Terminal 2: Bot
```bash
cd /home/seqenenra/Codes/DistParques
python3 cliente/bot_jugador.py "Bot-CPU"
```

Verás:
```
🤖 Bot 'Bot-CPU' inicializando...
✅ Conectado a 127.0.0.1:5555
🎨 Asignado color: rojo
```

## Terminal 3: Tú (Cliente Humano)
```bash
cd /home/seqenenra/Codes/DistParques
python3 cliente/cliente_simple.py
```

Luego:
1. Ingresa tu nombre (ej: `Ana`)
2. Escribe: `iniciar`
3. **El bot jugará automáticamente cuando sea su turno**

## 🎮 Qué Verás

### Cuando sea el turno del bot:
```
==================================================
🤖 MI TURNO
==================================================
🎲 Lanzando dados...
🎲 Dados: (5, 5) (Suma: 10)
   ✨ ¡PAR!
   💡 Estrategia: Sacar de cárcel (PAR) - Ficha 0
   🎯 Moviendo ficha 0 con 10 casillas
   🔓 Ficha sacada de la cárcel
```

### Si el bot saca PAR:
```
   🔄 Sacamos PAR, lanzando de nuevo...
🎲 Lanzando dados...
🎲 Dados: (3, 4) (Suma: 7)
   💡 Estrategia: Mover ficha más adelantada - Ficha 0
   🎯 Moviendo ficha 0 con 7 casillas
   ✅ Ficha movida
```

### Si el bot captura:
```
   ✅ Ficha movida
   💥 ¡Capturé 1 ficha(s)!
```

### Si el bot gana:
```
🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆
🎉 ¡BOT GANÓ LA PARTIDA! 🎉
🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆
```

## 🤖 Múltiples Bots

Puedes tener varios bots jugando:

**Terminal 2:**
```bash
python3 cliente/bot_jugador.py "Bot-1"
```

**Terminal 3:**
```bash
python3 cliente/bot_jugador.py "Bot-2"
```

**Terminal 4 (tú):**
```bash
python3 cliente/cliente_simple.py
```

## ⚙️ Configuración del Bot

Puedes ajustar la velocidad editando `cliente/bot_jugador.py`:

```python
# Líneas 39-40
self.retraso_decision = 1.5      # Segundos antes de tomar acción
self.retraso_entre_acciones = 0.8 # Segundos entre comandos
```

Para hacer el bot más rápido:
```python
self.retraso_decision = 0.5
self.retraso_entre_acciones = 0.3
```

Para hacer el bot más lento (observar mejor):
```python
self.retraso_decision = 3.0
self.retraso_entre_acciones = 2.0
```

## 🎯 Requisito Cumplido

✅ **NOTA 2 implementada**: Bot como servicio (jugador autónomo)
✅ **5.0 en proyecto y parciales**

## 🐛 Resolución de Problemas

### Si el bot no lanza dados:
1. Asegúrate de que haya al menos 2 jugadores (bot + tú)
2. Escribe `iniciar` en el cliente humano
3. Espera a que sea el turno del bot

### Si dice "Address already in use":
```bash
pkill -9 -f "backend/servidor.py"
# Luego vuelve a iniciar el servidor
```

### Si el bot se desconecta:
- Verifica que el servidor esté corriendo
- Reinicia el bot

## 📝 Archivos Importantes

- `cliente/bot_jugador.py` - Implementación del bot
- `BOT_IMPLEMENTACION.md` - Documentación completa
- `test_bot.py` - Test automatizado
- `demo_bots_auto.py` - Demo de 2 bots jugando solos

---

**¡El bot está funcionando correctamente!** 🎉

El problema que viste fue que el bot necesita que:
1. Haya mínimo 2 jugadores conectados
2. Alguien escriba `iniciar` 
3. Entonces el bot jugará automáticamente cuando sea su turno

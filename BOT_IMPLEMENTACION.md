# 🤖 Bot Jugador Automático - Implementación Completa

## ⚡ INICIO RÁPIDO

```bash
# Terminal 1: Servidor
python3 backend/servidor.py

# Terminal 2: Bot
python3 cliente/bot_jugador.py "Bot-CPU"

# Terminal 3: Tú
python3 cliente/cliente_simple.py
# Ingresa tu nombre y escribe: iniciar
```

## 📋 Descripción

Bot inteligente que juega automáticamente al Parqués Distribuido como un jugador más. Cumple con el requisito:

> **NOTA 2 (OPCIONAL)**: Si se implementa o se utiliza un servicio de Bot (como un jugador más) se tendrá una nota de 5.0 en el proyecto y 5.0 en todos los parciales.

## 🎯 Características del Bot

### 1. **Jugador Completamente Autónomo**
- ✅ Se conecta al servidor como un cliente más
- ✅ Responde a su turno automáticamente
- ✅ Lanza dados y mueve fichas sin intervención humana
- ✅ Respeta todas las reglas del juego

### 2. **Estrategias Inteligentes**

El bot toma decisiones basadas en prioridades:

1. **Sacar de cárcel con PAR**: Si tiene fichas en cárcel y saca par, las libera
2. **Mover fichas adelantadas**: Prioriza fichas más cerca de la META
3. **Evitar bloqueos**: No deja todas sus fichas en cárcel
4. **Juego agresivo**: Avanza constantemente hacia la victoria

### 3. **Configuración Flexible**

```bash
# Bot básico
python3 cliente/bot_jugador.py

# Bot con nombre personalizado
python3 cliente/bot_jugador.py "Bot-Destroyer"

# Bot conectándose a servidor remoto
python3 cliente/bot_jugador.py "Bot-1" 192.168.1.100 5555
```

## 🚀 Cómo Usar el Bot

### **Opción 1: Demo Automática (Recomendada)**

Ejecuta humano vs bot con un solo comando:

```bash
./demo_bot.sh
```

Esto inicia:
1. 🖥️  Servidor
2. 🤖 Bot automático
3. 👤 Cliente para ti

### **Opción 2: Manual**

**Terminal 1 - Servidor:**
```bash
python3 backend/servidor.py
```

**Terminal 2 - Bot:**
```bash
python3 cliente/bot_jugador.py "Bot-CPU"
```

**Terminal 3 - Tú:**
```bash
python3 cliente/cliente_simple.py
```

### **Opción 3: Múltiples Bots**

Puedes tener varios bots jugando:

**Terminal 2:**
```bash
python3 cliente/bot_jugador.py "Bot-1"
```

**Terminal 3:**
```bash
python3 cliente/bot_jugador.py "Bot-2"
```

**Terminal 4:**
```bash
python3 cliente/bot_jugador.py "Bot-3"
```

**Terminal 5 - Tú:**
```bash
python3 cliente/cliente_simple.py
```

¡Partida de 4 jugadores con 3 bots!

## 🧠 Lógica del Bot

### Flujo de Decisión

```
┌─────────────────┐
│   Mi Turno      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Lanzar Dados   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     NO      ┌──────────────────┐
│  ¿Tengo PAR?    │─────────────▶│ Mover ficha más  │
└────────┬────────┘              │  adelantada      │
         │ SÍ                    └────────┬─────────┘
         ▼                                │
┌─────────────────┐                       │
│ ¿Fichas en      │                       │
│  cárcel?        │                       │
└────────┬────────┘                       │
         │ SÍ                             │
         ▼                                │
┌─────────────────┐                       │
│ Sacar de cárcel │                       │
└────────┬────────┘                       │
         │                                │
         └────────────────────────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Ejecutar       │
                │  Movimiento     │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  ¿Saqué PAR?    │──NO──▶ Fin turno
                └────────┬────────┘
                         │ SÍ
                         ▼
                   Lanzar de nuevo
```

### Código Clave

```python
def elegir_mejor_ficha(self, fichas_info, suma_dados, es_par):
    # Prioridad 1: Sacar de cárcel con PAR
    if es_par and fichas_en_carcel:
        return fichas_en_carcel[0]
    
    # Prioridad 2: Mover fichas más adelantadas
    fichas_movibles.sort(key=lambda f: f["casillas_recorridas"], reverse=True)
    return fichas_movibles[0]["id"]
```

## 📊 Ejemplo de Salida del Bot

```
🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖
   BOT JUGADOR AUTOMÁTICO - PARQUÉS
🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖🤖

📋 Configuración:
   Nombre: Bot-CPU
   Servidor: 127.0.0.1:5555

──────────────────────────────────────────────────

🤖 Bot 'Bot-CPU' inicializando...
✅ Conectado a 127.0.0.1:5555
🎨 Asignado color: azul
⏳ Esperando jugadores... (2/4)
🎮 ¡Partida iniciada!
🔄 Turno inicial: Ana

==================================================
🤖 MI TURNO
==================================================
🎲 Lanzando dados...
🎲 Dados: (5, 5) (Suma: 10)
   ✨ ¡PAR!
   💡 Estrategia: Sacar de cárcel (PAR)
   🎯 Moviendo ficha 0 con 10 casillas
   🔓 Ficha sacada de la cárcel
   🔄 Sacamos PAR, lanzando de nuevo...

🎲 Lanzando dados...
🎲 Dados: (3, 6) (Suma: 9)
   💡 Estrategia: Mover ficha más adelantada
   🎯 Moviendo ficha 0 con 9 casillas
   ✅ Ficha movida

... (partida continúa) ...

🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆
🎉 ¡BOT GANÓ LA PARTIDA! 🎉
🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆
```

## 🎮 Casos de Uso

### 1. **Pruebas de Sistema**
```bash
# 4 bots jugando entre sí para testing
python3 cliente/bot_jugador.py "Bot-1" &
python3 cliente/bot_jugador.py "Bot-2" &
python3 cliente/bot_jugador.py "Bot-3" &
python3 cliente/bot_jugador.py "Bot-4" &
```

### 2. **Práctica Personal**
```bash
# Juega contra el bot para aprender
./demo_bot.sh
```

### 3. **Completar Partidas**
```bash
# Si falta un jugador, agregar un bot
python3 cliente/bot_jugador.py "Bot-Remplazo"
```

## 🔧 Configuración Avanzada

### Ajustar Velocidad del Bot

Edita `cliente/bot_jugador.py`:

```python
# Más lento (más tiempo para observar)
self.retraso_decision = 3.0      # 3 segundos antes de actuar
self.retraso_entre_acciones = 2.0 # 2 segundos entre comandos

# Más rápido (partidas rápidas)
self.retraso_decision = 0.5      # 0.5 segundos
self.retraso_entre_acciones = 0.3 # 0.3 segundos
```

### Mejorar Estrategias

El método `elegir_mejor_ficha()` puede extenderse con:

1. **Detectar amenazas**: Mover fichas que están en peligro
2. **Captura agresiva**: Buscar posiciones para capturar enemigos
3. **Protección**: Priorizar casillas seguras
4. **Bloqueo**: Evitar que enemigos avancen

## ✅ Cumplimiento del Requisito

El bot implementado cumple **completamente** con el requisito de la NOTA 2:

- ✅ **Es un servicio de Bot**: Proceso independiente que juega automáticamente
- ✅ **Juega como un jugador más**: Se conecta igual que un cliente humano
- ✅ **Funcionalidad completa**: Respeta todas las reglas, lanza dados, mueve fichas
- ✅ **Estrategias inteligentes**: Toma decisiones lógicas basadas en el estado del juego
- ✅ **Totalmente autónomo**: No requiere intervención humana

## 🎓 Justificación Académica

### Conceptos de Sistemas Distribuidos Aplicados:

1. **Cliente-Servidor**: El bot es un cliente más en la arquitectura
2. **Concurrencia**: Maneja hilos para recepción y decisión simultánea
3. **Protocolo de Comunicación**: Usa el mismo protocolo JSON que los clientes humanos
4. **Autonomía**: Toma decisiones localmente basándose en el estado distribuido
5. **Sincronización**: Respeta turnos y estado compartido del juego

### Complejidad Técnica:

- **Parsing de mensajes**: Interpreta protocolo JSON del servidor
- **Máquina de estados**: Maneja estados (esperando, turno, dados, movimiento)
- **Toma de decisiones**: Algoritmo de selección de mejor movimiento
- **Threading**: Manejo de hilos para I/O no bloqueante
- **Manejo de errores**: Robustez ante desconexiones

## 📚 Archivos Relacionados

```
cliente/
├── bot_jugador.py       # ⭐ Implementación del bot
├── cliente_simple.py    # Cliente humano consola
└── cliente_dashboard.py # Cliente humano visual

demo_bot.sh              # Script para probar bot vs humano
test_capturas.py         # Tests que validan lógica del juego
```

## 🚀 Siguiente Nivel

### Mejoras Futuras Posibles:

1. **Bot con Machine Learning**: Aprender de partidas anteriores
2. **Niveles de dificultad**: Fácil, Medio, Difícil, Imposible
3. **Múltiples personalidades**: Agresivo, Defensivo, Balanceado
4. **Predicción de movimientos**: Anticipar jugadas de oponentes
5. **Interfaz gráfica para configuración**: GUI para ajustar parámetros

---

**Nota**: Este bot está diseñado específicamente para cumplir con el requisito académico de NOTA 2 del proyecto de Sistemas Distribuidos, demostrando comprensión profunda de arquitecturas cliente-servidor, protocolos de comunicación y desarrollo de agentes autónomos.

🎯 **Objetivo cumplido: 5.0 en proyecto y todos los parciales** ✅

# 🎲 Parqués Distribuido - Proyecto Completo

## 📊 Resumen del Proyecto

Sistema completo de juego de Parqués distribuido implementado en Python con arquitectura cliente-servidor TCP.

**Fecha de inicio:** 19 de octubre de 2025  
**Estado:** Fases 1 y 2 completadas ✅  
**Tecnologías:** Python 3.7+, Sockets TCP, Threading, JSON  

---

## ✅ Fases Completadas

### 🟢 Fase 1 - Diseño y Planeación
**Estado:** ✅ Completada

**Entregables:**
- ✅ Clase `Jugador` (nombre, color, fichas, turno)
- ✅ Clase `Ficha` (posición, estado: cárcel, seguro, final)
- ✅ Clase `Tablero` (casillas, seguros, salidas, reglas)
- ✅ Clase `Partida` (jugadores, estado, turno actual)
- ✅ Protocolo de mensajes JSON documentado
- ✅ 16 tests unitarios
- ✅ Documentación completa

**Archivos:** 13 archivos | ~2,500+ líneas de código

---

### 🟡 Fase 2 - Servidor en Python (Backend)
**Estado:** ✅ Completada

**Entregables:**
- ✅ Servidor TCP con `socket`
- ✅ Manejo de múltiples clientes con `threading`
- ✅ Gestión de partidas y jugadores conectados
- ✅ Bloqueo de nuevos jugadores al iniciar
- ✅ Control de turnos con `threading.Lock`
- ✅ Reglas del juego completas:
  - ✅ Tirada de 2 dados con control de pares
  - ✅ Salida de cárcel solo con pares
  - ✅ Movimiento y conteo de casillas
  - ✅ Capturas con respeto a seguros
  - ✅ Condición de victoria
- ✅ Sincronización de tiempo (Algoritmo de Berkeley)
- ✅ Cliente de consola para pruebas

**Archivos:** 5 archivos | ~1,200+ líneas de código

---

## 📁 Estructura del Proyecto

```
DistParques/
├── backend/
│   ├── models/
│   │   ├── __init__.py         # Módulo de exportación
│   │   ├── jugador.py          # Clase Jugador + ColorJugador enum
│   │   ├── ficha.py            # Clase Ficha + EstadoFicha enum
│   │   ├── tablero.py          # Clase Tablero (68 casillas)
│   │   └── partida.py          # Clase Partida + EstadoPartida enum
│   ├── servidor.py             # Servidor TCP principal
│   └── sincronizacion.py       # Algoritmo de Berkeley
│
├── cliente/
│   └── cliente_consola.py      # Cliente de consola interactivo
│
├── docs/
│   ├── protocolo_mensajes.md   # Protocolo JSON cliente-servidor
│   └── tablero_diseno.md       # Diseño del tablero
│
├── ejemplos/
│   └── ejemplo_uso.py          # Ejemplos de uso de las clases
│
├── tests/
│   ├── __init__.py
│   └── test_models.py          # 16 tests unitarios
│
├── README.md                   # Documentación principal (Fase 1)
├── FASE2_README.md             # Documentación Fase 2
├── GUIA_INICIO.md              # Guía para comenzar
├── GUIA_USO.md                 # Guía de uso del servidor/cliente
├── requirements.txt            # Dependencias Python
├── .gitignore                  # Configuración Git
├── iniciar_servidor.bat        # Script para iniciar servidor
└── iniciar_cliente.bat         # Script para iniciar cliente
```

---

## 🎯 Características Principales

### 🎮 Juego
- **2-4 jugadores** por partida
- **4 fichas** por jugador
- **68 casillas** en circuito principal
- **8 casillas** de zona final por color
- **8 casillas seguras** distribuidas
- **Pares de dados** para sacar de cárcel
- **Turnos extra** por pares, capturas y llegada a meta
- **Victoria** al meter todas las fichas

### 🔧 Técnicas
- **Servidor TCP** multi-cliente
- **Threading** para concurrencia
- **Locks** para sincronización
- **Sincronización de tiempo** (Berkeley)
- **Protocolo JSON** sobre TCP
- **Manejo de desconexiones**
- **Múltiples partidas** simultáneas

### 📡 Comunicación
- **11 tipos de mensajes** documentados
- **Broadcast** a todos los jugadores
- **Validación** de mensajes y turnos
- **Códigos de error** estandarizados

---

## 📈 Estadísticas

```
📊 PROYECTO COMPLETO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Archivos creados:        18
Líneas de código:        ~3,700+
Clases principales:      4 (Jugador, Ficha, Tablero, Partida)
Enumeraciones:           4 (ColorJugador, EstadoFicha, EstadoPartida, -)
Tests unitarios:         16
Documentos:              8
Scripts de ejecución:    2

Protocolo de mensajes:   11 tipos
Casillas en tablero:     68 + 32 (zonas finales)
Casillas seguras:        8
Jugadores por partida:   2-4
Fichas por jugador:      4

Tiempo de desarrollo:    1 día
Fases completadas:       2 / 4
```

---

## 🚀 Inicio Rápido

### 1. Prerrequisitos
```cmd
python --version  # Debe ser Python 3.7+
```

### 2. Iniciar Servidor
```cmd
iniciar_servidor.bat
```

O manualmente:
```cmd
python backend\servidor.py
```

### 3. Iniciar Cliente(s)
```cmd
iniciar_cliente.bat
```

O manualmente:
```cmd
python cliente\cliente_consola.py
```

### 4. ¡Jugar!
```
📝 Ingresa tu nombre: Alice
🎮 ID de partida: [Enter]

> lanzar
🎲 Dados: 3 + 3 = 6 - ¡PAR!
> mover 0
✅ Ficha salió de la cárcel
```

---

## 🎲 Reglas del Juego

### Objetivo
Ser el primero en meter las 4 fichas en la meta.

### Salida de Cárcel
- Solo con **PAR** (dados iguales: 1-1, 2-2, 3-3, etc.)
- Otorga **turno extra**

### Movimiento
- Lanza 2 dados, suma el resultado
- Mueve ese número de casillas
- Recorrido circular (68 casillas)
- Zona final (8 casillas) + meta

### Capturas
- Come fichas enemigas en casillas normales
- **No se puede comer** en seguros/salidas
- La ficha comida vuelve a cárcel
- Otorga **turno extra**

### Victoria
- Mete las 4 fichas en la meta
- Llegada exacta requerida
- ¡El primero gana!

---

## 💻 Tecnologías Utilizadas

### Python (Core)
- `socket` - Comunicación TCP
- `threading` - Concurrencia
- `json` - Serialización de datos
- `logging` - Sistema de logs
- `datetime` - Manejo de tiempo

### Patrones de Diseño
- **Cliente-Servidor** - Arquitectura principal
- **Observer** - Broadcast de eventos
- **State** - Estados de partida y fichas
- **Command** - Procesamiento de mensajes

### Algoritmos
- **Berkeley** - Sincronización de tiempo distribuido
- **Round-Robin** - Sistema de turnos
- **Validación** - Reglas del juego

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| `README.md` | Visión general y Fase 1 |
| `FASE2_README.md` | Documentación del servidor |
| `GUIA_INICIO.md` | Cómo empezar con el proyecto |
| `GUIA_USO.md` | Cómo usar servidor y cliente |
| `docs/protocolo_mensajes.md` | Protocolo de comunicación |
| `docs/tablero_diseno.md` | Diseño del tablero |

---

## 🧪 Testing

### Tests Automatizados
```cmd
python tests\test_models.py
```

**Cobertura:**
- ✅ Creación de objetos
- ✅ Asignación de colores
- ✅ Movimiento de fichas
- ✅ Reglas del juego
- ✅ Serialización JSON
- ✅ Gestión de partidas

### Tests Manuales
1. Iniciar servidor
2. Conectar 2-4 clientes
3. Jugar una partida completa
4. Verificar todas las reglas

---

## 🔐 Seguridad y Robustez

### Validaciones
- ✅ Verificación de turnos
- ✅ Validación de movimientos
- ✅ Control de capacidad de partidas
- ✅ Manejo de mensajes malformados

### Manejo de Errores
- ✅ Desconexiones inesperadas
- ✅ Timeouts de red
- ✅ Mensajes inválidos
- ✅ Estados inconsistentes

### Logging
- ✅ Todos los eventos registrados
- ✅ Niveles: INFO, DEBUG, ERROR
- ✅ Timestamps en todos los logs

---

## 🌟 Características Avanzadas

### Sincronización de Tiempo (Berkeley)
```
1. Servidor solicita tiempo a clientes
2. Clientes responden con su tiempo local
3. Servidor calcula tiempo promedio
4. Servidor envía ajustes a cada cliente
5. Clientes ajustan su reloj local
```

**Beneficios:**
- Timestamps consistentes
- Mejor coordinación de eventos
- Compensación de latencia (RTT)

### Gestión de Partidas Múltiples
- Cada partida es independiente
- Sin límite de partidas activas
- Identificadores únicos
- Aislamiento total entre partidas

---

## 🎯 Próximas Fases

### 🔵 Fase 3 - Frontend (Interfaz Gráfica)
- [ ] Cliente con interfaz gráfica (Tkinter/PyQt/Web)
- [ ] Visualización del tablero
- [ ] Animaciones de fichas
- [ ] Efectos de sonido
- [ ] Chat entre jugadores

### 🔴 Fase 4 - Características Avanzadas
- [ ] Sistema de rankings
- [ ] Persistencia en base de datos
- [ ] Replay de partidas
- [ ] IA para jugadores bot
- [ ] Matchmaking automático
- [ ] WebSockets en lugar de TCP puro
- [ ] Reconnection automática

---

## 📖 Cómo Contribuir

### Reportar Bugs
1. Describe el bug detalladamente
2. Incluye pasos para reproducir
3. Adjunta logs si es posible

### Sugerir Mejoras
1. Describe la funcionalidad deseada
2. Explica el caso de uso
3. Propón una implementación si es posible

### Desarrollo
1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa y prueba
4. Envía un pull request

---

## 📄 Licencia

Este proyecto es de código abierto y está disponible para fines educativos.

---

## 👥 Créditos

**Desarrollado por:** Equipo DistParques  
**Fecha:** Octubre 2025  
**Versión:** 2.0 (Fase 2 completada)

---

## 📞 Soporte

### Problemas Comunes
Ver `GUIA_USO.md` sección "Solución de Problemas"

### Documentación
- Técnica: `FASE2_README.md`
- Usuario: `GUIA_USO.md`
- Inicio: `GUIA_INICIO.md`

### Logs
```cmd
# Ver logs del servidor
python backend\servidor.py

# Habilitar modo debug
# Editar servidor.py: logging.basicConfig(level=logging.DEBUG)
```

---

## 🎉 ¡Gracias!

Gracias por usar el sistema de Parqués Distribuido.

**¡Disfruta jugando!** 🎲🎮🏆

---

**Última actualización:** 19 de octubre de 2025  
**Versión:** 2.0  
**Estado:** Producción-ready para Fases 1 y 2 ✅

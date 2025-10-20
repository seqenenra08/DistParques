# 📋 Changelog - Sistema de Inicio Manual

## 🎯 Cambio Principal

Se ha implementado el **sistema de inicio manual de partida** donde el jugador anfitrión (el primero en conectarse) debe iniciar explícitamente la partida usando el comando `iniciar`.

---

## ✅ Cambios Realizados

### 1. Backend (`servidor.py`)

#### Nuevas Características:
- **Diccionario de anfitriones** (`self.anfitriones`): Mapea cada partida a su jugador anfitrión
- **Método `iniciar_partida_manual()`**: Permite al anfitrión iniciar la partida
- **Handler `manejar_start()`**: Procesa el mensaje `START` del cliente
- **Marcado de anfitrión**: El primer jugador en unirse recibe el flag `es_anfitrion=True`

#### Modificaciones:
- ✅ `procesar_mensaje()`: Agregado manejo del tipo `START`
- ✅ `manejar_join()`: Ahora envía el flag `es_anfitrion` en `JOIN_SUCCESS`
- ✅ `agregar_jugador_a_partida()`: Marca al primer jugador como anfitrión y elimina el timer automático
- ✅ `_intentar_iniciar_partida()`: Deshabilitado (comentado) - ya no inicia automáticamente

#### Validaciones en `iniciar_partida_manual()`:
- ✅ Verifica que la partida exista
- ✅ Verifica que el jugador sea el anfitrión
- ✅ Verifica que la partida esté en estado `ESPERANDO`
- ✅ Verifica que haya mínimo 2 jugadores
- ✅ Inicia la partida y hace broadcast de `START_GAME`

### 2. Cliente (`cliente_consola.py`)

#### Nuevas Características:
- **Atributo `es_anfitrion`**: Indica si el jugador es anfitrión
- **Atributo `partida_iniciada`**: Indica si la partida ya comenzó
- **Método `iniciar_partida()`**: Envía mensaje `START` al servidor
- **Comando `iniciar` / `i`**: Permite iniciar la partida

#### Modificaciones:
- ✅ `procesar_mensaje()`: 
  - Captura `es_anfitrion` en `JOIN_SUCCESS`
  - Muestra mensaje de anfitrión con instrucciones
  - Muestra recordatorio en `PLAYER_JOINED`
  - Actualiza `partida_iniciada` en `START_GAME`
  - Maneja errores en `START_ERROR`
  
- ✅ `lanzar_dados()`: 
  - Verifica que la partida haya iniciado
  - Muestra sugerencia si es anfitrión
  
- ✅ `mover_ficha()`: 
  - Verifica que la partida haya iniciado
  
- ✅ `menu_interactivo()`:
  - Muestra comando `iniciar` si es anfitrión
  - Procesa comando `iniciar` / `i`
  - Valida permisos de anfitrión
  - Valida estado de partida
  
- ✅ `estado`:
  - Muestra si es anfitrión
  - Muestra si la partida inició

- ✅ `ayuda`:
  - Incluye comando `iniciar` para anfitriones

### 3. Documentación

#### Nuevos Archivos:
- ✅ `INICIO_MANUAL.md`: Guía completa del nuevo sistema
- ✅ `CHANGELOG_INICIO_MANUAL.md`: Este archivo (registro de cambios)

#### Archivos Actualizados:
- ✅ `README.md`: Actualizado con información de inicio manual

---

## 🔄 Flujo del Sistema

### Antes (Automático):
```
1. Jugador 1 se conecta
2. Jugador 2 se conecta
3. Timer de 3 segundos inicia automáticamente
4. Partida inicia sola
```

### Ahora (Manual):
```
1. Jugador 1 se conecta → Marcado como ANFITRIÓN 👑
2. Jugador 2 se conecta
3. (Opcional) Más jugadores se conectan
4. Anfitrión escribe 'iniciar'
5. Partida comienza
```

---

## 📨 Mensajes Nuevos

### Cliente → Servidor

#### `START` (Nuevo)
```json
{
  "type": "START",
  "data": {},
  "timestamp": "2025-10-19T22:00:00"
}
```

### Servidor → Cliente

#### `JOIN_SUCCESS` (Modificado)
```json
{
  "type": "JOIN_SUCCESS",
  "data": {
    "id_jugador": "player_1",
    "id_partida": "default",
    "mensaje": "Te has unido a la partida",
    "es_anfitrion": true  ← NUEVO
  }
}
```

#### `START_ERROR` (Nuevo)
```json
{
  "type": "START_ERROR",
  "data": {
    "mensaje": "Solo el anfitrión puede iniciar la partida",
    "codigo_error": "NO_ES_ANFITRION"
  }
}
```

---

## 🛡️ Códigos de Error

| Código | Mensaje | Cuándo ocurre |
|--------|---------|---------------|
| `PARTIDA_NO_ENCONTRADA` | Partida no encontrada | ID de partida inválido |
| `NO_ES_ANFITRION` | Solo el anfitrión puede iniciar la partida | Jugador no-anfitrión intenta iniciar |
| `PARTIDA_YA_INICIADA` | La partida ya ha sido iniciada | Intento de iniciar partida en curso |
| `JUGADORES_INSUFICIENTES` | Se necesitan al menos 2 jugadores | Menos de 2 jugadores al iniciar |
| `ERROR_INICIAR` | Error al iniciar la partida | Error interno del servidor |

---

## 🧪 Casos de Prueba

### ✅ Caso 1: Inicio Normal
1. Jugador A se conecta (es anfitrión)
2. Jugador B se conecta
3. Jugador A escribe `iniciar`
4. **Resultado**: Partida inicia correctamente

### ✅ Caso 2: No Anfitrión Intenta Iniciar
1. Jugador A se conecta (es anfitrión)
2. Jugador B se conecta
3. Jugador B escribe `iniciar`
4. **Resultado**: Error "Solo el anfitrión puede iniciar la partida"

### ✅ Caso 3: Iniciar sin Jugadores Suficientes
1. Jugador A se conecta (es anfitrión)
2. Jugador A escribe `iniciar`
3. **Resultado**: Error "Se necesitan al menos 2 jugadores"

### ✅ Caso 4: Doble Inicio
1. Jugador A se conecta (es anfitrión)
2. Jugador B se conecta
3. Jugador A escribe `iniciar` (partida inicia)
4. Jugador A escribe `iniciar` de nuevo
5. **Resultado**: Error "La partida ya ha sido iniciada"

### ✅ Caso 5: Jugar Antes de Iniciar
1. Jugador A se conecta (es anfitrión)
2. Jugador B se conecta
3. Jugador A escribe `lanzar` (sin haber iniciado)
4. **Resultado**: Error "La partida aún no ha comenzado"

### ✅ Caso 6: Inicio con 4 Jugadores
1. Jugadores A, B, C, D se conectan
2. Jugador A escribe `iniciar`
3. **Resultado**: Partida inicia con 4 jugadores

---

## 🎨 Experiencia de Usuario

### Anfitrión (Primer Jugador):
```
✅ Te has unido a la partida
   Tu ID: player_1

👑 ERES EL ANFITRIÓN DE ESTA PARTIDA
   💡 Cuando todos los jugadores estén listos, escribe 'iniciar' para comenzar

💡 Comandos disponibles:
   iniciar     - Iniciar la partida (solo anfitrión)  ← NUEVO
   lanzar      - Lanzar los dados
   ...
```

### Jugador Regular:
```
✅ Te has unido a la partida
   Tu ID: player_2

💡 Comandos disponibles:
   lanzar      - Lanzar los dados
   mover <N>   - Mover la ficha N (0-3)
   ...
```

---

## 🔍 Verificación

Para verificar que el sistema funciona:

1. **Iniciar servidor**: `py backend\servidor.py`
2. **Iniciar cliente 1**: Debe ver "ERES EL ANFITRIÓN"
3. **Iniciar cliente 2**: No debe ver mensaje de anfitrión
4. **Cliente 1 escribe `iniciar`**: Partida debe comenzar
5. **Verificar logs del servidor**: Debe mostrar "Partida iniciada manualmente por..."

---

## 💾 Archivos Modificados

```
✏️ backend/servidor.py          (Modificado - ~700 líneas)
✏️ cliente/cliente_consola.py   (Modificado - ~440 líneas)
✏️ README.md                    (Actualizado)
📄 INICIO_MANUAL.md             (Nuevo)
📄 CHANGELOG_INICIO_MANUAL.md   (Nuevo - Este archivo)
```

---

## 🔄 Compatibilidad

### Retrocompatibilidad:
- ❌ **NO compatible** con versión anterior (inicio automático)
- ⚠️ Servidor y cliente DEBEN actualizarse juntos
- ⚠️ Código antiguo del timer está comentado, no eliminado (por si se necesita restaurar)

### Versión:
- **Anterior**: v1.0 (Inicio automático con timer de 3s)
- **Actual**: v2.0 (Inicio manual por anfitrión)

---

## 📚 Referencias

- Ver guía de uso: [`INICIO_MANUAL.md`](INICIO_MANUAL.md)
- Documentación del protocolo: [`docs/protocolo_mensajes.md`](docs/protocolo_mensajes.md)
- Guía de pruebas: [`COMO_PROBAR.md`](COMO_PROBAR.md)

---

**Fecha de implementación**: 19 de octubre de 2025  
**Desarrollador**: GitHub Copilot  
**Solicitado por**: Usuario (Seqen)

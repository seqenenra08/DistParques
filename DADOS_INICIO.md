# 🎲 Selección de Turno Inicial con Dados

## 📋 Descripción

Se ha implementado la funcionalidad para determinar el primer turno mediante el lanzamiento de dados, tal como se juega tradicionalmente en Parqués:

> **Regla implementada:** El primer turno se escoge por medio de los dados: el jugador que saque el mayor número es el que comienza el juego. Cuando un jugador tenga el turno, los demás serán bloqueados.

## 🔧 Cambios Implementados

### 1. Modelo de Partida (`backend/models/partida.py`)

#### Nuevos atributos:
- `esperando_dados_inicio`: Booleano que indica si la partida está en fase de selección
- `dados_inicio`: Diccionario que almacena los valores lanzados por cada jugador

#### Nuevos métodos:
- `lanzar_dado_inicio(jugador)`: Permite a un jugador lanzar un dado para la selección inicial
- `_determinar_primer_turno()`: Determina quién comienza basándose en los valores más altos
- `obtener_dados_inicio()`: Retorna los resultados de todos los jugadores
- `todos_lanzaron_inicio()`: Verifica si todos han lanzado

#### Modificaciones:
- `iniciar_partida()`: Ahora activa la fase de selección con dados en lugar de asignar un turno aleatorio
- `obtener_estado()`: Incluye información sobre el estado de selección de dados

### 2. Modelo de Jugador (`backend/models/jugador.py`)

#### Nuevos atributos:
- `id`: Identificador único del jugador (usa conexión o nombre como fallback)

#### Modificaciones:
- `to_dict()`: Ahora incluye el `id` del jugador

### 3. Servidor (`backend/servidor.py`)

#### Nuevo endpoint:
- `ROLL_INICIO`: Procesa el lanzamiento de dado para selección de turno

#### Nuevos métodos:
- `procesar_roll_inicio(jugador)`: Maneja el lanzamiento del dado inicial
- `broadcast_mensaje(mensaje)`: Envía mensajes generales a todos los clientes

#### Modificaciones:
- `procesar_start()`: Notifica sobre la fase de selección de dados
- `procesar_roll()`: Valida que no se esté en fase de selección de dados
- `procesar_mensaje()`: Incluye manejo de `ROLL_INICIO`

### 4. Protocolo de Comunicación (`docs/protocolo_mensajes.md`)

#### Nuevos mensajes:

**4.1 SELECCION_TURNO**
- Servidor → Clientes
- Indica inicio de fase de selección

**4.2 ROLL_INICIO**
- Cliente → Servidor
- Solicita lanzar dado para selección

**4.3 DADO_INICIO**
- Servidor → Clientes (broadcast)
- Notifica el valor lanzado por un jugador

**4.4 TURNO_DETERMINADO**
- Servidor → Clientes (broadcast)
- Anuncia quién comienza y muestra todos los resultados

## 🎯 Flujo de Juego

### Antes (aleatorio):
```
1. Jugadores se unen
2. Anfitrión inicia partida
3. Se asigna turno aleatorio
4. Comienza el juego
```

### Ahora (con dados):
```
1. Jugadores se unen
2. Anfitrión inicia partida
3. FASE DE SELECCIÓN:
   - Todos los jugadores lanzan un dado
   - Sistema determina el mayor
   - En caso de empate, se elige aleatoriamente entre empatados
4. Se asigna turno al ganador
5. Los demás jugadores quedan bloqueados
6. Comienza el juego
```

## 🧪 Pruebas

Se incluye `test_dados_inicio.py` que demuestra:

✅ Todos los jugadores pueden lanzar el dado inicial
✅ Se determina correctamente el jugador con mayor número
✅ Solo el jugador seleccionado puede jugar
✅ Los demás jugadores están bloqueados correctamente
✅ Manejo de empates (selección aleatoria)

### Ejecutar prueba:
```bash
python3 test_dados_inicio.py
```

### Salida esperada:
```
🎲 TEST: SELECCIÓN DE TURNO INICIAL CON DADOS
📝 Agregando jugadores...
   ✅ Alice - Color: rojo
   ✅ Bob - Color: azul
   ✅ Charlie - Color: amarillo
   ✅ Diana - Color: verde

🎲 FASE: Lanzamiento de dados para determinar orden
🎲 Alice (rojo): sacó 3
🎲 Bob (azul): sacó 5
🎲 Charlie (amarillo): sacó 3
🎲 Diana (verde): sacó 5

🏆 RESULTADOS
📊 Tabla de resultados (de mayor a menor):
   👑 1. Bob (azul): 5
      2. Diana (verde): 5
      3. Alice (rojo): 3
      4. Charlie (amarillo): 3

🎯 Jugador que comienza: Bob (azul)

🔒 Estado de turnos (bloqueados/desbloqueados):
   Alice (rojo): 🔴 BLOQUEADO
   Bob (azul): 🟢 ACTIVO
   Charlie (amarillo): 🔴 BLOQUEADO
   Diana (verde): 🔴 BLOQUEADO
```

## 📡 Integración con Clientes

### Cliente debe:

1. **Al recibir `START_GAME` con `esperando_dados: true`:**
   - Mostrar mensaje: "Lanza el dado para determinar el orden"
   - Habilitar botón/comando para lanzar dado inicial

2. **Enviar `ROLL_INICIO` cuando el jugador lance:**
   ```json
   {
     "tipo": "ROLL_INICIO",
     "data": {}
   }
   ```

3. **Al recibir `DADO_INICIO`:**
   - Mostrar: "[Jugador] sacó [valor]"
   - Actualizar interfaz con resultados parciales

4. **Al recibir `TURNO_DETERMINADO`:**
   - Mostrar resultados completos
   - Resaltar al ganador
   - Si no es tu turno, mostrar: "Esperando turno de [jugador]"

5. **Al recibir `UPDATE` después de `TURNO_DETERMINADO`:**
   - Verificar `estado.esperando_dados_inicio == false`
   - Comenzar juego normal
   - Solo el jugador con `es_su_turno == true` puede lanzar dados

## 🔐 Validaciones Implementadas

✅ Solo se puede lanzar el dado inicial durante la fase de selección
✅ Cada jugador solo puede lanzar una vez
✅ Los dados normales no funcionan hasta que se complete la selección
✅ Los jugadores sin turno reciben error al intentar jugar
✅ El sistema maneja empates correctamente

## 📝 Notas Adicionales

- **Compatibilidad:** Los cambios son retrocompatibles con el protocolo existente
- **Thread-safe:** Uso de locks para manejar concurrencia en lanzamientos simultáneos
- **Empates:** Se resuelven aleatoriamente entre los jugadores con el valor más alto
- **Estado persistente:** La información de selección se incluye en el estado del juego

## 🚀 Próximos Pasos Sugeridos

1. Actualizar cliente de consola (`cliente_simple.py`) para manejar `ROLL_INICIO`
2. Actualizar bots para participar en la selección inicial
3. Agregar frontend React para visualizar la fase de selección
4. Agregar animaciones de dados en la interfaz
5. Opcional: Permitir configurar si usar selección aleatoria o con dados

## 📚 Referencias

- [Protocolo de Mensajes](docs/protocolo_mensajes.md)
- [Test de Dados Inicio](test_dados_inicio.py)
- [Modelo de Partida](backend/models/partida.py)
- [Servidor](backend/servidor.py)

"""Servidor con soporte para múltiples salas de juego."""
import asyncio
import websockets
import json
import uuid
from typing import Dict, Set, Optional
from models.partida import Partida
from datetime import datetime

class SalaJuego:
    """Representa una sala de juego individual."""
    
    def __init__(self, codigo: str, host_socket, max_jugadores: int = 4, num_bots: int = 0):
        self.codigo = codigo
        self.host_socket = host_socket
        self.partida = Partida(id_partida=codigo, max_jugadores=max_jugadores)
        self.conexiones: Set[websockets.WebSocketServerProtocol] = {host_socket}
        self.jugadores: Dict[websockets.WebSocketServerProtocol, str] = {}  # socket -> jugador_id
        self.max_jugadores = max_jugadores
        self.num_bots = num_bots
        self.iniciada = False
        self.creada_en = datetime.now()
        
    def agregar_conexion(self, websocket):
        """Agrega una nueva conexión a la sala."""
        self.conexiones.add(websocket)
        
    def remover_conexion(self, websocket):
        """Remueve una conexión de la sala."""
        self.conexiones.discard(websocket)
        if websocket in self.jugadores:
            del self.jugadores[websocket]
            
    def esta_llena(self):
        """Verifica si la sala está llena."""
        return len(self.jugadores) >= self.max_jugadores
        
    def esta_vacia(self):
        """Verifica si la sala está vacía."""
        return len(self.conexiones) == 0


class ServidorSalas:
    """Servidor que maneja múltiples salas de juego."""
    
    def __init__(self, host: str = "0.0.0.0", puerto: int = 5555):
        self.host = host
        self.puerto = puerto
        self.salas: Dict[str, SalaJuego] = {}  # codigo_sala -> SalaJuego
        self.conexiones_salas: Dict[websockets.WebSocketServerProtocol, str] = {}  # websocket -> codigo_sala
        
    def generar_codigo_sala(self) -> str:
        """Genera un código único de 6 caracteres para una sala."""
        import random
        import string
        while True:
            codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if codigo not in self.salas:
                return codigo
    
    async def crear_sala(self, websocket, data: dict):
        """Crea una nueva sala de juego."""
        try:
            nombre_jugador = data.get('playerName', 'Anónimo')
            max_jugadores = data.get('maxPlayers', 4)
            num_bots = data.get('numBots', 0)
            color = data.get('color', 'red')
            
            # Generar código de sala
            codigo_sala = self.generar_codigo_sala()
            
            # Crear sala
            sala = SalaJuego(codigo_sala, websocket, max_jugadores, num_bots)
            self.salas[codigo_sala] = sala
            self.conexiones_salas[websocket] = codigo_sala
            
            # Agregar jugador host a la partida
            jugador = sala.partida.agregar_jugador(nombre_jugador, str(websocket.id))
            if jugador:
                sala.jugadores[websocket] = jugador.id
                
                # Agregar bots si se solicitó
                for i in range(num_bots):
                    bot_name = f"Bot {i+1}"
                    bot_id = f"bot_{uuid.uuid4().hex[:8]}"
                    sala.partida.agregar_jugador(bot_name, bot_id)
            
            # Enviar respuesta exitosa
            await websocket.send(json.dumps({
                "tipo": "SALA_CREADA",
                "exito": True,
                "codigo_sala": codigo_sala,
                "mensaje": f"Sala {codigo_sala} creada exitosamente",
                "jugador": {
                    "nombre": nombre_jugador,
                    "color": jugador.color if jugador else color,
                    "es_host": True
                },
                "estado_sala": self._obtener_estado_sala(sala)
            }))
            
            print(f"✅ Sala {codigo_sala} creada por {nombre_jugador}")
            
        except Exception as e:
            print(f"❌ Error al crear sala: {e}")
            await websocket.send(json.dumps({
                "tipo": "ERROR",
                "mensaje": f"Error al crear sala: {str(e)}"
            }))
    
    async def unirse_sala(self, websocket, data: dict):
        """Permite a un jugador unirse a una sala existente."""
        try:
            codigo_sala = data.get('roomCode', '').upper()
            nombre_jugador = data.get('playerName', 'Anónimo')
            color = data.get('color')
            
            # Verificar si la sala existe
            if codigo_sala not in self.salas:
                await websocket.send(json.dumps({
                    "tipo": "ERROR",
                    "mensaje": "Sala no encontrada"
                }))
                return
            
            sala = self.salas[codigo_sala]
            
            # Verificar si la sala está llena
            if sala.esta_llena():
                await websocket.send(json.dumps({
                    "tipo": "ERROR",
                    "mensaje": "La sala está llena"
                }))
                return
            
            # Si no se especificó color, obtener colores disponibles primero
            if not color:
                colores_usados = {j.color for j in sala.partida.jugadores}
                colores_disponibles = [c for c in ['red', 'blue', 'green', 'yellow'] if c not in colores_usados]
                
                await websocket.send(json.dumps({
                    "tipo": "COLORES_DISPONIBLES",
                    "exito": True,
                    "colores": colores_disponibles,
                    "codigo_sala": codigo_sala
                }))
                return
            
            # Agregar jugador a la sala
            jugador = sala.partida.agregar_jugador(nombre_jugador, str(websocket.id))
            
            if not jugador:
                await websocket.send(json.dumps({
                    "tipo": "ERROR",
                    "mensaje": "No se pudo unir a la sala"
                }))
                return
            
            # Registrar conexión
            sala.agregar_conexion(websocket)
            sala.jugadores[websocket] = jugador.id
            self.conexiones_salas[websocket] = codigo_sala
            
            # Enviar confirmación al jugador que se unió
            await websocket.send(json.dumps({
                "tipo": "UNIDO_A_SALA",
                "exito": True,
                "codigo_sala": codigo_sala,
                "jugador": {
                    "nombre": nombre_jugador,
                    "color": jugador.color,
                    "es_host": False
                },
                "estado_sala": self._obtener_estado_sala(sala)
            }))
            
            # Notificar a todos los jugadores en la sala
            await self.broadcast_sala(codigo_sala, {
                "tipo": "JUGADOR_UNIDO",
                "jugador": nombre_jugador,
                "color": jugador.color,
                "estado_sala": self._obtener_estado_sala(sala)
            })
            
            print(f"✅ {nombre_jugador} se unió a sala {codigo_sala}")
            
        except Exception as e:
            print(f"❌ Error al unirse a sala: {e}")
            await websocket.send(json.dumps({
                "tipo": "ERROR",
                "mensaje": f"Error al unirse a la sala: {str(e)}"
            }))
    
    async def iniciar_partida(self, websocket, data: dict):
        """Inicia la partida en una sala."""
        try:
            codigo_sala = self.conexiones_salas.get(websocket)
            
            if not codigo_sala or codigo_sala not in self.salas:
                await websocket.send(json.dumps({
                    "tipo": "ERROR",
                    "mensaje": "No estás en ninguna sala"
                }))
                return
            
            sala = self.salas[codigo_sala]
            
            # Verificar que sea el host
            if websocket != sala.host_socket:
                await websocket.send(json.dumps({
                    "tipo": "ERROR",
                    "mensaje": "Solo el host puede iniciar la partida"
                }))
                return
            
            # Iniciar partida
            if sala.partida.iniciar_partida():
                # ✅ IMPORTANTE: Saltar el modo "esperando_dados_inicio" 
                # El frontend ya determinó el orden
                sala.partida.esperando_dados_inicio = False
                
                # Asegurar que el primer jugador tenga su turno activado
                if sala.partida.jugadores:
                    for i, jugador in enumerate(sala.partida.jugadores):
                        jugador.es_su_turno = (i == sala.partida.turno_actual)
                
                sala.iniciada = True
                
                # Notificar a todos
                await self.broadcast_sala(codigo_sala, {
                    "tipo": "PARTIDA_INICIADA",
                    "mensaje": "¡La partida ha comenzado!",
                    "estado": sala.partida.obtener_estado()
                })
                
                print(f"🎮 Partida iniciada en sala {codigo_sala}")
                print(f"   Jugador actual: {sala.partida.jugadores[sala.partida.turno_actual].nombre if sala.partida.jugadores else 'Ninguno'}")
                
                # Si el jugador actual es un bot, ejecutar su turno automáticamente
                await self.ejecutar_turno_bot_si_necesario(codigo_sala)
            else:
                await websocket.send(json.dumps({
                    "tipo": "ERROR",
                    "mensaje": "No hay suficientes jugadores para iniciar"
                }))
                
        except Exception as e:
            print(f"❌ Error al iniciar partida: {e}")
            await websocket.send(json.dumps({
                "tipo": "ERROR",
                "mensaje": f"Error al iniciar partida: {str(e)}"
            }))
    
    async def procesar_mensaje(self, websocket, mensaje: dict):
        """Procesa los mensajes recibidos."""
        tipo = mensaje.get("tipo")
        
        if tipo == "CREAR_SALA":
            await self.crear_sala(websocket, mensaje)
        
        elif tipo == "UNIRSE_SALA":
            await self.unirse_sala(websocket, mensaje)
        
        elif tipo == "INICIAR_PARTIDA":
            await self.iniciar_partida(websocket, mensaje)
        
        elif tipo == "LANZAR_DADOS":
            await self.lanzar_dados(websocket, mensaje)
        
        elif tipo == "MOVER_FICHA":
            await self.mover_ficha(websocket, mensaje)
        
        else:
            await websocket.send(json.dumps({
                "tipo": "ERROR",
                "mensaje": "Tipo de mensaje desconocido"
            }))
    
    async def lanzar_dados(self, websocket, mensaje: dict):
        """Procesa el lanzamiento de dados."""
        codigo_sala = self.conexiones_salas.get(websocket)
        if not codigo_sala or codigo_sala not in self.salas:
            return
        
        sala = self.salas[codigo_sala]
        jugador_id = sala.jugadores.get(websocket)
        
        if not jugador_id:
            return
        
        # Buscar jugador en la partida
        jugador = next((j for j in sala.partida.jugadores if j.id == jugador_id), None)
        if not jugador or not jugador.es_su_turno:
            await websocket.send(json.dumps({
                "tipo": "ERROR",
                "mensaje": "No es tu turno"
            }))
            return
        
        # Lanzar dados
        dados = sala.partida.lanzar_dados()
        suma_dados = dados[0] + dados[1]
        es_par = dados[0] == dados[1]
        
        print(f"🎲 {jugador.nombre} lanzó dados: {dados} (suma: {suma_dados}, par: {es_par})")
        
        # Broadcast a todos en la sala
        await self.broadcast_sala(codigo_sala, {
            "tipo": "DADOS_LANZADOS",
            "jugador": jugador.nombre,
            "dados": list(dados),
            "suma": suma_dados,
            "es_par": es_par,
            "estado": sala.partida.obtener_estado()
        })
    
    async def mover_ficha(self, websocket, mensaje: dict):
        """Procesa el movimiento de una ficha."""
        codigo_sala = self.conexiones_salas.get(websocket)
        if not codigo_sala or codigo_sala not in self.salas:
            return
        
        sala = self.salas[codigo_sala]
        jugador_id = sala.jugadores.get(websocket)
        
        if not jugador_id:
            return
        
        jugador = next((j for j in sala.partida.jugadores if j.id == jugador_id), None)
        if not jugador:
            return
        
        id_ficha = mensaje.get("id_ficha")
        dados = tuple(mensaje.get("dados", []))
        
        # Procesar turno
        resultado = sala.partida.procesar_turno(jugador, dados, id_ficha)
        
        # Enviar resultado al jugador
        await websocket.send(json.dumps({
            "tipo": "RESULTADO_MOVIMIENTO",
            **resultado
        }))
        
        # Broadcast estado actualizado
        await self.broadcast_sala(codigo_sala, {
            "tipo": "ESTADO_ACTUALIZADO",
            "estado": sala.partida.obtener_estado()
        })
        
        # Si el siguiente jugador es un bot, ejecutar su turno
        await self.ejecutar_turno_bot_si_necesario(codigo_sala)
    
    def elegir_mejor_ficha_bot(self, jugador, suma_dados: int, es_par: bool) -> Optional[int]:
        """
        Elige la mejor ficha para mover según estrategias del bot.
        
        Prioridades (como bot_jugador.py):
        1. Si hay PAR y fichas en cárcel → Sacar de cárcel
        2. Fichas más adelantadas (cerca de META)
        3. Primera ficha disponible que pueda moverse
        """
        fichas_en_carcel = []
        fichas_movibles = []
        
        # Clasificar fichas
        for ficha in jugador.fichas:
            if ficha.esta_en_carcel():
                fichas_en_carcel.append(ficha.id)
            elif not ficha.esta_en_meta():
                # Verificar si puede moverse
                if jugador.puede_mover(ficha.id, suma_dados):
                    fichas_movibles.append({
                        'id': ficha.id,
                        'casillas_recorridas': ficha.casillas_recorridas,
                        'estado': ficha.estado
                    })
        
        # Estrategia 1: Priorizar sacar de cárcel con PAR
        if es_par and fichas_en_carcel:
            return fichas_en_carcel[0]
        
        # Estrategia 2: Mover la ficha más adelantada
        if fichas_movibles:
            # Ordenar por casillas recorridas (más adelantada primero)
            fichas_movibles.sort(key=lambda f: f['casillas_recorridas'], reverse=True)
            return fichas_movibles[0]['id']
        
        # No hay fichas disponibles
        return None
    
    async def ejecutar_turno_bot_si_necesario(self, codigo_sala: str):
        """Ejecuta el turno de un bot si es su turno."""
        if codigo_sala not in self.salas:
            print(f"   [BOT] Sala {codigo_sala} no existe")
            return
        
        sala = self.salas[codigo_sala]
        
        # Obtener el jugador actual
        jugador_actual = next((j for j in sala.partida.jugadores if j.es_su_turno), None)
        if not jugador_actual:
            print(f"   [BOT] No hay jugador con turno activo")
            return
        
        print(f"   [BOT] Verificando jugador: {jugador_actual.nombre} (ID: {jugador_actual.id})")
        
        # Verificar si es un bot
        if not jugador_actual.id.startswith('bot_'):
            print(f"   [BOT] {jugador_actual.nombre} no es un bot, esperando acción humana")
            return
        
        print(f"   🤖 [BOT] Es turno del bot {jugador_actual.nombre}, ejecutando turno automático...")
        
        # Esperar un poco para que parezca más natural (como bot_jugador.py)
        await asyncio.sleep(1.5)
        
        # Lanzar dados
        dados = sala.partida.lanzar_dados()
        suma_dados = dados[0] + dados[1]
        es_par = sala.partida.es_par(dados)
        
        # Broadcast del lanzamiento de dados
        await self.broadcast_sala(codigo_sala, {
            "tipo": "DADOS_LANZADOS",
            "jugador": jugador_actual.nombre,
            "dados": dados,
            "suma": suma_dados,
            "es_par": es_par
        })
        
        # Esperar un poco antes de decidir movimiento (como bot_jugador.py)
        await asyncio.sleep(1.0)
        
        # Usar la estrategia inteligente para elegir la mejor ficha
        id_ficha_a_mover = self.elegir_mejor_ficha_bot(jugador_actual, suma_dados, es_par)
        
        # Procesar el turno
        if id_ficha_a_mover is not None:
            resultado = sala.partida.procesar_turno(jugador_actual, dados, id_ficha_a_mover)
            
            # Broadcast del estado actualizado
            await self.broadcast_sala(codigo_sala, {
                "tipo": "ESTADO_ACTUALIZADO",
                "estado": sala.partida.obtener_estado()
            })
            
            # Esperar un poco entre acciones (como bot_jugador.py)
            await asyncio.sleep(0.8)
            
            # Si el bot puede seguir jugando (sacó pares y no cambió turno), ejecutar otro turno
            if es_par and not resultado.get('cambio_turno', False):
                await self.ejecutar_turno_bot_si_necesario(codigo_sala)
            else:
                # Verificar si el siguiente jugador también es bot
                await self.ejecutar_turno_bot_si_necesario(codigo_sala)
        else:
            # No hay movimientos posibles
            # Si todas están en cárcel y no sacó par, procesar turno sin ficha
            resultado = sala.partida.procesar_turno(jugador_actual, dados, None)
            
            await self.broadcast_sala(codigo_sala, {
                "tipo": "ESTADO_ACTUALIZADO",
                "estado": sala.partida.obtener_estado()
            })
            
            # Si cambió el turno, verificar si el siguiente también es bot
            if resultado.get('cambio_turno', False):
                await asyncio.sleep(0.8)
                await self.ejecutar_turno_bot_si_necesario(codigo_sala)
    
    async def broadcast_sala(self, codigo_sala: str, mensaje: dict):
        """Envía un mensaje a todos los jugadores de una sala."""
        if codigo_sala not in self.salas:
            return
        
        sala = self.salas[codigo_sala]
        mensaje_json = json.dumps(mensaje)
        
        # Enviar a todas las conexiones activas
        conexiones_cerradas = []
        for conexion in sala.conexiones:
            try:
                await conexion.send(mensaje_json)
            except:
                conexiones_cerradas.append(conexion)
        
        # Limpiar conexiones cerradas
        for conexion in conexiones_cerradas:
            sala.remover_conexion(conexion)
    
    def _obtener_estado_sala(self, sala: SalaJuego) -> dict:
        """Obtiene el estado actual de una sala."""
        return {
            "codigo": sala.codigo,
            "jugadores": [{
                "nombre": j.nombre,
                "color": j.color
            } for j in sala.partida.jugadores],
            "max_jugadores": sala.max_jugadores,
            "jugadores_conectados": len(sala.jugadores),
            "iniciada": sala.iniciada
        }
    
    async def manejar_conexion(self, websocket):
        """Maneja una nueva conexión de WebSocket."""
        print(f"🔌 Nueva conexión desde {websocket.remote_address}")
        
        try:
            # Enviar mensaje de bienvenida
            await websocket.send(json.dumps({
                "tipo": "CONECTADO",
                "mensaje": "Conectado al servidor de salas"
            }))
            
            # Escuchar mensajes
            async for mensaje in websocket:
                try:
                    data = json.loads(mensaje)
                    await self.procesar_mensaje(websocket, data)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "tipo": "ERROR",
                        "mensaje": "JSON inválido"
                    }))
                except Exception as e:
                    print(f"❌ Error procesando mensaje: {e}")
                    await websocket.send(json.dumps({
                        "tipo": "ERROR",
                        "mensaje": str(e)
                    }))
        
        except websockets.exceptions.ConnectionClosed:
            print(f"❌ Conexión cerrada: {websocket.remote_address}")
        
        finally:
            # Limpiar al desconectar
            await self.desconectar_cliente(websocket)
    
    async def desconectar_cliente(self, websocket):
        """Limpia recursos al desconectar un cliente."""
        codigo_sala = self.conexiones_salas.get(websocket)
        
        if codigo_sala and codigo_sala in self.salas:
            sala = self.salas[codigo_sala]
            sala.remover_conexion(websocket)
            
            # Notificar a otros jugadores
            if not sala.esta_vacia():
                await self.broadcast_sala(codigo_sala, {
                    "tipo": "JUGADOR_DESCONECTADO",
                    "estado_sala": self._obtener_estado_sala(sala)
                })
            else:
                # Eliminar sala si está vacía
                print(f"🗑️  Eliminando sala vacía {codigo_sala}")
                del self.salas[codigo_sala]
        
        if websocket in self.conexiones_salas:
            del self.conexiones_salas[websocket]
    
    async def iniciar(self):
        """Inicia el servidor."""
        print(f"🚀 Servidor de salas iniciando en {self.host}:{self.puerto}")
        
        async with websockets.serve(self.manejar_conexion, self.host, self.puerto):
            print(f"✅ Servidor escuchando en ws://{self.host}:{self.puerto}")
            print("Esperando conexiones...")
            await asyncio.Future()  # Mantener servidor corriendo


if __name__ == "__main__":
    import sys
    
    host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 5555
    
    servidor = ServidorSalas(host, puerto)
    
    try:
        asyncio.run(servidor.iniciar())
    except KeyboardInterrupt:
        print("\n⚠️  Servidor detenido por el usuario")

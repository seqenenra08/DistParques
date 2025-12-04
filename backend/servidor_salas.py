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
            players_info = data.get('players', [])  # ✅ NUEVO: Obtener info de todos los jugadores
            
            print(f"🔍 DEBUG - Datos recibidos en crear_sala:")
            print(f"  - playerName: {nombre_jugador}")
            print(f"  - maxPlayers: {max_jugadores}")
            print(f"  - numBots: {num_bots}")
            print(f"  - color: {color}")
            print(f"  - players (array): {players_info}")
            print(f"  - players length: {len(players_info)}")
            
            # Generar código de sala
            codigo_sala = self.generar_codigo_sala()
            
            # Crear sala
            sala = SalaJuego(codigo_sala, websocket, max_jugadores, num_bots)
            self.salas[codigo_sala] = sala
            self.conexiones_salas[websocket] = codigo_sala
            
            # ✅ NUEVO: Si viene información de jugadores con colores, usarla
            if players_info and len(players_info) > 0:
                print(f"🎨 Creando sala con jugadores pre-configurados:")
                for player_data in players_info:
                    player_name = player_data.get('name', 'Jugador')
                    player_color = player_data.get('color', 'red')
                    player_is_human = player_data.get('isHuman', True)
                    player_id = player_data.get('id', '')
                    
                    if player_is_human:
                        # Es el jugador humano (host)
                        print(f"  👤 {player_name} - Color: {player_color} (Humano)")
                        jugador = sala.partida.agregar_jugador(player_name, str(websocket.id), player_color)
                        if jugador:
                            sala.jugadores[websocket] = jugador.id
                    else:
                        # Es un bot
                        bot_id = player_id if player_id.startswith('bot_') else f"bot_{uuid.uuid4().hex[:8]}"
                        print(f"  🤖 {player_name} - Color: {player_color} (Bot)")
                        bot_jugador = sala.partida.agregar_jugador(player_name, bot_id, player_color)
            else:
                # Modo antiguo: agregar jugador y bots sin colores pre-configurados
                print(f"🎨 Creando sala - Jugador: {nombre_jugador}, Color solicitado: {color}")
                jugador = sala.partida.agregar_jugador(nombre_jugador, str(websocket.id), color)
                if jugador:
                    sala.jugadores[websocket] = jugador.id
                    print(f"✅ Jugador {nombre_jugador} agregado con color: {jugador.color}")
                    
                    # Agregar bots si se solicitó - asignar colores disponibles automáticamente
                    for i in range(num_bots):
                        bot_name = f"Bot {i+1}"
                        bot_id = f"bot_{uuid.uuid4().hex[:8]}"
                        bot_jugador = sala.partida.agregar_jugador(bot_name, bot_id)
                        if bot_jugador:
                            print(f"🤖 Bot {i+1} agregado con color: {bot_jugador.color}")
            
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
            
            print(f"🔍 [UNIRSE] Código: {codigo_sala}, Jugador: {nombre_jugador}, Color: {color}")
            
            # Verificar si la sala existe
            if codigo_sala not in self.salas:
                print(f"❌ [UNIRSE] Sala {codigo_sala} no encontrada. Salas disponibles: {list(self.salas.keys())}")
                await websocket.send(json.dumps({
                    "tipo": "ERROR",
                    "mensaje": "Sala no encontrada"
                }))
                return
            
            print(f"✅ [UNIRSE] Sala {codigo_sala} encontrada")
            sala = self.salas[codigo_sala]
            
            # Verificar si la sala está llena
            if sala.esta_llena():
                print(f"❌ [UNIRSE] Sala {codigo_sala} está llena")
                await websocket.send(json.dumps({
                    "tipo": "ERROR",
                    "mensaje": "La sala está llena"
                }))
                return
            
            print(f"✅ [UNIRSE] Sala tiene espacio disponible")
            
            # Si no se especificó color, obtener colores disponibles primero
            if not color:
                print(f"🎨 [UNIRSE] Color no especificado, enviando colores disponibles...")
                colores_usados = {j.color for j in sala.partida.jugadores}
                colores_disponibles = [c for c in ['red', 'blue', 'green', 'yellow'] if c not in colores_usados]
                
                print(f"🎨 [UNIRSE] Colores usados: {colores_usados}")
                print(f"🎨 [UNIRSE] Colores disponibles: {colores_disponibles}")
                
                mensaje_respuesta = {
                    "tipo": "COLORES_DISPONIBLES",
                    "exito": True,
                    "colores": colores_disponibles,
                    "codigo_sala": codigo_sala
                }
                print(f"📤 [UNIRSE] Enviando respuesta: {mensaje_respuesta}")
                await websocket.send(json.dumps(mensaje_respuesta))
                print(f"✅ [UNIRSE] COLORES_DISPONIBLES enviado correctamente")
                return
            
            # Agregar jugador a la sala con su color preferido
            print(f"🎨 Unirse a sala - Jugador: {nombre_jugador}, Color solicitado: {color}")
            jugador = sala.partida.agregar_jugador(nombre_jugador, str(websocket.id), color)
            
            if not jugador:
                await websocket.send(json.dumps({
                    "tipo": "ERROR",
                    "mensaje": "No se pudo unir a la sala (color no disponible o sala llena)"
                }))
                return
            
            print(f"✅ Jugador {nombre_jugador} unido con color: {jugador.color}")
            
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
            print(f"❌ [UNIRSE] Error al unirse a sala: {e}")
            import traceback
            traceback.print_exc()
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
                # ✅ IMPORTANTE: NO saltar la fase de dados iniciales
                # Cada jugador deberá lanzar el dado para determinar el orden
                # sala.partida.esperando_dados_inicio ya está en True por defecto
                
                sala.iniciada = True
                
                # Obtener estado y transformarlo para el frontend
                estado_backend = sala.partida.obtener_estado()
                estado_frontend = self._transformar_estado_para_frontend(estado_backend)
                
                # Notificar a todos - indicar que deben lanzar dados para determinar orden
                await self.broadcast_sala(codigo_sala, {
                    "tipo": "PARTIDA_INICIADA",
                    "mensaje": "¡Lanzad el dado para determinar quién empieza!",
                    "esperando_dados_inicio": True,
                    "estado": estado_frontend
                })
                
                print(f"🎮 Partida iniciada en sala {codigo_sala}")
                print(f"   ⚡ Esperando dados iniciales para determinar orden")
                
                # Hacer que los bots lancen sus dados iniciales automáticamente
                await self.ejecutar_dados_iniciales_bots(codigo_sala)
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
        print(f"📨 [MENSAJE] Tipo: {tipo}, Datos: {mensaje}")
        
        if tipo == "CREAR_SALA":
            await self.crear_sala(websocket, mensaje)
        
        elif tipo == "UNIRSE_SALA":
            print(f"🚪 [UNIRSE_SALA] Procesando solicitud de {mensaje.get('playerName')} para sala {mensaje.get('roomCode')}")
            await self.unirse_sala(websocket, mensaje)
        
        elif tipo == "INICIAR_PARTIDA":
            await self.iniciar_partida(websocket, mensaje)
        
        elif tipo == "LANZAR_DADOS":
            await self.lanzar_dados(websocket, mensaje)
        
        elif tipo == "MOVER_FICHA":
            await self.mover_ficha(websocket, mensaje)
        
        # ✅ NUEVOS HANDLERS - Protocolo del servidor.py
        elif tipo == "ROLL_INICIO":
            await self.procesar_roll_inicio(websocket, mensaje)
        
        elif tipo == "ROLL":
            await self.procesar_roll(websocket, mensaje)
        
        elif tipo == "MOVE":
            await self.procesar_move(websocket, mensaje)
        
        elif tipo == "MOVE_DIVIDIDO":
            await self.procesar_move_dividido(websocket, mensaje)
        
        elif tipo == "SACAR_FICHA_JUEGO":
            await self.procesar_sacar_ficha_juego(websocket, mensaje)
        
        elif tipo == "GET_FICHAS":
            await self.procesar_get_fichas(websocket, mensaje)
        
        elif tipo == "GET_STATE":
            await self.procesar_get_state(websocket, mensaje)
        
        elif tipo == "start_tiebreaker":
            await self.procesar_inicio_desempate(websocket, mensaje)
        
        elif tipo == "start_reroll":
            await self.procesar_reinicio_dados(websocket, mensaje)
        
        elif tipo == "COMENZAR_JUEGO":
            await self.procesar_comenzar_juego(websocket, mensaje)
        
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
        
        print(f"\n🎲 {jugador.nombre} intenta lanzar dados:")
        print(f"   Estado actual: intentos_carcel={jugador.intentos_carcel}, ya_lanzo={jugador.ya_lanzo_dados}")
        
        # Lanzar dados
        dados = sala.partida.lanzar_dados()
        suma_dados = dados[0] + dados[1]
        es_par = dados[0] == dados[1]
        
        print(f"🎲 {jugador.nombre} lanzó dados: {dados} (suma: {suma_dados}, par: {es_par})")
        
        # Verificar si todas las fichas están en la cárcel
        todas_en_carcel = all(f.esta_en_carcel() for f in jugador.fichas)
        
        # Procesar el resultado solo para obtener info de intentos (no mover fichas)
        resultado_info = {
            "start_phase": todas_en_carcel,
            "is_doubles": es_par,
            "can_retry": False,
            "turn_passed": False,
            "needs_piece_selection": False,
            "attempts_used": jugador.intentos_carcel,
            "attempts_remaining": jugador.max_intentos_carcel - jugador.intentos_carcel
        }
        
        if todas_en_carcel:
            # Incrementar intentos
            jugador.incrementar_intento_carcel()
            resultado_info["attempts_used"] = jugador.intentos_carcel
            resultado_info["attempts_remaining"] = jugador.max_intentos_carcel - jugador.intentos_carcel
            
            if not es_par:
                # No sacó par
                if jugador.agotar_intentos_carcel():
                    # Se agotaron los 3 intentos - pasar turno
                    resultado_info["turn_passed"] = True
                    resultado_info["can_retry"] = False
                    jugador.ya_lanzo_dados = True  # Marcar que ya lanzó para evitar más lanzamientos
                    jugador.resetear_intentos_carcel()
                    sala.partida._cambiar_turno()
                    print(f"❌ {jugador.nombre} agotó los 3 intentos sin sacar par. Turno pasado.")
                else:
                    # Puede intentar de nuevo - NO marcar ya_lanzo_dados para permitir relanzar
                    resultado_info["can_retry"] = True
                    print(f"⚠️ {jugador.nombre} no sacó par. Intentos: {resultado_info['attempts_used']}/3")
            else:
                # Sacó par - puede sacar ficha
                resultado_info["needs_piece_selection"] = True
                jugador.resetear_intentos_carcel()
                jugador.incrementar_pares()
                jugador.ya_lanzo_dados = True  # Marcar que ya lanzó
                jugador.puede_lanzar_de_nuevo = False  # Debe mover primero
                print(f"✅ {jugador.nombre} sacó par! Puede sacar ficha de la cárcel.")
        
        # Obtener fichas en cárcel si sacó par
        pieces_in_prison = []
        if es_par and todas_en_carcel:
            pieces_in_prison = [f.id for f in jugador.fichas if f.esta_en_carcel()]
        
        # Verificar si puede dividir los dados (solo si NO están todas en cárcel y NO es par)
        puede_dividir = False
        opciones_division = []
        fichas_movibles_info = {"fichas_movibles": [], "puede_dividir": False}
        
        if not todas_en_carcel:
            fichas_movibles_info = sala.partida.tiene_movimientos_validos(jugador, dados)
            puede_dividir = fichas_movibles_info.get("puede_dividir", False)
            opciones_division = fichas_movibles_info.get("opciones_division", [])
        
        # Broadcast a todos en la sala con nombre consistente DICE_RESULT
        await self.broadcast_sala(codigo_sala, {
            "tipo": "DICE_RESULT",
            "jugador": jugador.nombre,
            "dados": list(dados),
            "suma": suma_dados,
            "es_par": es_par,
            "todas_en_carcel": todas_en_carcel,
            "mensaje": f"{jugador.nombre} lanzó {dados[0]} + {dados[1]} = {suma_dados}",
            "estado": self._enviar_estado_actualizado(sala),
            "start_phase": resultado_info["start_phase"],
            "is_doubles": resultado_info["is_doubles"],
            "can_retry": resultado_info["can_retry"],
            "turn_passed": resultado_info["turn_passed"],
            "needs_piece_selection": resultado_info["needs_piece_selection"],
            "attempts_used": resultado_info["attempts_used"],
            "attempts_remaining": resultado_info["attempts_remaining"],
            "pieces_in_prison": pieces_in_prison,
            "puede_dividir_dados": puede_dividir,
            "opciones_division": opciones_division,
            "fichas_movibles": fichas_movibles_info.get("fichas_movibles", [])
        })
        
        # Si se pasó el turno, enviar mensaje adicional de cambio de turno
        if resultado_info["turn_passed"]:
            await asyncio.sleep(0.5)  # Breve pausa para que se procese el mensaje anterior
            
            # Obtener el nuevo jugador actual
            nuevo_jugador = sala.partida.obtener_jugador_actual()
            
            # Enviar mensaje de cambio de turno con estado limpio
            await self.broadcast_sala(codigo_sala, {
                "tipo": "TURN_CHANGE",
                "jugador_anterior": jugador.nombre,
                "jugador_actual": nuevo_jugador.nombre,
                "razon": "intentos_agotados",
                "mensaje": f"{jugador.nombre} agotó los 3 intentos. Turno de {nuevo_jugador.nombre}",
                "estado": self._enviar_estado_actualizado(sala)
            })
            
            await asyncio.sleep(1.0)  # Dar tiempo para que el frontend procese
            await self.ejecutar_turno_bot_si_necesario(codigo_sala)
    
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
            "estado": self._enviar_estado_actualizado(sala)
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
            # 🔥 CRÍTICO: Enviar estado actualizado al frontend para que sepa que es turno del humano
            print(f"   📡 [BOT] Enviando UPDATE al frontend - Turno de humano")
            await self.broadcast_sala(codigo_sala, {
                "tipo": "UPDATE",
                "estado": self._enviar_estado_actualizado(sala)
            })
            return
        
        print(f"   🤖 [BOT] Es turno del bot {jugador_actual.nombre}, ejecutando turno automático...")
        
        # Esperar un poco para que parezca más natural (como bot_jugador.py)
        await asyncio.sleep(1.5)
        
        # Lanzar dados
        print(f"   🎲 [BOT] Lanzando dados...")
        dados = sala.partida.lanzar_dados()
        suma_dados = dados[0] + dados[1]
        es_par = sala.partida.es_par(dados)
        print(f"   🎲 [BOT] Dados: {dados[0]} + {dados[1]} = {suma_dados}, Es par: {es_par}")
        
        # Verificar si todas las fichas están en la cárcel
        todas_en_carcel = all(f.esta_en_carcel() for f in jugador_actual.fichas)
        
        # Preparar info de resultado (igual que lanzar_dados)
        resultado_info = {
            "start_phase": todas_en_carcel,
            "is_doubles": es_par,
            "can_retry": False,
            "turn_passed": False,
            "needs_piece_selection": False,
            "attempts_used": jugador_actual.intentos_carcel,
            "attempts_remaining": jugador_actual.max_intentos_carcel - jugador_actual.intentos_carcel
        }
        
        if todas_en_carcel:
            jugador_actual.incrementar_intento_carcel()
            resultado_info["attempts_used"] = jugador_actual.intentos_carcel
            resultado_info["attempts_remaining"] = jugador_actual.max_intentos_carcel - jugador_actual.intentos_carcel
            
            if not es_par:
                if jugador_actual.agotar_intentos_carcel():
                    resultado_info["turn_passed"] = True
                    jugador_actual.resetear_intentos_carcel()
                    sala.partida._cambiar_turno()
                else:
                    resultado_info["can_retry"] = True
            else:
                resultado_info["needs_piece_selection"] = True
                jugador_actual.resetear_intentos_carcel()
                jugador_actual.incrementar_pares()
        
        pieces_in_prison = []
        if es_par and todas_en_carcel:
            pieces_in_prison = [f.id for f in jugador_actual.fichas if f.esta_en_carcel()]
        
        # Verificar si puede dividir los dados (solo si NO están todas en cárcel y NO es par)
        puede_dividir = False
        opciones_division = []
        fichas_movibles_info = {"fichas_movibles": [], "puede_dividir": False}
        
        if not todas_en_carcel:
            fichas_movibles_info = sala.partida.tiene_movimientos_validos(jugador_actual, dados)
            puede_dividir = fichas_movibles_info.get("puede_dividir", False)
            opciones_division = fichas_movibles_info.get("opciones_division", [])
        
        # Broadcast del lanzamiento de dados con estructura completa
        print(f"   📡 [BOT] Broadcasting DICE_RESULT...")
        await self.broadcast_sala(codigo_sala, {
            "tipo": "DICE_RESULT",
            "jugador": jugador_actual.nombre,
            "dados": list(dados),
            "suma": suma_dados,
            "es_par": es_par,
            "todas_en_carcel": todas_en_carcel,
            "mensaje": f"{jugador_actual.nombre} lanzó {dados[0]} + {dados[1]} = {suma_dados}",
            "estado": self._enviar_estado_actualizado(sala),
            "start_phase": resultado_info["start_phase"],
            "is_doubles": resultado_info["is_doubles"],
            "can_retry": resultado_info["can_retry"],
            "turn_passed": resultado_info["turn_passed"],
            "needs_piece_selection": resultado_info["needs_piece_selection"],
            "attempts_used": resultado_info["attempts_used"],
            "attempts_remaining": resultado_info["attempts_remaining"],
            "pieces_in_prison": pieces_in_prison,
            "puede_dividir_dados": puede_dividir,
            "opciones_division": opciones_division,
            "fichas_movibles": fichas_movibles_info.get("fichas_movibles", [])
        })
        
        # Si se pasó el turno, ejecutar siguiente bot si es necesario
        if resultado_info["turn_passed"]:
            print(f"   ⏭️  [BOT] Turno pasado, ejecutando siguiente bot...")
            await asyncio.sleep(1.5)
            await self.ejecutar_turno_bot_si_necesario(codigo_sala)
            return
        
        # Esperar un poco antes de decidir movimiento (como bot_jugador.py)
        print(f"   🤔 [BOT] Decidiendo qué ficha mover...")
        await asyncio.sleep(1.0)
        
        # Usar la estrategia inteligente para elegir la mejor ficha
        id_ficha_a_mover = self.elegir_mejor_ficha_bot(jugador_actual, suma_dados, es_par)
        print(f"   ✅ [BOT] Ficha elegida: {id_ficha_a_mover}")
        
        # Procesar el turno
        if id_ficha_a_mover is not None:
            resultado = sala.partida.procesar_turno(jugador_actual, dados, id_ficha_a_mover)
            
            # Verificar si hubo error
            if "error" in resultado:
                print(f"   ❌ [BOT] Error al mover: {resultado['error']}")
                # Si sacó par pero no pudo mover, forzar cambio de turno para evitar loop infinito
                if es_par:
                    print(f"   🔄 [BOT] Forzando cambio de turno por error en movimiento")
                    sala.partida._cambiar_turno()
                    await self.broadcast_sala(codigo_sala, {
                        "tipo": "UPDATE",
                        "estado": self._enviar_estado_actualizado(sala)
                    })
                    await asyncio.sleep(0.8)
                    await self.ejecutar_turno_bot_si_necesario(codigo_sala)
                return
            
            # Obtener estado actualizado
            estado_actualizado = self._enviar_estado_actualizado(sala)
            cambio_turno = resultado.get('cambio_turno', False)
            
            print(f"   🤖 [BOT] {jugador_actual.nombre} movió ficha {id_ficha_a_mover}")
            print(f"   🔄 [BOT] Cambio de turno: {cambio_turno}")
            print(f"   👤 [BOT] Siguiente turno: {estado_actualizado.get('jugador_actual', 'desconocido')}")
            
            # Broadcast MOVE_RESULT para que el frontend lo procese con sonidos y animaciones
            accion = resultado.get('accion', 'movimiento')
            await self.broadcast_sala(codigo_sala, {
                "tipo": "MOVE_RESULT",
                "exito": True,
                "accion": accion,
                "jugador": jugador_actual.nombre,
                "id_ficha": id_ficha_a_mover,
                "dados": list(dados),
                "fichas_capturadas": resultado.get('fichas_capturadas', []),
                "ganador": resultado.get('ganador'),
                "mensaje": f"{jugador_actual.nombre} movió la ficha {id_ficha_a_mover}"
            })
            
            # Broadcast del estado actualizado
            await self.broadcast_sala(codigo_sala, {
                "tipo": "UPDATE",
                "estado": estado_actualizado
            })
            
            # Esperar un poco entre acciones (como bot_jugador.py)
            await asyncio.sleep(0.8)
            
            # Si el bot puede seguir jugando (sacó pares y no cambió turno), ejecutar otro turno
            if es_par and not cambio_turno:
                print(f"   🎲 [BOT] Sacó par y no cambió turno, jugando de nuevo...")
                await self.ejecutar_turno_bot_si_necesario(codigo_sala)
            else:
                print(f"   ➡️  [BOT] Verificando si siguiente jugador es bot...")
                # Verificar si el siguiente jugador también es bot
                await self.ejecutar_turno_bot_si_necesario(codigo_sala)
        else:
            # No hay movimientos posibles
            print(f"   ⚠️  [BOT] No hay ficha válida para mover")
            
            # Diagnosticar por qué no hay fichas disponibles
            fichas_en_carcel = sum(1 for f in jugador_actual.fichas if f.esta_en_carcel())
            fichas_en_meta = sum(1 for f in jugador_actual.fichas if f.esta_en_meta())
            fichas_en_tablero = sum(1 for f in jugador_actual.fichas if not f.esta_en_carcel() and not f.esta_en_meta())
            
            print(f"   📊 [BOT] Estado de fichas: {fichas_en_carcel} cárcel, {fichas_en_tablero} tablero, {fichas_en_meta} meta")
            
            # Si todas están en cárcel y no sacó par, procesar turno sin ficha
            if todas_en_carcel:
                resultado = sala.partida.procesar_turno(jugador_actual, dados, None)
                print(f"   📊 [BOT] Resultado (todas en cárcel): {resultado.get('accion', 'desconocido')}")
                
                await self.broadcast_sala(codigo_sala, {
                    "tipo": "ESTADO_ACTUALIZADO",
                    "estado": self._enviar_estado_actualizado(sala)
                })
                
                cambio_turno = resultado.get('cambio_turno', False)
                intentos_restantes = resultado.get('intentos_restantes', 0)
                
                if cambio_turno:
                    print(f"   ➡️  [BOT] Cambió turno, verificando siguiente jugador...")
                    await asyncio.sleep(0.8)
                    await self.ejecutar_turno_bot_si_necesario(codigo_sala)
                elif intentos_restantes > 0:
                    print(f"   🔄 [BOT] Quedan {intentos_restantes} intentos, reintentando...")
                    await asyncio.sleep(1.0)
                    await self.ejecutar_turno_bot_si_necesario(codigo_sala)
                else:
                    print(f"   ⛔ [BOT] Sin intentos, esperando turno del siguiente jugador")
            else:
                # No está en cárcel pero no puede mover ninguna ficha
                # Esto puede pasar si todas las fichas están bloqueadas o en situaciones especiales
                print(f"   🚫 [BOT] No puede mover ninguna ficha. Forzando cambio de turno.")
                
                # Si sacó par, resetear contador de pares para evitar problemas
                if es_par:
                    jugador_actual.resetear_pares()
                
                # Forzar cambio de turno
                sala.partida._cambiar_turno()
                
                await self.broadcast_sala(codigo_sala, {
                    "tipo": "UPDATE",
                    "estado": self._enviar_estado_actualizado(sala)
                })
                
                await asyncio.sleep(0.8)
                await self.ejecutar_turno_bot_si_necesario(codigo_sala)
    
    # ========================================================================
    # NUEVOS MÉTODOS - Protocolo completo del servidor.py
    # ========================================================================
    
    async def ejecutar_dados_iniciales_bots(self, codigo_sala: str):
        """Hace que todos los bots lancen sus dados iniciales automáticamente."""
        if codigo_sala not in self.salas:
            return
        
        sala = self.salas[codigo_sala]
        
        # Buscar todos los bots que aún no han lanzado
        for jugador in sala.partida.jugadores:
            if jugador.id.startswith('bot_') and jugador.id not in sala.partida.dados_inicio:
                # Esperar un poco para que parezca más natural
                await asyncio.sleep(1.0)
                
                # Lanzar dado
                valor = sala.partida.lanzar_dado_inicio(jugador)
                
                if valor is not None:
                    print(f"🤖 {jugador.nombre} sacó {valor} para el orden inicial")
                    
                    # Broadcast del resultado a todos
                    await self.broadcast_sala(codigo_sala, {
                        "tipo": "DADO_INICIO",
                        "jugador": jugador.nombre,
                        "color": jugador.color,
                        "valor": valor
                    })
                    
                    # Verificar si todos lanzaron después de este bot
                    if sala.partida.todos_lanzaron_inicio():
                        # Esperar un poco antes de determinar el ganador
                        await asyncio.sleep(1.5)
                        
                        # Obtener el jugador actual (ya determinado)
                        jugador_actual = sala.partida.obtener_jugador_actual()
                        dados_inicio = sala.partida.obtener_dados_inicio()
                        
                        # Crear lista de resultados para mostrar
                        resultados = []
                        for j in sala.partida.jugadores:
                            resultados.append({
                                "nombre": j.nombre,
                                "color": j.color,
                                "valor": dados_inicio.get(j.id, 0)
                            })
                        
                        print(f"🏆 {jugador_actual.nombre} comienza la partida!")
                        
                        # Broadcast del ganador y inicio de juego
                        await self.broadcast_sala(codigo_sala, {
                            "tipo": "TURNO_DETERMINADO",
                            "jugador_inicial": jugador_actual.nombre,
                            "color_inicial": jugador_actual.color,
                            "resultados": resultados,
                            "mensaje": f"¡{jugador_actual.nombre} tiene el mayor número y comienza!"
                        })
                        
                        # Enviar estado actualizado
                        await self.broadcast_sala(codigo_sala, {
                            "tipo": "UPDATE",
                            "estado": self._enviar_estado_actualizado(sala)
                        })
                        
                        # CRÍTICO: Si el primer jugador es un bot, ejecutar su turno
                        print(f"   🔍 [BOT CHECK] Verificando si jugador inicial es bot...")
                        print(f"   👤 Jugador inicial: {jugador_actual.nombre} (ID: {jugador_actual.id})")
                        await asyncio.sleep(1.5)
                        await self.ejecutar_turno_bot_si_necesario(codigo_sala)
                        
                        return  # Salir después de determinar el orden
    
    async def procesar_roll_inicio(self, websocket, mensaje: dict):
        """Procesa lanzamiento de dado para determinar el primer turno."""
        codigo_sala = self.conexiones_salas.get(websocket)
        if not codigo_sala or codigo_sala not in self.salas:
            await websocket.send(json.dumps({"error": "No estás en ninguna sala"}))
            return
        
        sala = self.salas[codigo_sala]
        jugador_id = sala.jugadores.get(websocket)
        
        if not jugador_id:
            await websocket.send(json.dumps({"error": "No estás registrado"}))
            return
        
        jugador = next((j for j in sala.partida.jugadores if j.id == jugador_id), None)
        if not jugador:
            await websocket.send(json.dumps({"error": "No estás registrado"}))
            return
        
        if not sala.partida.esperando_dados_inicio:
            await websocket.send(json.dumps({"error": "No estás en fase de selección de turno"}))
            return
        
        valor = sala.partida.lanzar_dado_inicio(jugador)
        
        if valor is None:
            await websocket.send(json.dumps({"error": "Ya lanzaste el dado o no es válido"}))
            return
        
        print(f"🎲 {jugador.nombre} sacó {valor} para el orden inicial")
        
        # Broadcast del resultado a todos
        await self.broadcast_sala(codigo_sala, {
            "tipo": "DADO_INICIO",
            "jugador": jugador.nombre,
            "color": jugador.color,
            "valor": valor
        })
        
        # Verificar si todos lanzaron
        if sala.partida.todos_lanzaron_inicio():
            # Obtener el jugador actual (ya determinado)
            jugador_actual = sala.partida.obtener_jugador_actual()
            dados_inicio = sala.partida.obtener_dados_inicio()
            
            # Crear lista de resultados para mostrar
            resultados = []
            for j in sala.partida.jugadores:
                resultados.append({
                    "nombre": j.nombre,
                    "color": j.color,
                    "valor": dados_inicio.get(j.id, 0)
                })
            
            print(f"🏆 {jugador_actual.nombre} comienza la partida!")
            
            # Broadcast del ganador y inicio de juego
            await self.broadcast_sala(codigo_sala, {
                "tipo": "TURNO_DETERMINADO",
                "jugador_inicial": jugador_actual.nombre,
                "color_inicial": jugador_actual.color,
                "resultados": resultados,
                "mensaje": f"¡{jugador_actual.nombre} tiene el mayor número y comienza!"
            })
            
            # Enviar estado actualizado
            await self.broadcast_sala(codigo_sala, {
                "tipo": "UPDATE",
                "estado": self._enviar_estado_actualizado(sala)
            })
            
            # CRÍTICO: Si el jugador inicial es un bot, ejecutar su turno
            jugador_actual = sala.partida.obtener_jugador_actual()
            print(f"   🔍 [BOT CHECK] Turno inicial determinado - Jugador: {jugador_actual.nombre} (ID: {jugador_actual.id})")
            await asyncio.sleep(1.5)
            await self.ejecutar_turno_bot_si_necesario(codigo_sala)
        
        await websocket.send(json.dumps({
            "tipo": "DADO_INICIO_RESULT",
            "valor": valor,
            "mensaje": f"Sacaste {valor}. Esperando a los demás jugadores..."
        }))
        
        # Hacer que los bots restantes lancen sus dados automáticamente
        if not sala.partida.todos_lanzaron_inicio():
            await self.ejecutar_dados_iniciales_bots(codigo_sala)
    
    async def procesar_roll(self, websocket, mensaje: dict):
        """Procesa lanzamiento de dados."""
        codigo_sala = self.conexiones_salas.get(websocket)
        if not codigo_sala or codigo_sala not in self.salas:
            return
        
        sala = self.salas[codigo_sala]
        jugador_id = sala.jugadores.get(websocket)
        
        if not jugador_id:
            await websocket.send(json.dumps({"error": "No estás registrado"}))
            return
        
        jugador = next((j for j in sala.partida.jugadores if j.id == jugador_id), None)
        if not jugador:
            await websocket.send(json.dumps({"error": "No estás registrado"}))
            return
        
        if sala.partida.esperando_dados_inicio:
            await websocket.send(json.dumps({"error": "Primero deben lanzar el dado para determinar el orden inicial"}))
            return
        
        if not jugador.es_su_turno:
            await websocket.send(json.dumps({"error": "No es tu turno"}))
            return
        
        # Verificar si tiene penalización de 3 pares pendiente
        if sala.partida.jugador_puede_sacar_ficha == jugador:
            await websocket.send(json.dumps({
                "tipo": "ERROR",
                "mensaje": "¡3 pares consecutivos! Debes elegir una ficha para sacar del juego antes de continuar."
            }))
            return
        
        # Verificar si puede lanzar
        if not jugador.puede_lanzar():
            print(f"   ❌ {jugador.nombre} NO puede lanzar:")
            print(f"      ya_lanzo_dados: {jugador.ya_lanzo_dados}")
            print(f"      puede_lanzar_de_nuevo: {jugador.puede_lanzar_de_nuevo}")
            print(f"      intentos_carcel: {jugador.intentos_carcel}")
            print(f"      todas_en_carcel: {all(f.esta_en_carcel() for f in jugador.fichas)}")
            await websocket.send(json.dumps({"error": "Ya lanzaste los dados. Debes mover primero o esperar a sacar par."}))
            return
        
        dados = sala.partida.lanzar_dados()
        suma_dados = dados[0] + dados[1]
        es_par = dados[0] == dados[1]
        print(f"🎲 {jugador.nombre} lanzó {dados}")
        print(f"   📊 Estado antes: ya_lanzo={jugador.ya_lanzo_dados}, puede_lanzar_nuevo={jugador.puede_lanzar_de_nuevo}")
        
        # NO marcar ya_lanzo_dados aquí si todas están en cárcel - se manejará después según el resultado
        
        # Verificar si todas las fichas están en cárcel
        todas_en_carcel = all(f.esta_en_carcel() for f in jugador.fichas)
        
        # Preparar info de resultado (igual que lanzar_dados)
        resultado_info = {
            "start_phase": todas_en_carcel,
            "is_doubles": es_par,
            "can_retry": False,
            "turn_passed": False,
            "needs_piece_selection": False,
            "attempts_used": jugador.intentos_carcel,
            "attempts_remaining": jugador.max_intentos_carcel - jugador.intentos_carcel
        }
        
        if todas_en_carcel:
            # Incrementar intentos
            jugador.incrementar_intento_carcel()
            resultado_info["attempts_used"] = jugador.intentos_carcel
            resultado_info["attempts_remaining"] = jugador.max_intentos_carcel - jugador.intentos_carcel
            
            if not es_par:
                # No sacó par
                if jugador.agotar_intentos_carcel():
                    # Se agotaron los 3 intentos - pasar turno
                    resultado_info["turn_passed"] = True
                    resultado_info["can_retry"] = False
                    jugador.ya_lanzo_dados = True  # Marcar que ya lanzó para evitar más lanzamientos
                    jugador.resetear_intentos_carcel()
                    sala.partida._cambiar_turno()
                    print(f"❌ {jugador.nombre} agotó los 3 intentos sin sacar par. Turno pasado.")
                else:
                    # Puede intentar de nuevo - NO marcar ya_lanzo_dados para permitir relanzar
                    resultado_info["can_retry"] = True
                    print(f"⚠️ {jugador.nombre} no sacó par. Intentos: {resultado_info['attempts_used']}/3")
            else:
                # Sacó par - puede sacar ficha
                resultado_info["needs_piece_selection"] = True
                jugador.resetear_intentos_carcel()
                jugador.incrementar_pares()
                jugador.ya_lanzo_dados = True  # Marcar que ya lanzó
                jugador.puede_lanzar_de_nuevo = False  # Debe mover primero
                print(f"✅ {jugador.nombre} sacó par! Puede sacar ficha de la cárcel.")
        else:
            # Si NO todas están en cárcel, marcar que ya lanzó normalmente
            jugador.ya_lanzo_dados = True
            jugador.puede_lanzar_de_nuevo = False  # Por defecto no puede lanzar de nuevo, se activará si es par
        
        # Obtener fichas en cárcel si sacó par
        pieces_in_prison = []
        if es_par and todas_en_carcel:
            pieces_in_prison = [f.id for f in jugador.fichas if f.esta_en_carcel()]
        
        # Verificar si puede dividir los dados (solo si NO están todas en cárcel y NO es par)
        puede_dividir = False
        opciones_division = []
        fichas_movibles_info = {"fichas_movibles": [], "puede_dividir": False}
        
        if not todas_en_carcel:
            fichas_movibles_info = sala.partida.tiene_movimientos_validos(jugador, dados)
            puede_dividir = fichas_movibles_info.get("puede_dividir", False)
            opciones_division = fichas_movibles_info.get("opciones_division", [])
        
        # Preparar mensaje de dados
        dice_message = {
            "tipo": "DICE_RESULT",
            "dados": list(dados),
            "suma": suma_dados,
            "es_par": es_par,
            "todas_en_carcel": todas_en_carcel,
            "jugador": jugador.nombre,  # Agregar nombre del jugador
            "mensaje": f"{jugador.nombre} lanzó {dados[0]} + {dados[1]} = {suma_dados}",
            "start_phase": resultado_info["start_phase"],
            "is_doubles": resultado_info["is_doubles"],
            "can_retry": resultado_info["can_retry"],
            "turn_passed": resultado_info["turn_passed"],
            "needs_piece_selection": resultado_info["needs_piece_selection"],
            "attempts_used": resultado_info["attempts_used"],
            "attempts_remaining": resultado_info["attempts_remaining"],
            "pieces_in_prison": pieces_in_prison,
            "puede_dividir_dados": puede_dividir,
            "opciones_division": opciones_division,
            "fichas_movibles": fichas_movibles_info.get("fichas_movibles", [])
        }
        
        # Enviar al jugador que lanzó
        await websocket.send(json.dumps(dice_message))
        
        # Broadcast a todos los demás jugadores en la sala
        await self.broadcast_sala(codigo_sala, dice_message, exclude=websocket)
        
        # Si se pasó el turno, enviar mensaje adicional de cambio de turno
        if resultado_info["turn_passed"]:
            print(f"⏭️  {jugador.nombre} perdió el turno (intentos agotados)")
            await asyncio.sleep(0.5)
            
            # Obtener el nuevo jugador actual
            nuevo_jugador = sala.partida.obtener_jugador_actual()
            
            # Enviar mensaje de cambio de turno con estado limpio
            await self.broadcast_sala(codigo_sala, {
                "tipo": "TURN_CHANGE",
                "jugador_anterior": jugador.nombre,
                "jugador_actual": nuevo_jugador.nombre,
                "razon": "intentos_agotados",
                "mensaje": f"{jugador.nombre} agotó los 3 intentos. Turno de {nuevo_jugador.nombre}",
                "estado": self._enviar_estado_actualizado(sala)
            })
            
            await asyncio.sleep(1.0)
            await self.ejecutar_turno_bot_si_necesario(codigo_sala)
    
    async def procesar_get_fichas(self, websocket, mensaje: dict):
        """Retorna información detallada de las fichas del jugador."""
        codigo_sala = self.conexiones_salas.get(websocket)
        if not codigo_sala or codigo_sala not in self.salas:
            return
        
        sala = self.salas[codigo_sala]
        jugador_id = sala.jugadores.get(websocket)
        
        if not jugador_id:
            await websocket.send(json.dumps({"error": "No estás registrado"}))
            return
        
        jugador = next((j for j in sala.partida.jugadores if j.id == jugador_id), None)
        if not jugador:
            await websocket.send(json.dumps({"error": "No estás registrado"}))
            return
        
        fichas_info = sala.partida.obtener_fichas_disponibles(jugador)
        
        await websocket.send(json.dumps({
            "tipo": "FICHAS_INFO",
            "fichas": fichas_info
        }))
    
    async def procesar_move_dividido(self, websocket, mensaje: dict):
        """Procesa movimiento con dados divididos."""
        codigo_sala = self.conexiones_salas.get(websocket)
        if not codigo_sala or codigo_sala not in self.salas:
            return
        
        sala = self.salas[codigo_sala]
        jugador_id = sala.jugadores.get(websocket)
        
        if not jugador_id:
            await websocket.send(json.dumps({"error": "No estás registrado"}))
            return
        
        jugador = next((j for j in sala.partida.jugadores if j.id == jugador_id), None)
        if not jugador:
            await websocket.send(json.dumps({"error": "No estás registrado"}))
            return
        
        dados = tuple(mensaje.get("dados", []))
        movimientos = mensaje.get("movimientos", [])
        
        if not dados:
            await websocket.send(json.dumps({"error": "Debes lanzar los dados primero"}))
            return
        
        if not movimientos:
            await websocket.send(json.dumps({"error": "Debes especificar los movimientos"}))
            return
        
        resultado = sala.partida.procesar_turno_dividido(jugador, dados, movimientos)
        
        if "error" not in resultado:
            print(f"🚶 {jugador.nombre} hizo {len(movimientos)} movimiento(s)")
            # Log de capturas si hay
            total_capturas = sum(m.get("capturadas", 0) for m in resultado.get("movimientos_realizados", []))
            if total_capturas > 0:
                print(f"   💥 {jugador.nombre} capturó {total_capturas} ficha(s)")
        
        resultado["tipo"] = "MOVE_RESULT"
        await websocket.send(json.dumps(resultado))
        
        # Broadcast estado actualizado
        await self.broadcast_sala(codigo_sala, {
            "tipo": "UPDATE",
            "estado": self._enviar_estado_actualizado(sala)
        })
        
        # Si cambió el turno, ejecutar bot si es necesario
        if resultado.get('cambio_turno', False):
            await asyncio.sleep(1.0)
            await self.ejecutar_turno_bot_si_necesario(codigo_sala)
    
    async def procesar_move(self, websocket, mensaje: dict):
        """Procesa movimiento de ficha (modo clásico)."""
        codigo_sala = self.conexiones_salas.get(websocket)
        if not codigo_sala or codigo_sala not in self.salas:
            return
        
        sala = self.salas[codigo_sala]
        jugador_id = sala.jugadores.get(websocket)
        
        if not jugador_id:
            await websocket.send(json.dumps({"error": "No estás registrado"}))
            return
        
        jugador = next((j for j in sala.partida.jugadores if j.id == jugador_id), None)
        if not jugador:
            await websocket.send(json.dumps({"error": "No estás registrado"}))
            return
        
        id_ficha = mensaje.get("id_ficha")
        dados = tuple(mensaje.get("dados", []))
        
        print(f"📥 [MOVE] {jugador.nombre} intenta mover ficha {id_ficha} con dados {dados}")
        
        if not dados:
            await websocket.send(json.dumps({"error": "Debes lanzar los dados primero"}))
            return
        
        resultado = sala.partida.procesar_turno(jugador, dados, id_ficha)
        print(f"📤 [MOVE] Resultado: {resultado.get('accion', 'desconocido')}, error: {resultado.get('error', 'ninguno')}")
        
        # Si sacó de la cárcel, mostrar info de la ficha
        if resultado.get('accion') == 'sacar_carcel':
            ficha_info = jugador.fichas[id_ficha]
            print(f"   ✅ Ficha {id_ficha} sacada - Nueva posición: {ficha_info.posicion}, Estado: {ficha_info.estado}")
        
        # Si hubo capturas, mostrarlas
        if resultado.get('fichas_capturadas'):
            for ficha_cap in resultado['fichas_capturadas']:
                print(f"   🎯 ¡CAPTURA! Ficha {ficha_cap.get('color')}-{ficha_cap.get('id')} devuelta a la cárcel")
        
        if "error" not in resultado:
            accion = resultado.get('accion')
            if accion == "primer_turno_sin_par":
                print(f"🎲 {jugador.nombre} - Primer turno: sin par ({resultado.get('intentos_restantes')} intentos restantes)")
            elif accion == "primer_turno_agotado":
                print(f"⏭️  {jugador.nombre} - Primer turno agotado sin sacar par")
            elif accion == "tres_pares_premio":
                print(f"🎉 {jugador.nombre} - ¡3 PARES! Ficha {resultado.get('ficha_premiada')} va directo a la meta")
            else:
                print(f"🚶 {jugador.nombre} movió ficha {id_ficha}: {accion}")
        
        resultado["tipo"] = "MOVE_RESULT"
        await websocket.send(json.dumps(resultado))
        
        # Broadcast estado actualizado
        await self.broadcast_sala(codigo_sala, {
            "tipo": "UPDATE",
            "estado": self._enviar_estado_actualizado(sala)
        })
        
        # Si cambió el turno, ejecutar bot si es necesario
        if resultado.get('cambio_turno', False):
            await asyncio.sleep(1.0)
            await self.ejecutar_turno_bot_si_necesario(codigo_sala)
    
    async def procesar_sacar_ficha_juego(self, websocket, mensaje: dict):
        """Procesa sacar una ficha del juego (por 3 pares consecutivos)."""
        codigo_sala = self.conexiones_salas.get(websocket)
        if not codigo_sala or codigo_sala not in self.salas:
            return
        
        sala = self.salas[codigo_sala]
        jugador_id = sala.jugadores.get(websocket)
        
        if not jugador_id:
            await websocket.send(json.dumps({"error": "No estás registrado"}))
            return
        
        jugador = next((j for j in sala.partida.jugadores if j.id == jugador_id), None)
        if not jugador:
            await websocket.send(json.dumps({"error": "No estás registrado"}))
            return
        
        id_ficha = mensaje.get("id_ficha")
        
        if id_ficha is None:
            await websocket.send(json.dumps({"error": "Debes especificar la ficha a sacar"}))
            return
        
        resultado = sala.partida.sacar_ficha_del_juego(jugador, id_ficha)
        
        if "error" not in resultado:
            print(f"🎯 {jugador.nombre} sacó la ficha {id_ficha} del juego (3 pares)")
        
        resultado["tipo"] = "MOVE_RESULT"
        await websocket.send(json.dumps(resultado))
        
        # Broadcast estado actualizado
        await self.broadcast_sala(codigo_sala, {
            "tipo": "UPDATE",
            "estado": self._enviar_estado_actualizado(sala)
        })
        
        # Si cambió el turno, ejecutar bot si es necesario
        if resultado.get('cambio_turno', False):
            await asyncio.sleep(1.0)
            await self.ejecutar_turno_bot_si_necesario(codigo_sala)
    
    async def procesar_get_state(self, websocket, mensaje: dict):
        """Retorna el estado actual del juego."""
        codigo_sala = self.conexiones_salas.get(websocket)
        if not codigo_sala or codigo_sala not in self.salas:
            return
        
        sala = self.salas[codigo_sala]
        
        await websocket.send(json.dumps({
            "tipo": "UPDATE",
            "estado": self._enviar_estado_actualizado(sala)
        }))
    
    async def procesar_inicio_desempate(self, websocket, mensaje: dict):
        """Procesa la solicitud de iniciar un desempate."""
        codigo_sala = self.conexiones_salas.get(websocket)
        if not codigo_sala or codigo_sala not in self.salas:
            await websocket.send(json.dumps({"error": "No estás en ninguna sala"}))
            return
        
        sala = self.salas[codigo_sala]
        
        # Verificar que sea el host
        if websocket != sala.host_socket:
            await websocket.send(json.dumps({
                "tipo": "ERROR",
                "mensaje": "Solo el host puede iniciar el desempate"
            }))
            return
        
        # Obtener los jugadores empatados
        tied_players = mensaje.get("tiedPlayers", [])
        
        if not tied_players:
            await websocket.send(json.dumps({
                "tipo": "ERROR",
                "mensaje": "No se especificaron jugadores para desempate"
            }))
            return
        
        print(f"🎲 [DESEMPATE] Iniciando desempate para sala {codigo_sala}")
        print(f"   👥 Jugadores empatados: {[p['name'] for p in tied_players]}")
        
        # Reiniciar la fase de dados iniciales solo para los jugadores empatados
        # Limpiar los dados de los jugadores empatados
        for tied_player in tied_players:
            player_id = tied_player.get('id')
            jugador = next((j for j in sala.partida.jugadores if j.id == player_id), None)
            if jugador and hasattr(sala.partida, 'dados_inicio'):
                if jugador.id in sala.partida.dados_inicio:
                    del sala.partida.dados_inicio[jugador.id]
        
        # Broadcast a todos los jugadores
        await self.broadcast_sala(codigo_sala, {
            "tipo": "tiebreaker_started",
            "tiedPlayers": tied_players,
            "mensaje": "Iniciando desempate..."
        })
        
        # Hacer que los bots lancen automáticamente si están en el desempate
        await self.ejecutar_dados_iniciales_bots(codigo_sala)
    
    async def procesar_reinicio_dados(self, websocket, mensaje: dict):
        """Procesa la solicitud de reiniciar el lanzamiento de dados."""
        codigo_sala = self.conexiones_salas.get(websocket)
        if not codigo_sala or codigo_sala not in self.salas:
            await websocket.send(json.dumps({"error": "No estás en ninguna sala"}))
            return
        
        sala = self.salas[codigo_sala]
        
        # Verificar que sea el host
        if websocket != sala.host_socket:
            await websocket.send(json.dumps({
                "tipo": "ERROR",
                "mensaje": "Solo el host puede reiniciar"
            }))
            return
        
        print(f"🔄 [REINICIO] Reiniciando lanzamiento de dados en sala {codigo_sala}")
        
        # Limpiar todos los dados lanzados
        if hasattr(sala.partida, 'dados_inicio'):
            sala.partida.dados_inicio.clear()
        
        # Resetear la fase de espera
        sala.partida.esperando_dados_inicio = True
        
        # Broadcast a todos los jugadores
        await self.broadcast_sala(codigo_sala, {
            "tipo": "reroll_started",
            "mensaje": "Reiniciando lanzamiento de dados..."
        })
        
        # Hacer que los bots lancen automáticamente
        await self.ejecutar_dados_iniciales_bots(codigo_sala)
    
    async def procesar_comenzar_juego(self, websocket, mensaje: dict):
        """Procesa la solicitud de comenzar el juego después de determinar el orden."""
        codigo_sala = self.conexiones_salas.get(websocket)
        if not codigo_sala or codigo_sala not in self.salas:
            await websocket.send(json.dumps({"error": "No estás en ninguna sala"}))
            return
        
        sala = self.salas[codigo_sala]
        
        # Verificar que sea el host
        if websocket != sala.host_socket:
            await websocket.send(json.dumps({
                "tipo": "ERROR",
                "mensaje": "Solo el host puede comenzar el juego"
            }))
            return
        
        print(f"🎮 [COMENZAR JUEGO] Iniciando juego en sala {codigo_sala}")
        
        # Broadcast a todos los jugadores para que comiencen el juego
        await self.broadcast_sala(codigo_sala, {
            "tipo": "COMENZAR_JUEGO_CONFIRMADO",
            "mensaje": "¡Comenzando el juego!"
        })
    
    async def broadcast_sala(self, codigo_sala: str, mensaje: dict, exclude=None):
        """Envía un mensaje a todos los jugadores de una sala.
        
        Args:
            codigo_sala: Código de la sala
            mensaje: Mensaje a enviar
            exclude: WebSocket a excluir del broadcast (opcional)
        """
        if codigo_sala not in self.salas:
            return
        
        sala = self.salas[codigo_sala]
        mensaje_json = json.dumps(mensaje)
        
        # Enviar a todas las conexiones activas (excepto la excluida)
        conexiones_cerradas = []
        for conexion in sala.conexiones:
            if exclude and conexion == exclude:
                continue  # Saltar la conexión excluida
            try:
                await conexion.send(mensaje_json)
            except:
                conexiones_cerradas.append(conexion)
        
        # Limpiar conexiones cerradas
        for conexion in conexiones_cerradas:
            sala.remover_conexion(conexion)
    
    def _transformar_estado_para_frontend(self, estado: dict) -> dict:
        """Transforma el estado del backend al formato esperado por el frontend."""
        estado_frontend = estado.copy()
        
        # Transformar jugadores: 'fichas' -> 'pieces', 'nombre' -> 'name'
        if 'jugadores' in estado_frontend:
            jugadores_transformados = []
            for jugador in estado_frontend['jugadores']:
                jugador_frontend = {
                    'player_id': jugador.get('id'),
                    'name': jugador.get('nombre'),
                    'color': jugador.get('color'),
                    'es_su_turno': jugador.get('es_su_turno', False),
                    'pieces_in_home': sum(1 for f in jugador.get('fichas', []) if f.get('estado') == 'meta'),
                    'pieces': []
                }
                
                # Transformar fichas
                for ficha in jugador.get('fichas', []):
                    # Mapear posición según el estado de la ficha
                    posicion = -1  # Por defecto cárcel
                    
                    if ficha.get('estado') == 'carcel':
                        posicion = -1
                    elif ficha.get('estado') == 'meta':
                        posicion = 'center'
                    elif ficha.get('estado') == 'pasillo_final':
                        # Formato: color_posicion (ej: red_3)
                        posicion = f"{jugador.get('color')}_{ficha.get('posicion_pasillo', 0)}"
                    else:
                        # Posición en tablero normal
                        posicion = ficha.get('posicion', -1)
                    
                    jugador_frontend['pieces'].append({
                        'piece_id': ficha.get('id'),
                        'color': ficha.get('color'),
                        'position': posicion,
                        'estado': ficha.get('estado'),
                        'is_in_goal': ficha.get('estado') == 'meta'
                    })
                
                jugadores_transformados.append(jugador_frontend)
            
            estado_frontend['players'] = jugadores_transformados
            estado_frontend['jugadores'] = jugadores_transformados  # Mantener ambos por compatibilidad
        
        # Cambiar 'jugador_actual' -> 'currentPlayer'
        if 'jugador_actual' in estado_frontend:
            estado_frontend['currentPlayer'] = estado_frontend['jugador_actual']
        
        # Agregar currentPlayer también basado en turno
        if 'jugadores' in estado and estado.get('turno_actual') is not None:
            turno = estado.get('turno_actual', 0)
            if turno < len(estado['jugadores']):
                estado_frontend['currentPlayer'] = estado['jugadores'][turno].get('nombre')
        
        return estado_frontend
    
    def _enviar_estado_actualizado(self, sala: SalaJuego) -> dict:
        """Obtiene el estado transformado listo para enviar al frontend."""
        estado_backend = sala.partida.obtener_estado()
        return self._transformar_estado_para_frontend(estado_backend)
    
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

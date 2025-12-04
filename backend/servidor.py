"""Servidor TCP para el juego de Parqués."""
import socket
import threading
import json
import sys
import uuid
from typing import Dict
from models.partida import Partida

class ServidorParques:
    """Servidor multi-cliente para Parqués."""
    
    def __init__(self, host: str = "0.0.0.0", puerto: int = 5555):
        self.host = host
        self.puerto = puerto
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Generar ID único para la partida
        id_partida = str(uuid.uuid4())[:8]
        self.partida = Partida(id_partida=id_partida, max_jugadores=4)
        self.clientes: Dict[socket.socket, str] = {}  # socket -> nombre_jugador
        self.lock = threading.Lock()
    
    def iniciar(self):
        """Inicia el servidor y escucha conexiones."""
        try:
            self.servidor.bind((self.host, self.puerto))
            self.servidor.listen(4)
            print(f"✅ Servidor escuchando en {self.host}:{self.puerto}")
            print("Esperando jugadores... (mínimo 2, máximo 4)")
            
            while True:
                try:
                    cliente, direccion = self.servidor.accept()
                    print(f"🔌 Nueva conexión desde {direccion}")
                    thread = threading.Thread(target=self.manejar_cliente, args=(cliente,))
                    thread.daemon = True
                    thread.start()
                except KeyboardInterrupt:
                    print("\n⚠️  Cerrando servidor...")
                    break
        except Exception as e:
            print(f"❌ Error al iniciar servidor: {e}")
        finally:
            self.servidor.close()
    
    def manejar_cliente(self, cliente: socket.socket):
        """Maneja la comunicación con un cliente."""
        jugador = None
        
        try:
            while True:
                data = cliente.recv(4096).decode('utf-8')
                if not data:
                    break
                
                try:
                    mensaje = json.loads(data)
                    respuesta = self.procesar_mensaje(cliente, mensaje, jugador)
                    
                    # Actualizar referencia de jugador si es JOIN exitoso
                    if mensaje.get("tipo") == "JOIN" and respuesta.get("exito"):
                        jugador = respuesta.get("jugador_obj")
                    
                    # Enviar respuesta al cliente
                    self.enviar(cliente, respuesta)
                    
                    # Broadcast de estado si hubo cambio
                    if mensaje.get("tipo") in ["ROLL", "MOVE", "START", "MOVE_DIVIDIDO", "ROLL_INICIO", "SACAR_FICHA_JUEGO"]:
                        self.broadcast_estado()
                
                except json.JSONDecodeError:
                    self.enviar(cliente, {"error": "JSON inválido"})
        
        except Exception as e:
            print(f"❌ Error con cliente: {e}")
        finally:
            self.desconectar_cliente(cliente, jugador)
    
    def procesar_mensaje(self, cliente: socket.socket, mensaje: dict, jugador):
        """Procesa mensajes según el protocolo."""
        tipo = mensaje.get("tipo")
        
        if tipo == "JOIN":
            return self.procesar_join(cliente, mensaje)
        
        elif tipo == "START":
            return self.procesar_start()
        
        elif tipo == "ROLL_INICIO":
            return self.procesar_roll_inicio(jugador)
        
        elif tipo == "ROLL":
            return self.procesar_roll(jugador)
        
        elif tipo == "MOVE":
            return self.procesar_move(jugador, mensaje)
        
        elif tipo == "MOVE_DIVIDIDO":
            return self.procesar_move_dividido(jugador, mensaje)
        
        elif tipo == "SACAR_FICHA_JUEGO":
            return self.procesar_sacar_ficha_juego(jugador, mensaje)
        
        elif tipo == "GET_FICHAS":
            return self.procesar_get_fichas(jugador)
        
        elif tipo == "GET_STATE":
            return {"tipo": "UPDATE", "estado": self.partida.obtener_estado()}
        
        elif tipo == "EMOJI_REACTION":
            return self.procesar_emoji(mensaje)
        
        else:
            return {"error": "Tipo de mensaje desconocido"}
    
    def procesar_join(self, cliente: socket.socket, mensaje: dict) -> dict:
        """Procesa solicitud de unirse a la partida."""
        nombre = mensaje.get("nombre", "Anónimo")
        
        jugador = self.partida.agregar_jugador(nombre, cliente)
        
        if jugador:
            with self.lock:
                self.clientes[cliente] = nombre
            
            print(f"✅ {nombre} se unió como {jugador.color}")
            return {
                "tipo": "ASSIGN_COLOR",
                "exito": True,
                "color": jugador.color,
                "nombre": nombre,
                "jugador_obj": jugador,
                "mensaje": f"Bienvenido {nombre}, eres {jugador.color}"
            }
        else:
            return {
                "tipo": "ASSIGN_COLOR",
                "exito": False,
                "error": "Partida llena o ya iniciada"
            }
    
    def procesar_start(self) -> dict:
        """Inicia la partida si hay suficientes jugadores."""
        if self.partida.iniciar_partida():
            print(f"🎮 Partida iniciada! Todos los jugadores deben lanzar el dado para determinar quién comienza")
            
            # Enviar mensaje de inicio de selección con dados
            self.broadcast_mensaje({
                "tipo": "SELECCION_TURNO",
                "mensaje": "Todos los jugadores deben lanzar el dado. El mayor número comienza.",
                "esperando_dados": True
            })
            
            return {
                "tipo": "GAME_START",
                "exito": True,
                "esperando_dados": True,
                "mensaje": "Partida iniciada. Todos deben lanzar el dado para determinar el orden"
            }
        else:
            return {
                "tipo": "GAME_START",
                "exito": False,
                "error": "Se necesitan al menos 2 jugadores"
            }
    
    def procesar_roll_inicio(self, jugador) -> dict:
        """Procesa lanzamiento de dado para determinar el primer turno."""
        if not jugador:
            return {"error": "No estás registrado"}
        
        if not self.partida.esperando_dados_inicio:
            return {"error": "No estás en fase de selección de turno"}
        
        valor = self.partida.lanzar_dado_inicio(jugador)
        
        if valor is None:
            return {"error": "Ya lanzaste el dado o no es válido"}
        
        print(f"🎲 {jugador.nombre} sacó {valor} para el orden inicial")
        
        # Broadcast del resultado a todos
        self.broadcast_mensaje({
            "tipo": "DADO_INICIO",
            "jugador": jugador.nombre,
            "color": jugador.color,
            "valor": valor
        })
        
        # Verificar si todos lanzaron
        if self.partida.todos_lanzaron_inicio():
            # Obtener el jugador actual (ya determinado)
            jugador_actual = self.partida.obtener_jugador_actual()
            dados_inicio = self.partida.obtener_dados_inicio()
            
            # Crear lista de resultados para mostrar
            resultados = []
            for j in self.partida.jugadores:
                resultados.append({
                    "nombre": j.nombre,
                    "color": j.color,
                    "valor": dados_inicio.get(j.id, 0)
                })
            
            print(f"🏆 {jugador_actual.nombre} comienza la partida!")
            
            # Broadcast del ganador y inicio de juego
            self.broadcast_mensaje({
                "tipo": "TURNO_DETERMINADO",
                "jugador_inicial": jugador_actual.nombre,
                "color_inicial": jugador_actual.color,
                "resultados": resultados,
                "mensaje": f"¡{jugador_actual.nombre} tiene el mayor número y comienza!"
            })
            
            # Enviar estado actualizado
            self.broadcast_estado()
        
        return {
            "tipo": "DADO_INICIO_RESULT",
            "valor": valor,
            "mensaje": f"Sacaste {valor}. Esperando a los demás jugadores..."
        }
    
    def procesar_roll(self, jugador) -> dict:
        """Procesa lanzamiento de dados."""
        if not jugador:
            return {"error": "No estás registrado"}
        
        if self.partida.esperando_dados_inicio:
            return {"error": "Primero deben lanzar el dado para determinar el orden inicial"}
        
        if not jugador.es_su_turno:
            return {"error": "No es tu turno"}
        
        # Verificar si puede lanzar
        if not jugador.puede_lanzar():
            return {"error": "Ya lanzaste los dados. Debes mover primero o esperar a sacar par."}
        
        dados = self.partida.lanzar_dados()
        print(f"🎲 {jugador.nombre} lanzó {dados}")
        
        # Verificar si todas las fichas están en cárcel
        todas_en_carcel = all(f.esta_en_carcel() for f in jugador.fichas)
        es_par = dados[0] == dados[1]
        
        # TODAS EN CÁRCEL: Procesar SIEMPRE para manejar intentos correctamente
        if todas_en_carcel:
            # NO marcar lanzamiento aquí, procesar_turno maneja el flujo de cárcel
            # Procesar el turno para que se actualice el contador de intentos
            resultado = self.partida.procesar_turno(jugador, dados, None)
            resultado["tipo"] = "DICE_RESULT"
            
            if resultado.get('cambio_turno'):
                print(f"⏭️  {jugador.nombre} perdió el turno (intentos agotados)")
                self.broadcast_estado()
            
            return resultado
        
        # Para casos normales (no todas en cárcel), marcar lanzamiento
        jugador.marcar_lanzamiento()
        
        # Verificar si puede sacar de cárcel con par
        puede_sacar = es_par and jugador.tiene_fichas_en_carcel()
        
        # Verificar si tiene movimientos válidos
        info_movimientos = self.partida.tiene_movimientos_validos(jugador, dados)
        
        # Si NO tiene movimientos válidos, saltar turno automáticamente
        if not info_movimientos["tiene_movimientos"]:
            print(f"⏭️  {jugador.nombre} no tiene movimientos válidos - Saltando turno")
            print(f"   Razón: {info_movimientos.get('razon', 'Sin movimientos posibles')}")
            
            # Si no es par, cambiar turno
            if not es_par:
                self.partida._cambiar_turno()
                self.broadcast_estado()
                
                return {
                    "tipo": "DICE_RESULT",
                    "dados": dados,
                    "suma": dados[0] + dados[1],
                    "es_par": es_par,
                    "sin_movimientos": True,
                    "cambio_turno": True,
                    "mensaje": f"Sin movimientos válidos. {info_movimientos.get('razon', '')} - Turno saltado"
                }
            else:
                # Con par puede lanzar de nuevo
                jugador.permitir_lanzar_de_nuevo()
                return {
                    "tipo": "DICE_RESULT",
                    "dados": dados,
                    "suma": dados[0] + dados[1],
                    "es_par": es_par,
                    "sin_movimientos": True,
                    "cambio_turno": False,
                    "mensaje": f"Sin movimientos válidos pero sacaste par. Lanza de nuevo"
                }
        
        return {
            "tipo": "DICE_RESULT",
            "dados": dados,
            "suma": dados[0] + dados[1],
            "es_par": es_par,
            "puede_sacar_carcel": puede_sacar,
            "todas_en_carcel": todas_en_carcel,
            "puede_dividir_dados": info_movimientos["puede_dividir"],
            "opciones_division": info_movimientos.get("opciones_division", []),
            "fichas_movibles": info_movimientos["fichas_movibles"],
            "mensaje": "Saca una ficha con 'mover N'" if puede_sacar else ("Puedes dividir los dados entre diferentes fichas" if info_movimientos["puede_dividir"] else "Mueve una ficha con 'mover N'")
        }
    
    def procesar_get_fichas(self, jugador) -> dict:
        """Retorna información detallada de las fichas del jugador."""
        if not jugador:
            return {"error": "No estás registrado"}
        
        fichas_info = self.partida.obtener_fichas_disponibles(jugador)
        
        return {
            "tipo": "FICHAS_INFO",
            "fichas": fichas_info
        }
    
    def procesar_move_dividido(self, jugador, mensaje: dict) -> dict:
        """Procesa movimiento con dados divididos."""
        if not jugador:
            return {"error": "No estás registrado"}
        
        dados = tuple(mensaje.get("dados", []))
        movimientos = mensaje.get("movimientos", [])
        
        if not dados:
            return {"error": "Debes lanzar los dados primero"}
        
        if not movimientos:
            return {"error": "Debes especificar los movimientos"}
        
        resultado = self.partida.procesar_turno_dividido(jugador, dados, movimientos)
        
        if "error" not in resultado:
            print(f"🚶 {jugador.nombre} hizo {len(movimientos)} movimiento(s)")
            # Log de capturas si hay
            total_capturas = sum(m.get("capturadas", 0) for m in resultado.get("movimientos_realizados", []))
            if total_capturas > 0:
                print(f"   💥 {jugador.nombre} capturó {total_capturas} ficha(s)")
        
        resultado["tipo"] = "MOVE_RESULT"
        return resultado
    
    def procesar_move(self, jugador, mensaje: dict) -> dict:
        """Procesa movimiento de ficha (modo clásico)."""
        if not jugador:
            return {"error": "No estás registrado"}
        
        id_ficha = mensaje.get("id_ficha")
        dados = tuple(mensaje.get("dados", []))
        
        if not dados:
            return {"error": "Debes lanzar los dados primero"}
        
        resultado = self.partida.procesar_turno(jugador, dados, id_ficha)
        
        if "error" not in resultado:
            accion = resultado.get('accion')
            if accion == "primer_turno_sin_par":
                print(f"🎲 {jugador.nombre} - Primer turno: sin par ({resultado.get('intentos_restantes')} intentos restantes)")
            elif accion == "primer_turno_agotado":
                print(f"⏭️  {jugador.nombre} - Primer turno agotado sin sacar par")
            elif accion == "tres_pares_sacar_ficha":
                print(f"🎯 {jugador.nombre} - ¡3 PARES! Puede sacar una ficha del juego")
            else:
                print(f"🚶 {jugador.nombre} movió ficha {id_ficha}: {accion}")
        
        resultado["tipo"] = "MOVE_RESULT"
        return resultado
    
    def procesar_sacar_ficha_juego(self, jugador, mensaje: dict) -> dict:
        """Procesa sacar una ficha del juego (por 3 pares consecutivos)."""
        if not jugador:
            return {"error": "No estás registrado"}
        
        id_ficha = mensaje.get("id_ficha")
        
        if id_ficha is None:
            return {"error": "Debes especificar la ficha a sacar"}
        
        resultado = self.partida.sacar_ficha_del_juego(jugador, id_ficha)
        
        if "error" not in resultado:
            print(f"🎯 {jugador.nombre} sacó la ficha {id_ficha} del juego (3 pares)")
        
        resultado["tipo"] = "MOVE_RESULT"
        return resultado
    
    def procesar_emoji(self, mensaje: dict) -> dict:
        """Procesa y envía emoji a todos los jugadores."""
        playerColor = mensaje.get("playerColor")
        emoji = mensaje.get("emoji")
        
        if not playerColor or not emoji:
            return {"error": "Faltan datos de emoji"}
        
        # Preparar mensaje de emoji para broadcast
        emoji_message = {
            "tipo": "EMOJI_REACTION",
            "playerColor": playerColor,
            "emoji": emoji
        }
        
        print(f"😊 Emoji recibido: {emoji} del jugador {playerColor}")
        
        # Enviar a todos los clientes
        self.broadcast_mensaje(emoji_message)
        
        return {"tipo": "EMOJI_REACTION", "exito": True}
    
    def broadcast_estado(self):
        """Envía el estado actual a todos los clientes."""
        estado = self.partida.obtener_estado()
        mensaje = {"tipo": "UPDATE", "estado": estado}
        
        with self.lock:
            for cliente in list(self.clientes.keys()):
                try:
                    self.enviar(cliente, mensaje)
                except:
                    pass
    
    def broadcast_mensaje(self, mensaje: dict):
        """Envía un mensaje a todos los clientes."""
        with self.lock:
            for cliente in list(self.clientes.keys()):
                try:
                    self.enviar(cliente, mensaje)
                except:
                    pass
    
    def enviar(self, cliente: socket.socket, mensaje: dict):
        """Envía un mensaje JSON al cliente."""
        try:
            # Remover objetos no serializables
            if "jugador_obj" in mensaje:
                del mensaje["jugador_obj"]
            
            data = json.dumps(mensaje) + "\n"
            cliente.sendall(data.encode('utf-8'))
        except Exception as e:
            print(f"❌ Error al enviar mensaje: {e}")
    
    def desconectar_cliente(self, cliente: socket.socket, jugador):
        """Limpia recursos al desconectar un cliente."""
        with self.lock:
            nombre = self.clientes.pop(cliente, "Desconocido")
        
        print(f"❌ {nombre} se desconectó")
        cliente.close()

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 5555
    
    servidor = ServidorParques(host, puerto)
    servidor.iniciar()

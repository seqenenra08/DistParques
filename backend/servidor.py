"""
Servidor TCP para el juego de Parqués
Maneja múltiples clientes usando threading
"""

import socket
import threading
import json
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime

from models import Partida, Jugador, EstadoPartida


# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ClienteHandler:
    """Maneja la comunicación con un cliente individual."""
    
    def __init__(self, socket_cliente: socket.socket, direccion: tuple, servidor):
        self.socket = socket_cliente
        self.direccion = direccion
        self.servidor = servidor
        self.id_jugador = None
        self.nombre_jugador = None
        self.id_partida = None
        self.activo = True
        self.lock = threading.Lock()
    
    def enviar_mensaje(self, tipo: str, datos: dict):
        """
        Envía un mensaje JSON al cliente.
        
        Args:
            tipo (str): Tipo de mensaje
            datos (dict): Datos del mensaje
        """
        try:
            mensaje = {
                "type": tipo,
                "data": datos,
                "timestamp": datetime.now().isoformat()
            }
            mensaje_json = json.dumps(mensaje) + "\n"
            
            with self.lock:
                self.socket.sendall(mensaje_json.encode('utf-8'))
            
            logger.info(f"Enviado a {self.direccion}: {tipo}")
        except Exception as e:
            logger.error(f"Error enviando mensaje a {self.direccion}: {e}")
            self.desconectar()
    
    def recibir_mensaje(self) -> Optional[dict]:
        """
        Recibe un mensaje JSON del cliente.
        
        Returns:
            Optional[dict]: Mensaje recibido o None si hay error
        """
        try:
            buffer = ""
            while "\n" not in buffer:
                chunk = self.socket.recv(1024).decode('utf-8')
                if not chunk:
                    return None
                buffer += chunk
            
            mensaje_json = buffer.split("\n")[0]
            mensaje = json.loads(mensaje_json)
            
            logger.info(f"Recibido de {self.direccion}: {mensaje.get('type', 'UNKNOWN')}")
            return mensaje
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando JSON de {self.direccion}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error recibiendo mensaje de {self.direccion}: {e}")
            return None
    
    def procesar_mensaje(self, mensaje: dict):
        """
        Procesa un mensaje recibido del cliente.
        
        Args:
            mensaje (dict): Mensaje a procesar
        """
        tipo = mensaje.get("type")
        datos = mensaje.get("data", {})
        
        if tipo == "JOIN":
            self.manejar_join(datos)
        elif tipo == "START":
            self.manejar_start(datos)
        elif tipo == "ROLL":
            self.manejar_roll(datos)
        elif tipo == "MOVE":
            self.manejar_move(datos)
        elif tipo == "DISCONNECT":
            self.desconectar()
        else:
            self.enviar_mensaje("ERROR", {
                "codigo_error": "TIPO_INVALIDO",
                "mensaje": f"Tipo de mensaje desconocido: {tipo}"
            })
    
    def manejar_join(self, datos: dict):
        """Maneja la solicitud de unirse a una partida."""
        nombre = datos.get("nombre")
        id_partida = datos.get("id_partida", "default")
        
        if not nombre:
            self.enviar_mensaje("JOIN_ERROR", {
                "mensaje": "Nombre de jugador requerido",
                "codigo_error": "NOMBRE_REQUERIDO"
            })
            return
        
        resultado = self.servidor.agregar_jugador_a_partida(
            self, nombre, id_partida
        )
        
        if resultado["exito"]:
            self.id_jugador = resultado["id_jugador"]
            self.nombre_jugador = nombre
            self.id_partida = id_partida
            
            self.enviar_mensaje("JOIN_SUCCESS", {
                "id_jugador": self.id_jugador,
                "id_partida": id_partida,
                "mensaje": "Te has unido a la partida",
                "es_anfitrion": resultado.get("es_anfitrion", False)
            })
            
            # Enviar color asignado
            self.enviar_mensaje("ASSIGN_COLOR", resultado["datos_jugador"])
            
            # Notificar a otros jugadores
            self.servidor.broadcast_a_partida(
                id_partida,
                "PLAYER_JOINED",
                {
                    "id_jugador": self.id_jugador,
                    "nombre": nombre,
                    "color": resultado["datos_jugador"]["color"],
                    "jugadores_en_partida": resultado["jugadores_en_partida"]
                },
                excluir=self.id_jugador
            )
        else:
            self.enviar_mensaje("JOIN_ERROR", {
                "mensaje": resultado["mensaje"],
                "codigo_error": resultado["codigo_error"]
            })
    
    def manejar_start(self, datos: dict):
        """Maneja la solicitud de iniciar la partida (solo anfitrión)."""
        resultado = self.servidor.iniciar_partida_manual(
            self.id_partida,
            self.id_jugador
        )
        
        if not resultado["exito"]:
            self.enviar_mensaje("START_ERROR", {
                "mensaje": resultado["mensaje"],
                "codigo_error": resultado["codigo_error"]
            })
    
    def manejar_roll(self, datos: dict):
        """Maneja la solicitud de lanzar dados."""
        resultado = self.servidor.lanzar_dados(
            self.id_partida,
            self.id_jugador
        )
        
        if resultado["exito"]:
            self.enviar_mensaje("ROLL_RESULT", resultado["datos"])
            
            # Broadcast a otros jugadores
            self.servidor.broadcast_a_partida(
                self.id_partida,
                "PLAYER_ROLLED",
                {
                    "id_jugador": self.id_jugador,
                    "nombre": self.nombre_jugador,
                    "resultado_dados": resultado["datos"]["resultado_dados"],
                    "total": resultado["datos"]["total"],
                    "turno_perdido": resultado["datos"].get("turno_perdido", False)
                },
                excluir=self.id_jugador
            )
            
            # Si no hay fichas movibles, cambiar turno automáticamente
            if resultado.get("cambiar_turno", False):
                # Limpiar el lanzamiento ya que no se usará (dentro de lock)
                with self.servidor.lock_partidas:
                    if self.id_partida in self.servidor.partidas:
                        partida = self.servidor.partidas[self.id_partida]
                        if hasattr(partida, 'ultimo_lanzamiento') and self.id_jugador in partida.ultimo_lanzamiento:
                            del partida.ultimo_lanzamiento[self.id_jugador]
                
                # Cambiar turno (maneja su propio lock)
                self.servidor.cambiar_turno(self.id_partida)
        else:
            self.enviar_mensaje("ROLL_ERROR", {
                "mensaje": resultado["mensaje"],
                "codigo_error": resultado["codigo_error"]
            })
    
    def manejar_move(self, datos: dict):
        """Maneja la solicitud de mover una ficha."""
        id_ficha = datos.get("id_ficha")
        
        resultado = self.servidor.mover_ficha(
            self.id_partida,
            self.id_jugador,
            id_ficha
        )
        
        if resultado["exito"]:
            self.enviar_mensaje("MOVE_SUCCESS", resultado["datos"])
            
            # Broadcast del estado actualizado a todos
            self.servidor.broadcast_estado_partida(self.id_partida)
            
            # Si hubo ficha comida, notificar
            if resultado["datos"].get("ficha_comida"):
                self.servidor.broadcast_a_partida(
                    self.id_partida,
                    "EATEN",
                    resultado["datos"]["ficha_comida"]
                )
            
            # Si no hay turno extra, cambiar turno
            if not resultado["datos"].get("turno_extra"):
                self.servidor.cambiar_turno(self.id_partida)
        else:
            self.enviar_mensaje("MOVE_ERROR", {
                "mensaje": resultado["mensaje"],
                "codigo_error": resultado["codigo_error"]
            })
    
    def desconectar(self):
        """Desconecta al cliente."""
        if not self.activo:
            return
        
        self.activo = False
        
        try:
            self.socket.close()
        except:
            pass
        
        if self.id_jugador and self.id_partida:
            self.servidor.remover_jugador(self.id_partida, self.id_jugador)
            
            # Notificar a otros jugadores
            self.servidor.broadcast_a_partida(
                self.id_partida,
                "PLAYER_DISCONNECT",
                {
                    "id_jugador": self.id_jugador,
                    "nombre": self.nombre_jugador,
                    "mensaje": f"{self.nombre_jugador} se ha desconectado"
                }
            )
        
        logger.info(f"Cliente desconectado: {self.direccion}")
    
    def run(self):
        """Loop principal del handler del cliente."""
        try:
            while self.activo:
                mensaje = self.recibir_mensaje()
                
                if mensaje is None:
                    break
                
                self.procesar_mensaje(mensaje)
        except Exception as e:
            logger.error(f"Error en cliente {self.direccion}: {e}")
        finally:
            self.desconectar()


class ServidorParques:
    """Servidor principal del juego de Parqués."""
    
    def __init__(self, host: str = "localhost", puerto: int = 5555):
        self.host = host
        self.puerto = puerto
        self.socket_servidor = None
        self.activo = False
        
        # Diccionario de partidas: {id_partida: Partida}
        self.partidas: Dict[str, Partida] = {}
        
        # Diccionario de clientes: {id_jugador: ClienteHandler}
        self.clientes: Dict[str, ClienteHandler] = {}
        
        # Diccionario de anfitriones: {id_partida: id_jugador_anfitrion}
        self.anfitriones: Dict[str, str] = {}
        
        # Locks para sincronización
        self.lock_partidas = threading.Lock()
        self.lock_clientes = threading.Lock()
        
        # Contador para IDs únicos
        self.contador_jugadores = 0
        self.lock_contador = threading.Lock()
        
        logger.info(f"Servidor inicializado en {host}:{puerto}")
    
    def generar_id_jugador(self) -> str:
        """Genera un ID único para un jugador."""
        with self.lock_contador:
            self.contador_jugadores += 1
            return f"player_{self.contador_jugadores}"
    
    def obtener_o_crear_partida(self, id_partida: str) -> Partida:
        """
        Obtiene una partida existente o crea una nueva.
        
        Args:
            id_partida (str): ID de la partida
            
        Returns:
            Partida: La partida solicitada
        """
        with self.lock_partidas:
            if id_partida not in self.partidas:
                self.partidas[id_partida] = Partida(id_partida, max_jugadores=4)
                logger.info(f"Nueva partida creada: {id_partida}")
            
            return self.partidas[id_partida]
    
    def agregar_jugador_a_partida(self, cliente: ClienteHandler, 
                                   nombre: str, id_partida: str) -> dict:
        """
        Agrega un jugador a una partida.
        
        Args:
            cliente (ClienteHandler): Handler del cliente
            nombre (str): Nombre del jugador
            id_partida (str): ID de la partida
            
        Returns:
            dict: Resultado de la operación
        """
        partida = self.obtener_o_crear_partida(id_partida)
        
        # Verificar si la partida ya inició
        if partida.estado == EstadoPartida.EN_CURSO:
            return {
                "exito": False,
                "mensaje": "La partida ya ha comenzado",
                "codigo_error": "PARTIDA_YA_INICIADA"
            }
        
        # Verificar si puede unirse
        if not partida.puede_unirse():
            return {
                "exito": False,
                "mensaje": "La partida está llena",
                "codigo_error": "PARTIDA_LLENA"
            }
        
        # Generar ID y agregar jugador
        id_jugador = self.generar_id_jugador()
        jugador = partida.agregar_jugador(nombre, id_jugador)
        
        if jugador:
            with self.lock_clientes:
                self.clientes[id_jugador] = cliente
            
            # Marcar como anfitrión si es el primero
            es_anfitrion = False
            if len(partida.jugadores) == 1:
                self.anfitriones[id_partida] = id_jugador
                es_anfitrion = True
                logger.info(f"Jugador {nombre} ({id_jugador}) es el anfitrión de {id_partida}")
            
            return {
                "exito": True,
                "id_jugador": id_jugador,
                "es_anfitrion": es_anfitrion,
                "datos_jugador": {
                    "id": id_jugador,
                    "nombre": nombre,
                    "color": jugador.color.value,
                    "posicion_orden": jugador.posicion_orden,
                    "jugadores_en_partida": len(partida.jugadores),
                    "max_jugadores": partida.max_jugadores
                },
                "jugadores_en_partida": len(partida.jugadores)
            }
        
        return {
            "exito": False,
            "mensaje": "Error al agregar jugador",
            "codigo_error": "ERROR_INTERNO"
        }
    
    def iniciar_partida_manual(self, id_partida: str, id_jugador: str) -> dict:
        """
        Inicia una partida manualmente (solo el anfitrión puede hacerlo).
        
        Args:
            id_partida (str): ID de la partida
            id_jugador (str): ID del jugador que intenta iniciar
            
        Returns:
            dict: Resultado de la operación
        """
        # Realizar validaciones dentro del lock
        with self.lock_partidas:
            if id_partida not in self.partidas:
                return {
                    "exito": False,
                    "mensaje": "Partida no encontrada",
                    "codigo_error": "PARTIDA_NO_ENCONTRADA"
                }
            
            # Verificar que sea el anfitrión
            if id_partida not in self.anfitriones or self.anfitriones[id_partida] != id_jugador:
                return {
                    "exito": False,
                    "mensaje": "Solo el anfitrión puede iniciar la partida",
                    "codigo_error": "NO_ES_ANFITRION"
                }
            
            partida = self.partidas[id_partida]
            
            # Verificar estado
            if partida.estado != EstadoPartida.ESPERANDO:
                return {
                    "exito": False,
                    "mensaje": "La partida ya ha sido iniciada",
                    "codigo_error": "PARTIDA_YA_INICIADA"
                }
            
            # Verificar jugadores mínimos
            if len(partida.jugadores) < partida.MIN_JUGADORES:
                return {
                    "exito": False,
                    "mensaje": f"Se necesitan al menos {partida.MIN_JUGADORES} jugadores",
                    "codigo_error": "JUGADORES_INSUFICIENTES"
                }
            
            # Iniciar partida
            if not partida.iniciar_partida():
                return {
                    "exito": False,
                    "mensaje": "Error al iniciar la partida",
                    "codigo_error": "ERROR_INICIAR"
                }
            
            logger.info(f"Partida {id_partida} iniciada manualmente por {id_jugador} con {len(partida.jugadores)} jugadores")
            
            # Preparar datos para broadcast (dentro del lock)
            datos_broadcast = {
                "id_partida": id_partida,
                "jugadores": [j.to_dict() for j in partida.jugadores],
                "turno_actual": partida.turno_actual,
                "jugador_actual": partida.obtener_jugador_actual().to_dict(),
                "mensaje": "¡La partida ha comenzado!"
            }
        
        # Broadcast FUERA del lock para evitar deadlock
        self.broadcast_a_partida(id_partida, "START_GAME", datos_broadcast)
        
        return {
            "exito": True,
            "mensaje": "Partida iniciada correctamente"
        }
    
    def _intentar_iniciar_partida(self, id_partida: str):
        """
        [DESHABILITADO] Anteriormente iniciaba automáticamente.
        Ahora el anfitrión debe iniciar manualmente con el comando 'iniciar'.
        """
        pass
        # with self.lock_partidas:
        #     if id_partida in self.partidas:
        #         partida = self.partidas[id_partida]
        #         
        #         if partida.estado == EstadoPartida.ESPERANDO and \
        #            len(partida.jugadores) >= partida.MIN_JUGADORES:
        #             
        #             if partida.iniciar_partida():
        #                 logger.info(f"Partida {id_partida} iniciada con {len(partida.jugadores)} jugadores")
        #                 
        #                 # Broadcast de inicio de partida
        #                 self.broadcast_a_partida(
        #                     id_partida,
        #                     "START_GAME",
        #                     {
        #                         "id_partida": id_partida,
        #                         "jugadores": [j.to_dict() for j in partida.jugadores],
        #                         "turno_actual": partida.turno_actual,
        #                         "jugador_actual": partida.obtener_jugador_actual().to_dict(),
        #                         "mensaje": "¡La partida ha comenzado!"
        #                     }
        #                 )
    
    def lanzar_dados(self, id_partida: str, id_jugador: str) -> dict:
        """
        Maneja el lanzamiento de dados.
        
        Args:
            id_partida (str): ID de la partida
            id_jugador (str): ID del jugador
            
        Returns:
            dict: Resultado del lanzamiento
        """
        with self.lock_partidas:
            if id_partida not in self.partidas:
                return {
                    "exito": False,
                    "mensaje": "Partida no encontrada",
                    "codigo_error": "PARTIDA_NO_ENCONTRADA"
                }
            
            partida = self.partidas[id_partida]
            jugador_actual = partida.obtener_jugador_actual()
            
            if not jugador_actual or jugador_actual.id != id_jugador:
                return {
                    "exito": False,
                    "mensaje": "No es tu turno",
                    "codigo_error": "TURNO_INVALIDO"
                }
            
            # Lanzar 2 dados
            dado1 = partida.lanzar_dado()
            dado2 = partida.lanzar_dado()
            total = dado1 + dado2
            es_par = (dado1 == dado2)
            
            # Guardar resultados en la partida
            if not hasattr(partida, 'ultimo_lanzamiento'):
                partida.ultimo_lanzamiento = {}
            
            partida.ultimo_lanzamiento[id_jugador] = {
                "dados": [dado1, dado2],
                "total": total,
                "es_par": es_par
            }
            
            # Obtener fichas movibles
            fichas_movibles = jugador_actual.obtener_fichas_movibles(total, es_par)
            
            # Verificar si puede sacar de la cárcel
            puede_sacar = es_par and jugador_actual.tiene_fichas_en_carcel()
            
            # Si no hay fichas movibles, pasar turno automáticamente
            turno_perdido = len(fichas_movibles) == 0
            
            datos_respuesta = {
                "id_jugador": id_jugador,
                "resultado_dados": [dado1, dado2],
                "total": total,
                "es_par": es_par,
                "puede_sacar": puede_sacar,
                "fichas_movibles": [f.id for f in fichas_movibles],
                "turno_perdido": turno_perdido,
                "mensaje": f"Lanzaste {dado1} y {dado2} (Total: {total})" + 
                          (" - ¡PAR!" if es_par else "")
            }
            
            return {
                "exito": True,
                "datos": datos_respuesta,
                "cambiar_turno": turno_perdido  # Flag para indicar si hay que cambiar turno
            }
    
    def mover_ficha(self, id_partida: str, id_jugador: str, id_ficha: int) -> dict:
        """
        Maneja el movimiento de una ficha.
        
        Args:
            id_partida (str): ID de la partida
            id_jugador (str): ID del jugador
            id_ficha (int): ID de la ficha a mover
            
        Returns:
            dict: Resultado del movimiento
        """
        with self.lock_partidas:
            if id_partida not in self.partidas:
                return {
                    "exito": False,
                    "mensaje": "Partida no encontrada",
                    "codigo_error": "PARTIDA_NO_ENCONTRADA"
                }
            
            partida = self.partidas[id_partida]
            
            # Verificar que se hayan lanzado los dados
            if not hasattr(partida, 'ultimo_lanzamiento') or \
               id_jugador not in partida.ultimo_lanzamiento:
                return {
                    "exito": False,
                    "mensaje": "Debes lanzar los dados primero",
                    "codigo_error": "DADO_NO_LANZADO"
                }
            
            lanzamiento = partida.ultimo_lanzamiento[id_jugador]
            pasos = lanzamiento["total"]
            
            # Mover la ficha
            resultado = partida.mover_ficha(id_jugador, id_ficha, pasos)
            
            # Si el movimiento fue exitoso, limpiar el lanzamiento
            if resultado["exito"]:
                del partida.ultimo_lanzamiento[id_jugador]
                
                # Verificar si el jugador ganó
                jugador = next((j for j in partida.jugadores if j.id == id_jugador), None)
                if jugador and jugador.todas_fichas_en_meta():
                    # Broadcast de victoria
                    self.broadcast_a_partida(
                        id_partida,
                        "WIN",
                        {
                            "id_partida": id_partida,
                            "ganador": jugador.to_dict(),
                            "mensaje": f"¡{jugador.nombre} ha ganado la partida!"
                        }
                    )
            
            return {
                "exito": resultado["exito"],
                "mensaje": resultado["mensaje"],
                "datos": resultado,
                "codigo_error": "MOVIMIENTO_INVALIDO" if not resultado["exito"] else None
            }
    
    def cambiar_turno(self, id_partida: str):
        """Cambia el turno al siguiente jugador."""
        # Preparar datos dentro del lock
        with self.lock_partidas:
            if id_partida not in self.partidas:
                return
            
            partida = self.partidas[id_partida]
            siguiente = partida.pasar_turno()
            
            datos_broadcast = {
                "turno_actual": partida.turno_actual,
                "jugador_actual": siguiente.to_dict(),
                "mensaje": f"Es el turno de {siguiente.nombre}"
            }
        
        # Broadcast FUERA del lock
        self.broadcast_a_partida(id_partida, "TURN_CHANGE", datos_broadcast)
    
    def broadcast_estado_partida(self, id_partida: str):
        """Envía el estado completo de la partida a todos los jugadores."""
        # Preparar datos dentro del lock
        with self.lock_partidas:
            if id_partida not in self.partidas:
                return
            
            partida = self.partidas[id_partida]
            estado = partida.to_dict()
        
        # Broadcast FUERA del lock
        self.broadcast_a_partida(id_partida, "UPDATE", estado)
    
    def broadcast_a_partida(self, id_partida: str, tipo: str, datos: dict, excluir: str = None):
        """
        Envía un mensaje a todos los jugadores de una partida.
        
        Args:
            id_partida (str): ID de la partida
            tipo (str): Tipo de mensaje
            datos (dict): Datos del mensaje
            excluir (str): ID de jugador a excluir (opcional)
        """
        with self.lock_partidas:
            if id_partida in self.partidas:
                partida = self.partidas[id_partida]
                
                for jugador in partida.jugadores:
                    if jugador.id != excluir and jugador.id in self.clientes:
                        cliente = self.clientes[jugador.id]
                        cliente.enviar_mensaje(tipo, datos)
    
    def remover_jugador(self, id_partida: str, id_jugador: str):
        """Remueve un jugador de una partida."""
        with self.lock_partidas:
            if id_partida in self.partidas:
                partida = self.partidas[id_partida]
                partida.remover_jugador(id_jugador)
                
                # Si no quedan jugadores, eliminar partida
                if len(partida.jugadores) == 0:
                    del self.partidas[id_partida]
                    logger.info(f"Partida {id_partida} eliminada (sin jugadores)")
        
        with self.lock_clientes:
            if id_jugador in self.clientes:
                del self.clientes[id_jugador]
    
    def aceptar_clientes(self):
        """Loop para aceptar nuevas conexiones de clientes."""
        logger.info(f"Esperando conexiones en {self.host}:{self.puerto}...")
        
        while self.activo:
            try:
                socket_cliente, direccion = self.socket_servidor.accept()
                logger.info(f"Nueva conexión desde {direccion}")
                
                # Crear handler para el cliente
                handler = ClienteHandler(socket_cliente, direccion, self)
                
                # Iniciar thread para manejar el cliente
                thread_cliente = threading.Thread(target=handler.run)
                thread_cliente.daemon = True
                thread_cliente.start()
                
            except Exception as e:
                if self.activo:
                    logger.error(f"Error aceptando cliente: {e}")
    
    def iniciar(self):
        """Inicia el servidor."""
        try:
            self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_servidor.bind((self.host, self.puerto))
            self.socket_servidor.listen(5)
            
            self.activo = True
            logger.info(f"Servidor iniciado en {self.host}:{self.puerto}")
            
            # Iniciar thread para aceptar clientes
            thread_aceptar = threading.Thread(target=self.aceptar_clientes)
            thread_aceptar.daemon = True
            thread_aceptar.start()
            
            # Mantener el servidor activo
            try:
                while self.activo:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Interrupción de teclado recibida")
                self.detener()
        
        except Exception as e:
            logger.error(f"Error iniciando servidor: {e}")
            self.detener()
    
    def detener(self):
        """Detiene el servidor."""
        logger.info("Deteniendo servidor...")
        self.activo = False
        
        # Cerrar todos los clientes
        with self.lock_clientes:
            for cliente in self.clientes.values():
                cliente.desconectar()
        
        # Cerrar socket del servidor
        if self.socket_servidor:
            try:
                self.socket_servidor.close()
            except:
                pass
        
        logger.info("Servidor detenido")


if __name__ == "__main__":
    # Crear e iniciar servidor
    servidor = ServidorParques(host="0.0.0.0", puerto=5555)
    servidor.iniciar()

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
                    if mensaje.get("tipo") in ["ROLL", "MOVE", "START", "MOVE_DIVIDIDO"]:
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
        
        elif tipo == "ROLL":
            return self.procesar_roll(jugador)
        
        elif tipo == "MOVE":
            return self.procesar_move(jugador, mensaje)
        
        elif tipo == "MOVE_DIVIDIDO":
            return self.procesar_move_dividido(jugador, mensaje)
        
        elif tipo == "GET_FICHAS":
            return self.procesar_get_fichas(jugador)
        
        elif tipo == "GET_STATE":
            return {"tipo": "UPDATE", "estado": self.partida.obtener_estado()}
        
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
            jugador_actual = self.partida.obtener_jugador_actual()
            print(f"🎮 Partida iniciada! Turno de {jugador_actual.nombre}")
            
            return {
                "tipo": "GAME_START",
                "exito": True,
                "jugador_actual": jugador_actual.nombre,
                "mensaje": f"Partida iniciada. Turno de {jugador_actual.nombre}"
            }
        else:
            return {
                "tipo": "GAME_START",
                "exito": False,
                "error": "Se necesitan al menos 2 jugadores"
            }
    
    def procesar_roll(self, jugador) -> dict:
        """Procesa lanzamiento de dados."""
        if not jugador:
            return {"error": "No estás registrado"}
        
        if not jugador.es_su_turno:
            return {"error": "No es tu turno"}
        
        dados = self.partida.lanzar_dados()
        print(f"🎲 {jugador.nombre} lanzó {dados}")
        
        # Verificar si todas las fichas están en cárcel
        todas_en_carcel = all(f.esta_en_carcel() for f in jugador.fichas)
        es_par = dados[0] == dados[1]
        
        # Si todas están en cárcel y no es par, cambiar turno automáticamente
        if todas_en_carcel and not es_par:
            resultado = self.partida.procesar_turno(jugador, dados, None)
            resultado["tipo"] = "DICE_RESULT"
            print(f"⏭️  {jugador.nombre} pierde turno (todas en cárcel, sin par)")
            # Broadcast para actualizar turnos
            self.broadcast_estado()
            return resultado
        
        # Verificar si puede sacar de cárcel con par
        puede_sacar = es_par and jugador.tiene_fichas_en_carcel()
        
        return {
            "tipo": "DICE_RESULT",
            "dados": dados,
            "suma": dados[0] + dados[1],
            "es_par": es_par,
            "puede_sacar_carcel": puede_sacar,
            "todas_en_carcel": todas_en_carcel,
            "mensaje": "Saca una ficha con 'mover N'" if puede_sacar else "Mueve una ficha con 'mover N'"
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
            print(f"🚶 {jugador.nombre} movió ficha {id_ficha}: {resultado['accion']}")
        
        resultado["tipo"] = "MOVE_RESULT"
        return resultado
    
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

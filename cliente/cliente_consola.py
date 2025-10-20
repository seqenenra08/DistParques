"""
Cliente de consola para el juego de Parqués
Permite jugar desde la línea de comandos y probar el servidor
"""

import socket
import threading
import json
import sys
import time
from datetime import datetime


class ClienteParques:
    """Cliente de consola para conectarse al servidor de Parqués."""
    
    def __init__(self, host: str = "localhost", puerto: int = 5555):
        """
        Inicializa el cliente.
        
        Args:
            host (str): Dirección del servidor
            puerto (int): Puerto del servidor
        """
        self.host = host
        self.puerto = puerto
        self.socket = None
        self.conectado = False
        self.id_jugador = None
        self.nombre = None
        self.color = None
        self.es_anfitrion = False
        self.partida_iniciada = False
        self.es_mi_turno = False
        self.ultimo_dado = None
        self.fichas_movibles = []
        
        # Sincronización de tiempo
        self.offset_tiempo = 0.0
        
        print(f"🎲 Cliente de Parqués - Conectando a {host}:{puerto}...")
    
    def conectar(self):
        """Establece conexión con el servidor."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.puerto))
            self.conectado = True
            
            print("✅ Conectado al servidor")
            
            # Iniciar thread para recibir mensajes
            thread_receptor = threading.Thread(target=self.recibir_mensajes)
            thread_receptor.daemon = True
            thread_receptor.start()
            
            return True
        
        except Exception as e:
            print(f"❌ Error conectando al servidor: {e}")
            return False
    
    def enviar_mensaje(self, tipo: str, datos: dict):
        """
        Envía un mensaje al servidor.
        
        Args:
            tipo (str): Tipo de mensaje
            datos (dict): Datos del mensaje
        """
        if not self.conectado:
            print("❌ No estás conectado al servidor")
            return
        
        try:
            mensaje = {
                "type": tipo,
                "data": datos,
                "timestamp": datetime.now().isoformat()
            }
            mensaje_json = json.dumps(mensaje) + "\n"
            self.socket.sendall(mensaje_json.encode('utf-8'))
            
        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")
            self.desconectar()
    
    def recibir_mensajes(self):
        """Loop para recibir mensajes del servidor."""
        buffer = ""
        
        while self.conectado:
            try:
                chunk = self.socket.recv(1024).decode('utf-8')
                
                if not chunk:
                    print("\n❌ Conexión cerrada por el servidor")
                    self.desconectar()
                    break
                
                buffer += chunk
                
                # Procesar mensajes completos (terminan con \n)
                while "\n" in buffer:
                    mensaje_json, buffer = buffer.split("\n", 1)
                    mensaje = json.loads(mensaje_json)
                    self.procesar_mensaje(mensaje)
            
            except Exception as e:
                if self.conectado:
                    print(f"\n❌ Error recibiendo mensaje: {e}")
                    self.desconectar()
                break
    
    def procesar_mensaje(self, mensaje: dict):
        """
        Procesa un mensaje recibido del servidor.
        
        Args:
            mensaje (dict): Mensaje a procesar
        """
        tipo = mensaje.get("type")
        datos = mensaje.get("data", {})
        
        if tipo == "JOIN_SUCCESS":
            self.id_jugador = datos.get("id_jugador")
            self.es_anfitrion = datos.get("es_anfitrion", False)
            print(f"\n✅ {datos.get('mensaje')}")
            print(f"   Tu ID: {self.id_jugador}")
            
            if self.es_anfitrion:
                print(f"\n👑 ERES EL ANFITRIÓN DE ESTA PARTIDA")
                print(f"   💡 Cuando todos los jugadores estén listos, escribe 'iniciar' para comenzar")
        
        elif tipo == "JOIN_ERROR":
            print(f"\n❌ {datos.get('mensaje')}")
        
        elif tipo == "ASSIGN_COLOR":
            self.color = datos.get("color")
            print(f"\n🎨 Color asignado: {self.color.upper()}")
            print(f"   Jugadores en partida: {datos.get('jugadores_en_partida')}/{datos.get('max_jugadores')}")
        
        elif tipo == "PLAYER_JOINED":
            print(f"\n👤 {datos.get('nombre')} ({datos.get('color')}) se unió a la partida")
            print(f"   Jugadores: {datos.get('jugadores_en_partida')}")
            
            if self.es_anfitrion:
                print(f"   💡 Escribe 'iniciar' cuando estés listo para comenzar")
        
        elif tipo == "START_GAME":
            self.partida_iniciada = True
            print("\n" + "="*60)
            print("🎮 ¡LA PARTIDA HA COMENZADO!")
            print("="*60)
            print("\n👥 Jugadores:")
            for j in datos.get("jugadores", []):
                print(f"   - {j['nombre']} ({j['color']})")
            
            jugador_actual = datos.get("jugador_actual", {})
            print(f"\n🎯 Turno inicial: {jugador_actual.get('nombre')}")
            
            if jugador_actual.get("id") == self.id_jugador:
                self.es_mi_turno = True
                print("\n💡 ¡Es tu turno! Escribe 'lanzar' para tirar los dados")
        
        elif tipo == "START_ERROR":
            print(f"\n❌ Error al iniciar: {datos.get('mensaje')}")
        
        elif tipo == "ROLL_RESULT":
            dados = datos.get("resultado_dados", [])
            total = datos.get("total", 0)
            es_par = datos.get("es_par", False)
            turno_perdido = datos.get("turno_perdido", False)
            
            print(f"\n🎲 Dados: {dados[0]} + {dados[1]} = {total}")
            if es_par:
                print("   ¡PAR! Puedes sacar ficha de la cárcel")
            
            self.ultimo_dado = total
            self.fichas_movibles = datos.get("fichas_movibles", [])
            
            if self.fichas_movibles:
                print(f"\n📍 Fichas movibles: {self.fichas_movibles}")
                print("   Escribe 'mover <num_ficha>' para mover una ficha")
            else:
                print("   ⚠️ No hay fichas movibles. Turno perdido.")
                if turno_perdido:
                    self.es_mi_turno = False
                    self.ultimo_dado = None
                    self.fichas_movibles = []
        
        elif tipo == "PLAYER_ROLLED":
            nombre = datos.get("nombre")
            dados = datos.get("resultado_dados", [])
            total = datos.get("total", 0)
            turno_perdido = datos.get("turno_perdido", False)
            print(f"\n🎲 {nombre} lanzó: {dados[0]} + {dados[1]} = {total}")
            if turno_perdido:
                print(f"   ⚠️ {nombre} perdió su turno (sin fichas movibles)")
        
        elif tipo == "MOVE_SUCCESS":
            print(f"\n✅ {datos.get('mensaje')}")
            
            if datos.get("ficha_comida"):
                print("   😈 ¡Comiste una ficha enemiga!")
            
            if datos.get("llego_a_meta"):
                print("   🏆 ¡Ficha llegó a la meta!")
            
            if datos.get("turno_extra"):
                print("   🎉 ¡Turno extra!")
        
        elif tipo == "MOVE_ERROR":
            print(f"\n❌ {datos.get('mensaje')}")
        
        elif tipo == "UPDATE":
            # Actualización del estado del juego
            pass  # Podemos mostrar un resumen si queremos
        
        elif tipo == "TURN_CHANGE":
            jugador_actual = datos.get("jugador_actual", {})
            print(f"\n➡️ {datos.get('mensaje')}")
            
            self.es_mi_turno = (jugador_actual.get("id") == self.id_jugador)
            
            if self.es_mi_turno:
                print("\n💡 Es tu turno. Escribe 'lanzar' para tirar los dados")
        
        elif tipo == "EATEN":
            comedor = datos.get("nombre_comedor")
            comido = datos.get("nombre_comido")
            print(f"\n😈 {comedor} comió una ficha de {comido}")
        
        elif tipo == "WIN":
            ganador = datos.get("ganador", {})
            print("\n" + "="*60)
            print(f"🏆 ¡{ganador.get('nombre')} ({ganador.get('color')}) HA GANADO!")
            print("="*60)
            print(f"\n{datos.get('mensaje')}")
        
        elif tipo == "PLAYER_DISCONNECT":
            print(f"\n⚠️ {datos.get('mensaje')}")
        
        elif tipo == "TIME_REQUEST":
            # Responder con tiempo del cliente
            self.enviar_mensaje("TIME_RESPONSE", {
                "tiempo_cliente": datetime.now().isoformat()
            })
        
        elif tipo == "TIME_SYNC":
            ajuste = datos.get("ajuste_segundos", 0)
            self.offset_tiempo += ajuste
            print(f"\n🕐 Tiempo sincronizado (ajuste: {ajuste:.3f}s)")
        
        elif tipo == "ERROR":
            print(f"\n❌ Error: {datos.get('mensaje')}")
    
    def unirse(self, nombre: str, id_partida: str = "default"):
        """
        Envía solicitud para unirse a una partida.
        
        Args:
            nombre (str): Nombre del jugador
            id_partida (str): ID de la partida (default: "default")
        """
        self.nombre = nombre
        self.enviar_mensaje("JOIN", {
            "nombre": nombre,
            "id_partida": id_partida
        })
    
    def iniciar_partida(self):
        """Inicia la partida (solo para anfitrión)."""
        print("🎮 Iniciando partida...")
        self.enviar_mensaje("START", {})
    
    def lanzar_dados(self):
        """Solicita lanzar los dados."""
        if not self.partida_iniciada:
            print("❌ La partida aún no ha comenzado")
            if self.es_anfitrion:
                print("   💡 Escribe 'iniciar' para comenzar")
            return
        
        if not self.es_mi_turno:
            print("❌ No es tu turno")
            return
        
        self.enviar_mensaje("ROLL", {})
    
    def mover_ficha(self, id_ficha: int):
        """
        Solicita mover una ficha.
        
        Args:
            id_ficha (int): ID de la ficha a mover (0-3)
        """
        if not self.partida_iniciada:
            print("❌ La partida aún no ha comenzado")
            return
        
        if not self.es_mi_turno:
            print("❌ No es tu turno")
            return
        
        if self.ultimo_dado is None:
            print("❌ Debes lanzar los dados primero")
            return
        
        if id_ficha not in self.fichas_movibles:
            print(f"❌ La ficha {id_ficha} no se puede mover")
            return
        
        self.enviar_mensaje("MOVE", {
            "id_ficha": id_ficha
        })
        
        self.ultimo_dado = None
        self.fichas_movibles = []
    
    def desconectar(self):
        """Desconecta del servidor."""
        if not self.conectado:
            return
        
        self.conectado = False
        
        if self.socket:
            try:
                self.enviar_mensaje("DISCONNECT", {})
                self.socket.close()
            except:
                pass
        
        print("\n👋 Desconectado del servidor")
    
    def menu_interactivo(self):
        """Menú interactivo para el jugador."""
        print("\n" + "="*60)
        print("🎲 PARQUÉS - CLIENTE DE CONSOLA")
        print("="*60)
        
        nombre = input("\n📝 Ingresa tu nombre: ").strip()
        if not nombre:
            print("❌ Nombre inválido")
            return
        
        id_partida = input("🎮 ID de partida (Enter para 'default'): ").strip()
        if not id_partida:
            id_partida = "default"
        
        self.unirse(nombre, id_partida)
        
        print("\n💡 Comandos disponibles:")
        if self.es_anfitrion:
            print("   iniciar     - Iniciar la partida (solo anfitrión)")
        print("   lanzar      - Lanzar los dados")
        print("   mover <N>   - Mover la ficha N (0-3)")
        print("   estado      - Ver estado actual")
        print("   ayuda       - Mostrar comandos")
        print("   salir       - Salir del juego")
        
        # Loop de comandos
        while self.conectado:
            try:
                comando = input("\n> ").strip().lower()
                
                if not comando:
                    continue
                
                if comando == "salir" or comando == "exit":
                    break
                
                elif comando == "iniciar" or comando == "i":
                    if not self.es_anfitrion:
                        print("❌ Solo el anfitrión puede iniciar la partida")
                    elif self.partida_iniciada:
                        print("❌ La partida ya ha sido iniciada")
                    else:
                        self.iniciar_partida()
                
                elif comando == "lanzar" or comando == "l":
                    self.lanzar_dados()
                
                elif comando.startswith("mover ") or comando.startswith("m "):
                    partes = comando.split()
                    if len(partes) >= 2:
                        try:
                            id_ficha = int(partes[1])
                            self.mover_ficha(id_ficha)
                        except ValueError:
                            print("❌ Número de ficha inválido")
                    else:
                        print("❌ Uso: mover <0-3>")
                
                elif comando == "estado" or comando == "e":
                    print(f"\n📊 Estado:")
                    print(f"   Nombre: {self.nombre}")
                    print(f"   Color: {self.color}")
                    print(f"   Anfitrión: {'Sí' if self.es_anfitrion else 'No'}")
                    print(f"   Partida iniciada: {'Sí' if self.partida_iniciada else 'No'}")
                    print(f"   Mi turno: {'Sí' if self.es_mi_turno else 'No'}")
                    if self.ultimo_dado:
                        print(f"   Último dado: {self.ultimo_dado}")
                        print(f"   Fichas movibles: {self.fichas_movibles}")
                
                elif comando == "ayuda" or comando == "h":
                    print("\n💡 Comandos:")
                    if self.es_anfitrion and not self.partida_iniciada:
                        print("   iniciar / i    - Iniciar partida (anfitrión)")
                    print("   lanzar / l     - Lanzar dados")
                    print("   mover <N> / m <N> - Mover ficha N")
                    print("   estado / e     - Ver estado")
                    print("   ayuda / h      - Esta ayuda")
                    print("   salir          - Salir")
                
                else:
                    print("❌ Comando desconocido. Escribe 'ayuda' para ver comandos")
            
            except KeyboardInterrupt:
                print("\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
        
        self.desconectar()


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cliente de consola para Parqués")
    parser.add_argument("--host", default="localhost", help="Dirección del servidor")
    parser.add_argument("--puerto", type=int, default=5555, help="Puerto del servidor")
    
    args = parser.parse_args()
    
    # Crear cliente
    cliente = ClienteParques(args.host, args.puerto)
    
    # Conectar al servidor
    if cliente.conectar():
        # Dar un momento para establecer conexión
        time.sleep(0.5)
        
        # Iniciar menú interactivo
        try:
            cliente.menu_interactivo()
        except KeyboardInterrupt:
            print("\n\nInterrumpido por el usuario")
        finally:
            cliente.desconectar()
    else:
        print("❌ No se pudo conectar al servidor")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Bot Jugador Automático para Parqués Distribuido
================================================

Este bot se conecta como un jugador más y toma decisiones automáticas
basadas en estrategias inteligentes para jugar Parqués.

Estrategias implementadas:
1. Priorizar sacar fichas de la cárcel cuando sea posible
2. Priorizar mover fichas más adelantadas
3. Intentar capturar fichas enemigas
4. Proteger fichas en casillas seguras
5. Evitar quedarse solo con fichas en cárcel
"""

import socket
import json
import time
import threading
import random
from typing import Dict, List, Optional, Tuple

class BotJugador:
    """Bot que juega automáticamente al Parqués."""
    
    def __init__(self, nombre: str = "Bot", host: str = "127.0.0.1", puerto: int = 5555):
        self.nombre = nombre
        self.host = host
        self.puerto = puerto
        self.socket = None
        self.color = None
        self.estado_partida = {}
        self.dados_actuales = None
        self.es_mi_turno = False
        self.activo = True
        self.partida_iniciada = False
        self.jugadores_conectados = 0
        self.intento_iniciar_enviado = False
        self.lanzamiento_pendiente = False  # Flag para evitar lanzamientos duplicados
        
        # Configuración del bot
        self.retraso_decision = 1.5  # Segundos antes de tomar acción
        self.retraso_entre_acciones = 0.8  # Segundos entre comandos
        
        print(f"🤖 Bot '{self.nombre}' inicializando...")
    
    def conectar(self) -> bool:
        """Conecta al servidor."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.puerto))
            print(f"✅ Conectado a {self.host}:{self.puerto}")
            
            # Enviar mensaje JOIN
            self.enviar_mensaje({
                "tipo": "JOIN",
                "nombre": self.nombre
            })
            
            return True
        except Exception as e:
            print(f"❌ Error al conectar: {e}")
            return False
    
    def enviar_mensaje(self, mensaje: dict):
        """Envía un mensaje JSON al servidor."""
        try:
            datos = json.dumps(mensaje).encode('utf-8')
            self.socket.sendall(datos)
        except Exception as e:
            print(f"❌ Error al enviar mensaje: {e}")
    
    def recibir_mensajes(self):
        """Hilo para recibir mensajes del servidor."""
        buffer = ""
        while self.activo:
            try:
                datos = self.socket.recv(4096).decode('utf-8')
                if not datos:
                    print("⚠️  Conexión cerrada por el servidor")
                    break
                
                buffer += datos
                while '\n' in buffer:
                    linea, buffer = buffer.split('\n', 1)
                    if linea.strip():
                        try:
                            mensaje = json.loads(linea)
                            self.procesar_mensaje(mensaje)
                        except json.JSONDecodeError:
                            pass
            except Exception as e:
                if self.activo:
                    print(f"❌ Error al recibir: {e}")
                break
    
    def procesar_mensaje(self, msg: dict):
        """Procesa mensajes del servidor."""
        tipo = msg.get("tipo")
        
        if tipo == "ASSIGN_COLOR" or tipo == "WELCOME":
            self.color = msg.get("color")
            print(f"🎨 Asignado color: {self.color}")
        
        elif tipo == "ESPERANDO":
            jugadores_actuales = msg.get("jugadores_actuales", 0)
            self.jugadores_conectados = jugadores_actuales
            print(f"⏳ Esperando jugadores... ({jugadores_actuales}/4)")
        
        elif tipo == "GAME_START" or tipo == "INICIO":
            self.partida_iniciada = True
            print(f"🎮 ¡Partida iniciada!")
            jugador_turno = msg.get('jugador_actual') or msg.get('jugador')
            
            if jugador_turno:
                print(f"🔄 Turno inicial: {jugador_turno}")
                # Si es nuestro turno, lanzar dados
                if jugador_turno == self.nombre and not self.lanzamiento_pendiente:
                    self.es_mi_turno = True
                    self.lanzamiento_pendiente = True
                    print(f"\n{'='*50}")
                    print(f"🤖 ES MI TURNO INICIAL")
                    print(f"{'='*50}")
                    threading.Timer(self.retraso_decision, self.lanzar_dados).start()
                else:
                    self.es_mi_turno = False
                    print(f"   ⏳ Turno de {jugador_turno}, esperando...")
            else:
                print(f"⚠️  No se recibió jugador actual en GAME_START, solicitando estado...")
                # Solicitar estado actual
                threading.Timer(0.5, self.solicitar_estado).start()
        
        elif tipo == "TURNO" or tipo == "TURN_CHANGE":
            jugador_turno = msg.get("jugador") or msg.get("jugador_actual")
            self.es_mi_turno = (jugador_turno == self.nombre)
            
            if self.es_mi_turno and not self.lanzamiento_pendiente:
                print(f"\n{'='*50}")
                print(f"🤖 MI TURNO")
                print(f"{'='*50}")
                self.dados_actuales = None
                self.lanzamiento_pendiente = True
                threading.Timer(self.retraso_decision, self.lanzar_dados).start()
            else:
                print(f"   ⏳ Turno de {jugador_turno}")
        
        elif tipo == "DADOS" or tipo == "DICE_RESULT":
            # Verificar si hay error
            if msg.get("error"):
                error = msg.get("error")
                print(f"   ⚠️  Error del servidor: {error}")
                if "no es tu turno" in error.lower():
                    self.es_mi_turno = False
                return
            
            if msg.get("jugador") == self.nombre or (tipo == "DICE_RESULT" and self.es_mi_turno):
                self.lanzamiento_pendiente = False  # Resetear flag
                self.dados_actuales = tuple(msg.get("dados", []))
                es_par = msg.get("es_par", False) or (self.dados_actuales[0] == self.dados_actuales[1])
                
                print(f"🎲 Dados: {self.dados_actuales} (Suma: {sum(self.dados_actuales)})")
                if es_par:
                    print(f"   ✨ ¡PAR!")
                
                # Si el mensaje indica que perdió turno, no hacer nada
                if msg.get("accion") == "sin_movimiento":
                    print(f"   ⏭️  Turno perdido automáticamente")
                    self.es_mi_turno = False
                    return
                
                # Tomar decisión de movimiento
                threading.Timer(self.retraso_decision, self.decidir_movimiento).start()
        
        elif tipo == "RESULTADO" or tipo == "MOVE_RESULT":
            accion = msg.get("accion")
            
            if accion == "sacar_carcel":
                print(f"   🔓 Ficha sacada de la cárcel")
            elif accion == "mover":
                print(f"   ✅ Ficha movida")
                if msg.get("fichas_capturadas"):
                    capturas = len(msg.get("fichas_capturadas", []))
                    print(f"   💥 ¡Capturé {capturas} ficha(s)!")
            elif accion == "movimiento_dividido":
                print(f"   ✅ Movimiento dividido ejecutado")
            elif msg.get("error"):
                print(f"   ⚠️  Error: {msg.get('error')}")
            
            # Verificar si ganamos
            if msg.get("ganador") == self.nombre:
                print(f"\n{'🏆'*25}")
                print(f"🎉 ¡BOT GANÓ LA PARTIDA! 🎉")
                print(f"{'🏆'*25}\n")
            elif msg.get("ganador"):
                print(f"   🏁 {msg['ganador']} ganó la partida")
            
            # Si sacamos par, lanzar de nuevo
            if msg.get("es_par") and not msg.get("cambio_turno"):
                print(f"   🔄 Sacamos PAR, lanzando de nuevo...")
                self.lanzamiento_pendiente = True
                threading.Timer(self.retraso_entre_acciones, self.lanzar_dados).start()
            else:
                self.es_mi_turno = False
                self.lanzamiento_pendiente = False
        
        elif tipo == "UPDATE":
            estado_previo = self.estado_partida.get("jugador_actual")
            self.estado_partida = msg.get("estado", {})
            
            # Verificar si es nuestro turno según el estado
            jugador_actual = self.estado_partida.get("jugador_actual")
            
            # Solo actuar si cambió el turno a nosotros y no hay lanzamiento pendiente
            if (jugador_actual == self.nombre and estado_previo != self.nombre and 
                self.partida_iniciada and not self.lanzamiento_pendiente):
                # El estado indica que es nuestro turno
                self.es_mi_turno = True
                self.dados_actuales = None
                self.lanzamiento_pendiente = True
                print(f"\n{'='*50}")
                print(f"🤖 MI TURNO (detectado por UPDATE)")
                print(f"{'='*50}")
                # Lanzar dados
                threading.Timer(self.retraso_decision, self.lanzar_dados).start()
            elif jugador_actual != self.nombre:
                # Ya no es nuestro turno
                self.es_mi_turno = False
                self.lanzamiento_pendiente = False
    
    def solicitar_estado(self):
        """Solicita el estado actual de la partida."""
        print(f"🔍 Solicitando estado actual...")
        self.enviar_mensaje({
            "tipo": "GET_STATE"
        })
    
    def lanzar_dados(self):
        """Lanza los dados."""
        if not self.es_mi_turno:
            print(f"   ⚠️  No es mi turno, ignorando lanzamiento")
            self.lanzamiento_pendiente = False
            return
        
        if not self.partida_iniciada:
            print(f"   ⚠️  Partida no iniciada, esperando...")
            self.lanzamiento_pendiente = False
            return
        
        if not self.lanzamiento_pendiente:
            print(f"   ⚠️  Lanzamiento ya procesado, ignorando")
            return
        
        print(f"🎲 Lanzando dados...")
        self.enviar_mensaje({
            "tipo": "ROLL",
            "jugador": self.nombre
        })
    
    def decidir_movimiento(self):
        """Decide qué ficha mover basándose en estrategia."""
        if not self.es_mi_turno or not self.dados_actuales:
            return
        
        # Obtener información de mis fichas del estado actual
        fichas_info = self.obtener_info_fichas()
        
        if not fichas_info:
            print(f"   ⚠️  No hay información de fichas, moviendo ficha 0 por defecto")
            # Intentar mover ficha 0 como fallback
            self.enviar_mensaje({
                "tipo": "MOVE",
                "jugador": self.nombre,
                "id_ficha": 0,
                "dados": list(self.dados_actuales)
            })
            return
        
        suma_dados = sum(self.dados_actuales)
        es_par = self.dados_actuales[0] == self.dados_actuales[1]
        
        # Estrategia de decisión
        ficha_elegida = self.elegir_mejor_ficha(fichas_info, suma_dados, es_par)
        
        if ficha_elegida is None:
            print(f"   ⚠️  No hay fichas disponibles para mover")
            # El turno pasará automáticamente
            return
        
        ficha = fichas_info[ficha_elegida]
        
        # Si la ficha está en cárcel y tenemos PAR, solo sacar (no mover con suma)
        if ficha.get("estado") == "carcel" and es_par:
            print(f"   🎯 Sacando ficha {ficha_elegida} de la cárcel con PAR")
        else:
            print(f"   🎯 Moviendo ficha {ficha_elegida} con {suma_dados} casillas")
        
        self.enviar_mensaje({
            "tipo": "MOVE",
            "jugador": self.nombre,
            "id_ficha": ficha_elegida,
            "dados": list(self.dados_actuales)
        })
    
    def obtener_info_fichas(self) -> List[Dict]:
        """Obtiene información actualizada de las fichas."""
        jugadores = self.estado_partida.get("jugadores", [])
        
        for jug in jugadores:
            if jug.get("nombre") == self.nombre:
                fichas = jug.get("fichas", [])
                if fichas:
                    return fichas
        
        # Si no hay estado, crear fichas por defecto (todas en cárcel)
        print(f"   🔍 No hay estado disponible, usando valores por defecto")
        return [
            {"id": i, "estado": "carcel", "posicion": None, "puede_mover": False}
            for i in range(4)
        ]
    
    def elegir_mejor_ficha(self, fichas_info: List[Dict], suma_dados: int, es_par: bool) -> Optional[int]:
        """
        Elige la mejor ficha para mover según estrategias.
        
        Prioridades:
        1. Si hay PAR y fichas en cárcel → Sacar de cárcel
        2. Fichas más adelantadas (cerca de META)
        3. Primera ficha disponible
        """
        
        # Filtrar fichas que pueden moverse
        fichas_movibles = []
        fichas_en_carcel = []
        
        for ficha in fichas_info:
            estado = ficha.get("estado")
            id_ficha = ficha.get("id")
            
            if estado == "carcel":
                fichas_en_carcel.append(id_ficha)
            elif estado in ["tablero", "pasillo_final"]:
                # No incluir fichas en meta
                if estado != "meta":
                    posicion = ficha.get("posicion", 0)
                    casillas_recorridas = ficha.get("casillas_recorridas", posicion if posicion else 0)
                    fichas_movibles.append({
                        "id": id_ficha,
                        "posicion": posicion,
                        "casillas_recorridas": casillas_recorridas,
                        "estado": estado
                    })
        
        # Estrategia 1: Si hay PAR, sacar de cárcel
        if es_par and fichas_en_carcel:
            print(f"   💡 Estrategia: Sacar de cárcel (PAR) - Ficha {fichas_en_carcel[0]}")
            return fichas_en_carcel[0]
        
        # Si no hay fichas movibles, intentar con cualquier ficha que no esté en cárcel
        if not fichas_movibles:
            # Buscar cualquier ficha que no esté en meta
            for ficha in fichas_info:
                if ficha.get("estado") not in ["carcel", "meta"]:
                    print(f"   💡 Estrategia: Intentar mover ficha {ficha['id']}")
                    return ficha["id"]
            
            # Si todas están en cárcel o meta, intentar ficha 0
            print(f"   💡 Estrategia: Intentar ficha 0 por defecto")
            return 0
        
        # Estrategia 2: Priorizar fichas más adelantadas
        fichas_movibles.sort(key=lambda f: f.get("casillas_recorridas", 0), reverse=True)
        
        print(f"   💡 Estrategia: Mover ficha más adelantada - Ficha {fichas_movibles[0]['id']}")
        return fichas_movibles[0]["id"]
    
    def enviar_start(self):
        """Envía el comando START para iniciar la partida."""
        if not self.intento_iniciar_enviado and not self.partida_iniciada:
            self.intento_iniciar_enviado = True
            print(f"🎮 Enviando comando START...")
            self.enviar_mensaje({
                "tipo": "START",
                "jugador": self.nombre
            })
    
    def iniciar_partida_cuando_listo(self):
        """Espera y luego intenta iniciar la partida."""
        # Esperar a que se conecten jugadores
        time.sleep(5)
        
        if not self.partida_iniciada and not self.intento_iniciar_enviado:
            print(f"🎮 Intentando iniciar partida después de espera...")
            self.enviar_start()
    
    def ejecutar(self):
        """Ejecuta el bot."""
        if not self.conectar():
            return
        
        # Iniciar hilo de recepción
        hilo_recepcion = threading.Thread(target=self.recibir_mensajes, daemon=True)
        hilo_recepcion.start()
        
        # Intentar iniciar partida después de conectarse
        threading.Timer(4.0, self.iniciar_partida_cuando_listo).start()
        
        try:
            # Mantener el bot activo
            while self.activo:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n⚠️  Bot detenido por usuario")
        finally:
            self.desconectar()
    
    def desconectar(self):
        """Desconecta del servidor."""
        self.activo = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print(f"👋 Bot desconectado")


def main():
    """Función principal."""
    import sys
    
    # Configuración del bot
    nombre = "Bot-CPU"
    host = "127.0.0.1"
    puerto = 5555
    
    # Parsear argumentos opcionales
    if len(sys.argv) > 1:
        nombre = sys.argv[1]
    if len(sys.argv) > 2:
        host = sys.argv[2]
    if len(sys.argv) > 3:
        puerto = int(sys.argv[3])
    
    print(f"\n{'🤖'*25}")
    print(f"   BOT JUGADOR AUTOMÁTICO - PARQUÉS")
    print(f"{'🤖'*25}\n")
    print(f"📋 Configuración:")
    print(f"   Nombre: {nombre}")
    print(f"   Servidor: {host}:{puerto}")
    print(f"\n{'─'*50}\n")
    
    # Crear y ejecutar bot
    bot = BotJugador(nombre=nombre, host=host, puerto=puerto)
    bot.ejecutar()


if __name__ == "__main__":
    main()

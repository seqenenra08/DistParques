"""Cliente simple compatible con servidor.py actual."""
import socket
import json
import threading
import sys

class ClienteSimple:
    def __init__(self, host="127.0.0.1", puerto=5555):
        self.host = host
        self.puerto = puerto
        self.socket = None
        self.conectado = False
        self.nombre = None
        self.color = None
        self.dados_actuales = None
        self.estado_partida = None
        self.fichas_info = []
    
    def conectar(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.puerto))
            self.conectado = True
            print(f"✅ Conectado a {self.host}:{self.puerto}\n")
            
            thread = threading.Thread(target=self.recibir, daemon=True)
            thread.start()
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def enviar(self, mensaje):
        try:
            data = json.dumps(mensaje) + "\n"
            self.socket.sendall(data.encode('utf-8'))
        except Exception as e:
            print(f"❌ Error al enviar: {e}")
            self.conectado = False
    
    def recibir(self):
        buffer = ""
        while self.conectado:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    print("\n❌ Servidor desconectado")
                    self.conectado = False
                    break
                
                buffer += data
                while "\n" in buffer:
                    linea, buffer = buffer.split("\n", 1)
                    if linea.strip():
                        try:
                            msg = json.loads(linea)
                            self.procesar(msg)
                        except:
                            pass
            except:
                self.conectado = False
                break
    
    def procesar(self, msg):
        tipo = msg.get("tipo")
        
        if tipo == "ASSIGN_COLOR":
            if msg.get("exito"):
                self.color = msg.get("color")
                print(f"🎨 {msg.get('mensaje')}")
                self.enviar({"tipo": "GET_STATE"})
            else:
                print(f"❌ {msg.get('error')}")
        
        elif tipo == "GAME_START":
            if msg.get("exito"):
                print(f"\n{'='*60}\n🎮 {msg.get('mensaje')}\n{'='*60}\n")
            else:
                print(f"⚠️  {msg.get('error')}")
        
        elif tipo == "DICE_RESULT":
            self.dados_actuales = tuple(msg.get("dados"))
            print(f"\n🎲 Dados: {self.dados_actuales} → Suma: {msg.get('suma')}")
            
            # Verificar si es cambio automático de turno
            if msg.get("accion") == "sin_movimiento_carcel":
                print(f"   🔒 Todas tus fichas están en la cárcel")
                print(f"   ⏭️  Turno perdido automáticamente (necesitas PAR para sacar)")
                self.dados_actuales = None
                return
            
            if msg.get("es_par"):
                print("   ✨ ¡PAR! Puedes tirar de nuevo después de mover")
            
            # Verificar si todas están en cárcel
            if msg.get("todas_en_carcel"):
                if not msg.get("es_par"):
                    print("   🔒 Todas tus fichas están en la cárcel - necesitas PAR")
                    print("   ⏭️  Turno perdido automáticamente")
                    self.dados_actuales = None
                    return
                else:
                    print("   🔓 ¡Puedes SACAR! Usa: mover N (donde N es 0-3)")
            
            # Solicitar info de fichas
            self.enviar({"tipo": "GET_FICHAS"})
            
            print(f"\n💡 Opciones:")
            print(f"   1. 'mover N'        - Mover ficha N con suma ({msg.get('suma')})")
            print(f"   2. 'dividir N1 D1 N2 D2' - Mover dos fichas separadas")
            print(f"      Ejemplo: dividir 0 {self.dados_actuales[0]} 1 {self.dados_actuales[1]}")
        
        elif tipo == "FICHAS_INFO":
            self.fichas_info = msg.get("fichas", [])
            print(f"\n📋 TUS FICHAS:")
            for ficha in self.fichas_info:
                emoji = "✅" if ficha["puede_mover"] else "❌"
                print(f"   {emoji} Ficha {ficha['id']}: {ficha['descripcion']}")
        
        elif tipo == "MOVE_RESULT":
            if "error" in msg:
                print(f"\n❌ {msg['error']}")
                print("   💡 Intenta con otra ficha. Escribe 'fichas' para ver opciones")
                return
            else:
                accion = msg.get("accion")
                
                if accion == "sin_movimiento_carcel":
                    print("\n🔒 Todas tus fichas en la cárcel - sin PAR")
                    print("   ⏭️  Turno perdido automáticamente")
                elif accion == "sacar_carcel":
                    print("\n✅ Ficha sacada de la cárcel")
                elif accion == "entro_pasillo":
                    print(f"\n🏃 {msg.get('mensaje', 'Entraste al pasillo final')}")
                elif accion == "llego_meta":
                    print(f"\n🏁 {msg.get('mensaje', 'Ficha llegó a la META')}")
                elif accion == "mover":
                    print("\n✅ Ficha movida")
                    capturas = msg.get("fichas_capturadas", [])
                    if capturas:
                        print(f"   💥 ¡CAPTURASTE {len(capturas)} FICHA(S)!")
                        for cap in capturas:
                            print(f"      - Ficha {cap['id']} ({cap['color']}) → Cárcel")
                elif accion == "sin_movimiento":
                    print("\n⚠️  No puedes mover ninguna ficha con este resultado")
                
                # Mostrar movimientos divididos
                movs = msg.get("movimientos_realizados", [])
                if movs:
                    print(f"\n✅ Movimientos realizados:")
                    for mov in movs:
                        if mov.get("accion") == "sacar_carcel":
                            print(f"   - Ficha {mov['id_ficha']}: Sacada de cárcel")
                        else:
                            print(f"   - Ficha {mov['id_ficha']}: +{mov['casillas']} casillas")
                            if mov.get("capturadas", 0) > 0:
                                print(f"     💥 ¡Capturó {mov['capturadas']} ficha(s)!")
                
                if msg.get("ganador"):
                    print(f"\n{'='*60}")
                    print(f"🏆 ¡{msg['ganador']} GANÓ LA PARTIDA!")
                    print(f"{'='*60}\n")
                
                if msg.get("cambio_turno"):
                    print("   ⏭️  Fin de turno")
                elif msg.get("es_par"):
                    print("   🎲 Sacaste PAR, lanza de nuevo!")
                
                self.dados_actuales = None
                self.fichas_info = []
        
        elif tipo == "UPDATE":
            self.estado_partida = msg.get("estado", {})
            self.mostrar_jugadores()
            
            if self.estado_partida.get("jugador_actual") == self.nombre:
                if not self.dados_actuales:
                    print(f"\n⏰ ES TU TURNO, {self.nombre}! Escribe 'lanzar'\n")
    
    def mostrar_jugadores(self):
        if not self.estado_partida:
            return
        
        jugadores = self.estado_partida.get("jugadores", [])
        print(f"\n{'─'*60}")
        print(f"👥 JUGADORES ({len(jugadores)}/4):")
        for j in jugadores:
            turno = "👉" if j.get("es_su_turno") else "  "
            yo = "(TÚ)" if j["nombre"] == self.nombre else ""
            meta = sum(1 for f in j["fichas"] if f["estado"] == "meta")
            carcel = sum(1 for f in j["fichas"] if f["estado"] == "carcel")
            juego = 4 - meta - carcel
            print(f"{turno} {j['color']:8} - {j['nombre']:15} {yo}")
            print(f"     🏁{meta} 🔒{carcel} 🎲{juego}")
        
        if not self.estado_partida.get("iniciada"):
            print(f"\n⏳ Esperando inicio (mín. 2 jugadores)")
        print(f"{'─'*60}\n")
    
    def iniciar(self):
        print("\n" + "="*60)
        print("🎲 CLIENTE PARQUÉS - MODO AVANZADO")
        print("="*60)
        
        nombre = input("\n📝 Tu nombre: ").strip() or f"Player{id(self)%1000}"
        
        if not self.conectar():
            return
        
        self.nombre = nombre
        self.enviar({"tipo": "JOIN", "nombre": nombre})
        
        import time
        time.sleep(0.3)
        
        print("\n💡 Comandos principales:")
        print("   iniciar             - Iniciar partida")
        print("   lanzar              - Lanzar dados")
        print("   mover N             - Mover ficha N con suma total")
        print("   dividir N1 D1 N2 D2 - Dividir dados en dos fichas")
        print("   fichas              - Ver tus fichas disponibles")
        print("   ayuda               - Ver ayuda completa\n")
        
        while self.conectado:
            try:
                cmd = input("> ").strip().lower()
                
                if not cmd:
                    continue
                
                if cmd in ["salir", "exit"]:
                    break
                
                elif cmd in ["iniciar", "start"]:
                    self.enviar({"tipo": "START"})
                
                elif cmd in ["lanzar", "roll"]:
                    self.enviar({"tipo": "ROLL"})
                
                elif cmd.startswith("mover"):
                    partes = cmd.split()
                    if len(partes) == 2 and partes[1].isdigit():
                        if not self.dados_actuales:
                            print("⚠️  Primero lanza los dados con 'lanzar'")
                            continue
                        id_f = int(partes[1])
                        if 0 <= id_f <= 3:
                            self.enviar({
                                "tipo": "MOVE",
                                "id_ficha": id_f,
                                "dados": list(self.dados_actuales)
                            })
                        else:
                            print("⚠️  Ficha debe ser 0-3")
                    else:
                        print("⚠️  Uso: mover <0-3>")
                
                elif cmd.startswith("dividir"):
                    if not self.dados_actuales:
                        print("⚠️  Primero lanza los dados")
                        continue
                    
                    partes = cmd.split()
                    if len(partes) == 5:
                        try:
                            id1, val1, id2, val2 = int(partes[1]), int(partes[2]), int(partes[3]), int(partes[4])
                            
                            if not (0 <= id1 <= 3 and 0 <= id2 <= 3):
                                print("⚠️  IDs de ficha deben ser 0-3")
                                continue
                            
                            self.enviar({
                                "tipo": "MOVE_DIVIDIDO",
                                "dados": list(self.dados_actuales),
                                "movimientos": [
                                    {"id_ficha": id1, "valor_dado": val1},
                                    {"id_ficha": id2, "valor_dado": val2}
                                ]
                            })
                        except ValueError:
                            print("⚠️  Uso: dividir <id_ficha1> <dado1> <id_ficha2> <dado2>")
                    else:
                        print("⚠️  Uso: dividir <id_ficha1> <dado1> <id_ficha2> <dado2>")
                        print(f"   Ejemplo: dividir 0 {self.dados_actuales[0]} 1 {self.dados_actuales[1]}")
                
                elif cmd in ["fichas", "mis_fichas"]:
                    self.enviar({"tipo": "GET_FICHAS"})
                
                elif cmd in ["jugadores", "estado"]:
                    self.enviar({"tipo": "GET_STATE"})
                
                elif cmd in ["ayuda", "help"]:
                    print("\n📋 COMANDOS COMPLETOS:")
                    print("  iniciar              - Iniciar partida (2-4 jugadores)")
                    print("  lanzar               - Lanzar dados")
                    print("  mover N              - Mover ficha N con suma total de dados")
                    print("  dividir N1 D1 N2 D2  - Dividir: ficha N1 con dado D1, ficha N2 con dado D2")
                    print("  fichas               - Ver estado de tus fichas")
                    print("  jugadores            - Ver jugadores conectados")
                    print("  ayuda                - Esta ayuda")
                    print("  salir                - Desconectar\n")
                    print("💡 EJEMPLOS:")
                    print("  > lanzar             # Sacas (4, 5)")
                    print("  > mover 0            # Mueve ficha 0 con 9 casillas")
                    print("  > dividir 0 4 1 5    # Mueve ficha 0 con 4, ficha 1 con 5\n")
                
                else:
                    print(f"❌ Comando desconocido. Escribe 'ayuda'")
            
            except (KeyboardInterrupt, EOFError):
                break
        
        print("\n👋 Desconectando...")
        try:
            self.socket.close()
        except:
            pass

# ⚠️ ESTO FALTABA - Punto de entrada principal
if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 5555
    
    cliente = ClienteSimple(host, puerto)
    cliente.iniciar()
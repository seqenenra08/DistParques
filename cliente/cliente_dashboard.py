#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tablero visual de Parqués para terminal usando curses.
Cliente con interfaz gráfica de tarjetas para el juego distribuido.

Ejecuta: python3 cliente_dashboard.py [host] [puerto]
"""

import socket
import json
import threading
import sys
import curses
import time

CARD_W = 32
CARD_H = 11
PADDING_X = 2
PADDING_Y = 1

def clamp(x, a, b):
    return max(a, min(b, x))

class ClienteDashboard:
    """Cliente con interfaz visual curses."""
    
    def __init__(self, stdscr, host="127.0.0.1", puerto=5555):
        self.stdscr = stdscr
        self.host = host
        self.puerto = puerto
        self.socket = None
        self.conectado = False
        self.nombre = None
        self.color = None
        self.estado_partida = None
        self.dados_actuales = None
        self.fichas_info = []
        self.mensaje = ""
        self.last_msg_time = 0
        self.msg_timeout = 5
        self.input_mode = False
        self.input_buffer = ""
        self.command_history = []
        self.selected_player = 0
        
        # Colores
        self.init_colors()
    
    def init_colors(self):
        """Inicializa pares de colores para curses."""
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            # Pares: 1=Amarillo, 2=Azul, 3=Rojo, 4=Verde, 5=Destacado, 6=Error
            curses.init_pair(1, curses.COLOR_YELLOW, -1)
            curses.init_pair(2, curses.COLOR_BLUE, -1)
            curses.init_pair(3, curses.COLOR_RED, -1)
            curses.init_pair(4, curses.COLOR_GREEN, -1)
            curses.init_pair(5, curses.COLOR_CYAN, -1)
            curses.init_pair(6, curses.COLOR_MAGENTA, -1)
    
    def get_color_pair(self, color_name):
        """Retorna el par de colores según el nombre del jugador."""
        color_map = {
            "AMARILLO": 1,
            "AZUL": 2,
            "ROJO": 3,
            "VERDE": 4
        }
        return curses.color_pair(color_map.get(color_name, 0))
    
    def set_message(self, text, timeout=5):
        """Establece mensaje temporal."""
        self.mensaje = text
        self.last_msg_time = time.time()
        self.msg_timeout = timeout
    
    def conectar(self):
        """Conecta al servidor."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.puerto))
            self.conectado = True
            
            # Hilo para recibir mensajes
            thread = threading.Thread(target=self.recibir, daemon=True)
            thread.start()
            return True
        except Exception as e:
            self.set_message(f"❌ Error al conectar: {e}", 10)
            return False
    
    def enviar(self, mensaje):
        """Envía mensaje JSON al servidor."""
        if not self.conectado:
            return
        try:
            data = json.dumps(mensaje) + "\n"
            self.socket.sendall(data.encode('utf-8'))
        except Exception as e:
            self.set_message(f"❌ Error al enviar: {e}")
            self.conectado = False
    
    def recibir(self):
        """Recibe mensajes del servidor."""
        buffer = ""
        while self.conectado:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    self.set_message("❌ Servidor desconectado", 10)
                    self.conectado = False
                    break
                
                buffer += data
                while "\n" in buffer:
                    linea, buffer = buffer.split("\n", 1)
                    if linea.strip():
                        try:
                            msg = json.loads(linea)
                            self.procesar(msg)
                        except json.JSONDecodeError:
                            pass
            except Exception as e:
                if self.conectado:
                    self.set_message(f"❌ Error: {e}")
                self.conectado = False
                break
    
    def procesar(self, msg):
        """Procesa mensajes del servidor."""
        tipo = msg.get("tipo")
        
        if tipo == "ASSIGN_COLOR":
            if msg.get("exito"):
                self.color = msg.get("color")
                self.set_message(f"🎨 {msg.get('mensaje')}")
                self.enviar({"tipo": "GET_STATE"})
            else:
                self.set_message(f"❌ {msg.get('error')}")
        
        elif tipo == "GAME_START":
            if msg.get("exito"):
                self.set_message(f"🎮 {msg.get('mensaje')}")
            else:
                self.set_message(f"⚠️  {msg.get('error')}")
        
        elif tipo == "DICE_RESULT":
            self.dados_actuales = tuple(msg.get("dados"))
            dados_str = f"🎲 Dados: {self.dados_actuales[0]} + {self.dados_actuales[1]} = {msg.get('suma')}"
            if msg.get("es_par"):
                dados_str += " ✨ ¡PAR!"
            self.set_message(dados_str, 8)
            self.enviar({"tipo": "GET_FICHAS"})
        
        elif tipo == "FICHAS_INFO":
            self.fichas_info = msg.get("fichas", [])
        
        elif tipo == "MOVE_RESULT":
            if "error" in msg:
                self.set_message(f"❌ {msg['error']}", 6)
            else:
                movs = msg.get("movimientos_realizados", [])
                if movs:
                    capturas_totales = sum(m.get("capturadas", 0) for m in movs)
                    msg_text = f"✅ {len(movs)} movimiento(s)"
                    if capturas_totales > 0:
                        msg_text += f" | 💥 {capturas_totales} captura(s)"
                    self.set_message(msg_text, 5)
                else:
                    accion = msg.get("accion")
                    if accion == "sacar_carcel":
                        self.set_message("✅ Ficha sacada de cárcel", 5)
                    elif accion == "mover":
                        caps = len(msg.get("fichas_capturadas", []))
                        msg_text = "✅ Ficha movida"
                        if caps > 0:
                            msg_text += f" | 💥 {caps} captura(s)"
                        self.set_message(msg_text, 5)
                
                if msg.get("ganador"):
                    self.set_message(f"🏆 ¡{msg['ganador']} GANÓ!", 20)
                
                self.dados_actuales = None
                self.fichas_info = []
        
        elif tipo == "UPDATE":
            self.estado_partida = msg.get("estado", {})
    
    def draw(self):
        """Dibuja la interfaz completa."""
        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()
        
        # Título
        title = f"🎲 PARQUÉS DASHBOARD — {self.nombre or 'Conectando...'} ({self.color or '?'}) — q:Salir"
        try:
            self.stdscr.addstr(0, 0, title[:w-1], curses.A_REVERSE | curses.A_BOLD)
        except curses.error:
            pass
        
        # Información de partida
        if self.estado_partida:
            info_y = 1
            iniciada = self.estado_partida.get("iniciada", False)
            jugador_actual = self.estado_partida.get("jugador_actual", "?")
            
            estado_str = "🎮 EN JUEGO" if iniciada else "⏳ ESPERANDO"
            turno_str = f"| Turno: {jugador_actual}"
            
            try:
                self.stdscr.addstr(info_y, 2, estado_str, curses.color_pair(4) if iniciada else curses.color_pair(1))
                if iniciada:
                    self.stdscr.addstr(info_y, 2 + len(estado_str) + 1, turno_str)
                
                # Info de dados actuales
                if self.dados_actuales and jugador_actual == self.nombre:
                    dados_str = f"| 🎲 {self.dados_actuales[0]} + {self.dados_actuales[1]}"
                    self.stdscr.addstr(info_y, w - len(dados_str) - 2, dados_str, curses.color_pair(5))
            except curses.error:
                pass
            
            # Dibujar tarjetas de jugadores
            self.draw_player_cards(h, w)
        else:
            try:
                self.stdscr.addstr(3, 2, "Conectando al servidor...", curses.A_DIM)
            except curses.error:
                pass
        
        # Línea de comando
        cmd_y = h - 4
        try:
            self.stdscr.addstr(cmd_y, 0, "─" * (w-1))
            
            if self.input_mode:
                prompt = "Comando> "
                self.stdscr.addstr(cmd_y + 1, 0, prompt + self.input_buffer[:w-len(prompt)-2])
                curses.curs_set(1)
            else:
                hint = "Presiona ENTER para comandos | ↑↓←→: Navegar | h: Ayuda"
                self.stdscr.addstr(cmd_y + 1, 0, hint[:w-1], curses.A_DIM)
                curses.curs_set(0)
        except curses.error:
            pass
        
        # Mensajes
        try:
            if self.mensaje and time.time() - self.last_msg_time < self.msg_timeout:
                self.stdscr.addstr(h-2, 0, f"💬 {self.mensaje}"[:w-1], curses.A_BOLD)
            else:
                self.mensaje = ""
        except curses.error:
            pass
        
        # Ayuda rápida
        try:
            ayuda = "i:Iniciar | l:Lanzar | m:Mover | f:Fichas | d:Dividir | s:Estado"
            self.stdscr.addstr(h-1, 0, ayuda[:w-1], curses.A_DIM)
        except curses.error:
            pass
        
        self.stdscr.refresh()
    
    def draw_player_cards(self, screen_h, screen_w):
        """Dibuja tarjetas de jugadores en grid."""
        if not self.estado_partida:
            return
        
        jugadores = self.estado_partida.get("jugadores", [])
        if not jugadores:
            return
        
        # Calcular grid
        usable_h = screen_h - 8
        usable_w = screen_w - 4
        cols = max(1, usable_w // (CARD_W + PADDING_X))
        
        for idx, jugador in enumerate(jugadores):
            r = idx // cols
            c = idx % cols
            x = 2 + c * (CARD_W + PADDING_X)
            y = 3 + r * (CARD_H + PADDING_Y)
            
            if y + CARD_H > screen_h - 8:
                break
            
            is_selected = (idx == self.selected_player)
            is_mi_turno = jugador.get("es_su_turno", False)
            is_yo = (jugador["nombre"] == self.nombre)
            
            self.draw_player_card(y, x, jugador, is_selected, is_mi_turno, is_yo, screen_w)
    
    def draw_player_card(self, y, x, jugador, is_selected, is_mi_turno, is_yo, screen_w):
        """Dibuja una tarjeta de jugador."""
        color_pair = self.get_color_pair(jugador["color"])
        
        # Borde
        border_attr = curses.A_BOLD if is_selected else curses.A_NORMAL
        if is_mi_turno:
            border_attr |= curses.A_REVERSE
        
        try:
            # Línea superior e inferior
            for i in range(CARD_W):
                if x + i < screen_w:
                    self.stdscr.addch(y, x+i, ord('═'), border_attr | color_pair)
                    self.stdscr.addch(y+CARD_H-1, x+i, ord('═'), border_attr | color_pair)
            
            # Líneas laterales
            for j in range(1, CARD_H-1):
                if y + j < curses.LINES:
                    self.stdscr.addch(y+j, x, ord('║'), border_attr | color_pair)
                    if x+CARD_W-1 < screen_w:
                        self.stdscr.addch(y+j, x+CARD_W-1, ord('║'), border_attr | color_pair)
            
            # Esquinas
            self.stdscr.addch(y, x, ord('╔'), border_attr | color_pair)
            self.stdscr.addch(y, x+CARD_W-1, ord('╗'), border_attr | color_pair)
            self.stdscr.addch(y+CARD_H-1, x, ord('╚'), border_attr | color_pair)
            self.stdscr.addch(y+CARD_H-1, x+CARD_W-1, ord('╝'), border_attr | color_pair)
            
            # Nombre y color
            nombre = jugador["nombre"][:CARD_W-6]
            turno_mark = "👉 " if is_mi_turno else "   "
            yo_mark = " (TÚ)" if is_yo else ""
            header = f"{turno_mark}{nombre}{yo_mark}"
            self.stdscr.addstr(y+1, x+2, header[:CARD_W-4], curses.A_BOLD | color_pair)
            
            color_emoji = {
                "AMARILLO": "🟨",
                "AZUL": "🟦",
                "ROJO": "🟥",
                "VERDE": "🟩"
            }
            color_str = f"{color_emoji.get(jugador['color'], '⬜')} {jugador['color']}"
            self.stdscr.addstr(y+2, x+2, color_str[:CARD_W-4], color_pair)
            
            # Estado de fichas
            fichas = jugador.get("fichas", [])
            meta = sum(1 for f in fichas if f["estado"] == "meta")
            carcel = sum(1 for f in fichas if f["estado"] == "carcel")
            juego = 4 - meta - carcel
            
            self.stdscr.addstr(y+4, x+2, f"🏁 En meta:    {meta}/4"[:CARD_W-4])
            self.stdscr.addstr(y+5, x+2, f"🎲 En juego:   {juego}"[:CARD_W-4])
            self.stdscr.addstr(y+6, x+2, f"🔒 En cárcel:  {carcel}"[:CARD_W-4])
            
            # Barra de progreso
            progreso = int((meta / 4) * 100)
            bar_w = CARD_W - 6
            filled = int(bar_w * progreso / 100)
            bar = "█" * filled + "░" * (bar_w - filled)
            self.stdscr.addstr(y+8, x+2, f"[{bar}]"[:CARD_W-4], color_pair)
            self.stdscr.addstr(y+9, x+2, f"{progreso}% completado"[:CARD_W-4], curses.A_DIM)
            
        except curses.error:
            pass
    
    def process_command(self, cmd):
        """Procesa un comando ingresado."""
        cmd = cmd.strip().lower()
        
        if not cmd:
            return
        
        self.command_history.append(cmd)
        
        if cmd in ["salir", "exit", "quit", "q"]:
            self.conectado = False
            return
        
        elif cmd in ["iniciar", "start", "i"]:
            self.enviar({"tipo": "START"})
        
        elif cmd in ["lanzar", "roll", "l", "r"]:
            self.enviar({"tipo": "ROLL"})
        
        elif cmd.startswith("mover") or cmd.startswith("m "):
            partes = cmd.split()
            if len(partes) >= 2 and partes[-1].isdigit():
                if not self.dados_actuales:
                    self.set_message("⚠️  Primero lanza los dados (l)")
                    return
                id_f = int(partes[-1])
                if 0 <= id_f <= 3:
                    self.enviar({
                        "tipo": "MOVE",
                        "id_ficha": id_f,
                        "dados": list(self.dados_actuales)
                    })
                else:
                    self.set_message("⚠️  Ficha debe ser 0-3")
            else:
                self.set_message("⚠️  Uso: mover <0-3> o m <0-3>")
        
        elif cmd.startswith("dividir") or cmd.startswith("d "):
            if not self.dados_actuales:
                self.set_message("⚠️  Primero lanza los dados (l)")
                return
            
            partes = cmd.split()
            if len(partes) == 5:
                try:
                    id1, val1, id2, val2 = int(partes[1]), int(partes[2]), int(partes[3]), int(partes[4])
                    
                    if not (0 <= id1 <= 3 and 0 <= id2 <= 3):
                        self.set_message("⚠️  IDs deben ser 0-3")
                        return
                    
                    self.enviar({
                        "tipo": "MOVE_DIVIDIDO",
                        "dados": list(self.dados_actuales),
                        "movimientos": [
                            {"id_ficha": id1, "valor_dado": val1},
                            {"id_ficha": id2, "valor_dado": val2}
                        ]
                    })
                except ValueError:
                    self.set_message("⚠️  Uso: dividir <id1> <dado1> <id2> <dado2>")
            else:
                if self.dados_actuales:
                    self.set_message(f"Ej: dividir 0 {self.dados_actuales[0]} 1 {self.dados_actuales[1]}")
                else:
                    self.set_message("⚠️  Uso: dividir <id1> <dado1> <id2> <dado2>")
        
        elif cmd in ["fichas", "mis_fichas", "f"]:
            self.enviar({"tipo": "GET_FICHAS"})
            self.show_fichas_detail()
        
        elif cmd in ["jugadores", "estado", "s"]:
            self.enviar({"tipo": "GET_STATE"})
            self.set_message("📊 Estado actualizado")
        
        elif cmd in ["ayuda", "help", "h", "?"]:
            self.show_help()
        
        else:
            self.set_message(f"❌ Comando desconocido: '{cmd}'. Usa 'h' para ayuda")
    
    def show_fichas_detail(self):
        """Muestra detalles de fichas en mensaje."""
        if not self.fichas_info:
            time.sleep(0.2)  # Esperar respuesta
        
        if self.fichas_info:
            info = " | ".join([f"F{f['id']}: {f['estado']}" for f in self.fichas_info[:4]])
            self.set_message(f"📋 {info}", 8)
    
    def show_help(self):
        """Muestra ayuda en mensaje."""
        help_text = "Comandos: i(niciar) l(anzar) m(over) <N> d(ividir) f(ichas) s(estado) q(salir)"
        self.set_message(help_text, 10)
    
    def run(self):
        """Loop principal del dashboard."""
        curses.curs_set(0)
        self.stdscr.nodelay(True)
        self.stdscr.timeout(100)
        
        # Solicitar nombre
        curses.echo()
        curses.curs_set(1)
        h, w = self.stdscr.getmaxyx()
        
        self.stdscr.addstr(h//2, 2, "📝 Tu nombre: ")
        self.stdscr.refresh()
        nombre_input = self.stdscr.getstr(h//2, 16, 30).decode("utf-8").strip()
        
        curses.noecho()
        curses.curs_set(0)
        
        if not nombre_input:
            nombre_input = f"Player{id(self)%1000}"
        
        self.nombre = nombre_input
        
        # Conectar
        if not self.conectar():
            self.set_message("❌ No se pudo conectar. Presiona cualquier tecla...", 30)
            self.draw()
            self.stdscr.getch()
            return
        
        # Unirse
        self.enviar({"tipo": "JOIN", "nombre": self.nombre})
        time.sleep(0.3)
        
        # Loop principal
        last_update = time.time()
        
        while self.conectado:
            # Redibujar periódicamente
            if time.time() - last_update > 0.1:
                self.draw()
                last_update = time.time()
            
            # Leer teclas
            try:
                ch = self.stdscr.getch()
            except:
                ch = -1
            
            if ch == -1:
                continue
            
            # Modo input
            if self.input_mode:
                if ch == ord('\n'):  # Enter
                    self.input_mode = False
                    self.process_command(self.input_buffer)
                    self.input_buffer = ""
                elif ch in (curses.KEY_BACKSPACE, 127, 8):
                    self.input_buffer = self.input_buffer[:-1]
                elif ch == 27:  # ESC
                    self.input_mode = False
                    self.input_buffer = ""
                elif 32 <= ch <= 126:  # Caracteres imprimibles
                    self.input_buffer += chr(ch)
            else:
                # Modo navegación
                if ch in (ord('q'), ord('Q')):
                    break
                
                elif ch == ord('\n'):  # Enter para modo comando
                    self.input_mode = True
                    self.input_buffer = ""
                
                # Atajos rápidos
                elif ch in (ord('i'), ord('I')):
                    self.process_command("iniciar")
                
                elif ch in (ord('l'), ord('L'), ord('r'), ord('R')):
                    self.process_command("lanzar")
                
                elif ch in (ord('f'), ord('F')):
                    self.process_command("fichas")
                
                elif ch in (ord('s'), ord('S')):
                    self.process_command("estado")
                
                elif ch in (ord('h'), ord('H'), ord('?')):
                    self.show_help()
                
                elif ch in (ord('m'), ord('M')):
                    self.input_mode = True
                    self.input_buffer = "mover "
                
                elif ch in (ord('d'), ord('D')):
                    self.input_mode = True
                    self.input_buffer = "dividir "
                
                # Navegación entre jugadores
                elif ch == curses.KEY_RIGHT:
                    if self.estado_partida:
                        n_jugadores = len(self.estado_partida.get("jugadores", []))
                        self.selected_player = (self.selected_player + 1) % n_jugadores
                
                elif ch == curses.KEY_LEFT:
                    if self.estado_partida:
                        n_jugadores = len(self.estado_partida.get("jugadores", []))
                        self.selected_player = (self.selected_player - 1) % n_jugadores
        
        # Desconectar
        try:
            self.socket.close()
        except:
            pass

def main(stdscr):
    """Punto de entrada principal."""
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 5555
    
    dashboard = ClienteDashboard(stdscr, host, puerto)
    dashboard.run()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

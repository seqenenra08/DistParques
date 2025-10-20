"""
Clase Partida - Gestiona el estado y la lógica de una partida de Parqués
"""
from typing import List, Dict, Optional
from enum import Enum
import random
from datetime import datetime

from .jugador import Jugador, ColorJugador
from .tablero import Tablero
from .ficha import Ficha


class EstadoPartida(Enum):
    """Estados posibles de una partida"""
    ESPERANDO = "esperando"      # Esperando jugadores
    EN_CURSO = "en_curso"        # Partida en progreso
    PAUSADA = "pausada"          # Partida pausada
    FINALIZADA = "finalizada"    # Partida terminada


class Partida:
    """
    Clase que gestiona una partida completa de Parqués.
    
    Atributos:
        id (str): Identificador único de la partida
        jugadores (List[Jugador]): Lista de jugadores (2-4 jugadores)
        tablero (Tablero): Tablero de juego
        estado (EstadoPartida): Estado actual de la partida
        turno_actual (int): Índice del jugador con el turno actual
        ganador (Optional[Jugador]): Jugador ganador (si la partida finalizó)
        colores_disponibles (List[ColorJugador]): Colores aún no asignados
        max_jugadores (int): Número máximo de jugadores (default 4)
        ultimo_dado (int): Último valor de dado lanzado
        turnos_consecutivos (int): Turnos consecutivos del mismo jugador
    """
    
    MAX_JUGADORES = 4
    MIN_JUGADORES = 2
    
    def __init__(self, id_partida: str, max_jugadores: int = 4):
        """
        Inicializa una nueva partida.
        
        Args:
            id_partida (str): Identificador único de la partida
            max_jugadores (int): Número máximo de jugadores (2-4)
        """
        self.id = id_partida
        self.jugadores: List[Jugador] = []
        self.tablero = Tablero()
        self.estado = EstadoPartida.ESPERANDO
        self.turno_actual = 0
        self.ganador: Optional[Jugador] = None
        self.max_jugadores = min(max_jugadores, self.MAX_JUGADORES)
        self.ultimo_dado = 0
        self.turnos_consecutivos = 0
        self.fecha_creacion = datetime.now()
        self.fecha_inicio: Optional[datetime] = None
        self.fecha_fin: Optional[datetime] = None
        
        # Colores disponibles para asignar
        self.colores_disponibles = [
            ColorJugador.ROJO,
            ColorJugador.AZUL,
            ColorJugador.AMARILLO,
            ColorJugador.VERDE
        ]
        
        # Historial de movimientos
        self.historial_movimientos = []
    
    def puede_unirse(self) -> bool:
        """
        Verifica si un nuevo jugador puede unirse a la partida.
        
        Returns:
            bool: True si hay espacio disponible
        """
        return (len(self.jugadores) < self.max_jugadores and 
                self.estado == EstadoPartida.ESPERANDO)
    
    def agregar_jugador(self, nombre: str, id_jugador: str = None) -> Optional[Jugador]:
        """
        Agrega un nuevo jugador a la partida y le asigna un color.
        
        Args:
            nombre (str): Nombre del jugador
            id_jugador (str): ID único del jugador
            
        Returns:
            Optional[Jugador]: Jugador creado o None si no pudo unirse
        """
        if not self.puede_unirse():
            return None
        
        # Crear jugador
        jugador = Jugador(nombre, id_jugador)
        
        # Asignar color disponible
        if self.colores_disponibles:
            color = self.colores_disponibles.pop(0)
            jugador.asignar_color(color)
            jugador.posicion_orden = len(self.jugadores) + 1
        
        self.jugadores.append(jugador)
        
        return jugador
    
    def remover_jugador(self, id_jugador: str) -> bool:
        """
        Remueve un jugador de la partida.
        
        Args:
            id_jugador (str): ID del jugador a remover
            
        Returns:
            bool: True si se removió exitosamente
        """
        for jugador in self.jugadores:
            if jugador.id == id_jugador:
                # Devolver el color a disponibles
                if jugador.color:
                    self.colores_disponibles.append(jugador.color)
                
                self.jugadores.remove(jugador)
                return True
        
        return False
    
    def iniciar_partida(self) -> bool:
        """
        Inicia la partida si hay suficientes jugadores.
        
        Returns:
            bool: True si se inició correctamente
        """
        if len(self.jugadores) < self.MIN_JUGADORES:
            return False
        
        if self.estado != EstadoPartida.ESPERANDO:
            return False
        
        # Determinar orden aleatorio de turnos
        random.shuffle(self.jugadores)
        for i, jugador in enumerate(self.jugadores):
            jugador.posicion_orden = i + 1
        
        # Activar turno del primer jugador
        self.jugadores[0].activar_turno()
        self.turno_actual = 0
        
        self.estado = EstadoPartida.EN_CURSO
        self.fecha_inicio = datetime.now()
        
        return True
    
    def obtener_jugador_actual(self) -> Optional[Jugador]:
        """
        Obtiene el jugador que tiene el turno actual.
        
        Returns:
            Optional[Jugador]: Jugador con el turno actual
        """
        if self.jugadores and 0 <= self.turno_actual < len(self.jugadores):
            return self.jugadores[self.turno_actual]
        return None
    
    def lanzar_dado(self) -> int:
        """
        Simula el lanzamiento de un dado (1-6).
        
        Returns:
            int: Resultado del dado
        """
        self.ultimo_dado = random.randint(1, 6)
        return self.ultimo_dado
    
    def puede_sacar_de_carcel(self, es_par: bool = False) -> bool:
        """
        Verifica si se puede sacar una ficha de la cárcel.
        En Parqués se saca con pares (sacar dos dados iguales)
        
        Args:
            es_par (bool): Si los dos dados sacados son iguales
            
        Returns:
            bool: True si puede sacar (cuando es par)
        """
        return es_par
    
    def pasar_turno(self) -> Jugador:
        """
        Pasa el turno al siguiente jugador.
        
        Returns:
            Jugador: Jugador que ahora tiene el turno
        """
        # Desactivar turno del jugador actual
        if self.jugadores:
            self.jugadores[self.turno_actual].desactivar_turno()
        
        # Avanzar al siguiente jugador
        self.turno_actual = (self.turno_actual + 1) % len(self.jugadores)
        self.turnos_consecutivos = 0
        
        # Activar turno del nuevo jugador
        self.jugadores[self.turno_actual].activar_turno()
        
        return self.jugadores[self.turno_actual]
    
    def otorgar_turno_extra(self):
        """Otorga un turno extra al jugador actual (por sacar 5, comer, etc.)"""
        self.turnos_consecutivos += 1
    
    def mover_ficha(self, id_jugador: str, id_ficha: int, pasos: int) -> Dict:
        """
        Mueve una ficha del jugador.
        
        Args:
            id_jugador (str): ID del jugador
            id_ficha (int): ID de la ficha a mover
            pasos (int): Número de pasos a mover
            
        Returns:
            Dict: Resultado del movimiento con detalles
        """
        resultado = {
            "exito": False,
            "mensaje": "",
            "ficha_comida": None,
            "turno_extra": False,
            "llego_a_meta": False
        }
        
        # Verificar que sea el turno del jugador
        jugador = self.obtener_jugador_actual()
        if not jugador or jugador.id != id_jugador:
            resultado["mensaje"] = "No es tu turno"
            return resultado
        
        # Buscar la ficha
        ficha = None
        for f in jugador.fichas:
            if f.id == id_ficha:
                ficha = f
                break
        
        if not ficha:
            resultado["mensaje"] = "Ficha no encontrada"
            return resultado
        
        # Verificar si puede moverse
        if not ficha.puede_moverse(pasos):
            resultado["mensaje"] = "La ficha no puede moverse"
            return resultado
        
        # Realizar el movimiento según el estado de la ficha
        if ficha.esta_en_carcel():
            # Sacar de la cárcel
            if self.puede_sacar_de_carcel(pasos):
                pos_salida = self.tablero.obtener_posicion_salida(jugador.color)
                ficha.sacar_de_carcel(pos_salida)
                self.tablero.agregar_ficha_a_casilla(ficha, pos_salida)
                
                resultado["exito"] = True
                resultado["mensaje"] = "Ficha salió de la cárcel"
                resultado["turno_extra"] = True
            else:
                resultado["mensaje"] = "No se puede sacar con ese número"
        else:
            # Mover ficha activa
            pos_antigua = ficha.posicion
            nueva_pos, entro_final = self.tablero.calcular_nueva_posicion(
                pos_antigua, pasos, jugador.color, ficha.en_recta_final
            )
            
            # Verificar si llega exactamente a la meta
            if self.tablero.puede_llegar_a_meta(pos_antigua, pasos, 
                                                 jugador.color, ficha.en_recta_final):
                ficha.marcar_como_final()
                self.tablero.remover_ficha_de_casilla(ficha, pos_antigua)
                
                resultado["exito"] = True
                resultado["mensaje"] = "¡Ficha llegó a la meta!"
                resultado["llego_a_meta"] = True
                resultado["turno_extra"] = True
            else:
                # Mover normalmente
                self.tablero.remover_ficha_de_casilla(ficha, pos_antigua)
                
                es_seguro = self.tablero.es_casilla_segura(nueva_pos)
                ficha.mover(nueva_pos, es_seguro)
                ficha.en_recta_final = entro_final
                
                if not entro_final:
                    self.tablero.agregar_ficha_a_casilla(ficha, nueva_pos)
                
                # Verificar colisión (comer ficha enemiga)
                if not es_seguro and not entro_final:
                    ficha_enemiga = self.tablero.verificar_colision(nueva_pos, jugador.color)
                    if ficha_enemiga:
                        ficha_enemiga.enviar_a_carcel()
                        self.tablero.remover_ficha_de_casilla(ficha_enemiga, nueva_pos)
                        
                        resultado["ficha_comida"] = ficha_enemiga.to_dict()
                        resultado["turno_extra"] = True
                        resultado["mensaje"] = "¡Comiste una ficha enemiga!"
                
                resultado["exito"] = True
                if not resultado["mensaje"]:
                    resultado["mensaje"] = "Ficha movida correctamente"
        
        # Registrar en historial
        self.historial_movimientos.append({
            "jugador": id_jugador,
            "ficha": id_ficha,
            "pasos": pasos,
            "timestamp": datetime.now().isoformat(),
            "resultado": resultado["mensaje"]
        })
        
        # Verificar si el jugador ganó
        if jugador.todas_fichas_en_meta():
            self.finalizar_partida(jugador)
        
        return resultado
    
    def finalizar_partida(self, ganador: Jugador):
        """
        Finaliza la partida declarando un ganador.
        
        Args:
            ganador (Jugador): Jugador ganador
        """
        self.estado = EstadoPartida.FINALIZADA
        self.ganador = ganador
        self.fecha_fin = datetime.now()
    
    def pausar_partida(self):
        """Pausa la partida."""
        if self.estado == EstadoPartida.EN_CURSO:
            self.estado = EstadoPartida.PAUSADA
    
    def reanudar_partida(self):
        """Reanuda la partida pausada."""
        if self.estado == EstadoPartida.PAUSADA:
            self.estado = EstadoPartida.EN_CURSO
    
    def to_dict(self) -> dict:
        """
        Convierte la partida a un diccionario para serialización JSON.
        
        Returns:
            dict: Representación de la partida en formato diccionario
        """
        return {
            "id": self.id,
            "estado": self.estado.value,
            "jugadores": [j.to_dict() for j in self.jugadores],
            "num_jugadores": len(self.jugadores),
            "max_jugadores": self.max_jugadores,
            "turno_actual": self.turno_actual,
            "jugador_actual": self.jugadores[self.turno_actual].to_dict() if self.jugadores else None,
            "ultimo_dado": self.ultimo_dado,
            "ganador": self.ganador.to_dict() if self.ganador else None,
            "tablero": self.tablero.to_dict(),
            "fecha_creacion": self.fecha_creacion.isoformat(),
            "fecha_inicio": self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            "fecha_fin": self.fecha_fin.isoformat() if self.fecha_fin else None
        }
    
    def __repr__(self):
        return f"Partida({self.id}, {len(self.jugadores)} jugadores, {self.estado.value})"

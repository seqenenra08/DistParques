"""
Modelo de Ficha para el juego de Parqués.
"""
from enum import Enum
from typing import Optional


class EstadoFicha(Enum):
    """Estados posibles de una ficha."""
    CARCEL = "carcel"
    TABLERO = "tablero"
    SEGURO = "seguro"
    PASILLO_FINAL = "pasillo_final"
    META = "meta"


class Ficha:
    """Representa una ficha del jugador en el tablero."""
    
    def __init__(self, id_ficha: int, color: str):
        self.id = id_ficha
        self.color = color
        self.posicion: Optional[int] = None  # None = cárcel, 0-67 = tablero
        self.estado = EstadoFicha.CARCEL
        self.posicion_pasillo: Optional[int] = None  # 0-7 en pasillo final
        self.casillas_recorridas = 0  # Contador total de casillas recorridas
    
    def esta_en_carcel(self) -> bool:
        return self.estado == EstadoFicha.CARCEL
    
    def esta_en_meta(self) -> bool:
        return self.estado == EstadoFicha.META
    
    def puede_salir(self) -> bool:
        """Verifica si la ficha puede salir de la cárcel."""
        return self.esta_en_carcel()
    
    def mover_a_tablero(self, posicion: int):
        """Saca la ficha de la cárcel al tablero."""
        self.posicion = posicion
        self.estado = EstadoFicha.TABLERO
        self.casillas_recorridas = 0
    
    def mover(self, casillas: int, es_seguro: bool = False) -> bool:
        """Mueve la ficha N casillas. Retorna True si completó el movimiento."""
        if self.estado == EstadoFicha.CARCEL:
            return False
        
        if self.estado == EstadoFicha.PASILLO_FINAL:
            self.posicion_pasillo += casillas
            if self.posicion_pasillo >= 8:
                self.estado = EstadoFicha.META
                self.posicion_pasillo = 7
            return True
        
        # Mover en el tablero
        self.posicion = (self.posicion + casillas) % 68
        self.casillas_recorridas += casillas
        
        if es_seguro:
            self.estado = EstadoFicha.SEGURO
        else:
            self.estado = EstadoFicha.TABLERO
        
        return True
    
    def entrar_pasillo(self):
        """Entra al pasillo final."""
        self.estado = EstadoFicha.PASILLO_FINAL
        self.posicion_pasillo = 0
        self.posicion = None  # Ya no está en el tablero principal
    
    def capturar(self):
        """Envía la ficha de vuelta a la cárcel."""
        self.posicion = None
        self.estado = EstadoFicha.CARCEL
        self.posicion_pasillo = None
        self.casillas_recorridas = 0
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "color": self.color,
            "posicion": self.posicion,
            "estado": self.estado.value,
            "posicion_pasillo": self.posicion_pasillo,
            "casillas_recorridas": self.casillas_recorridas
        }

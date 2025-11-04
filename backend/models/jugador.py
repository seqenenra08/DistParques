"""Modelo de Jugador para el juego de Parqués."""
from typing import List, Optional
from .ficha import Ficha


class Jugador:
    """Representa un jugador en la partida."""
    
    COLORES_DISPONIBLES = ["rojo", "azul", "amarillo", "verde"]
    
    def __init__(self, nombre: str, color: str, conexion=None):
        self.nombre = nombre
        self.color = color
        self.conexion = conexion  # Socket del cliente
        self.fichas: List[Ficha] = [Ficha(i, color) for i in range(4)]
        self.es_su_turno = False
        self.pares_consecutivos = 0
        self.casilla_salida = self._calcular_casilla_salida()
    
    def _calcular_casilla_salida(self) -> int:
        """Calcula la casilla de salida según el color."""
        salidas = {"rojo": 5, "azul": 22, "amarillo": 39, "verde": 56}
        return salidas.get(self.color, 0)
    
    def tiene_fichas_en_carcel(self) -> bool:
        return any(f.esta_en_carcel() for f in self.fichas)
    
    def todas_fichas_en_meta(self) -> bool:
        """Verifica si el jugador ganó."""
        return all(f.esta_en_meta() for f in self.fichas)
    
    def puede_mover(self, id_ficha: int, dados: int) -> bool:
        """Valida si una ficha puede moverse con el resultado de dados."""
        if id_ficha < 0 or id_ficha >= 4:
            return False
        
        ficha = self.fichas[id_ficha]
        
        # Si está en cárcel, solo puede salir con pares
        if ficha.esta_en_carcel():
            return False  # Ya validado en puede_sacar_de_carcel
        
        # Si está en meta, no puede moverse
        if ficha.esta_en_meta():
            return False
        
        return True
    
    def puede_sacar_de_carcel(self, dados: tuple) -> bool:
        """Solo puede sacar con par de dados."""
        return dados[0] == dados[1] and self.tiene_fichas_en_carcel()
    
    def incrementar_pares(self):
        self.pares_consecutivos += 1
    
    def resetear_pares(self):
        self.pares_consecutivos = 0
    
    def tiene_tres_pares(self) -> bool:
        """Si saca 3 pares seguidos, pierde el turno y manda ficha más adelantada a cárcel."""
        return self.pares_consecutivos >= 3
    
    def to_dict(self) -> dict:
        return {
            "nombre": self.nombre,
            "color": self.color,
            "fichas": [f.to_dict() for f in self.fichas],
            "es_su_turno": self.es_su_turno,
            "casilla_salida": self.casilla_salida
        }

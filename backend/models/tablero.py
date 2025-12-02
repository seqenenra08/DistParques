"""
Modelo de Tablero para el juego de Parqués.
"""
from typing import List, Optional, Set
from .ficha import Ficha


class Tablero:
    """Representa el tablero del juego con 68 casillas."""
    
    SEGUROS: Set[int] = {5, 12, 17, 22, 29, 34, 39, 46, 51, 56, 63, 0}  # Casillas seguras
    SALIDAS = {"red": 39, "blue": 22, "yellow": 5, "green": 56}
    ENTRADAS_PASILLO = {"red": 29, "blue": 12, "yellow": 63, "green": 46}
    
    def __init__(self):
        # casillas[i] = lista de fichas en esa posición
        self.casillas: List[List] = [[] for _ in range(68)]
    
    def es_seguro(self, posicion: int) -> bool:
        """Verifica si una casilla es segura."""
        return posicion in self.SEGUROS
    
    def es_salida(self, posicion: int, color: str) -> bool:
        """Verifica si es la salida del color del jugador."""
        return self.SALIDAS.get(color) == posicion
    
    def obtener_fichas_en(self, posicion: int) -> List[Ficha]:
        """Devuelve fichas en una casilla."""
        return self.casillas[posicion]
    
    def agregar_ficha(self, posicion: int, ficha: Ficha):
        """Coloca una ficha en el tablero."""
        if 0 <= posicion < 68:
            self.casillas[posicion].append(ficha)
    
    def remover_ficha(self, posicion: int, ficha: Ficha):
        """Remueve una ficha del tablero."""
        if 0 <= posicion < 68 and ficha in self.casillas[posicion]:
            self.casillas[posicion].remove(ficha)
    
    def verificar_captura(self, posicion: int, ficha_movida) -> List:
        """
        Verifica si hay fichas enemigas para capturar.
        Retorna lista de fichas capturadas.
        """
        # No se captura en seguros
        if self.es_seguro(posicion):
            return []
        
        # No se captura en la salida del mismo color
        if self.es_salida(posicion, ficha_movida.color):
            return []
        
        fichas_en_casilla = self.obtener_fichas_en(posicion)
        capturadas = []
        
        for ficha in fichas_en_casilla:
            # Capturar solo fichas de diferente color (comparar por objeto, no por ID)
            # Nota: no comparamos con ficha_movida porque aún no está en el tablero
            if ficha.color != ficha_movida.color:
                capturadas.append(ficha)
        
        return capturadas
    
    def debe_entrar_pasillo(self, posicion: int, color: str) -> bool:
        """Verifica si la ficha debe entrar al pasillo final."""
        return self.ENTRADAS_PASILLO.get(color) == posicion
    
    def to_dict(self) -> dict:
        """Serializa el estado del tablero."""
        estado = {}
        for pos, fichas in enumerate(self.casillas):
            if fichas:
                estado[pos] = [{"color": f.color, "id": f.id} for f in fichas]
        return estado
    
    def __repr__(self):
        return f"Tablero({len(self.casillas)} casillas, {len(self.SEGUROS)} seguros)"

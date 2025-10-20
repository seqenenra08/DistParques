"""
Clase Jugador - Representa un jugador en el juego de Parqués
"""
from typing import List
from enum import Enum


class ColorJugador(Enum):
    """Colores disponibles para los jugadores"""
    ROJO = "rojo"
    AZUL = "azul"
    AMARILLO = "amarillo"
    VERDE = "verde"


class Jugador:
    """
    Clase que representa a un jugador en el juego de Parqués.
    
    Atributos:
        nombre (str): Nombre del jugador
        color (ColorJugador): Color asignado al jugador
        fichas (List[Ficha]): Lista de fichas del jugador (4 fichas)
        turno (bool): Indica si es el turno del jugador
        id (str): Identificador único del jugador
    """
    
    def __init__(self, nombre: str, id_jugador: str = None):
        """
        Inicializa un nuevo jugador.
        
        Args:
            nombre (str): Nombre del jugador
            id_jugador (str, optional): Identificador único del jugador
        """
        self.nombre = nombre
        self.color = None  # Se asigna cuando se une a la partida
        self.fichas = []  # Se inicializa cuando se asigna el color
        self.turno = False
        self.id = id_jugador or nombre
        self.posicion_orden = None  # Orden de juego (1-4)
    
    def asignar_color(self, color: ColorJugador):
        """
        Asigna un color al jugador y crea sus fichas.
        
        Args:
            color (ColorJugador): Color a asignar
        """
        from .ficha import Ficha
        
        self.color = color
        # Crear 4 fichas para el jugador
        self.fichas = [Ficha(i, color, self.id) for i in range(4)]
    
    def activar_turno(self):
        """Activa el turno del jugador"""
        self.turno = True
    
    def desactivar_turno(self):
        """Desactiva el turno del jugador"""
        self.turno = False
    
    def tiene_fichas_en_carcel(self) -> bool:
        """
        Verifica si el jugador tiene fichas en la cárcel.
        
        Returns:
            bool: True si hay fichas en la cárcel
        """
        return any(ficha.esta_en_carcel() for ficha in self.fichas)
    
    def tiene_fichas_activas(self) -> bool:
        """
        Verifica si el jugador tiene fichas activas en el tablero.
        
        Returns:
            bool: True si hay fichas activas
        """
        return any(ficha.esta_activa() for ficha in self.fichas)
    
    def todas_fichas_en_meta(self) -> bool:
        """
        Verifica si todas las fichas del jugador están en la meta.
        
        Returns:
            bool: True si todas las fichas están en la meta
        """
        return all(ficha.esta_en_final() for ficha in self.fichas)
    
    def obtener_fichas_movibles(self, pasos: int, es_par: bool = False) -> List:
        """
        Obtiene las fichas que pueden moverse con el número de pasos dado.
        
        Args:
            pasos (int): Número de pasos a mover
            es_par (bool): Si se sacó un par de dados
            
        Returns:
            List[Ficha]: Lista de fichas que pueden moverse
        """
        fichas_movibles = []
        
        for ficha in self.fichas:
            if ficha.puede_moverse(pasos, es_par):
                fichas_movibles.append(ficha)
        
        return fichas_movibles
    
    def to_dict(self) -> dict:
        """
        Convierte el jugador a un diccionario para serialización JSON.
        
        Returns:
            dict: Representación del jugador en formato diccionario
        """
        return {
            "id": self.id,
            "nombre": self.nombre,
            "color": self.color.value if self.color else None,
            "turno": self.turno,
            "posicion_orden": self.posicion_orden,
            "fichas": [ficha.to_dict() for ficha in self.fichas],
            "fichas_en_meta": sum(1 for f in self.fichas if f.esta_en_final())
        }
    
    def __repr__(self):
        return f"Jugador({self.nombre}, {self.color.value if self.color else 'sin color'})"

"""
Clase Ficha - Representa una ficha en el juego de Parqués
"""
from enum import Enum


class EstadoFicha(Enum):
    """Estados posibles de una ficha"""
    CARCEL = "carcel"  # Ficha en la cárcel (posición inicial)
    ACTIVA = "activa"  # Ficha en movimiento en el tablero
    SEGURO = "seguro"  # Ficha en una casilla segura
    FINAL = "final"    # Ficha ha llegado a la meta


class Ficha:
    """
    Clase que representa una ficha en el juego de Parqués.
    
    Atributos:
        id (int): Identificador de la ficha (0-3)
        color (ColorJugador): Color de la ficha (hereda del jugador)
        posicion (int): Posición actual en el tablero (-1 si está en cárcel)
        estado (EstadoFicha): Estado actual de la ficha
        id_jugador (str): ID del jugador propietario
        pasos_recorridos (int): Número de pasos recorridos desde la salida
    """
    
    def __init__(self, id_ficha: int, color, id_jugador: str):
        """
        Inicializa una nueva ficha.
        
        Args:
            id_ficha (int): Identificador de la ficha (0-3)
            color (ColorJugador): Color de la ficha
            id_jugador (str): ID del jugador propietario
        """
        self.id = id_ficha
        self.color = color
        self.posicion = -1  # -1 indica que está en la cárcel
        self.estado = EstadoFicha.CARCEL
        self.id_jugador = id_jugador
        self.pasos_recorridos = 0
        self.en_recta_final = False  # True cuando entra a la zona de llegada
    
    def esta_en_carcel(self) -> bool:
        """
        Verifica si la ficha está en la cárcel.
        
        Returns:
            bool: True si está en la cárcel
        """
        return self.estado == EstadoFicha.CARCEL
    
    def esta_activa(self) -> bool:
        """
        Verifica si la ficha está activa en el tablero.
        
        Returns:
            bool: True si está activa
        """
        return self.estado in [EstadoFicha.ACTIVA, EstadoFicha.SEGURO]
    
    def esta_en_seguro(self) -> bool:
        """
        Verifica si la ficha está en una casilla segura.
        
        Returns:
            bool: True si está en un seguro
        """
        return self.estado == EstadoFicha.SEGURO
    
    def esta_en_final(self) -> bool:
        """
        Verifica si la ficha ha llegado a la meta.
        
        Returns:
            bool: True si está en la meta
        """
        return self.estado == EstadoFicha.FINAL
    
    def sacar_de_carcel(self, posicion_salida: int):
        """
        Saca la ficha de la cárcel y la coloca en la posición de salida.
        
        Args:
            posicion_salida (int): Posición de salida según el color
        """
        self.posicion = posicion_salida
        self.estado = EstadoFicha.ACTIVA
        self.pasos_recorridos = 0
    
    def mover(self, nueva_posicion: int, es_seguro: bool = False):
        """
        Mueve la ficha a una nueva posición.
        
        Args:
            nueva_posicion (int): Nueva posición en el tablero
            es_seguro (bool): Si la nueva posición es una casilla segura
        """
        self.posicion = nueva_posicion
        self.pasos_recorridos += 1
        
        if es_seguro:
            self.estado = EstadoFicha.SEGURO
        else:
            self.estado = EstadoFicha.ACTIVA
    
    def enviar_a_carcel(self):
        """Envía la ficha de vuelta a la cárcel (cuando es comida)."""
        self.posicion = -1
        self.estado = EstadoFicha.CARCEL
        self.pasos_recorridos = 0
        self.en_recta_final = False
    
    def marcar_como_final(self):
        """Marca la ficha como llegada a la meta."""
        self.estado = EstadoFicha.FINAL
        self.en_recta_final = True
    
    def puede_moverse(self, pasos: int, es_par: bool = False) -> bool:
        """
        Verifica si la ficha puede moverse con el número de pasos dado.
        
        Args:
            pasos (int): Número de pasos a mover
            es_par (bool): Si se sacó un par de dados
            
        Returns:
            bool: True si puede moverse
        """
        # Si está en la meta, no puede moverse
        if self.esta_en_final():
            return False
        
        # Si está en la cárcel, solo puede salir con par
        if self.esta_en_carcel():
            return es_par
        
        # Si está activa, siempre puede moverse (validaciones adicionales en Tablero)
        return True
    
    def puede_comer(self, otra_ficha: 'Ficha') -> bool:
        """
        Verifica si esta ficha puede comer a otra.
        
        Args:
            otra_ficha (Ficha): La otra ficha a verificar
            
        Returns:
            bool: True si puede comerla
        """
        # No puede comer fichas del mismo jugador
        if self.id_jugador == otra_ficha.id_jugador:
            return False
        
        # No puede comer fichas en seguros
        if otra_ficha.esta_en_seguro():
            return False
        
        # No puede comer fichas en la meta
        if otra_ficha.esta_en_final():
            return False
        
        # Debe estar en la misma posición
        return self.posicion == otra_ficha.posicion
    
    def to_dict(self) -> dict:
        """
        Convierte la ficha a un diccionario para serialización JSON.
        
        Returns:
            dict: Representación de la ficha en formato diccionario
        """
        return {
            "id": self.id,
            "color": self.color.value,
            "posicion": self.posicion,
            "estado": self.estado.value,
            "id_jugador": self.id_jugador,
            "pasos_recorridos": self.pasos_recorridos,
            "en_recta_final": self.en_recta_final
        }
    
    def __repr__(self):
        return f"Ficha({self.id}, {self.color.value}, pos={self.posicion}, {self.estado.value})"

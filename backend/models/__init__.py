"""Modelos del juego de Parqués."""
from .ficha import Ficha, EstadoFicha
from .jugador import Jugador
from .tablero import Tablero
from .partida import Partida

__all__ = ["Ficha", "EstadoFicha", "Jugador", "Tablero", "Partida"]

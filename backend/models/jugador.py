"""Modelo de Jugador para el juego de Parqués."""
from typing import List, Optional
from .ficha import Ficha


class Jugador:
    """Representa un jugador en la partida."""
    
    COLORES_DISPONIBLES = ["red", "blue", "yellow", "green"]
    
    def __init__(self, nombre: str, color: str, conexion=None):
        self.nombre = nombre
        self.color = color
        self.conexion = conexion  # Socket del cliente
        # Generar ID único si no se proporciona conexión
        self.id = id(conexion) if conexion else nombre.lower()
        self.fichas: List[Ficha] = [Ficha(i, color) for i in range(4)]
        self.es_su_turno = False
        self.pares_consecutivos = 0
        self.casilla_salida = self._calcular_casilla_salida()
        # Sistema de 3 intentos cuando todas las fichas están en cárcel
        self.intentos_carcel = 0
        self.max_intentos_carcel = 3
        # Control de lanzamiento de dados
        self.ya_lanzo_dados = False
        self.puede_lanzar_de_nuevo = False
    
    def _calcular_casilla_salida(self) -> int:
        """Calcula la casilla de salida según el color."""
        salidas = {"red": 39, "blue": 22, "yellow": 5, "green": 56}
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
        
        # Si está en pasillo final, verificar que no se pase de la meta
        from .ficha import EstadoFicha
        if ficha.estado == EstadoFicha.PASILLO_FINAL:
            nueva_pos_pasillo = ficha.posicion_pasillo + dados
            # Solo puede mover si cae exacto o antes de la meta (posición 8)
            if nueva_pos_pasillo > 8:
                return False
            return True
        
        # Si está en tablero normal, permitir el movimiento
        # La validación detallada de entrada al pasillo se hace en _mover_ficha
        return True
    
    def puede_sacar_de_carcel(self, dados: tuple) -> bool:
        """Solo puede sacar con par de dados."""
        return dados[0] == dados[1] and self.tiene_fichas_en_carcel()
    
    def incrementar_pares(self):
        self.pares_consecutivos += 1
    
    def resetear_pares(self):
        self.pares_consecutivos = 0
    
    def tiene_tres_pares(self) -> bool:
        """Si saca 3 pares seguidos, puede sacar una ficha del juego."""
        return self.pares_consecutivos >= 3
    
    def incrementar_intento_carcel(self):
        """Incrementa el contador de intentos cuando todas están en cárcel."""
        self.intentos_carcel += 1
    
    def agotar_intentos_carcel(self) -> bool:
        """Verifica si se agotaron los 3 intentos.
        
        Returns:
            bool: True si se agotaron los intentos
        """
        return self.intentos_carcel >= self.max_intentos_carcel
    
    def resetear_intentos_carcel(self):
        """Resetea el contador de intentos de cárcel."""
        self.intentos_carcel = 0
    
    def marcar_lanzamiento(self):
        """Marca que el jugador lanzó los dados."""
        # Si ya tenía permiso para lanzar de nuevo, consumirlo
        if self.puede_lanzar_de_nuevo:
            self.puede_lanzar_de_nuevo = False
        
        self.ya_lanzo_dados = True
    
    def permitir_lanzar_de_nuevo(self):
        """Permite lanzar de nuevo (cuando saca par)."""
        self.puede_lanzar_de_nuevo = True
        # NO resetear ya_lanzo_dados, solo marcar que puede lanzar de nuevo
    
    def puede_lanzar(self) -> bool:
        """Verifica si el jugador puede lanzar los dados.
        
        Returns:
            bool: True si puede lanzar
        """
        # Si todas las fichas están en cárcel, puede lanzar hasta 3 veces
        todas_en_carcel = all(f.esta_en_carcel() for f in self.fichas)
        if todas_en_carcel:
            return not self.agotar_intentos_carcel()
        
        # Si tiene permiso explícito para lanzar de nuevo (por par), sí puede
        if self.puede_lanzar_de_nuevo:
            return True
        
        # Si no puede lanzar de nuevo Y ya lanzó, NO puede
        if not self.puede_lanzar_de_nuevo and self.ya_lanzo_dados:
            return False
        
        # Si no ha lanzado aún en este turno, puede lanzar
        return True
    
    def resetear_lanzamiento(self):
        """Resetea el estado de lanzamiento al cambiar de turno."""
        self.ya_lanzo_dados = False
        self.puede_lanzar_de_nuevo = False
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "nombre": self.nombre,
            "color": self.color,
            "fichas": [f.to_dict() for f in self.fichas],
            "es_su_turno": self.es_su_turno,
            "casilla_salida": self.casilla_salida,
            "intentos_carcel": self.intentos_carcel,
            "ya_lanzo_dados": self.ya_lanzo_dados,
            "puede_lanzar_de_nuevo": self.puede_lanzar_de_nuevo
        }

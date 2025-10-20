"""
Clase Tablero - Representa el tablero del juego de Parqués
"""
from typing import List, Dict, Tuple, Optional
from .jugador import ColorJugador
from .ficha import Ficha


class Tablero:
    """
    Clase que representa el tablero del juego de Parqués.
    
    El tablero tradicional tiene 68 casillas en total, organizadas en un circuito.
    Cada color tiene:
    - Una casilla de salida
    - Casillas seguras
    - Una zona de llegada (recta final) de 8 casillas
    
    Atributos:
        casillas (List[dict]): Lista de casillas del tablero
        seguros (List[int]): Posiciones de las casillas seguras
        salidas (Dict[ColorJugador, int]): Posiciones de salida por color
        entradas_finales (Dict[ColorJugador, int]): Posiciones de entrada a zona final
        num_casillas (int): Número total de casillas en el circuito principal
    """
    
    # Configuración del tablero tradicional de Parqués
    NUM_CASILLAS = 68  # Casillas del circuito principal
    CASILLAS_ZONA_FINAL = 8  # Casillas para llegar a la meta
    NUM_FICHAS_POR_JUGADOR = 4
    
    def __init__(self):
        """Inicializa el tablero con la configuración estándar de Parqués."""
        self.num_casillas = self.NUM_CASILLAS
        
        # Definir las salidas de cada color (distribuidas equitativamente)
        # En un tablero real, cada color sale en una posición diferente
        self.salidas = {
            ColorJugador.ROJO: 5,      # Casilla de salida del rojo
            ColorJugador.AZUL: 22,     # Casilla de salida del azul
            ColorJugador.AMARILLO: 39, # Casilla de salida del amarillo
            ColorJugador.VERDE: 56     # Casilla de salida del verde
        }
        
        # Casillas seguras (aproximadamente cada 17 casillas + las salidas)
        self.seguros = [
            5, 12, 22, 29,  # Seguros del primer cuarto
            39, 46, 56, 63  # Seguros del segundo cuarto
        ]
        
        # Posición donde cada color entra a su zona final (antes de llegar a meta)
        # Cada color tiene 68 casillas de recorrido antes de su entrada
        self.entradas_finales = {
            ColorJugador.ROJO: 4,
            ColorJugador.AZUL: 21,
            ColorJugador.AMARILLO: 38,
            ColorJugador.VERDE: 55
        }
        
        # Inicializar las casillas del tablero
        self.casillas = self._inicializar_casillas()
        
        # Zonas finales para cada color (8 casillas antes de la meta)
        self.zonas_finales = {
            color: [-100 - i for i in range(self.CASILLAS_ZONA_FINAL)]
            for color in ColorJugador
        }
    
    def _inicializar_casillas(self) -> List[Dict]:
        """
        Inicializa la estructura de casillas del tablero.
        
        Returns:
            List[Dict]: Lista de casillas con su configuración
        """
        casillas = []
        
        for i in range(self.num_casillas):
            casilla = {
                "posicion": i,
                "es_seguro": i in self.seguros,
                "es_salida": i in self.salidas.values(),
                "fichas": []  # Lista de fichas en esta casilla
            }
            
            # Asignar color de salida si corresponde
            for color, pos_salida in self.salidas.items():
                if i == pos_salida:
                    casilla["color_salida"] = color
                    break
            
            casillas.append(casilla)
        
        return casillas
    
    def obtener_posicion_salida(self, color: ColorJugador) -> int:
        """
        Obtiene la posición de salida para un color específico.
        
        Args:
            color (ColorJugador): Color del jugador
            
        Returns:
            int: Posición de salida
        """
        return self.salidas[color]
    
    def es_casilla_segura(self, posicion: int) -> bool:
        """
        Verifica si una posición es una casilla segura.
        
        Args:
            posicion (int): Posición a verificar
            
        Returns:
            bool: True si es seguro
        """
        return posicion in self.seguros
    
    def calcular_nueva_posicion(self, posicion_actual: int, pasos: int, 
                                color: ColorJugador, en_recta_final: bool = False) -> Tuple[int, bool]:
        """
        Calcula la nueva posición después de mover cierto número de pasos.
        
        Args:
            posicion_actual (int): Posición actual de la ficha
            pasos (int): Número de pasos a mover
            color (ColorJugador): Color de la ficha
            en_recta_final (bool): Si la ficha ya está en la recta final
            
        Returns:
            Tuple[int, bool]: (nueva_posicion, entro_a_zona_final)
        """
        if en_recta_final:
            # Ya está en la zona final, solo avanzar en ella
            nueva_pos = posicion_actual + pasos
            return nueva_pos, True
        
        # Calcular nueva posición en el circuito principal
        nueva_posicion = (posicion_actual + pasos) % self.num_casillas
        
        # Verificar si debe entrar a la zona final
        entrada_final = self.entradas_finales[color]
        
        # Si pasa por su entrada a la zona final, debe entrar
        pasos_desde_salida = self._calcular_pasos_desde_salida(posicion_actual, color)
        nuevos_pasos = pasos_desde_salida + pasos
        
        # Si ha dado la vuelta completa (68 pasos) debe entrar a zona final
        if nuevos_pasos >= self.num_casillas:
            # Entrar a zona final
            pasos_en_final = nuevos_pasos - self.num_casillas
            return pasos_en_final, True
        
        return nueva_posicion, False
    
    def _calcular_pasos_desde_salida(self, posicion_actual: int, color: ColorJugador) -> int:
        """
        Calcula cuántos pasos ha recorrido una ficha desde su salida.
        
        Args:
            posicion_actual (int): Posición actual
            color (ColorJugador): Color de la ficha
            
        Returns:
            int: Número de pasos recorridos
        """
        salida = self.salidas[color]
        
        if posicion_actual >= salida:
            return posicion_actual - salida
        else:
            return self.num_casillas - salida + posicion_actual
    
    def puede_llegar_a_meta(self, posicion_actual: int, pasos: int, 
                           color: ColorJugador, en_recta_final: bool) -> bool:
        """
        Verifica si con los pasos dados la ficha puede llegar exactamente a la meta.
        
        Args:
            posicion_actual (int): Posición actual
            pasos (int): Pasos a mover
            color (ColorJugador): Color de la ficha
            en_recta_final (bool): Si está en recta final
            
        Returns:
            bool: True si llega exactamente a la meta
        """
        if en_recta_final:
            return posicion_actual + pasos == self.CASILLAS_ZONA_FINAL
        
        pasos_desde_salida = self._calcular_pasos_desde_salida(posicion_actual, color)
        total_pasos = pasos_desde_salida + pasos
        
        # Debe llegar exactamente a 68 + 8 = 76 pasos
        return total_pasos == self.num_casillas + self.CASILLAS_ZONA_FINAL
    
    def obtener_fichas_en_posicion(self, posicion: int) -> List[Ficha]:
        """
        Obtiene todas las fichas que están en una posición específica.
        
        Args:
            posicion (int): Posición a consultar
            
        Returns:
            List[Ficha]: Lista de fichas en esa posición
        """
        if 0 <= posicion < self.num_casillas:
            return self.casillas[posicion]["fichas"].copy()
        return []
    
    def agregar_ficha_a_casilla(self, ficha: Ficha, posicion: int):
        """
        Agrega una ficha a una casilla del tablero.
        
        Args:
            ficha (Ficha): Ficha a agregar
            posicion (int): Posición donde colocar la ficha
        """
        if 0 <= posicion < self.num_casillas:
            self.casillas[posicion]["fichas"].append(ficha)
    
    def remover_ficha_de_casilla(self, ficha: Ficha, posicion: int):
        """
        Remueve una ficha de una casilla del tablero.
        
        Args:
            ficha (Ficha): Ficha a remover
            posicion (int): Posición de donde remover la ficha
        """
        if 0 <= posicion < self.num_casillas:
            if ficha in self.casillas[posicion]["fichas"]:
                self.casillas[posicion]["fichas"].remove(ficha)
    
    def verificar_colision(self, posicion: int, color_ficha: ColorJugador) -> Optional[Ficha]:
        """
        Verifica si hay una ficha enemiga en la posición que pueda ser comida.
        
        Args:
            posicion (int): Posición a verificar
            color_ficha (ColorJugador): Color de la ficha que se mueve
            
        Returns:
            Optional[Ficha]: Ficha enemiga si existe, None si no hay colisión
        """
        if self.es_casilla_segura(posicion):
            return None
        
        fichas = self.obtener_fichas_en_posicion(posicion)
        
        for ficha in fichas:
            if ficha.color != color_ficha and not ficha.esta_en_seguro():
                return ficha
        
        return None
    
    def to_dict(self) -> dict:
        """
        Convierte el tablero a un diccionario para serialización JSON.
        
        Returns:
            dict: Representación del tablero en formato diccionario
        """
        return {
            "num_casillas": self.num_casillas,
            "seguros": self.seguros,
            "salidas": {color.value: pos for color, pos in self.salidas.items()},
            "casillas": [
                {
                    "posicion": c["posicion"],
                    "es_seguro": c["es_seguro"],
                    "es_salida": c["es_salida"],
                    "num_fichas": len(c["fichas"]),
                    "fichas": [f.to_dict() for f in c["fichas"]]
                }
                for c in self.casillas
            ]
        }
    
    def __repr__(self):
        return f"Tablero({self.num_casillas} casillas, {len(self.seguros)} seguros)"

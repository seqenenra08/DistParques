"""Modelo de Partida para el juego de Parqués."""
import random
import threading
from typing import List, Optional, Dict, Tuple
from .jugador import Jugador
from .tablero import Tablero
from .ficha import EstadoFicha

class Partida:
    """Representa una partida completa del juego."""

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
        self.max_jugadores = min(max_jugadores, self.MAX_JUGADORES)
        self.iniciada = False
        self.turno_actual = 0
        self.ganador: Optional[Jugador] = None
        self.lock = threading.Lock()  # Para sincronización de turnos
        self.dados_pendientes: Dict[str, List[int]] = {}  # jugador -> [dado1, dado2]
        # Estados para determinar primer turno con dados
        self.esperando_dados_inicio = False
        self.dados_inicio: Dict[str, int] = {}  # jugador_id -> valor_dado
        # Control de 3 pares consecutivos
        self.jugador_puede_sacar_ficha: Optional[Jugador] = None

    def puede_unirse(self) -> bool:
        """
        Verifica si un nuevo jugador puede unirse a la partida.

        Returns:
            bool: True si hay espacio disponible
        """
        return (len(self.jugadores) < self.max_jugadores and
                not self.iniciada)

    def agregar_jugador(self, nombre: str, id_jugador: str = None, color_preferido: str = None) -> Optional[Jugador]:
        """
        Agrega un nuevo jugador a la partida y le asigna un color.

        Args:
            nombre (str): Nombre del jugador
            id_jugador (str): ID único del jugador (puede ser conexión o string)
            color_preferido (str): Color deseado por el jugador (opcional)

        Returns:
            Optional[Jugador]: Jugador creado o None si no pudo unirse
        """
        with self.lock:
            if self.iniciada:
                return None

            if len(self.jugadores) >= self.max_jugadores:
                return None

            # Determinar colores disponibles
            colores_usados = {j.color for j in self.jugadores}
            colores_disponibles = [c for c in Jugador.COLORES_DISPONIBLES if c not in colores_usados]

            if not colores_disponibles:
                return None

            # Usar color preferido si está disponible, de lo contrario asignar el primero disponible
            if color_preferido and color_preferido in colores_disponibles:
                color = color_preferido
                print(f"✅ Asignando color preferido '{color}' a jugador '{nombre}'")
            else:
                color = colores_disponibles[0]
                if color_preferido:
                    print(f"⚠️ Color preferido '{color_preferido}' no disponible para '{nombre}', asignando '{color}'")
                else:
                    print(f"📌 Asignando color automático '{color}' a jugador '{nombre}'")
            
            jugador = Jugador(nombre, color, id_jugador)
            # Si se pasó un id_jugador personalizado, sobrescribirlo
            if id_jugador and not isinstance(id_jugador, int):
                jugador.id = id_jugador
            self.jugadores.append(jugador)

            return jugador

    def iniciar_partida(self) -> bool:
        """Inicia la partida si hay al menos 2 jugadores."""
        with self.lock:
            if len(self.jugadores) < self.MIN_JUGADORES:
                return False

            self.iniciada = True
            # Activar modo de selección de turno con dados
            self.esperando_dados_inicio = True
            self.dados_inicio = {}
            # Todos los jugadores pueden lanzar dados para determinar el orden
            return True

    def obtener_jugador_actual(self) -> Optional[Jugador]:
        """Retorna el jugador del turno actual."""
        if not self.jugadores:
            return None
        return self.jugadores[self.turno_actual]

    def lanzar_dados(self) -> tuple:
        """Simula el lanzamiento de 2 dados."""
        return (random.randint(1, 6), random.randint(1, 6))
    
    def lanzar_dado_inicio(self, jugador: Jugador) -> Optional[int]:
        """Lanza un dado para determinar el orden inicial.
        
        Args:
            jugador: Jugador que lanza el dado
            
        Returns:
            Valor del dado (1-6) o None si no está en fase de inicio
        """
        with self.lock:
            if not self.esperando_dados_inicio:
                return None
            
            if jugador.id in self.dados_inicio:
                return None  # Ya lanzó
            
            # Lanzar un dado
            valor = random.randint(1, 6)
            self.dados_inicio[jugador.id] = valor
            
            # Verificar si todos han lanzado
            if len(self.dados_inicio) == len(self.jugadores):
                self._determinar_primer_turno()
            
            return valor
    
    def _determinar_primer_turno(self):
        """Determina el jugador que comienza según los dados lanzados."""
        # Encontrar el valor máximo
        max_valor = max(self.dados_inicio.values())
        
        # Encontrar jugadores con el valor máximo (puede haber empate)
        ganadores = [jid for jid, valor in self.dados_inicio.items() if valor == max_valor]
        
        # Si hay empate, elegir uno aleatoriamente
        if len(ganadores) > 1:
            jugador_id_ganador = random.choice(ganadores)
        else:
            jugador_id_ganador = ganadores[0]
        
        # Encontrar el índice del jugador ganador
        for i, jugador in enumerate(self.jugadores):
            if jugador.id == jugador_id_ganador:
                self.turno_actual = i
                jugador.es_su_turno = True
            else:
                jugador.es_su_turno = False
        
        # Terminar fase de inicio
        self.esperando_dados_inicio = False
    
    def obtener_dados_inicio(self) -> Dict[str, int]:
        """Retorna el diccionario de dados de inicio."""
        return self.dados_inicio.copy()
    
    def todos_lanzaron_inicio(self) -> bool:
        """Verifica si todos los jugadores lanzaron el dado de inicio."""
        return len(self.dados_inicio) == len(self.jugadores)

    def es_par(self, dados: tuple) -> bool:
        """Verifica si los dados son pares."""
        return dados[0] == dados[1]

    def obtener_fichas_disponibles(self, jugador: Jugador) -> List[Dict]:
        """Retorna información de fichas que pueden moverse."""
        fichas_info = []
        for ficha in jugador.fichas:
            info = {
                "id": ficha.id,
                "estado": ficha.estado.value,
                "posicion": ficha.posicion,
                "puede_mover": not ficha.esta_en_meta()
            }
            
            if ficha.esta_en_carcel():
                info["descripcion"] = "🔒 En cárcel (necesita par para salir)"
                info["puede_mover"] = False
            elif ficha.esta_en_meta():
                info["descripcion"] = "🏁 En la meta"
                info["puede_mover"] = False
            elif ficha.estado == EstadoFicha.PASILLO_FINAL:
                faltantes = 8 - ficha.posicion_pasillo
                info["descripcion"] = f"🏃 Pasillo final - Faltan {faltantes} casillas para meta"
                info["posicion_pasillo"] = ficha.posicion_pasillo
                info["puede_mover"] = True
            else:
                info["descripcion"] = f"🎲 En posición {ficha.posicion}"
                info["puede_mover"] = True
            
            fichas_info.append(info)
        
        return fichas_info

    def procesar_turno_dividido(self, jugador: Jugador, dados: tuple,
                                movimientos: List[Dict]) -> Dict:
        """
        Procesa turno con dados divididos.
        movimientos = [{"id_ficha": 0, "valor_dado": 5}, {"id_ficha": 1, "valor_dado": 6}]
        o [{"id_ficha": 0, "valor_dado": 11}]
        """
        with self.lock:
            if not jugador.es_su_turno:
                return {"error": "No es tu turno"}

            resultado = {
                "dados": dados,
                "es_par": self.es_par(dados),
                "movimientos_realizados": [],
                "fichas_capturadas": [],
                "cambio_turno": False,
                "tres_pares": False
            }

            # Verificar 3 pares consecutivos
            if self.es_par(dados):
                jugador.incrementar_pares()
                if jugador.tiene_tres_pares():
                    self._penalizar_tres_pares(jugador)
                    resultado["tres_pares"] = True
                    resultado["accion"] = "penalizacion_tres_pares"
                    self._cambiar_turno()
                    resultado["cambio_turno"] = True
                    return resultado
            else:
                jugador.resetear_pares()

            # Validar que los valores de dados sumen correctamente
            valores_usados = [m["valor_dado"] for m in movimientos]
            suma_total = sum(valores_usados)

            if suma_total != dados[0] + dados[1]:
                return {"error": f"Los valores no suman {dados[0] + dados[1]}"}

            # Validar que no se use un valor mayor que cualquier dado individual
            # a menos que sea la suma completa
            if len(movimientos) > 1:
                for valor in valores_usados:
                    if valor not in dados:
                        return {"error": f"Valor {valor} no coincide con ningún dado"}

            # Ejecutar movimientos
            for mov in movimientos:
                id_ficha = mov["id_ficha"]
                valor = mov["valor_dado"]

                # Intentar sacar de cárcel si es necesario
                ficha = jugador.fichas[id_ficha]
                if ficha.esta_en_carcel():
                    if self.es_par(dados) and valor == dados[0]:
                        exito = self._sacar_ficha_carcel(jugador, id_ficha)
                        if exito:
                            resultado["movimientos_realizados"].append({
                                "id_ficha": id_ficha,
                                "accion": "sacar_carcel"
                            })
                    else:
                        return {"error": f"Ficha {id_ficha} está en cárcel, necesitas par para salir"}
                else:
                    # Mover ficha normal
                    if not jugador.puede_mover(id_ficha, valor):
                        return {"error": f"No puedes mover la ficha {id_ficha}"}

                    capturadas = self._mover_ficha(jugador, id_ficha, valor)
                    resultado["movimientos_realizados"].append({
                        "id_ficha": id_ficha,
                        "casillas": valor,
                        "capturadas": len(capturadas)
                    })
                    resultado["fichas_capturadas"].extend([f.to_dict() for f in capturadas])

            # Verificar victoria
            if jugador.todas_fichas_en_meta():
                self.ganador = jugador
                resultado["ganador"] = jugador.nombre

            # Cambiar turno si no es par
            if not self.es_par(dados):
                self._cambiar_turno()
                resultado["cambio_turno"] = True

            return resultado

    def procesar_turno(self, jugador: Jugador, dados: tuple, id_ficha: Optional[int] = None) -> Dict:
        """Procesa un turno completo del jugador (modo clásico: suma de dados)."""
        with self.lock:
            if not jugador.es_su_turno:
                return {"error": "No es tu turno"}
            
            # Marcar que lanzó los dados (se validará antes en procesar_roll)
            jugador.marcar_lanzamiento()
            
            resultado = {
                "dados": dados,
                "es_par": self.es_par(dados),
                "accion": None,
                "fichas_capturadas": [],
                "cambio_turno": False,
                "tres_pares": False,
                "todas_en_carcel": False,
                "intentos_restantes": 0
            }
            
            suma_dados = dados[0] + dados[1]
            todas_en_carcel = all(f.esta_en_carcel() for f in jugador.fichas)
            resultado["todas_en_carcel"] = todas_en_carcel
            
            # TODAS LAS FICHAS EN CÁRCEL: 3 oportunidades para sacar fichas con pares
            if todas_en_carcel:
                jugador.incrementar_intento_carcel()
                resultado["intentos_restantes"] = jugador.max_intentos_carcel - jugador.intentos_carcel
                
                if not self.es_par(dados):
                    # No sacó par
                    if jugador.agotar_intentos_carcel():
                        # Se agotaron las 3 oportunidades
                        resultado["accion"] = "intentos_agotados"
                        resultado["mensaje"] = f"No sacaste par en 3 intentos. Turno perdido."
                        jugador.resetear_intentos_carcel()
                        self._cambiar_turno()
                        resultado["cambio_turno"] = True
                        return resultado
                    else:
                        # Aún tiene oportunidades
                        resultado["accion"] = "sin_par_carcel"
                        resultado["mensaje"] = f"No sacaste par. Te quedan {resultado['intentos_restantes']} intentos."
                        return resultado
                else:
                    # Sacó par - debe sacar ficha
                    jugador.resetear_intentos_carcel()
                    jugador.incrementar_pares()  # Contar este par para futuros lanzamientos
                    
                    if id_ficha is not None:
                        # Intentar sacar la ficha especificada
                        ficha = jugador.fichas[id_ficha]
                        if not ficha.esta_en_carcel():
                            return {"error": f"La ficha {id_ficha} no está en la cárcel."}
                        
                        exito = self._sacar_ficha_carcel(jugador, id_ficha)
                        if exito:
                            resultado["accion"] = "sacar_carcel"
                            resultado["mensaje"] = "Ficha sacada. Puedes lanzar de nuevo."
                            # Con par puede tirar de nuevo
                            jugador.permitir_lanzar_de_nuevo()
                            return resultado
                    else:
                        # Esperar que especifique la ficha
                        resultado["accion"] = "par_sacar_carcel"
                        resultado["mensaje"] = "¡Sacaste par! Ahora saca una ficha de la cárcel."
                        return resultado
            
            # REGLA DE 3 PARES CONSECUTIVOS: Permite sacar una ficha del juego
            # (Solo cuenta si NO es primer turno, ya que el primer turno ya lo maneja arriba)
            if self.es_par(dados):
                jugador.incrementar_pares()
                if jugador.tiene_tres_pares():
                    resultado["tres_pares"] = True
                    resultado["accion"] = "tres_pares_sacar_ficha"
                    resultado["mensaje"] = "¡3 pares consecutivos! Elige una ficha para sacar del juego."
                    self.jugador_puede_sacar_ficha = jugador
                    jugador.resetear_pares()
                    # No cambiar turno, esperar que elija ficha
                    return resultado
            else:
                jugador.resetear_pares()
            
            # Intentar sacar de cárcel con pares (para caso en que no todas estén en cárcel)
            if self.es_par(dados) and jugador.puede_sacar_de_carcel(dados):
                if id_ficha is not None:
                    ficha = jugador.fichas[id_ficha]
                    if not ficha.esta_en_carcel():
                        return {"error": f"La ficha {id_ficha} no está en la cárcel. Fichas en cárcel: {[f.id for f in jugador.fichas if f.esta_en_carcel()]}"}
                    
                    exito = self._sacar_ficha_carcel(jugador, id_ficha)
                    if exito:
                        resultado["accion"] = "sacar_carcel"
                        # Con par puede tirar de nuevo, no cambiar turno
                        jugador.permitir_lanzar_de_nuevo()
                        return resultado
                else:
                    # Sacó par pero no especificó ficha, esperar movimiento
                    return resultado
            
            # Mover ficha existente
            if id_ficha is not None:
                ficha = jugador.fichas[id_ficha]
                
                if ficha.esta_en_carcel():
                    return {"error": f"La ficha {id_ficha} está en la cárcel. Necesitas sacar PAR para liberarla."}
                
                if not jugador.puede_mover(id_ficha, suma_dados):
                    return {"error": f"No puedes mover la ficha {id_ficha}. Intenta con otra ficha."}
                
                # Verificar si el movimiento es válido (no se pasa de la meta)
                if ficha.estado == EstadoFicha.PASILLO_FINAL:
                    nueva_pos = ficha.posicion_pasillo + suma_dados
                    if nueva_pos > 8:
                        return {"error": f"No puedes mover {suma_dados} casillas. Necesitas caer EXACTO en la meta (te faltan {8 - ficha.posicion_pasillo})."}
                elif ficha.casillas_recorridas + suma_dados > 76:  # 68 tablero + 8 pasillo
                    casillas_faltantes = 76 - ficha.casillas_recorridas
                    return {"error": f"No puedes mover {suma_dados} casillas. Solo te faltan {casillas_faltantes} para llegar EXACTO a la meta."}
                
                capturadas = self._mover_ficha(jugador, id_ficha, suma_dados)
                
                # Verificar si entró al pasillo
                if ficha.estado == EstadoFicha.PASILLO_FINAL and ficha.posicion_pasillo < 8:
                    resultado["accion"] = "entro_pasillo"
                    resultado["mensaje"] = f"¡Entraste al pasillo final! Te faltan {8 - ficha.posicion_pasillo} casillas para la meta"
                elif ficha.esta_en_meta():
                    resultado["accion"] = "llego_meta"
                    resultado["mensaje"] = f"¡Ficha {id_ficha} llegó a la META!"
                else:
                    resultado["accion"] = "mover"
                
                resultado["fichas_capturadas"] = [f.to_dict() for f in capturadas]
                
                # Verificar victoria
                if jugador.todas_fichas_en_meta():
                    self.ganador = jugador
                    resultado["ganador"] = jugador.nombre
                
                # Si es par, puede lanzar de nuevo
                if self.es_par(dados):
                    jugador.permitir_lanzar_de_nuevo()
                else:
                    # Si no es par, cambiar turno
                    self._cambiar_turno()
                    resultado["cambio_turno"] = True
            else:
                # No especificó ficha
                fichas_fuera = [f for f in jugador.fichas if not f.esta_en_carcel() and not f.esta_en_meta()]
                
                if not fichas_fuera:
                    resultado["accion"] = "sin_movimiento"
                    if not self.es_par(dados):
                        self._cambiar_turno()
                        resultado["cambio_turno"] = True
                else:
                    resultado["accion"] = "esperando_movimiento"
            
            return resultado

    def _sacar_ficha_carcel(self, jugador: Jugador, id_ficha: int) -> bool:
        """Saca una ficha de la cárcel a su casilla de salida."""
        ficha = jugador.fichas[id_ficha]
        if not ficha.esta_en_carcel():
            return False

        casilla_salida = jugador.casilla_salida
        ficha.mover_a_tablero(casilla_salida)
        self.tablero.agregar_ficha(casilla_salida, ficha)
        return True

    def _mover_ficha(self, jugador: Jugador, id_ficha: int, casillas: int) -> List:
        """Mueve una ficha y procesa capturas."""
        ficha = jugador.fichas[id_ficha]
        posicion_anterior = ficha.posicion
        
        # Si está en pasillo final
        if ficha.estado == EstadoFicha.PASILLO_FINAL:
            nueva_pos_pasillo = ficha.posicion_pasillo + casillas
            
            if nueva_pos_pasillo == 8:
                # Llega exacto a la meta
                ficha.estado = EstadoFicha.META
                ficha.posicion_pasillo = 8
                return []
            elif nueva_pos_pasillo > 8:
                # Se pasa de la meta, NO puede mover
                return []
            else:
                # Movimiento válido en pasillo
                ficha.posicion_pasillo = nueva_pos_pasillo
                return []
        
        # Remover de posición anterior si está en tablero
        if posicion_anterior is not None:
            self.tablero.remover_ficha(posicion_anterior, ficha)
        
        # Verificar si debe entrar al pasillo final
        casillas_totales = ficha.casillas_recorridas + casillas
        
        if casillas_totales >= 68:
            # Entra al pasillo final
            casillas_en_pasillo = casillas_totales - 68
            
            if casillas_en_pasillo == 8:
                # Llega exacto a la meta
                ficha.entrar_pasillo()
                ficha.posicion_pasillo = 8
                ficha.estado = EstadoFicha.META
                return []
            elif casillas_en_pasillo > 8:
                # Se pasaría de la meta, NO puede mover
                # Restaurar posición
                if posicion_anterior is not None:
                    self.tablero.agregar_ficha(posicion_anterior, ficha)
                return []
            else:
                # Entra al pasillo sin llegar a meta
                ficha.entrar_pasillo()
                ficha.posicion_pasillo = casillas_en_pasillo
                ficha.casillas_recorridas = casillas_totales
                return []
        
        # Movimiento normal en el tablero
        nueva_posicion = (posicion_anterior + casillas) % 68
        es_seguro = self.tablero.es_seguro(nueva_posicion)
        
        ficha.mover(casillas, es_seguro)
        
        # Agregar a nueva posición
        if ficha.posicion is not None:
            # ✅ PRIMERO verificar capturas (ANTES de agregar la ficha)
            capturadas = []
            if not es_seguro:
                capturadas = self.tablero.verificar_captura(ficha.posicion, ficha)
                for capturada in capturadas:
                    capturada.capturar()
                    self.tablero.remover_ficha(ficha.posicion, capturada)
            
            # Luego agregar la ficha que se movió
            self.tablero.agregar_ficha(ficha.posicion, ficha)
            
            return capturadas
        
        return []

    def sacar_ficha_del_juego(self, jugador: Jugador, id_ficha: int) -> Dict:
        """Saca una ficha del juego (la manda directo a la meta) por obtener 3 pares.
        
        Args:
            jugador: Jugador que saca la ficha
            id_ficha: ID de la ficha a sacar del juego
            
        Returns:
            Dict con el resultado de la acción
        """
        with self.lock:
            if self.jugador_puede_sacar_ficha != jugador:
                return {"error": "No tienes derecho a sacar una ficha del juego"}
            
            if id_ficha < 0 or id_ficha >= 4:
                return {"error": "ID de ficha inválido"}
            
            ficha = jugador.fichas[id_ficha]
            
            # Solo se pueden sacar fichas que estén en juego (no en cárcel ni en meta)
            if ficha.esta_en_carcel():
                return {"error": "No puedes sacar una ficha que está en la cárcel"}
            
            if ficha.esta_en_meta():
                return {"error": "La ficha ya está en la meta"}
            
            # Remover del tablero si está ahí
            if ficha.posicion is not None:
                self.tablero.remover_ficha(ficha.posicion, ficha)
            
            # Mover directo a la meta
            ficha.estado = EstadoFicha.META
            ficha.posicion = None
            
            # Limpiar estado
            self.jugador_puede_sacar_ficha = None
            
            # Verificar victoria
            resultado = {
                "accion": "ficha_sacada_del_juego",
                "mensaje": f"¡Ficha {id_ficha} sacada del juego y enviada a la meta!",
                "id_ficha": id_ficha
            }
            
            if jugador.todas_fichas_en_meta():
                self.ganador = jugador
                resultado["ganador"] = jugador.nombre
            
            # Cambiar turno después de sacar la ficha
            self._cambiar_turno()
            resultado["cambio_turno"] = True
            
            return resultado
    
    def _penalizar_tres_pares(self, jugador: Jugador):
        """OBSOLETO: Ahora 3 pares permiten sacar una ficha del juego."""
        # Mantener por compatibilidad pero ya no se usa
        jugador.resetear_pares()

    def _cambiar_turno(self):
        """Cambia al siguiente jugador."""
        self.jugadores[self.turno_actual].es_su_turno = False
        self.jugadores[self.turno_actual].resetear_lanzamiento()
        self.jugadores[self.turno_actual].resetear_intentos_carcel()
        self.turno_actual = (self.turno_actual + 1) % len(self.jugadores)
        self.jugadores[self.turno_actual].es_su_turno = True
        self.jugadores[self.turno_actual].resetear_lanzamiento()
        self.jugadores[self.turno_actual].resetear_intentos_carcel()

    def obtener_estado(self) -> dict:
        """Retorna el estado completo de la partida."""
        estado = {
            "id": self.id,
            "iniciada": self.iniciada,
            "turno_actual": self.turno_actual,
            "jugador_actual": self.jugadores[self.turno_actual].nombre if self.jugadores and not self.esperando_dados_inicio else None,
            "jugadores": [j.to_dict() for j in self.jugadores],
            "tablero": self.tablero.to_dict(),
            "ganador": self.ganador.nombre if self.ganador else None,
            "esperando_dados_inicio": self.esperando_dados_inicio
        }
        
        # Agregar información de dados de inicio si está en esa fase
        if self.esperando_dados_inicio:
            estado["dados_inicio"] = {}
            for j in self.jugadores:
                if j.id in self.dados_inicio:
                    estado["dados_inicio"][j.nombre] = self.dados_inicio[j.id]
        
        return estado

    def __repr__(self):
        return f"Partida({self.id}, {len(self.jugadores)} jugadores, {'en curso' if self.iniciada else 'esperando'})"

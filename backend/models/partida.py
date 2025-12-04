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

    def tiene_movimientos_validos(self, jugador: Jugador, dados: tuple) -> Dict:
        """Verifica si el jugador tiene algún movimiento válido con los dados.
        
        Returns:
            Dict con información sobre movimientos posibles:
            - tiene_movimientos: bool
            - fichas_movibles: List[int] IDs de fichas que pueden moverse
            - puede_dividir: bool - Si puede dividir los dados
            - opciones_division: List - Opciones para dividir dados
        """
        es_par = self.es_par(dados)
        suma = dados[0] + dados[1]
        
        # Verificar si puede sacar de cárcel
        if es_par and jugador.tiene_fichas_en_carcel():
            fichas_en_carcel = [i for i, f in enumerate(jugador.fichas) if f.esta_en_carcel()]
            return {
                "tiene_movimientos": True,
                "fichas_movibles": fichas_en_carcel,
                "puede_dividir": False,
                "razon": "Debes sacar una ficha de la cárcel con el par"
            }
        
        # Fichas fuera de la cárcel
        fichas_fuera = [(i, f) for i, f in enumerate(jugador.fichas) 
                       if not f.esta_en_carcel() and not f.esta_en_meta()]
        
        if not fichas_fuera:
            return {
                "tiene_movimientos": False,
                "fichas_movibles": [],
                "puede_dividir": False,
                "razon": "No hay fichas disponibles para mover"
            }
        
        # Verificar movimientos con suma completa
        fichas_movibles_suma = [i for i, f in fichas_fuera if jugador.puede_mover(i, suma)]
        
        # Verificar movimientos con dados individuales (para división)
        fichas_movibles_dado1 = [i for i, f in fichas_fuera if jugador.puede_mover(i, dados[0])]
        fichas_movibles_dado2 = [i for i, f in fichas_fuera if jugador.puede_mover(i, dados[1])]
        
        # Determinar si puede dividir dados
        puede_dividir = False
        opciones_division = []
        
        # Puede dividir si:
        # 1. Los dados son diferentes Y
        # 2. Tiene al menos 2 fichas fuera de cárcel Y
        # 3. Al menos una ficha puede moverse con dado1 Y otra con dado2
        if dados[0] != dados[1] and len(fichas_fuera) >= 2:
            if fichas_movibles_dado1 and fichas_movibles_dado2:
                puede_dividir = True
                opciones_division = [
                    {"tipo": "suma", "valor": suma, "fichas": fichas_movibles_suma},
                    {"tipo": "dado1", "valor": dados[0], "fichas": fichas_movibles_dado1},
                    {"tipo": "dado2", "valor": dados[1], "fichas": fichas_movibles_dado2}
                ]
        
        # Combinar todas las fichas movibles
        fichas_movibles = list(set(fichas_movibles_suma + fichas_movibles_dado1 + fichas_movibles_dado2))
        
        return {
            "tiene_movimientos": len(fichas_movibles) > 0,
            "fichas_movibles": fichas_movibles,
            "puede_dividir": puede_dividir,
            "opciones_division": opciones_division,
            "fichas_movibles_suma": fichas_movibles_suma,
            "fichas_movibles_dado1": fichas_movibles_dado1,
            "fichas_movibles_dado2": fichas_movibles_dado2
        }

    def procesar_turno_dividido(self, jugador: Jugador, dados: tuple,
                                movimientos: List[Dict]) -> Dict:
        """
        Procesa turno con dados divididos.
        movimientos = [{"id_ficha": 0, "valor_dado": 5}, {"id_ficha": 1, "valor_dado": 6}]
        o [{"id_ficha": 0, "valor_dado": 11}]
        
        Reglas:
        - Si se divide, cada dado debe usarse con una ficha diferente
        - No se puede mover la misma ficha dos veces
        - Los valores deben corresponder a los dados lanzados
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
            fichas_usadas = [m["id_ficha"] for m in movimientos]
            suma_total = sum(valores_usados)

            if suma_total != dados[0] + dados[1]:
                return {"error": f"Los valores no suman {dados[0] + dados[1]}"}

            # VALIDACIÓN CRÍTICA: No se puede usar la misma ficha dos veces
            if len(fichas_usadas) != len(set(fichas_usadas)):
                return {"error": "No puedes mover la misma ficha dos veces en un turno"}

            # Validar que los valores correspondan a los dados
            if len(movimientos) > 1:
                # Si hay más de un movimiento, cada valor debe ser un dado individual
                for valor in valores_usados:
                    if valor not in dados:
                        return {"error": f"Valor {valor} no coincide con ningún dado"}
                
                # Verificar que cada dado se use exactamente una vez
                dados_list = list(dados)
                for valor in valores_usados:
                    if valor in dados_list:
                        dados_list.remove(valor)
                    else:
                        return {"error": f"El dado {valor} ya fue usado o no existe"}
            else:
                # Si es un solo movimiento, debe ser la suma completa
                if valores_usados[0] != suma_total:
                    return {"error": f"Para mover una sola ficha usa la suma completa ({suma_total})"}

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
                # Solo incrementar intentos si NO se está especificando una ficha (primera llamada desde ROLL)
                # Esto evita incrementar dos veces: una en ROLL y otra en MOVE
                if id_ficha is None:
                    jugador.incrementar_intento_carcel()
                
                resultado["intentos_restantes"] = jugador.max_intentos_carcel - jugador.intentos_carcel
                
                if not self.es_par(dados):
                    # No sacó par - solo validar si es la primera llamada (id_ficha es None)
                    if id_ficha is None:
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
                        # Esto no debería ocurrir (intentar mover sin par cuando todas están en cárcel)
                        return {"error": "No puedes mover fichas. Necesitas sacar PAR para sacar de la cárcel."}
                else:
                    # Sacó par - debe sacar ficha de la cárcel
                    if id_ficha is None:
                        # Primera llamada desde ROLL - informar que sacó par
                        jugador.resetear_intentos_carcel()
                        jugador.incrementar_pares()  # Contar este par para futuros lanzamientos
                        resultado["accion"] = "par_sacar_carcel"
                        resultado["puede_sacar_carcel"] = True
                        resultado["mensaje"] = "¡Sacaste par! Ahora saca una ficha de la cárcel con 'mover N'."
                        return resultado
                    else:
                        # Segunda llamada desde MOVE - ejecutar sacar ficha
                        ficha = jugador.fichas[id_ficha]
                        if not ficha.esta_en_carcel():
                            return {"error": f"La ficha {id_ficha} no está en la cárcel."}
                        
                        exito = self._sacar_ficha_carcel(jugador, id_ficha)
                        if exito:
                            resultado["accion"] = "sacar_carcel"
                            resultado["mensaje"] = "Ficha sacada de la cárcel. Puedes lanzar de nuevo."
                            # Con par puede tirar de nuevo
                            jugador.permitir_lanzar_de_nuevo()
                            return resultado
                        else:
                            return {"error": "No se pudo sacar la ficha de la cárcel."}
            
            # REGLA DE 3 PARES CONSECUTIVOS: Permite sacar una ficha del juego
            # (Solo cuenta si NO es primer turno, ya que el primer turno ya lo maneja arriba)
            if self.es_par(dados):
                jugador.incrementar_pares()
                if jugador.tiene_tres_pares():
                    resultado["tres_pares"] = True
                    resultado["accion"] = "tres_pares_premio"
                    jugador.resetear_pares()
                    
                    # Buscar la ficha más avanzada en el tablero (no en cárcel ni meta) para meterla a la meta
                    fichas_jugando = [f for f in jugador.fichas if f.estado == EstadoFicha.TABLERO or f.estado == EstadoFicha.PASILLO_FINAL]
                    
                    if fichas_jugando:
                        # Meter la más avanzada directo a la meta (PREMIO)
                        ficha_premiada = max(fichas_jugando, key=lambda f: f.casillas_recorridas)
                        
                        # Remover del tablero
                        if ficha_premiada.posicion is not None:
                            self.tablero.remover_ficha(ficha_premiada.posicion, ficha_premiada)
                        
                        # Meter a la meta
                        ficha_premiada.estado = EstadoFicha.META
                        ficha_premiada.posicion = None
                        ficha_premiada.posicion_pasillo = 8  # Llegó al final
                        
                        resultado["mensaje"] = f"¡3 pares consecutivos! Ficha {ficha_premiada.id} va directo a la meta."
                        resultado["ficha_premiada"] = ficha_premiada.id
                        print(f"🎉 {jugador.nombre} - 3 PARES: Ficha {ficha_premiada.id} va directo a la meta!")
                        
                        # Verificar victoria
                        if jugador.todas_fichas_en_meta():
                            self.ganador = jugador
                            resultado["ganador"] = jugador.nombre
                            print(f"🏆 ¡{jugador.nombre} ha ganado!")
                    else:
                        resultado["mensaje"] = "¡3 pares consecutivos! Pero no tienes fichas en juego para meter a la meta."
                    
                    # Cambiar turno después del premio
                    self._cambiar_turno()
                    resultado["cambio_turno"] = True
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
        
        # Calcular nueva posición
        nueva_posicion = (posicion_anterior + casillas) % 68
        entrada_pasillo = self.tablero.ENTRADAS_PASILLO.get(jugador.color)
        
        # Verificar si la ficha pasa por la entrada del pasillo
        # Necesitamos verificar todas las casillas del movimiento
        debe_entrar_pasillo = False
        casillas_en_pasillo = 0
        
        for i in range(1, casillas + 1):
            pos_intermedia = (posicion_anterior + i) % 68
            if pos_intermedia == entrada_pasillo:
                # La ficha pasa por su entrada al pasillo
                debe_entrar_pasillo = True
                casillas_en_pasillo = casillas - i
                break
        
        if debe_entrar_pasillo:
            # Entra al pasillo final
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
                ficha.casillas_recorridas += casillas
                return []
        
        # Movimiento normal en el tablero
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

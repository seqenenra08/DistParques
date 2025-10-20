"""
Módulo de Sincronización de Tiempo - Algoritmo de Berkeley
Sincroniza los relojes de todos los clientes conectados
"""

import threading
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SincronizadorBerkeley:
    """
    Implementa el algoritmo de Berkeley para sincronización de tiempo distribuido.
    
    El servidor actúa como coordinador que:
    1. Solicita el tiempo de todos los clientes
    2. Calcula el tiempo promedio
    3. Envía a cada cliente el ajuste necesario
    """
    
    def __init__(self, servidor):
        """
        Inicializa el sincronizador de tiempo.
        
        Args:
            servidor: Instancia del ServidorParques
        """
        self.servidor = servidor
        self.activo = False
        self.intervalo_sincronizacion = 30  # Sincronizar cada 30 segundos
        self.thread_sincronizacion = None
        
        # Almacenar tiempos de los clientes
        self.tiempos_clientes: Dict[str, datetime] = {}
        self.lock_tiempos = threading.Lock()
        
        logger.info("Sincronizador de Berkeley inicializado")
    
    def iniciar(self):
        """Inicia el proceso de sincronización periódica."""
        if self.activo:
            return
        
        self.activo = True
        self.thread_sincronizacion = threading.Thread(target=self._loop_sincronizacion)
        self.thread_sincronizacion.daemon = True
        self.thread_sincronizacion.start()
        
        logger.info("Sincronización de tiempo iniciada")
    
    def detener(self):
        """Detiene el proceso de sincronización."""
        self.activo = False
        if self.thread_sincronizacion:
            self.thread_sincronizacion.join(timeout=2.0)
        
        logger.info("Sincronización de tiempo detenida")
    
    def _loop_sincronizacion(self):
        """Loop principal de sincronización."""
        while self.activo:
            try:
                self.sincronizar_clientes()
            except Exception as e:
                logger.error(f"Error en sincronización: {e}")
            
            # Esperar antes de la próxima sincronización
            time.sleep(self.intervalo_sincronizacion)
    
    def solicitar_tiempo(self, id_jugador: str, cliente):
        """
        Solicita el tiempo actual a un cliente.
        
        Args:
            id_jugador (str): ID del jugador
            cliente: Handler del cliente
        """
        try:
            # Enviar solicitud de tiempo
            cliente.enviar_mensaje("TIME_REQUEST", {
                "timestamp_servidor": datetime.now().isoformat()
            })
            
            # El cliente debe responder con su tiempo local
            # (Se procesa en el método procesar_respuesta_tiempo)
        
        except Exception as e:
            logger.error(f"Error solicitando tiempo a {id_jugador}: {e}")
    
    def procesar_respuesta_tiempo(self, id_jugador: str, tiempo_cliente: str, rtt: float):
        """
        Procesa la respuesta de tiempo de un cliente.
        
        Args:
            id_jugador (str): ID del jugador
            tiempo_cliente (str): Tiempo del cliente en formato ISO
            rtt (float): Round-trip time en segundos
        """
        try:
            tiempo = datetime.fromisoformat(tiempo_cliente)
            
            # Compensar por el RTT (dividir entre 2)
            tiempo_ajustado = tiempo + timedelta(seconds=rtt/2)
            
            with self.lock_tiempos:
                self.tiempos_clientes[id_jugador] = tiempo_ajustado
            
            logger.debug(f"Tiempo recibido de {id_jugador}: {tiempo_ajustado}")
        
        except Exception as e:
            logger.error(f"Error procesando tiempo de {id_jugador}: {e}")
    
    def calcular_tiempo_promedio(self) -> datetime:
        """
        Calcula el tiempo promedio de todos los clientes.
        
        Returns:
            datetime: Tiempo promedio calculado
        """
        with self.lock_tiempos:
            if not self.tiempos_clientes:
                return datetime.now()
            
            # Incluir el tiempo del servidor
            tiempos = list(self.tiempos_clientes.values())
            tiempos.append(datetime.now())
            
            # Convertir a timestamps para promediar
            timestamps = [t.timestamp() for t in tiempos]
            timestamp_promedio = sum(timestamps) / len(timestamps)
            
            return datetime.fromtimestamp(timestamp_promedio)
    
    def calcular_ajustes(self, tiempo_promedio: datetime) -> Dict[str, float]:
        """
        Calcula el ajuste necesario para cada cliente.
        
        Args:
            tiempo_promedio (datetime): Tiempo promedio de referencia
            
        Returns:
            Dict[str, float]: Diccionario con ajustes en segundos por cliente
        """
        ajustes = {}
        
        with self.lock_tiempos:
            for id_jugador, tiempo_cliente in self.tiempos_clientes.items():
                # Calcular diferencia en segundos
                diferencia = (tiempo_promedio - tiempo_cliente).total_seconds()
                ajustes[id_jugador] = diferencia
        
        # Ajuste para el servidor (siempre 0 ya que es el coordinador)
        tiempo_servidor = datetime.now()
        ajuste_servidor = (tiempo_promedio - tiempo_servidor).total_seconds()
        
        logger.info(f"Ajuste del servidor: {ajuste_servidor:.3f}s")
        
        return ajustes
    
    def enviar_ajustes(self, ajustes: Dict[str, float]):
        """
        Envía los ajustes de tiempo a cada cliente.
        
        Args:
            ajustes (Dict[str, float]): Ajustes por cliente en segundos
        """
        for id_jugador, ajuste in ajustes.items():
            if id_jugador in self.servidor.clientes:
                cliente = self.servidor.clientes[id_jugador]
                
                try:
                    cliente.enviar_mensaje("TIME_SYNC", {
                        "ajuste_segundos": ajuste,
                        "timestamp_servidor": datetime.now().isoformat(),
                        "mensaje": f"Ajustar reloj en {ajuste:.3f} segundos"
                    })
                    
                    logger.debug(f"Ajuste enviado a {id_jugador}: {ajuste:.3f}s")
                
                except Exception as e:
                    logger.error(f"Error enviando ajuste a {id_jugador}: {e}")
    
    def sincronizar_clientes(self):
        """
        Ejecuta un ciclo completo de sincronización.
        
        Pasos del algoritmo de Berkeley:
        1. Solicitar tiempo a todos los clientes
        2. Esperar respuestas
        3. Calcular tiempo promedio
        4. Calcular ajustes
        5. Enviar ajustes a clientes
        """
        if not self.servidor.clientes:
            return
        
        logger.info("Iniciando sincronización de tiempo...")
        
        # Paso 1: Limpiar tiempos anteriores
        with self.lock_tiempos:
            self.tiempos_clientes.clear()
        
        # Paso 2: Solicitar tiempo a todos los clientes
        for id_jugador, cliente in list(self.servidor.clientes.items()):
            self.solicitar_tiempo(id_jugador, cliente)
        
        # Paso 3: Esperar respuestas (dar tiempo para que respondan)
        time.sleep(2.0)
        
        # Paso 4: Calcular tiempo promedio
        tiempo_promedio = self.calcular_tiempo_promedio()
        logger.info(f"Tiempo promedio calculado: {tiempo_promedio}")
        
        # Paso 5: Calcular ajustes para cada cliente
        ajustes = self.calcular_ajustes(tiempo_promedio)
        
        # Paso 6: Enviar ajustes a los clientes
        self.enviar_ajustes(ajustes)
        
        logger.info("Sincronización de tiempo completada")
    
    def obtener_tiempo_sincronizado(self) -> datetime:
        """
        Obtiene el tiempo actual sincronizado.
        
        Returns:
            datetime: Tiempo sincronizado actual
        """
        # En el servidor, el tiempo sincronizado es el tiempo promedio
        return self.calcular_tiempo_promedio()


class RelojSincronizado:
    """
    Reloj local que mantiene un offset con respecto al tiempo del sistema.
    Se usa en los clientes para mantener el tiempo sincronizado.
    """
    
    def __init__(self):
        """Inicializa el reloj sincronizado."""
        self.offset = timedelta(seconds=0)
        self.lock = threading.Lock()
        self.ultima_sincronizacion = None
    
    def ajustar(self, ajuste_segundos: float):
        """
        Ajusta el reloj local.
        
        Args:
            ajuste_segundos (float): Ajuste en segundos
        """
        with self.lock:
            self.offset += timedelta(seconds=ajuste_segundos)
            self.ultima_sincronizacion = datetime.now()
            
        logger.info(f"Reloj ajustado en {ajuste_segundos:.3f}s. Offset total: {self.offset.total_seconds():.3f}s")
    
    def obtener_tiempo(self) -> datetime:
        """
        Obtiene el tiempo sincronizado actual.
        
        Returns:
            datetime: Tiempo actual con el offset aplicado
        """
        with self.lock:
            return datetime.now() + self.offset
    
    def obtener_offset(self) -> float:
        """
        Obtiene el offset actual en segundos.
        
        Returns:
            float: Offset en segundos
        """
        with self.lock:
            return self.offset.total_seconds()
    
    def tiempo_desde_ultima_sincronizacion(self) -> Optional[float]:
        """
        Calcula cuánto tiempo ha pasado desde la última sincronización.
        
        Returns:
            Optional[float]: Segundos desde última sincronización o None
        """
        with self.lock:
            if self.ultima_sincronizacion is None:
                return None
            
            return (datetime.now() - self.ultima_sincronizacion).total_seconds()


# Función auxiliar para medir RTT (Round-Trip Time)
def medir_rtt(cliente) -> float:
    """
    Mide el tiempo de ida y vuelta a un cliente.
    
    Args:
        cliente: Handler del cliente
        
    Returns:
        float: RTT en segundos
    """
    inicio = time.time()
    
    try:
        # Enviar ping
        cliente.enviar_mensaje("PING", {"timestamp": inicio})
        
        # Aquí debería esperar el PONG del cliente
        # Por simplicidad, retornamos un valor estimado
        # En producción, esto debería ser asíncrono
        
        return 0.05  # 50ms estimado
    
    except Exception as e:
        logger.error(f"Error midiendo RTT: {e}")
        return 0.1  # 100ms por defecto


if __name__ == "__main__":
    # Test del sincronizador
    print("Módulo de Sincronización de Tiempo - Algoritmo de Berkeley")
    print("Este módulo debe ser importado por el servidor.")

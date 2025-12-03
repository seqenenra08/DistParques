#!/usr/bin/env python3
"""
Test de caso límite: verificar que el par se detecta incluso cuando
intentos_carcel == 2 (justo antes de agotar los intentos).
"""
import sys
sys.path.insert(0, '/home/seqenenra/Codes/DistParques/backend')

from models.partida import Partida
from models.ficha import EstadoFicha

def test_caso_limite():
    """Verifica el caso límite donde intentos_carcel = 2 y se saca par."""
    print("=" * 70)
    print("TEST CASO LÍMITE: Par exactamente en el último intento válido")
    print("=" * 70)
    
    # Crear partida
    partida = Partida("test_sala", max_jugadores=2)
    
    # Agregar jugadores
    jugador1 = partida.agregar_jugador("Jugador1", "player1", "red")
    jugador2 = partida.agregar_jugador("Jugador2", "player2", "blue")
    
    # Iniciar partida
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    jugador1.es_su_turno = True
    partida.turno_actual = 0
    
    print(f"\n🎮 Partida iniciada - Turno de: {jugador1.nombre}")
    print(f"📊 Estado inicial: todas las fichas en cárcel")
    print(f"   intentos_carcel: {jugador1.intentos_carcel}")
    print(f"   max_intentos_carcel: {jugador1.max_intentos_carcel}")
    
    # Simular manualmente que el jugador ya usó 2 intentos
    jugador1.intentos_carcel = 2
    print(f"\n⚡ Simulando que ya usó 2 intentos")
    print(f"   intentos_carcel: {jugador1.intentos_carcel}")
    print(f"   ¿Agotó intentos?: {jugador1.agotar_intentos_carcel()}")
    
    # INTENTO 3: Sacar PAR justo en el último intento
    print(f"\n--- ÚLTIMO INTENTO (PAR) ---")
    dados = (5, 5)
    print(f"🎲 Lanzando par: {dados}")
    print(f"   Estado ANTES de procesar:")
    print(f"      intentos_carcel: {jugador1.intentos_carcel}")
    print(f"      agotar_intentos_carcel(): {jugador1.agotar_intentos_carcel()}")
    
    resultado = partida.procesar_turno(jugador1, dados, None)
    
    print(f"\n   Estado DESPUÉS de procesar:")
    print(f"      intentos_carcel: {jugador1.intentos_carcel}")
    print(f"      Acción: {resultado.get('accion', 'N/A')}")
    print(f"      Mensaje: {resultado.get('mensaje', 'N/A')}")
    print(f"      ¿Cambió turno?: {resultado.get('cambio_turno', False)}")
    
    # VERIFICACIONES CRÍTICAS
    if resultado.get('accion') == 'intentos_agotados':
        print(f"\n❌ BUG: Se procesó como 'intentos_agotados' aunque sacó PAR")
        return False
    
    if resultado.get('cambio_turno'):
        print(f"\n❌ BUG: Cambió turno aunque sacó par")
        return False
    
    if resultado.get('accion') != 'par_sacar_carcel':
        print(f"\n❌ BUG: Acción incorrecta '{resultado.get('accion')}', esperaba 'par_sacar_carcel'")
        return False
    
    if jugador1.intentos_carcel != 0:
        print(f"\n❌ BUG: El contador no se reseteó (intentos_carcel = {jugador1.intentos_carcel})")
        return False
    
    print(f"\n✅ CORRECTO: Detectó el par y reseteó los intentos")
    
    # Sacar la ficha
    print(f"\n🎯 Sacando ficha 0...")
    resultado_sacar = partida.procesar_turno(jugador1, dados, id_ficha=0)
    
    ficha0 = jugador1.fichas[0]
    if ficha0.estado == EstadoFicha.TABLERO:
        print(f"   ✅ Ficha salió a posición {ficha0.posicion}")
        return True
    else:
        print(f"   ❌ ERROR: Ficha no salió")
        return False

def test_realmente_agotar_intentos():
    """Verifica que SÍ se agoten los intentos cuando NO saca par en el 3er intento."""
    print("\n\n" + "=" * 70)
    print("TEST: Verificar que SÍ se agoten intentos cuando NO saca par")
    print("=" * 70)
    
    # Crear partida
    partida = Partida("test_sala2", max_jugadores=2)
    
    # Agregar jugadores
    jugador1 = partida.agregar_jugador("Jugador1", "player1", "red")
    jugador2 = partida.agregar_jugador("Jugador2", "player2", "blue")
    
    # Iniciar partida
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    jugador1.es_su_turno = True
    partida.turno_actual = 0
    
    print(f"\n🎮 Partida iniciada - Turno de: {jugador1.nombre}")
    
    # Simular 2 intentos previos
    jugador1.intentos_carcel = 2
    print(f"⚡ Simulando 2 intentos previos")
    print(f"   intentos_carcel: {jugador1.intentos_carcel}")
    
    # INTENTO 3: NO sacar par
    print(f"\n--- ÚLTIMO INTENTO (NO PAR) ---")
    dados = (3, 5)
    print(f"🎲 Lanzando: {dados} (NO es par)")
    
    resultado = partida.procesar_turno(jugador1, dados, None)
    
    print(f"\n   Acción: {resultado.get('accion', 'N/A')}")
    print(f"   Mensaje: {resultado.get('mensaje', 'N/A')}")
    print(f"   ¿Cambió turno?: {resultado.get('cambio_turno', False)}")
    print(f"   intentos_carcel: {jugador1.intentos_carcel}")
    
    # VERIFICACIONES
    if resultado.get('accion') != 'intentos_agotados':
        print(f"\n❌ ERROR: Debería haber agotado intentos")
        return False
    
    if not resultado.get('cambio_turno'):
        print(f"\n❌ ERROR: Debería haber cambiado de turno")
        return False
    
    if jugador1.intentos_carcel != 0:
        print(f"\n❌ ERROR: Los intentos deberían resetearse después de perder el turno")
        return False
    
    print(f"\n✅ CORRECTO: Se agotaron los intentos y cambió de turno")
    return True

if __name__ == "__main__":
    print("\n🧪 TESTS DE CASOS LÍMITE\n")
    
    test1 = test_caso_limite()
    test2 = test_realmente_agotar_intentos()
    
    print("\n\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"Test 1 (Par en último intento): {'✅ EXITOSO' if test1 else '❌ FALLIDO'}")
    print(f"Test 2 (Agotar intentos sin par): {'✅ EXITOSO' if test2 else '❌ FALLIDO'}")
    print(f"\n{'✅ TODOS LOS TESTS PASARON' if test1 and test2 else '❌ ALGUNOS TESTS FALLARON'}")
    print("=" * 70)

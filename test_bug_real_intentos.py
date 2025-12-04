"""
Test para bug reportado:
Cuando jugador 1 saca par para salir de la cárcel, 
al cambiar turno el jugador 2 NO puede lanzar los dados en el frontend.
Simulamos el flujo completo del servidor.
"""

from backend.models.partida import Partida

def test_bug_real_intentos():
    """
    Escenario real:
    - Jugador 1 y 2 tienen todas las fichas en cárcel
    - Jugador 1 lanza ROLL -> saca par (6,6)
    - Jugador 1 hace MOVE -> saca ficha
    - Jugador 1 lanza ROLL de nuevo (por el par) -> saca no-par (3,5)
    - Jugador 1 hace MOVE -> mueve ficha
    - Cambia turno a Jugador 2
    - Jugador 2 intenta ROLL -> ¿puede lanzar?
    """
    partida = Partida("test-bug", max_jugadores=2)
    jugador1 = partida.agregar_jugador("Jugador1", "j1", "red")
    jugador2 = partida.agregar_jugador("Jugador2", "j2", "blue")
    partida.iniciar_partida()
    
    # Saltar fase de dados de inicio
    partida.esperando_dados_inicio = False
    partida.turno_actual = 0
    jugador1.es_su_turno = True
    jugador2.es_su_turno = False
    
    print("\n=== ESCENARIO INICIAL ===")
    print(f"Turno: {jugador1.nombre} ({jugador1.color})")
    print(f"J1 todas en cárcel: {all(f.esta_en_carcel() for f in jugador1.fichas)}")
    print(f"J2 todas en cárcel: {all(f.esta_en_carcel() for f in jugador2.fichas)}")
    
    # ===== JUGADOR 1 - TURNO 1 =====
    print("\n=== JUGADOR 1: PRIMER LANZAMIENTO ===")
    print(f"Puede lanzar? {jugador1.puede_lanzar()}")
    
    # Simular ROLL (servidor marca lanzamiento solo si NO todas en cárcel, pero aquí sí están todas)
    dados1 = (6, 6)
    todas_en_carcel = all(f.esta_en_carcel() for f in jugador1.fichas)
    es_par = dados1[0] == dados1[1]
    
    print(f"Lanzó: {dados1} (PAR={es_par}, todas_carcel={todas_en_carcel})")
    
    # Si todas en cárcel, NO marcar lanzamiento en el servidor (línea 258 de servidor.py)
    # Solo procesar_turno maneja el flujo
    resultado = partida.procesar_turno(jugador1, dados1, None)
    print(f"Resultado: {resultado.get('accion')}")
    print(f"Puede sacar: {resultado.get('puede_sacar_carcel', False)}")
    print(f"J1 puede_lanzar después: {jugador1.puede_lanzar()}")
    
    # Simular MOVE para sacar ficha
    print("\n--- J1: MOVE (sacar ficha) ---")
    resultado = partida.procesar_turno(jugador1, dados1, 0)
    print(f"Resultado: {resultado.get('accion')}")
    print(f"J1 puede_lanzar después: {jugador1.puede_lanzar()}")
    print(f"J1 puede_lanzar_de_nuevo: {jugador1.puede_lanzar_de_nuevo}")
    
    # ===== JUGADOR 1 - SEGUNDO LANZAMIENTO (por el par) =====
    print("\n=== JUGADOR 1: SEGUNDO LANZAMIENTO (por el par) ===")
    print(f"Puede lanzar? {jugador1.puede_lanzar()}")
    
    # Ahora NO todas están en cárcel (una salió)
    todas_en_carcel = all(f.esta_en_carcel() for f in jugador1.fichas)
    print(f"Todas en cárcel ahora? {todas_en_carcel}")
    
    # Simular ROLL - ahora SÍ marca lanzamiento (línea 264 del servidor)
    dados2 = (3, 5)
    es_par = dados2[0] == dados2[1]
    
    # En el servidor, línea 264: jugador.marcar_lanzamiento()
    jugador1.marcar_lanzamiento()
    print(f"Lanzó: {dados2} (PAR={es_par})")
    print(f"J1 ya_lanzo_dados: {jugador1.ya_lanzo_dados}")
    
    # Simular MOVE
    print("\n--- J1: MOVE (mover ficha) ---")
    resultado = partida.procesar_turno(jugador1, dados2, 0)
    print(f"Resultado: {resultado.get('accion')}")
    print(f"Cambió turno? {resultado.get('cambio_turno', False)}")
    print(f"Turno actual: {partida.turno_actual}")
    
    # ===== JUGADOR 2 - SU TURNO =====
    print("\n=== JUGADOR 2: SU TURNO ===")
    print(f"Es turno de: {partida.jugadores[partida.turno_actual].nombre}")
    print(f"J2 es_su_turno: {jugador2.es_su_turno}")
    print(f"J2 ya_lanzo_dados: {jugador2.ya_lanzo_dados}")
    print(f"J2 puede_lanzar_de_nuevo: {jugador2.puede_lanzar_de_nuevo}")
    print(f"J2 intentos_carcel: {jugador2.intentos_carcel}")
    print(f"J2 todas en cárcel: {all(f.esta_en_carcel() for f in jugador2.fichas)}")
    
    # VERIFICACIÓN CRÍTICA
    puede_lanzar = jugador2.puede_lanzar()
    print(f"\n🔍 J2 puede_lanzar(): {puede_lanzar}")
    
    if not puede_lanzar:
        print("❌ BUG ENCONTRADO: Jugador 2 NO puede lanzar!")
        print(f"   ya_lanzo_dados: {jugador2.ya_lanzo_dados}")
        print(f"   puede_lanzar_de_nuevo: {jugador2.puede_lanzar_de_nuevo}")
        print(f"   intentos_carcel: {jugador2.intentos_carcel}")
    else:
        print("✅ Jugador 2 SÍ puede lanzar")
    
    assert puede_lanzar, "❌ BUG: Jugador2 NO puede lanzar cuando debería poder (1er intento)"
    
    # Simular primer intento de J2
    print("\n=== JUGADOR 2: INTENTO 1 ===")
    dados = (2, 4)
    todas_en_carcel = all(f.esta_en_carcel() for f in jugador2.fichas)
    
    # NO marcar lanzamiento porque todas están en cárcel
    resultado = partida.procesar_turno(jugador2, dados, None)
    print(f"Lanzó: {dados} (PAR={dados[0] == dados[1]})")
    print(f"Resultado: {resultado.get('accion')}")
    print(f"Intentos restantes: {resultado.get('intentos_restantes', 0)}")
    print(f"J2 puede_lanzar después: {jugador2.puede_lanzar()}")
    
    assert jugador2.puede_lanzar(), "Jugador2 debería poder lanzar de nuevo (intento 2)"
    
    print("\n✅ TEST PASÓ: Jugador2 puede lanzar correctamente")

if __name__ == "__main__":
    try:
        test_bug_real_intentos()
        print("\n🎉 TODOS LOS TESTS PASARON")
    except AssertionError as e:
        print(f"\n💥 TEST FALLÓ: {e}")
        import traceback
        traceback.print_exc()

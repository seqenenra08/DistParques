"""
Test para bug reportado:
Cuando jugador 1 saca par para salir de la cárcel y luego termina su turno,
el jugador 2 no puede lanzar 3 veces si todas sus fichas están en la cárcel.
"""

from backend.models.partida import Partida
from backend.models.jugador import Jugador
from backend.models.ficha import EstadoFicha

def test_bug_intentos_carcel_dos_jugadores():
    """
    Escenario:
    - Jugador 1 (rojo) tiene todas sus fichas en cárcel
    - Jugador 2 (azul) tiene todas sus fichas en cárcel
    - Jugador 1 saca par y libera una ficha
    - Jugador 1 continúa su turno (puede volver a lanzar por el par)
    - Jugador 1 eventualmente no saca par y su turno termina
    - Jugador 2 debe poder lanzar hasta 3 veces para intentar sacar par
    """
    partida = Partida()
    jugador1 = Jugador("Jugador1", "rojo")
    jugador2 = Jugador("Jugador2", "azul")
    
    partida.agregar_jugador(jugador1)
    partida.agregar_jugador(jugador2)
    partida.iniciar()
    
    # Forzar turno de jugador1
    partida.turno_actual = 0
    jugador1.es_su_turno = True
    jugador2.es_su_turno = False
    
    print("\n=== INICIO DEL TEST ===")
    print(f"Turno de: {jugador1.nombre}")
    print(f"Jugador1 fichas en cárcel: {all(f.esta_en_carcel() for f in jugador1.fichas)}")
    print(f"Jugador2 fichas en cárcel: {all(f.esta_en_carcel() for f in jugador2.fichas)}")
    
    # --- Turno de Jugador 1 ---
    print("\n--- JUGADOR 1: Intento 1 ---")
    
    # Intento 1: Saca par (6, 6)
    dados_par = (6, 6)
    print(f"puede_lanzar antes: {jugador1.puede_lanzar()}")
    print(f"ya_lanzo_dados: {jugador1.ya_lanzo_dados}")
    print(f"puede_lanzar_de_nuevo: {jugador1.puede_lanzar_de_nuevo}")
    print(f"intentos_carcel: {jugador1.intentos_carcel}")
    
    # Simular procesar_roll (parte de todas en cárcel)
    jugador1.incrementar_intento_carcel()
    jugador1.resetear_intentos_carcel()  # Porque sacó par
    jugador1.incrementar_pares()
    jugador1.ya_lanzo_dados = True
    jugador1.puede_lanzar_de_nuevo = False  # Debe mover primero
    
    print(f"Jugador1 lanzó: {dados_par} (PAR)")
    print(f"Estado después del lanzamiento:")
    print(f"  ya_lanzo_dados: {jugador1.ya_lanzo_dados}")
    print(f"  puede_lanzar_de_nuevo: {jugador1.puede_lanzar_de_nuevo}")
    print(f"  intentos_carcel: {jugador1.intentos_carcel}")
    
    # Mover ficha 0 de la cárcel
    resultado = partida.procesar_turno(jugador1, dados_par, 0)
    print(f"Resultado mover: {resultado.get('accion')}")
    print(f"Estado después de mover:")
    print(f"  ya_lanzo_dados: {jugador1.ya_lanzo_dados}")
    print(f"  puede_lanzar_de_nuevo: {jugador1.puede_lanzar_de_nuevo}")
    print(f"  puede_lanzar ahora: {jugador1.puede_lanzar()}")
    
    # Verificar que puede lanzar de nuevo
    assert jugador1.puede_lanzar(), "Jugador1 debería poder lanzar de nuevo después de sacar par"
    
    # --- Segundo lanzamiento de Jugador 1 ---
    print("\n--- JUGADOR 1: Segundo lanzamiento (por el par) ---")
    
    # Lanzar de nuevo (esta vez sin par: 3, 5)
    dados_no_par = (3, 5)
    # Simular marcar_lanzamiento
    if jugador1.puede_lanzar_de_nuevo:
        jugador1.puede_lanzar_de_nuevo = False
    jugador1.ya_lanzo_dados = True
    jugador1.puede_lanzar_de_nuevo = False  # Por defecto
    
    print(f"Jugador1 lanzó: {dados_no_par} (NO PAR)")
    
    # Mover ficha con los nuevos dados
    resultado = partida.procesar_turno(jugador1, dados_no_par, 0)
    print(f"Resultado mover: {resultado.get('accion')}")
    print(f"¿Cambió turno?: {resultado.get('cambio_turno', False)}")
    
    # Verificar que cambió el turno
    assert resultado.get('cambio_turno', False), "El turno debería haber cambiado porque no sacó par"
    assert partida.turno_actual == 1, "Ahora debería ser el turno de Jugador2"
    
    # --- Turno de Jugador 2 ---
    print("\n--- JUGADOR 2: Su turno ---")
    print(f"Turno actual: {partida.turno_actual}")
    print(f"Es turno de: {partida.jugadores[partida.turno_actual].nombre}")
    print(f"Jugador2 estado:")
    print(f"  ya_lanzo_dados: {jugador2.ya_lanzo_dados}")
    print(f"  puede_lanzar_de_nuevo: {jugador2.puede_lanzar_de_nuevo}")
    print(f"  intentos_carcel: {jugador2.intentos_carcel}")
    print(f"  todas en cárcel: {all(f.esta_en_carcel() for f in jugador2.fichas)}")
    
    # Verificar que Jugador2 puede lanzar
    puede = jugador2.puede_lanzar()
    print(f"  puede_lanzar: {puede}")
    
    # AQUÍ ESTÁ EL BUG: puede_lanzar() debería retornar True
    assert puede, "❌ BUG: Jugador2 NO puede lanzar pero debería poder (1er intento)"
    
    # Intento 1: No saca par (2, 4)
    print("\n--- JUGADOR 2: Intento 1 ---")
    dados = (2, 4)
    jugador2.incrementar_intento_carcel()
    # No marcar ya_lanzo_dados porque puede reintentar
    print(f"Jugador2 lanzó: {dados} (NO PAR)")
    print(f"Intentos: {jugador2.intentos_carcel}/3")
    print(f"puede_lanzar después: {jugador2.puede_lanzar()}")
    
    assert jugador2.puede_lanzar(), "Jugador2 debería poder lanzar de nuevo (intento 2)"
    
    # Intento 2: No saca par (1, 3)
    print("\n--- JUGADOR 2: Intento 2 ---")
    dados = (1, 3)
    jugador2.incrementar_intento_carcel()
    print(f"Jugador2 lanzó: {dados} (NO PAR)")
    print(f"Intentos: {jugador2.intentos_carcel}/3")
    print(f"puede_lanzar después: {jugador2.puede_lanzar()}")
    
    assert jugador2.puede_lanzar(), "Jugador2 debería poder lanzar de nuevo (intento 3)"
    
    # Intento 3: No saca par (2, 5)
    print("\n--- JUGADOR 2: Intento 3 ---")
    dados = (2, 5)
    jugador2.incrementar_intento_carcel()
    jugador2.ya_lanzo_dados = True  # Último intento
    print(f"Jugador2 lanzó: {dados} (NO PAR)")
    print(f"Intentos: {jugador2.intentos_carcel}/3")
    print(f"¿Agotó intentos?: {jugador2.agotar_intentos_carcel()}")
    
    # Verificar que agotó los 3 intentos
    assert jugador2.agotar_intentos_carcel(), "Jugador2 debería haber agotado sus 3 intentos"
    
    print("\n✅ TEST PASÓ: Jugador2 pudo lanzar 3 veces correctamente")

if __name__ == "__main__":
    try:
        test_bug_intentos_carcel_dos_jugadores()
        print("\n🎉 TODOS LOS TESTS PASARON")
    except AssertionError as e:
        print(f"\n💥 TEST FALLÓ: {e}")
        import traceback
        traceback.print_exc()

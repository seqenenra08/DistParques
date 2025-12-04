"""
Test más completo que simula el flujo exacto del servidor
incluyendo broadcast_estado
"""

from backend.models.partida import Partida

def test_bug_flujo_completo():
    """
    Simula el flujo EXACTO:
    1. J1 y J2 tienen todas en cárcel
    2. J1 saca par -> libera ficha
    3. J1 lanza de nuevo -> no-par -> mueve
    4. Cambia turno -> J2 debe poder lanzar
    """
    partida = Partida("test", max_jugadores=2)
    j1 = partida.agregar_jugador("J1", "j1", "red")
    j2 = partida.agregar_jugador("J2", "j2", "blue")
    partida.iniciar_partida()
    
    # Saltar dados de inicio
    partida.esperando_dados_inicio = False
    partida.turno_actual = 0
    j1.es_su_turno = True
    j2.es_su_turno = False
    
    print("\n=== ESTADO INICIAL ===")
    print(f"Turno: J1")
    print(f"J1: ya_lanzo={j1.ya_lanzo_dados}, puede_lanzar_nuevo={j1.puede_lanzar_de_nuevo}, intentos={j1.intentos_carcel}")
    print(f"J2: ya_lanzo={j2.ya_lanzo_dados}, puede_lanzar_nuevo={j2.puede_lanzar_de_nuevo}, intentos={j2.intentos_carcel}")
    
    # ===== J1 ROLL 1 =====
    print("\n=== J1: ROLL (todas en cárcel) ===")
    if not j1.puede_lanzar():
        print("❌ ERROR: J1 NO puede lanzar!")
        return False
    
    dados = (6, 6)
    todas_en_carcel = all(f.esta_en_carcel() for f in j1.fichas)
    
    # Servidor NO marca lanzamiento si todas en cárcel (línea 250 servidor.py)
    resultado = partida.procesar_turno(j1, dados, None)
    
    print(f"Lanzó: {dados}")
    print(f"Resultado: {resultado.get('accion')}")
    print(f"J1 después: ya_lanzo={j1.ya_lanzo_dados}, puede_lanzar_nuevo={j1.puede_lanzar_de_nuevo}")
    
    # Estado del juego (lo que vería el frontend)
    estado = partida.obtener_estado()
    j1_estado = next(j for j in estado['jugadores'] if j['nombre'] == 'J1')
    print(f"Estado J1 en broadcast: ya_lanzo={j1_estado['ya_lanzo_dados']}, puede_lanzar_nuevo={j1_estado['puede_lanzar_de_nuevo']}")
    
    # ===== J1 MOVE (sacar ficha) =====
    print("\n=== J1: MOVE (sacar ficha 0) ===")
    resultado = partida.procesar_turno(j1, dados, 0)
    print(f"Resultado: {resultado.get('accion')}")
    print(f"J1 después: ya_lanzo={j1.ya_lanzo_dados}, puede_lanzar_nuevo={j1.puede_lanzar_de_nuevo}")
    print(f"J1 puede_lanzar: {j1.puede_lanzar()}")
    
    # ===== J1 ROLL 2 (por el par) =====
    print("\n=== J1: ROLL 2 (por el par) ===")
    if not j1.puede_lanzar():
        print("❌ ERROR: J1 NO puede lanzar de nuevo!")
        return False
    
    dados2 = (3, 5)
    todas_en_carcel = all(f.esta_en_carcel() for f in j1.fichas)
    
    # Ahora NO todas están en cárcel, servidor marca lanzamiento (línea 264)
    j1.marcar_lanzamiento()
    
    print(f"Lanzó: {dados2}")
    print(f"J1 después marcar: ya_lanzo={j1.ya_lanzo_dados}, puede_lanzar_nuevo={j1.puede_lanzar_de_nuevo}")
    
    # ===== J1 MOVE 2 =====
    print("\n=== J1: MOVE 2 (mover ficha 0) ===")
    resultado = partida.procesar_turno(j1, dados2, 0)
    print(f"Resultado: {resultado.get('accion')}")
    print(f"Cambió turno: {resultado.get('cambio_turno', False)}")
    
    if not resultado.get('cambio_turno', False):
        print("❌ ERROR: NO cambió el turno!")
        return False
    
    # ===== DESPUÉS DEL CAMBIO DE TURNO =====
    print("\n=== DESPUÉS DEL CAMBIO DE TURNO ===")
    print(f"Turno actual: {partida.turno_actual}")
    print(f"Jugador actual: {partida.jugadores[partida.turno_actual].nombre}")
    
    print(f"\nJ1 después cambio: ya_lanzo={j1.ya_lanzo_dados}, puede_lanzar_nuevo={j1.puede_lanzar_de_nuevo}, intentos={j1.intentos_carcel}")
    print(f"J2 después cambio: ya_lanzo={j2.ya_lanzo_dados}, puede_lanzar_nuevo={j2.puede_lanzar_de_nuevo}, intentos={j2.intentos_carcel}")
    
    # Estado broadcast
    estado = partida.obtener_estado()
    j1_estado = next(j for j in estado['jugadores'] if j['nombre'] == 'J1')
    j2_estado = next(j for j in estado['jugadores'] if j['nombre'] == 'J2')
    
    print(f"\nEstado J1 en broadcast:")
    print(f"  ya_lanzo: {j1_estado['ya_lanzo_dados']}")
    print(f"  puede_lanzar_nuevo: {j1_estado['puede_lanzar_de_nuevo']}")
    print(f"  intentos_carcel: {j1_estado['intentos_carcel']}")
    
    print(f"\nEstado J2 en broadcast:")
    print(f"  es_su_turno: {j2_estado['es_su_turno']}")
    print(f"  ya_lanzo: {j2_estado['ya_lanzo_dados']}")
    print(f"  puede_lanzar_nuevo: {j2_estado['puede_lanzar_de_nuevo']}")
    print(f"  intentos_carcel: {j2_estado['intentos_carcel']}")
    
    # ===== VERIFICACIÓN CRÍTICA =====
    print("\n=== VERIFICACIÓN ===")
    puede_lanzar_j2 = j2.puede_lanzar()
    print(f"J2 puede_lanzar(): {puede_lanzar_j2}")
    
    if not puede_lanzar_j2:
        print("\n❌ BUG CONFIRMADO!")
        print(f"J2 NO puede lanzar cuando debería poder.")
        print(f"Valores:")
        print(f"  ya_lanzo_dados: {j2.ya_lanzo_dados} (debería ser False)")
        print(f"  puede_lanzar_de_nuevo: {j2.puede_lanzar_de_nuevo} (debería ser False)")
        print(f"  todas_en_carcel: {all(f.esta_en_carcel() for f in j2.fichas)} (True)")
        print(f"  intentos_carcel: {j2.intentos_carcel} (debería ser 0)")
        return False
    
    print("\n✅ TEST PASÓ: J2 puede lanzar correctamente")
    
    # ===== J2 INTENTO 1 =====
    print("\n=== J2: INTENTO 1 ===")
    dados_j2 = (2, 4)
    resultado = partida.procesar_turno(j2, dados_j2, None)
    print(f"Lanzó: {dados_j2}")
    print(f"Resultado: {resultado.get('accion')}")
    print(f"Intentos restantes: {resultado.get('intentos_restantes', 0)}")
    print(f"J2 puede_lanzar después: {j2.puede_lanzar()}")
    
    if not j2.puede_lanzar():
        print("❌ ERROR: J2 NO puede lanzar intento 2!")
        return False
    
    print("\n✅ TODOS LOS TESTS PASARON")
    return True

if __name__ == "__main__":
    try:
        exito = test_bug_flujo_completo()
        if exito:
            print("\n🎉 TEST EXITOSO")
        else:
            print("\n💥 TEST FALLÓ")
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()

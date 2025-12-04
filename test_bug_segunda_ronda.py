"""Test para reproducir el bug de la segunda ronda donde no cambia el turno."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.partida import Partida
from models.jugador import Jugador

def test_segunda_ronda_sin_par():
    """Prueba que funciona correctamente en múltiples rondas."""
    print("\n" + "="*80)
    print("TEST: Segunda ronda sin par con todas las fichas en cárcel")
    print("="*80)
    
    # Crear partida con 2 jugadores
    partida = Partida("test-segunda-ronda", max_jugadores=2)
    jugador1 = partida.agregar_jugador("Jugador1", "j1", "rojo")
    jugador2 = partida.agregar_jugador("Jugador2", "j2", "azul")
    
    # Iniciar partida
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    
    # Establecer turno inicial en jugador 1
    partida.turno_actual = 0
    jugador1.es_su_turno = True
    jugador2.es_su_turno = False
    
    print(f"\n{'='*80}")
    print("PRIMERA RONDA - Jugador 1")
    print('='*80)
    
    # PRIMERA RONDA: Jugador 1 - 3 intentos sin par
    for intento in range(1, 4):
        print(f"\n   Intento {intento}/3 [J1]:")
        print(f"      Estado antes: intentos_carcel={jugador1.intentos_carcel}, puede_lanzar={jugador1.puede_lanzar()}")
        
        dados_sin_par = (1, 2)
        resultado = partida.procesar_turno(jugador1, dados_sin_par, None)
        
        print(f"      Dados: {dados_sin_par}")
        print(f"      Acción: {resultado.get('accion')}")
        print(f"      Intentos usados: {jugador1.intentos_carcel}")
        print(f"      Cambio turno: {resultado.get('cambio_turno', False)}")
        print(f"      Turno actual: Jugador {partida.turno_actual + 1}")
    
    assert partida.turno_actual == 1, "Debería haber cambiado a Jugador 2"
    assert jugador2.es_su_turno, "Jugador 2 debería tener el turno"
    print(f"\n   ✅ Turno cambió correctamente a Jugador 2")
    
    print(f"\n{'='*80}")
    print("PRIMERA RONDA - Jugador 2")
    print('='*80)
    
    # PRIMERA RONDA: Jugador 2 - 3 intentos sin par
    for intento in range(1, 4):
        print(f"\n   Intento {intento}/3 [J2]:")
        print(f"      Estado antes: intentos_carcel={jugador2.intentos_carcel}, puede_lanzar={jugador2.puede_lanzar()}")
        
        dados_sin_par = (2, 3)
        resultado = partida.procesar_turno(jugador2, dados_sin_par, None)
        
        print(f"      Dados: {dados_sin_par}")
        print(f"      Acción: {resultado.get('accion')}")
        print(f"      Intentos usados: {jugador2.intentos_carcel}")
        print(f"      Cambio turno: {resultado.get('cambio_turno', False)}")
        print(f"      Turno actual: Jugador {partida.turno_actual + 1}")
    
    assert partida.turno_actual == 0, "Debería haber vuelto a Jugador 1"
    assert jugador1.es_su_turno, "Jugador 1 debería tener el turno de nuevo"
    print(f"\n   ✅ Turno volvió correctamente a Jugador 1")
    
    print(f"\n{'='*80}")
    print("SEGUNDA RONDA - Jugador 1 (AQUÍ ESTÁ EL BUG)")
    print('='*80)
    
    # SEGUNDA RONDA: Jugador 1 - Verificar estado inicial
    print(f"\n   Estado inicial de Jugador 1:")
    print(f"      intentos_carcel: {jugador1.intentos_carcel}")
    print(f"      ya_lanzo_dados: {jugador1.ya_lanzo_dados}")
    print(f"      puede_lanzar_de_nuevo: {jugador1.puede_lanzar_de_nuevo}")
    print(f"      puede_lanzar(): {jugador1.puede_lanzar()}")
    print(f"      todas_en_carcel: {all(f.esta_en_carcel() for f in jugador1.fichas)}")
    
    assert jugador1.intentos_carcel == 0, "Los intentos deberían estar en 0"
    assert jugador1.puede_lanzar(), "Jugador 1 DEBERÍA poder lanzar"
    
    # SEGUNDA RONDA: Jugador 1 - 3 intentos sin par
    for intento in range(1, 4):
        print(f"\n   Intento {intento}/3 [J1 - SEGUNDA RONDA]:")
        print(f"      Estado antes: intentos_carcel={jugador1.intentos_carcel}, puede_lanzar={jugador1.puede_lanzar()}")
        
        dados_sin_par = (1, 3)
        resultado = partida.procesar_turno(jugador1, dados_sin_par, None)
        
        print(f"      Dados: {dados_sin_par}")
        print(f"      Acción: {resultado.get('accion')}")
        print(f"      Intentos usados: {jugador1.intentos_carcel}")
        print(f"      Cambio turno: {resultado.get('cambio_turno', False)}")
        print(f"      Turno actual: Jugador {partida.turno_actual + 1}")
        
        if intento < 3:
            assert not resultado.get('cambio_turno'), f"No debería cambiar turno en intento {intento}"
        else:
            assert resultado.get('cambio_turno'), "Debería cambiar turno en intento 3"
    
    assert partida.turno_actual == 1, "Debería haber cambiado a Jugador 2 de nuevo"
    assert jugador2.es_su_turno, "Jugador 2 debería tener el turno"
    print(f"\n   ✅ Turno cambió correctamente a Jugador 2 en la segunda ronda")
    
    print("\n" + "="*80)
    print("✅ TEST PASADO: La segunda ronda funciona correctamente")
    print("="*80)


if __name__ == "__main__":
    try:
        test_segunda_ronda_sin_par()
    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

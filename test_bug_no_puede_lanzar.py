"""Test para verificar que NO se puede lanzar después de agotar los 3 intentos."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.partida import Partida
from models.jugador import Jugador

def test_no_puede_lanzar_despues_agotar_intentos():
    """Prueba que el jugador NO puede lanzar después de agotar los 3 intentos."""
    print("\n" + "="*80)
    print("TEST: No puede lanzar después de agotar intentos")
    print("="*80)
    
    # Crear partida con 2 jugadores
    partida = Partida("test-no-lanzar", max_jugadores=2)
    jugador1 = partida.agregar_jugador("Jugador1", "j1", "rojo")
    jugador2 = partida.agregar_jugador("Jugador2", "j2", "azul")
    
    # Iniciar partida
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    
    # Establecer turno inicial en jugador 1
    partida.turno_actual = 0
    jugador1.es_su_turno = True
    jugador2.es_su_turno = False
    
    print(f"\n📍 Jugador 1 tiene el turno")
    print(f"   Todas en cárcel: {all(f.esta_en_carcel() for f in jugador1.fichas)}")
    print(f"   puede_lanzar(): {jugador1.puede_lanzar()}")
    
    # Simular 3 intentos sin sacar par
    for intento in range(1, 4):
        print(f"\n🎲 Intento {intento}/3:")
        print(f"   ANTES: intentos_carcel={jugador1.intentos_carcel}, ya_lanzo={jugador1.ya_lanzo_dados}, puede_lanzar={jugador1.puede_lanzar()}")
        
        # Verificar que PUEDE lanzar antes del intento
        assert jugador1.puede_lanzar(), f"Debería poder lanzar en intento {intento}"
        
        dados_sin_par = (1, 2)
        resultado = partida.procesar_turno(jugador1, dados_sin_par, None)
        
        print(f"   DESPUÉS: intentos_carcel={jugador1.intentos_carcel}, ya_lanzo={jugador1.ya_lanzo_dados}, puede_lanzar={jugador1.puede_lanzar()}")
        print(f"   Acción: {resultado.get('accion')}")
        print(f"   Cambio turno: {resultado.get('cambio_turno', False)}")
        
        if intento == 3:
            # Después del tercer intento, debe cambiar turno
            assert resultado.get('cambio_turno'), "Debería haber cambiado turno"
            assert not jugador1.es_su_turno, "Jugador 1 no debería tener el turno"
            assert jugador2.es_su_turno, "Jugador 2 debería tener el turno"
            print(f"   ✅ Turno cambió correctamente")
            
            # VERIFICACIÓN CRÍTICA: Jugador 1 NO debería poder lanzar más
            print(f"\n🔍 VERIFICACIÓN CRÍTICA:")
            print(f"   Jugador 1 - puede_lanzar(): {jugador1.puede_lanzar()}")
            print(f"   Jugador 1 - es_su_turno: {jugador1.es_su_turno}")
            print(f"   Jugador 1 - ya_lanzo_dados: {jugador1.ya_lanzo_dados}")
            print(f"   Jugador 1 - intentos_carcel: {jugador1.intentos_carcel}")
            
            # Jugador 1 NO debe poder lanzar porque ya no es su turno
            assert not jugador1.puede_lanzar(), "❌ Jugador 1 NO debería poder lanzar (ya no es su turno)"
            print(f"   ✅ Jugador 1 NO puede lanzar (correcto)")
    
    print("\n" + "="*80)
    print("✅ TEST PASADO: No se puede lanzar después de agotar intentos")
    print("="*80)


if __name__ == "__main__":
    try:
        test_no_puede_lanzar_despues_agotar_intentos()
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

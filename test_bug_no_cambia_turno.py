"""Test para reproducir el bug donde no cambia el turno cuando todas las fichas están en cárcel y no se saca par."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.partida import Partida
from models.jugador import Jugador

def test_cambio_turno_sin_par_todas_carcel():
    """Prueba que el turno cambia cuando no se saca par con todas las fichas en cárcel."""
    print("\n" + "="*80)
    print("TEST: Cambio de turno sin par con todas las fichas en cárcel")
    print("="*80)
    
    # Crear partida con 2 jugadores
    partida = Partida("test-turno", max_jugadores=2)
    jugador1 = partida.agregar_jugador("Jugador1", "j1", "rojo")
    jugador2 = partida.agregar_jugador("Jugador2", "j2", "azul")
    
    assert jugador1 is not None
    assert jugador2 is not None
    
    # Iniciar partida
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    
    # Establecer turno inicial en jugador 1
    partida.turno_actual = 0
    jugador1.es_su_turno = True
    jugador2.es_su_turno = False
    
    print(f"\n📍 Estado inicial:")
    print(f"   Turno actual: Jugador {partida.turno_actual + 1} ({partida.jugadores[partida.turno_actual].nombre})")
    print(f"   {jugador1.nombre} - es_su_turno: {jugador1.es_su_turno}")
    print(f"   {jugador2.nombre} - es_su_turno: {jugador2.es_su_turno}")
    
    # Verificar que todas las fichas de jugador1 están en cárcel
    todas_en_carcel = all(f.esta_en_carcel() for f in jugador1.fichas)
    print(f"\n🔒 Todas las fichas de {jugador1.nombre} en cárcel: {todas_en_carcel}")
    
    assert todas_en_carcel, "Las fichas deberían estar en cárcel inicialmente"
    
    # Simular 3 intentos sin sacar par
    print(f"\n🎲 Simulando 3 intentos sin sacar par:")
    
    for intento in range(1, 4):
        print(f"\n   Intento {intento}/3:")
        
        # Lanzar dados sin par
        dados_sin_par = (1, 2)
        print(f"      Dados: {dados_sin_par} - Es par: {partida.es_par(dados_sin_par)}")
        
        # Procesar turno (sin especificar ficha, solo lanzar dados)
        resultado = partida.procesar_turno(jugador1, dados_sin_par, None)
        
        print(f"      Acción: {resultado.get('accion')}")
        print(f"      Intentos usados: {jugador1.intentos_carcel}")
        print(f"      Cambio turno: {resultado.get('cambio_turno', False)}")
        print(f"      Turno actual después: Jugador {partida.turno_actual + 1} ({partida.jugadores[partida.turno_actual].nombre})")
        print(f"      {jugador1.nombre}.es_su_turno: {jugador1.es_su_turno}")
        print(f"      {jugador2.nombre}.es_su_turno: {jugador2.es_su_turno}")
        
        if intento < 3:
            # No debería cambiar turno en intentos 1 y 2
            assert resultado.get('accion') == 'sin_par_carcel', f"En intento {intento} debería poder reintentar"
            assert not resultado.get('cambio_turno'), f"No debería cambiar turno en intento {intento}"
            assert jugador1.es_su_turno, f"Jugador1 debería seguir con el turno en intento {intento}"
            assert not jugador2.es_su_turno, f"Jugador2 no debería tener el turno en intento {intento}"
            print(f"      ✅ Correcto: No cambió turno (puede reintentar)")
        else:
            # En el intento 3, debe cambiar turno
            assert resultado.get('accion') == 'intentos_agotados', "En intento 3 debería agotar intentos"
            assert resultado.get('cambio_turno'), "Debería cambiar turno en intento 3"
            assert not jugador1.es_su_turno, "Jugador1 NO debería tener el turno"
            assert jugador2.es_su_turno, "Jugador2 DEBERÍA tener el turno"
            assert partida.turno_actual == 1, "El turno actual debería ser 1 (Jugador2)"
            print(f"      ✅ Correcto: Cambió turno al Jugador 2")
    
    print(f"\n📍 Estado final:")
    print(f"   Turno actual: Jugador {partida.turno_actual + 1} ({partida.jugadores[partida.turno_actual].nombre})")
    print(f"   {jugador1.nombre} - es_su_turno: {jugador1.es_su_turno}")
    print(f"   {jugador2.nombre} - es_su_turno: {jugador2.es_su_turno}")
    
    print("\n" + "="*80)
    print("✅ TEST PASADO: El turno cambió correctamente")
    print("="*80)


if __name__ == "__main__":
    try:
        test_cambio_turno_sin_par_todas_carcel()
    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

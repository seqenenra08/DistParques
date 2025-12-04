"""
Test para verificar que las fichas entran correctamente al pasillo
después de completar 68 casillas.
"""
import sys
sys.path.append('./backend')

from models.partida import Partida
from models.ficha import EstadoFicha

def test_entrada_pasillo_rojo():
    """Test: Ficha roja entra al pasillo en la posición 29 después de 68 casillas."""
    print("\n🧪 TEST: Ficha roja debe entrar al pasillo en pos 29 tras 68 casillas")
    print("=" * 70)
    
    partida = Partida("test_pasillo", 2)
    j1 = partida.agregar_jugador("Rojo", "j1", "red")
    j2 = partida.agregar_jugador("Azul", "j2", "blue")
    partida.iniciar_partida()
    
    # Marcar que ambos lanzaron dados de inicio
    partida.dados_inicio = {"j1": 6, "j2": 3}
    partida._determinar_primer_turno()
    
    # Sacar ficha roja de la cárcel (sale en posición 39)
    ficha = j1.fichas[0]
    partida._sacar_ficha_carcel(j1, 0)
    print(f"✅ Ficha roja sale de cárcel en posición {ficha.posicion} (debe ser 39)")
    print(f"   Casillas recorridas: {ficha.casillas_recorridas}")
    
    # La entrada al pasillo rojo es la posición 34
    # Desde la posición 39, necesita llegar a 34 completando la vuelta
    # 39 -> 67 = 28 casillas (para llegar a pos 67)
    # 0 -> 34 = 34 casillas más
    # Total: 29 + 34 = 63 casillas para llegar a pos 34
    # Pero debe haber recorrido 68 casillas en total
    
    # Estrategia: Mover al menos 68 casillas y cruzar por pos 34
    
    # Movimiento 1: 30 casillas (llega a pos (39+30)%68 = 1)
    print(f"\n📍 Movimiento 1: +30 casillas")
    partida._mover_ficha(j1, 0, 30)
    print(f"   Posición: {ficha.posicion}, Recorridas: {ficha.casillas_recorridas}, Estado: {ficha.estado.value}")
    assert ficha.posicion == 1, f"Debería estar en pos 1, está en {ficha.posicion}"
    assert ficha.casillas_recorridas == 30, f"Debería tener 30 recorridas, tiene {ficha.casillas_recorridas}"
    
    # Movimiento 2: 33 casillas más (total 63, llega a pos 34)
    # Pero aún no tiene 68 casillas recorridas, así que NO debe entrar al pasillo
    print(f"\n📍 Movimiento 2: +33 casillas (total 63)")
    partida._mover_ficha(j1, 0, 33)
    print(f"   Posición: {ficha.posicion}, Recorridas: {ficha.casillas_recorridas}, Estado: {ficha.estado.value}")
    assert ficha.posicion == 34, f"Debería estar en pos 34, está en {ficha.posicion}"
    assert ficha.casillas_recorridas == 63, f"Debería tener 63 recorridas, tiene {ficha.casillas_recorridas}"
    assert ficha.estado != EstadoFicha.PASILLO_FINAL, "NO debería estar en el pasillo (solo 63 casillas)"
    
    # Movimiento 3: 5 casillas más (total 68, llega a pos 39)
    print(f"\n📍 Movimiento 3: +5 casillas (total 68)")
    partida._mover_ficha(j1, 0, 5)
    print(f"   Posición: {ficha.posicion}, Recorridas: {ficha.casillas_recorridas}, Estado: {ficha.estado.value}")
    assert ficha.posicion == 39, f"Debería estar en pos 39, está en {ficha.posicion}"
    assert ficha.casillas_recorridas == 68, f"Debería tener 68 recorridas, tiene {ficha.casillas_recorridas}"
    
    # Movimiento 4: Ahora con 68 casillas recorridas, al avanzar y pasar por 34, DEBE entrar al pasillo
    # Desde pos 39, para llegar a pos 34: 
    # 39 -> 67 (29 casillas) -> 0 -> 34 (34 casillas) = 63 casillas total
    print(f"\n📍 Movimiento 4: +63 casillas (cruzará pos 34 con 131 casillas recorridas)")
    partida._mover_ficha(j1, 0, 63)
    print(f"   Estado: {ficha.estado.value}")
    print(f"   Posición tablero: {ficha.posicion}")
    print(f"   Posición pasillo: {ficha.posicion_pasillo}")
    print(f"   Casillas recorridas: {ficha.casillas_recorridas}")
    
    # Verificación: Debe estar en el pasillo
    assert ficha.estado == EstadoFicha.PASILLO_FINAL, f"❌ Debería estar en PASILLO_FINAL, está en {ficha.estado.value}"
    assert ficha.posicion is None, f"❌ No debería tener posición en tablero"
    print(f"\n✅ TEST PASADO: La ficha entró correctamente al pasillo")


def test_entrada_pasillo_diferentes_colores():
    """Test: Verificar entrada al pasillo para cada color."""
    print("\n🧪 TEST: Verificar entrada al pasillo para todos los colores")
    print("=" * 70)
    
    # Entradas de pasillo según tablero.py
    entradas = {
        "red": 34,
        "blue": 17,
        "yellow": 0,
        "green": 51
    }
    
    # Salidas según tablero.py
    salidas = {
        "red": 39,
        "blue": 22,
        "yellow": 5,
        "green": 56
    }
    
    for color, entrada in entradas.items():
        print(f"\n--- Probando color {color.upper()} ---")
        partida = Partida(f"test_{color}", 2)
        j1 = partida.agregar_jugador(f"Jugador {color}", "j1", color)
        j2 = partida.agregar_jugador("Otro", "j2", "red" if color != "red" else "blue")
        partida.iniciar_partida()
        
        partida.dados_inicio = {"j1": 6, "j2": 3}
        partida._determinar_primer_turno()
        
        # Sacar ficha
        ficha = j1.fichas[0]
        salida = salidas[color]
        partida._sacar_ficha_carcel(j1, 0)
        print(f"   Salida: pos {salida}, Entrada pasillo: pos {entrada}")
        
        # Calcular casillas para llegar a la entrada desde la salida
        if entrada >= salida:
            casillas_a_entrada = entrada - salida
        else:
            casillas_a_entrada = (68 - salida) + entrada
        
        print(f"   Casillas desde salida hasta entrada: {casillas_a_entrada}")
        
        # Mover para completar 68 casillas sin llegar a la entrada
        if casillas_a_entrada < 68:
            # Mover cerca pero sin llegar a 68
            partida._mover_ficha(j1, 0, 67)
            print(f"   Después de 67 casillas: pos {ficha.posicion}, recorridas {ficha.casillas_recorridas}")
            
            # Ahora mover 1 más para llegar a 68
            partida._mover_ficha(j1, 0, 1)
            print(f"   Después de 68 casillas: pos {ficha.posicion}, recorridas {ficha.casillas_recorridas}")
            
            # Calcular cuánto falta para llegar a la entrada con 68+ recorridas
            pos_actual = ficha.posicion
            if entrada >= pos_actual:
                faltan = entrada - pos_actual
            else:
                faltan = (68 - pos_actual) + entrada
            
            print(f"   Faltan {faltan} casillas para llegar a entrada")
            
            # Mover para cruzar la entrada
            partida._mover_ficha(j1, 0, faltan + 5)  # +5 para entrar con casillas en el pasillo
            
            print(f"   Estado final: {ficha.estado.value}, Pos pasillo: {ficha.posicion_pasillo}")
            assert ficha.estado == EstadoFicha.PASILLO_FINAL, f"❌ {color}: No entró al pasillo"
            print(f"   ✅ {color.upper()}: Entró correctamente al pasillo")
    
    print(f"\n✅ TODOS LOS COLORES ENTRARON CORRECTAMENTE AL PASILLO")


if __name__ == "__main__":
    try:
        test_entrada_pasillo_rojo()
        test_entrada_pasillo_diferentes_colores()
        print("\n" + "="*70)
        print("🎉 TODOS LOS TESTS PASARON")
        print("="*70)
    except AssertionError as e:
        print(f"\n❌ TEST FALLÓ: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
Test para verificar que las fichas SOLO entran al pasillo después de 68 casillas
"""

import sys
sys.path.append('./backend')

from models.partida import Partida
from models.ficha import EstadoFicha

def test_no_entra_antes_de_vuelta_completa():
    """Test: Ficha NO debe entrar al pasillo si no completó la vuelta"""
    print("\n" + "="*60)
    print("TEST: Ficha NO entra al pasillo sin completar vuelta")
    print("="*60)
    
    partida = Partida("test", 2)
    j1 = partida.agregar_jugador("Rojo", "s1", "red")
    j2 = partida.agregar_jugador("Azul", "s2", "blue")
    
    partida.iniciada = True
    partida.esperando_dados_inicio = False
    j1.es_su_turno = True
    
    # Sacar ficha en posición 39 (salida roja)
    dados_par = (1, 1)
    partida.procesar_turno(j1, dados_par, None)
    partida.procesar_turno(j1, dados_par, 0)
    
    ficha = j1.fichas[0]
    print(f"\n1. Ficha 0 salió en posición: {ficha.posicion}")
    print(f"   Casillas recorridas: {ficha.casillas_recorridas}")
    
    # Colocar manualmente la ficha en casilla 25 (4 antes de la entrada 29)
    # pero con pocas casillas recorridas
    ficha.posicion = 25
    ficha.casillas_recorridas = 54  # Menos de 68
    partida.tablero.remover_ficha(39, ficha)
    partida.tablero.agregar_ficha(25, ficha)
    
    print(f"\n2. Ficha colocada en posición 25")
    print(f"   Casillas recorridas: {ficha.casillas_recorridas} (menos de 68)")
    
    # Resetear pares
    j1.resetear_pares()
    
    # Mover 6 casillas (pasará por 29 pero NO debe entrar al pasillo)
    dados = (2, 4)
    print(f"\n3. Moviendo 6 casillas con dados {dados}...")
    partida.procesar_turno(j1, dados, None)
    resultado = partida.procesar_turno(j1, dados, 0)
    
    print(f"\n4. Estado después del movimiento:")
    print(f"   - Posición tablero: {ficha.posicion}")
    print(f"   - Estado: {ficha.estado.value}")
    print(f"   - Casillas recorridas: {ficha.casillas_recorridas}")
    print(f"   - Posición pasillo: {ficha.posicion_pasillo}")
    
    # La ficha debe seguir en el tablero (posición 31 = 25+6)
    if ficha.estado == EstadoFicha.TABLERO and ficha.posicion == 31:
        print(f"\n✅ TEST PASADO: Ficha NO entró al pasillo (aún faltan casillas)")
        return True
    else:
        print(f"\n❌ TEST FALLIDO: Ficha entró al pasillo sin completar la vuelta")
        return False

def test_entra_despues_de_vuelta_completa():
    """Test: Ficha SÍ debe entrar al pasillo después de 68 casillas"""
    print("\n" + "="*60)
    print("TEST: Ficha SÍ entra al pasillo tras completar vuelta")
    print("="*60)
    
    partida = Partida("test2", 2)
    j1 = partida.agregar_jugador("Rojo", "s1", "red")
    j2 = partida.agregar_jugador("Azul", "s2", "blue")
    
    partida.iniciada = True
    partida.esperando_dados_inicio = False
    j1.es_su_turno = True
    
    # Sacar ficha
    dados_par = (1, 1)
    partida.procesar_turno(j1, dados_par, None)
    partida.procesar_turno(j1, dados_par, 0)
    
    ficha = j1.fichas[0]
    
    # Colocar ficha en casilla 25 (4 antes de la entrada 29)
    # pero con 64 casillas recorridas (falta poco para completar vuelta)
    ficha.posicion = 25
    ficha.casillas_recorridas = 64  # 64 + 6 = 70 > 68, debe entrar
    partida.tablero.remover_ficha(39, ficha)
    partida.tablero.agregar_ficha(25, ficha)
    
    print(f"\n1. Ficha colocada en posición 25")
    print(f"   Casillas recorridas: {ficha.casillas_recorridas}")
    print(f"   Entrada al pasillo: 29")
    
    # Resetear pares
    j1.resetear_pares()
    
    # Mover 6 casillas (pasará por 29 Y debe entrar con 2 en pasillo)
    # De 25 a 29 = 4 casillas, quedan 2 para el pasillo
    dados = (2, 4)
    print(f"\n2. Moviendo 6 casillas con dados {dados}...")
    partida.procesar_turno(j1, dados, None)
    resultado = partida.procesar_turno(j1, dados, 0)
    
    print(f"\n3. Estado después del movimiento:")
    print(f"   - Posición tablero: {ficha.posicion}")
    print(f"   - Estado: {ficha.estado.value}")
    print(f"   - Casillas recorridas: {ficha.casillas_recorridas}")
    print(f"   - Posición pasillo: {ficha.posicion_pasillo}")
    
    # La ficha debe estar en el pasillo con posición 2
    if ficha.estado == EstadoFicha.PASILLO_FINAL and ficha.posicion_pasillo == 2:
        print(f"\n✅ TEST PASADO: Ficha entró al pasillo correctamente")
        return True
    else:
        print(f"\n❌ TEST FALLIDO: Ficha NO entró al pasillo")
        return False

if __name__ == "__main__":
    print("\n" + "🔄"*30)
    print("TESTS: VUELTA COMPLETA ANTES DE ENTRAR AL PASILLO")
    print("🔄"*30)
    
    try:
        resultado1 = test_no_entra_antes_de_vuelta_completa()
        resultado2 = test_entra_despues_de_vuelta_completa()
        
        print("\n" + "="*60)
        if resultado1 and resultado2:
            print("🎉 TODOS LOS TESTS PASARON")
            print("="*60)
            print("\n✅ Las fichas ahora requieren 68 casillas antes de entrar al pasillo")
        else:
            print("❌ ALGUNOS TESTS FALLARON")
            print("="*60)
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

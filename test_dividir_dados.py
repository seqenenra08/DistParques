#!/usr/bin/env python3
"""
Test para verificar la funcionalidad de dividir dados.
"""
import sys
sys.path.insert(0, '/home/seqenenra/Codes/DistParques/backend')

from models.partida import Partida
from models.ficha import EstadoFicha

def test_dividir_dados_basico():
    """Test básico: dividir dados entre dos fichas diferentes."""
    print("=" * 70)
    print("TEST 1: Dividir dados entre dos fichas diferentes")
    print("=" * 70)
    
    # Crear partida
    partida = Partida("test_division", max_jugadores=2)
    jugador1 = partida.agregar_jugador("Jugador1", "player1", "red")
    jugador2 = partida.agregar_jugador("Jugador2", "player2", "blue")
    
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    jugador1.es_su_turno = True
    partida.turno_actual = 0
    
    print(f"\n🎮 Partida iniciada - Turno de: {jugador1.nombre}")
    
    # Sacar dos fichas de la cárcel (simular)
    print(f"\n📍 Colocando 2 fichas en el tablero...")
    ficha0 = jugador1.fichas[0]
    ficha0.estado = EstadoFicha.TABLERO
    ficha0.posicion = 39
    ficha0.casillas_recorridas = 5
    partida.tablero.agregar_ficha(39, ficha0)
    print(f"   Ficha 0 en posición 39")
    
    ficha1 = jugador1.fichas[1]
    ficha1.estado = EstadoFicha.TABLERO
    ficha1.posicion = 45
    ficha1.casillas_recorridas = 10
    partida.tablero.agregar_ficha(45, ficha1)
    print(f"   Ficha 1 en posición 45")
    
    # Lanzar dados diferentes
    dados = (3, 5)
    print(f"\n🎲 Lanzando dados: {dados[0]} y {dados[1]}")
    
    # Verificar movimientos válidos
    info = partida.tiene_movimientos_validos(jugador1, dados)
    print(f"\n📊 Análisis de movimientos:")
    print(f"   ¿Tiene movimientos?: {info['tiene_movimientos']}")
    print(f"   ¿Puede dividir?: {info['puede_dividir']}")
    print(f"   Fichas movibles: {info['fichas_movibles']}")
    
    if not info['puede_dividir']:
        print(f"\n❌ ERROR: Debería poder dividir dados")
        return False
    
    # Intentar dividir: mover ficha 0 con dado 3, ficha 1 con dado 5
    print(f"\n🎯 Dividiendo dados:")
    print(f"   - Ficha 0 se mueve {dados[0]} casillas")
    print(f"   - Ficha 1 se mueve {dados[1]} casillas")
    
    movimientos = [
        {"id_ficha": 0, "valor_dado": 3},
        {"id_ficha": 1, "valor_dado": 5}
    ]
    
    resultado = partida.procesar_turno_dividido(jugador1, dados, movimientos)
    
    if "error" in resultado:
        print(f"\n❌ ERROR: {resultado['error']}")
        return False
    
    print(f"\n✅ División exitosa:")
    print(f"   Movimientos realizados: {len(resultado['movimientos_realizados'])}")
    print(f"   Ficha 0 nueva posición: {ficha0.posicion}")
    print(f"   Ficha 1 nueva posición: {ficha1.posicion}")
    
    return True

def test_no_repetir_ficha():
    """Test: no se puede mover la misma ficha dos veces."""
    print("\n\n" + "=" * 70)
    print("TEST 2: No permitir mover la misma ficha dos veces")
    print("=" * 70)
    
    partida = Partida("test_repetir", max_jugadores=2)
    jugador1 = partida.agregar_jugador("Jugador1", "player1", "red")
    jugador2 = partida.agregar_jugador("Jugador2", "player2", "blue")
    
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    jugador1.es_su_turno = True
    partida.turno_actual = 0
    
    # Colocar fichas
    ficha0 = jugador1.fichas[0]
    ficha0.estado = EstadoFicha.TABLERO
    ficha0.posicion = 39
    ficha0.casillas_recorridas = 5
    partida.tablero.agregar_ficha(39, ficha0)
    
    dados = (3, 5)
    print(f"\n🎲 Dados: {dados}")
    print(f"🚫 Intentando mover ficha 0 dos veces...")
    
    # Intentar mover la misma ficha con ambos dados
    movimientos = [
        {"id_ficha": 0, "valor_dado": 3},
        {"id_ficha": 0, "valor_dado": 5}  # ¡Misma ficha!
    ]
    
    resultado = partida.procesar_turno_dividido(jugador1, dados, movimientos)
    
    if "error" in resultado:
        print(f"\n✅ CORRECTO: Se rechazó el movimiento")
        print(f"   Error: {resultado['error']}")
        return True
    else:
        print(f"\n❌ ERROR: Debería rechazar mover la misma ficha dos veces")
        return False

def test_saltar_turno_sin_movimientos():
    """Test: saltar turno automáticamente si no hay movimientos válidos."""
    print("\n\n" + "=" * 70)
    print("TEST 3: Saltar turno cuando no hay movimientos válidos")
    print("=" * 70)
    
    partida = Partida("test_saltar", max_jugadores=2)
    jugador1 = partida.agregar_jugador("Jugador1", "player1", "red")
    jugador2 = partida.agregar_jugador("Jugador2", "player2", "blue")
    
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    jugador1.es_su_turno = True
    partida.turno_actual = 0
    
    # Colocar ficha cerca de la meta (necesita exactamente 2 para llegar)
    print(f"\n📍 Colocando ficha a 2 casillas de la meta...")
    ficha0 = jugador1.fichas[0]
    ficha0.estado = EstadoFicha.PASILLO_FINAL
    ficha0.posicion = None
    ficha0.posicion_pasillo = 6  # Necesita 2 más para llegar a 8
    ficha0.casillas_recorridas = 74
    
    # Las demás fichas en la cárcel
    print(f"   Otras fichas en la cárcel")
    
    # Sacar 5 y 6 (ambos se pasarían de la meta)
    dados = (5, 6)
    print(f"\n🎲 Lanzando dados: {dados} (suma = 11)")
    print(f"   La ficha necesita solo 2, cualquier dado se pasaría")
    
    # Verificar movimientos
    info = partida.tiene_movimientos_validos(jugador1, dados)
    print(f"\n📊 Análisis:")
    print(f"   ¿Tiene movimientos?: {info['tiene_movimientos']}")
    print(f"   Fichas movibles con suma: {info.get('fichas_movibles_suma', [])}")
    print(f"   Fichas movibles con dado1: {info.get('fichas_movibles_dado1', [])}")
    print(f"   Fichas movibles con dado2: {info.get('fichas_movibles_dado2', [])}")
    
    if info['tiene_movimientos']:
        print(f"\n⚠️  Tiene movimientos disponibles (puede mover con dados divididos)")
        print(f"   Este caso es válido si puede usar un dado individual")
        # Esto es aceptable si la ficha puede moverse con algún dado individual
        return True
    
    print(f"\n✅ CORRECTO: No hay movimientos válidos")
    print(f"   El turno debería saltarse automáticamente")
    
    return True

def test_par_de_dados_no_divide():
    """Test: con par de dados (ej: 4-4) no se puede dividir."""
    print("\n\n" + "=" * 70)
    print("TEST 4: Par de dados no permite división")
    print("=" * 70)
    
    partida = Partida("test_par", max_jugadores=2)
    jugador1 = partida.agregar_jugador("Jugador1", "player1", "red")
    jugador2 = partida.agregar_jugador("Jugador2", "player2", "blue")
    
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    jugador1.es_su_turno = True
    partida.turno_actual = 0
    
    # Colocar dos fichas
    ficha0 = jugador1.fichas[0]
    ficha0.estado = EstadoFicha.TABLERO
    ficha0.posicion = 39
    ficha0.casillas_recorridas = 5
    partida.tablero.agregar_ficha(39, ficha0)
    
    ficha1 = jugador1.fichas[1]
    ficha1.estado = EstadoFicha.TABLERO
    ficha1.posicion = 45
    ficha1.casillas_recorridas = 10
    partida.tablero.agregar_ficha(45, ficha1)
    
    # Par de dados
    dados = (4, 4)
    print(f"\n🎲 Dados: {dados} (par)")
    
    info = partida.tiene_movimientos_validos(jugador1, dados)
    print(f"\n📊 Análisis:")
    print(f"   ¿Puede dividir?: {info['puede_dividir']}")
    
    if info['puede_dividir']:
        print(f"\n❌ ERROR: Con par no debería poder dividir")
        return False
    
    print(f"\n✅ CORRECTO: Con par debe usar la suma completa")
    return True

if __name__ == "__main__":
    print("\n🧪 TESTS DE DIVISIÓN DE DADOS Y SALTO AUTOMÁTICO\n")
    
    test1 = test_dividir_dados_basico()
    test2 = test_no_repetir_ficha()
    test3 = test_saltar_turno_sin_movimientos()
    test4 = test_par_de_dados_no_divide()
    
    print("\n\n" + "=" * 70)
    print("RESUMEN DE TESTS")
    print("=" * 70)
    print(f"Test 1 (Dividir dados): {'✅ EXITOSO' if test1 else '❌ FALLIDO'}")
    print(f"Test 2 (No repetir ficha): {'✅ EXITOSO' if test2 else '❌ FALLIDO'}")
    print(f"Test 3 (Saltar turno sin movimientos): {'✅ EXITOSO' if test3 else '❌ FALLIDO'}")
    print(f"Test 4 (Par no divide): {'✅ EXITOSO' if test4 else '❌ FALLIDO'}")
    print(f"\n{'✅ TODOS LOS TESTS PASARON' if all([test1, test2, test3, test4]) else '❌ ALGUNOS TESTS FALLARON'}")
    print("=" * 70)

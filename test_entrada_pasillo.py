#!/usr/bin/env python3
"""
Test para verificar que las fichas entren correctamente al pasillo final
"""

import sys
sys.path.append('./backend')

from models.partida import Partida
from models.ficha import EstadoFicha

def test_entrada_pasillo_red():
    """Test: Ficha roja debe entrar al pasillo en la casilla 29"""
    print("\n" + "="*60)
    print("TEST: Ficha ROJA entra al pasillo en casilla 29")
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
    
    print(f"\n1. Ficha 0 salió en posición: {j1.fichas[0].posicion}")
    assert j1.fichas[0].posicion == 39, "Ficha debe salir en 39"
    
    # Mover la ficha justo a la entrada del pasillo (casilla 29)
    # De 39 a 29 son: 68-39+29 = 58 casillas (dando la vuelta)
    # Pero podemos hacerlo en pasos
    
    # Primero mover cerca de la entrada: de 39 a 27 (56 casillas antes de la entrada)
    print("\n2. Moviendo ficha cerca de la entrada del pasillo...")
    for paso in range(3):  # 3 movimientos de 10 casillas
        dados = (5, 5)
        resultado = partida.procesar_turno(j1, dados, 0)
        print(f"   Paso {paso+1}: Posición = {j1.fichas[0].posicion}")
    
    print(f"\n3. Posición actual: {j1.fichas[0].posicion}")
    
    # Ahora mover exactamente a la entrada (casilla 29)
    # Calcular cuántas casillas faltan para llegar a 29
    pos_actual = j1.fichas[0].posicion
    if pos_actual > 29:
        casillas_a_29 = 68 - pos_actual + 29
    else:
        casillas_a_29 = 29 - pos_actual
    
    print(f"4. Faltan {casillas_a_29} casillas para llegar a la entrada (29)")
    
    # Mover justo a la entrada
    dados = (casillas_a_29, 0) if casillas_a_29 <= 6 else (6, casillas_a_29 - 6)
    if dados[1] == 0:
        dados = (casillas_a_29 // 2, casillas_a_29 - casillas_a_29 // 2)
    
    # Mejor: mover en pasos pequeños hasta llegar cerca
    while True:
        pos_actual = j1.fichas[0].posicion
        if pos_actual is None:
            break  # Ya entró al pasillo
        
        if pos_actual > 29:
            casillas_a_29 = 68 - pos_actual + 29
        else:
            casillas_a_29 = 29 - pos_actual
        
        if casillas_a_29 == 0:
            break
        
        # Mover en pasos de máximo 6
        mover = min(casillas_a_29, 6)
        dados = (mover // 2, mover - mover // 2)
        
        print(f"   Moviendo {mover} casillas (dados {dados})...")
        resultado = partida.procesar_turno(j1, dados, 0)
        
        if j1.fichas[0].posicion is None:
            print(f"   ✅ Ficha entró al pasillo!")
            break
        else:
            print(f"   Posición: {j1.fichas[0].posicion}")
    
    print(f"\n5. Estado final de la ficha:")
    print(f"   - Posición tablero: {j1.fichas[0].posicion}")
    print(f"   - Estado: {j1.fichas[0].estado.value}")
    print(f"   - Posición pasillo: {j1.fichas[0].posicion_pasillo}")
    
    if j1.fichas[0].estado == EstadoFicha.PASILLO_FINAL:
        print(f"\n✅ TEST PASADO: Ficha entró correctamente al pasillo!")
        return True
    else:
        print(f"\n❌ TEST FALLIDO: Ficha no entró al pasillo (estado: {j1.fichas[0].estado.value})")
        return False

def test_entrada_pasillo_simple():
    """Test simplificado: colocar ficha cerca de entrada y moverla"""
    print("\n" + "="*60)
    print("TEST SIMPLE: Entrada al pasillo rojo (casilla 29)")
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
    
    # Colocar manualmente la ficha en casilla 25 (4 casillas antes de la entrada 29)
    ficha = j1.fichas[0]
    ficha.posicion = 25
    partida.tablero.remover_ficha(39, ficha)  # Remover de salida
    partida.tablero.agregar_ficha(25, ficha)
    
    # Resetear contador de pares para evitar el premio de 3 pares
    j1.resetear_pares()
    
    print(f"\n1. Ficha colocada manualmente en posición: {ficha.posicion}")
    
    # Mover 6 casillas (debe pasar por 29 y entrar con 2 casillas en el pasillo)
    # Usar dados SIN par para evitar complicaciones
    dados = (2, 4)
    print(f"2. Moviendo 6 casillas con dados {dados}...")
    # Primero llamar sin ficha (ROLL)
    resultado_roll = partida.procesar_turno(j1, dados, None)
    print(f"   ROLL resultado: {resultado_roll}")
    # Luego mover la ficha (MOVE)
    resultado = partida.procesar_turno(j1, dados, 0)
    print(f"   MOVE resultado: {resultado}")
    
    print(f"\n3. Estado después del movimiento:")
    print(f"   - Posición tablero: {ficha.posicion}")
    print(f"   - Estado: {ficha.estado.value}")
    print(f"   - Posición pasillo: {ficha.posicion_pasillo}")
    
    if ficha.estado == EstadoFicha.PASILLO_FINAL and ficha.posicion_pasillo == 2:
        print(f"\n✅ TEST PASADO: Ficha entró al pasillo con 2 casillas!")
        return True
    else:
        print(f"\n❌ TEST FALLIDO: Estado incorrecto")
        return False

if __name__ == "__main__":
    print("\n" + "🏠"*30)
    print("TESTS DE ENTRADA AL PASILLO FINAL")
    print("🏠"*30)
    
    try:
        resultado1 = test_entrada_pasillo_simple()
        
        print("\n" + "="*60)
        if resultado1:
            print("🎉 TEST PASÓ")
            print("="*60)
            print("\n✅ Las fichas ahora entran correctamente al pasillo final")
        else:
            print("❌ TEST FALLÓ")
            print("="*60)
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

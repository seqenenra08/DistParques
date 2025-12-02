#!/usr/bin/env python3
"""
Script de prueba para verificar la lógica de sacar fichas de la cárcel con pares.
"""
import sys
sys.path.insert(0, '/home/seqenenra/Codes/DistParques/backend')

from models.partida import Partida

def test_sacar_de_carcel_con_par():
    """Prueba que cuando todas las fichas están en cárcel y se saca par, se pueda sacar una ficha."""
    print("=" * 60)
    print("TEST: Sacar fichas de la cárcel con PAR")
    print("=" * 60)
    
    # Crear partida
    partida = Partida("test_sala", max_jugadores=2)
    
    # Agregar jugadores
    jugador1 = partida.agregar_jugador("Jugador1", "player1", "red")
    jugador2 = partida.agregar_jugador("Bot1", "bot_123", "blue")
    
    print(f"\n✅ Jugadores creados:")
    print(f"   - {jugador1.nombre} ({jugador1.color})")
    print(f"   - {jugador2.nombre} ({jugador2.color})")
    
    # Iniciar partida (saltamos la fase de dados de inicio)
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    jugador1.es_su_turno = True
    partida.turno_actual = 0
    
    print(f"\n🎮 Partida iniciada - Turno de: {jugador1.nombre}")
    
    # Verificar que todas las fichas estén en cárcel
    todas_en_carcel = all(f.esta_en_carcel() for f in jugador1.fichas)
    print(f"\n📊 Estado inicial:")
    print(f"   - Todas las fichas en cárcel: {todas_en_carcel}")
    print(f"   - Fichas en cárcel: {[f.id for f in jugador1.fichas if f.esta_en_carcel()]}")
    
    # Simular lanzamiento de dados (PAR)
    print(f"\n🎲 Simulando lanzamiento de dados...")
    dados_par = (5, 5)
    print(f"   Dados: {dados_par[0]} + {dados_par[1]} = {sum(dados_par)}")
    print(f"   ¿Es par?: {dados_par[0] == dados_par[1]}")
    
    # Intentar procesar turno con el par
    print(f"\n🎯 Procesando turno - Sacando ficha 0 de la cárcel...")
    resultado = partida.procesar_turno(jugador1, dados_par, id_ficha=0)
    
    print(f"\n📤 Resultado del turno:")
    print(f"   - Acción: {resultado.get('accion', 'desconocida')}")
    print(f"   - Error: {resultado.get('error', 'ninguno')}")
    print(f"   - Mensaje: {resultado.get('mensaje', 'sin mensaje')}")
    print(f"   - Cambio de turno: {resultado.get('cambio_turno', False)}")
    
    # Verificar estado de la ficha después
    ficha0 = jugador1.fichas[0]
    print(f"\n📍 Estado de ficha 0 después del movimiento:")
    print(f"   - Estado: {ficha0.estado.value}")
    print(f"   - Posición: {ficha0.posicion}")
    print(f"   - En cárcel: {ficha0.esta_en_carcel()}")
    print(f"   - Casilla de salida del jugador: {jugador1.casilla_salida}")
    
    if "error" in resultado:
        print(f"\n❌ ERROR: {resultado['error']}")
        return False
    
    if resultado.get('accion') == 'sacar_carcel':
        print(f"\n✅ TEST EXITOSO: La ficha fue sacada de la cárcel correctamente")
        return True
    else:
        print(f"\n❌ TEST FALLIDO: Se esperaba 'sacar_carcel' pero se obtuvo '{resultado.get('accion')}'")
        return False

def test_sin_par_todas_en_carcel():
    """Prueba que sin par, no se puede sacar de la cárcel."""
    print("\n\n" + "=" * 60)
    print("TEST: Sin PAR, no se puede sacar de la cárcel")
    print("=" * 60)
    
    # Crear partida
    partida = Partida("test_sala2", max_jugadores=2)
    
    # Agregar jugadores
    jugador1 = partida.agregar_jugador("Jugador1", "player1", "red")
    jugador2 = partida.agregar_jugador("Bot1", "bot_123", "blue")
    
    # Iniciar partida
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    jugador1.es_su_turno = True
    partida.turno_actual = 0
    
    print(f"\n🎮 Partida iniciada - Turno de: {jugador1.nombre}")
    
    # Simular lanzamiento de dados (NO PAR)
    print(f"\n🎲 Simulando lanzamiento de dados...")
    dados_no_par = (3, 5)
    print(f"   Dados: {dados_no_par[0]} + {dados_no_par[1]} = {sum(dados_no_par)}")
    print(f"   ¿Es par?: {dados_no_par[0] == dados_no_par[1]}")
    
    # Procesar turnos hasta agotar intentos (sin especificar ficha)
    print(f"\n🔄 Procesando intentos sin par...")
    for intento in range(3):
        print(f"\n   Intento {intento + 1}/3:")
        resultado = partida.procesar_turno(jugador1, dados_no_par, id_ficha=None)
        print(f"      - Acción: {resultado.get('accion', 'desconocida')}")
        print(f"      - Intentos restantes: {resultado.get('intentos_restantes', 0)}")
        print(f"      - Cambio turno: {resultado.get('cambio_turno', False)}")
        
        if resultado.get('cambio_turno'):
            print(f"\n✅ TEST EXITOSO: El turno cambió después de agotar intentos")
            return True
    
    print(f"\n❌ TEST FALLIDO: Debería haber cambiado el turno después de 3 intentos")
    return False

if __name__ == "__main__":
    print("\n🧪 EJECUTANDO TESTS DE SACAR FICHAS DE LA CÁRCEL\n")
    
    test1 = test_sacar_de_carcel_con_par()
    test2 = test_sin_par_todas_en_carcel()
    
    print("\n\n" + "=" * 60)
    print("RESUMEN DE TESTS")
    print("=" * 60)
    print(f"Test 1 (Con PAR): {'✅ EXITOSO' if test1 else '❌ FALLIDO'}")
    print(f"Test 2 (Sin PAR): {'✅ EXITOSO' if test2 else '❌ FALLIDO'}")
    print(f"\n{'✅ TODOS LOS TESTS PASARON' if test1 and test2 else '❌ ALGUNOS TESTS FALLARON'}")
    print("=" * 60)

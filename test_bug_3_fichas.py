#!/usr/bin/env python3
"""
Test para reproducir el bug de 3 fichas en la misma casilla.
"""
import sys
sys.path.insert(0, '/home/seqenenra/Codes/DistParques/backend')

from models.partida import Partida
from models.ficha import EstadoFicha

def test_3_fichas_misma_casilla():
    """Simula el escenario donde 3 fichas llegan a la misma casilla."""
    print("=" * 70)
    print("TEST: 3 fichas en la misma casilla + intentar mover")
    print("=" * 70)
    
    # Crear partida
    partida = Partida("test_sala", max_jugadores=2)
    
    # Agregar jugadores
    bot1 = partida.agregar_jugador("Bot1", "bot_123", "red")
    jugador2 = partida.agregar_jugador("Jugador2", "player2", "blue")
    
    # Iniciar partida
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    bot1.es_su_turno = True
    partida.turno_actual = 0
    
    print(f"\n🎮 Partida iniciada - Turno de: {bot1.nombre}")
    
    # Simular que 3 fichas están en la misma casilla (posición 30)
    print(f"\n📍 Simulando 3 fichas del bot en posición 30...")
    
    # Sacar las fichas de la cárcel manualmente
    for i in range(3):
        ficha = bot1.fichas[i]
        ficha.estado = EstadoFicha.TABLERO
        ficha.posicion = 30
        ficha.casillas_recorridas = 25  # Simular que ya recorrieron 25 casillas
        partida.tablero.agregar_ficha(30, ficha)
        print(f"   ✅ Ficha {i} colocada en posición 30")
    
    # La ficha 3 en meta
    bot1.fichas[3].estado = EstadoFicha.META
    print(f"   🏁 Ficha 3 en META")
    
    # Simular varios turnos lanzando dados
    print(f"\n🎲 Simulando 5 turnos del bot...")
    
    for turno in range(5):
        print(f"\n--- Turno {turno + 1} ---")
        
        # Lanzar dados
        dados = partida.lanzar_dados()
        suma = dados[0] + dados[1]
        es_par = dados[0] == dados[1]
        
        print(f"🎲 Dados: {dados[0]} + {dados[1]} = {suma}, Par: {es_par}")
        
        # Verificar qué fichas puede mover
        print(f"\n📊 Verificando fichas disponibles:")
        fichas_disponibles = []
        for i, ficha in enumerate(bot1.fichas):
            puede = bot1.puede_mover(i, suma)
            estado = f"{ficha.estado.value}"
            if ficha.estado == EstadoFicha.TABLERO:
                estado += f" (pos: {ficha.posicion}, recorridas: {ficha.casillas_recorridas})"
            print(f"   Ficha {i}: {estado} - ¿Puede mover {suma}?: {puede}")
            if puede:
                fichas_disponibles.append(i)
        
        if not fichas_disponibles:
            print(f"\n⚠️  ¡No hay fichas disponibles! Esto causa el loop infinito.")
            print(f"   El bot debería cambiar de turno pero no lo hace.")
            return False
        
        # Intentar mover la primera ficha disponible
        id_ficha = fichas_disponibles[0]
        print(f"\n🎯 Intentando mover ficha {id_ficha}...")
        
        resultado = partida.procesar_turno(bot1, dados, id_ficha)
        
        if "error" in resultado:
            print(f"   ❌ Error: {resultado['error']}")
            print(f"   🚫 El bot no puede mover pero el juego no cambia de turno.")
            return False
        else:
            print(f"   ✅ Movimiento exitoso: {resultado.get('accion', 'desconocido')}")
            
            # Verificar nueva posición
            ficha_movida = bot1.fichas[id_ficha]
            if ficha_movida.estado == EstadoFicha.TABLERO:
                print(f"   📍 Nueva posición: {ficha_movida.posicion}")
        
        # Si no es par, debería cambiar turno
        if not es_par and not resultado.get('cambio_turno'):
            print(f"\n⚠️  No era par pero no cambió turno. ¿Bug?")
    
    print(f"\n✅ TEST COMPLETADO: Se procesaron 5 turnos sin loop infinito")
    return True

def test_ficha_cerca_meta():
    """Test cuando una ficha está muy cerca de la meta y no puede moverse con dados altos."""
    print("\n\n" + "=" * 70)
    print("TEST: Ficha cerca de la meta con dados que la pasan")
    print("=" * 70)
    
    # Crear partida
    partida = Partida("test_sala2", max_jugadores=2)
    
    # Agregar jugadores
    bot1 = partida.agregar_jugador("Bot1", "bot_123", "red")
    jugador2 = partida.agregar_jugador("Jugador2", "player2", "blue")
    
    # Iniciar partida
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    bot1.es_su_turno = True
    partida.turno_actual = 0
    
    print(f"\n🎮 Partida iniciada - Turno de: {bot1.nombre}")
    
    # Simular que una ficha está muy cerca de la meta
    # 76 casillas totales (68 tablero + 8 pasillo)
    # Poner ficha en casilla 73 (necesita 3 para llegar a meta)
    
    print(f"\n📍 Colocando ficha 0 en casilla 73 (3 casillas de la meta)...")
    ficha = bot1.fichas[0]
    ficha.estado = EstadoFicha.TABLERO
    ficha.posicion = 5  # Posición en tablero
    ficha.casillas_recorridas = 73
    partida.tablero.agregar_ficha(5, ficha)
    
    # Las otras fichas en la cárcel
    print(f"   🔒 Fichas 1, 2, 3 en cárcel")
    
    # Lanzar dados altos (ej: 6 + 6 = 12)
    dados = (6, 6)
    suma = 12
    
    print(f"\n🎲 Lanzando dados: {dados[0]} + {dados[1]} = {suma}")
    print(f"   La ficha necesita solo 3 para llegar a meta (76 - 73 = 3)")
    print(f"   Con 12 se pasaría (73 + 12 = 85 > 76)")
    
    # Verificar si puede mover
    puede = bot1.puede_mover(0, suma)
    print(f"\n📊 ¿Puede mover ficha 0 con {suma}?: {puede}")
    
    if puede:
        print(f"   ❌ ERROR: No debería poder mover (se pasaría de la meta)")
        return False
    else:
        print(f"   ✅ CORRECTO: No puede mover porque se pasaría")
    
    # En este caso el bot debe sacar de la cárcel con el par
    print(f"\n🎯 Como sacó par, debe sacar una ficha de la cárcel...")
    
    resultado = partida.procesar_turno(bot1, dados, id_ficha=1)
    
    if "error" in resultado:
        print(f"   ❌ Error: {resultado['error']}")
        return False
    
    if resultado.get('accion') == 'sacar_carcel':
        print(f"   ✅ CORRECTO: Sacó ficha de la cárcel")
        return True
    else:
        print(f"   ⚠️  Acción inesperada: {resultado.get('accion')}")
        return False

if __name__ == "__main__":
    print("\n🧪 EJECUTANDO TESTS DE BUGS DEL BOT\n")
    
    test1 = test_3_fichas_misma_casilla()
    test2 = test_ficha_cerca_meta()
    
    print("\n\n" + "=" * 70)
    print("RESUMEN DE TESTS")
    print("=" * 70)
    print(f"Test 1 (3 fichas misma casilla): {'✅ EXITOSO' if test1 else '❌ FALLIDO'}")
    print(f"Test 2 (Ficha cerca de meta): {'✅ EXITOSO' if test2 else '❌ FALLIDO'}")
    print(f"\n{'✅ TODOS LOS TESTS PASARON' if test1 and test2 else '❌ ALGUNOS TESTS FALLARON'}")
    print("=" * 70)

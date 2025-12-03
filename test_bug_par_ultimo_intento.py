#!/usr/bin/env python3
"""
Test para reproducir el bug: cuando todas las fichas están en cárcel
y sacas par en el 3er intento, no detecta el par.
"""
import sys
sys.path.insert(0, '/home/seqenenra/Codes/DistParques/backend')

from models.partida import Partida
from models.ficha import EstadoFicha

def test_par_en_tercer_intento():
    """Simula el escenario donde sacas par en el último intento."""
    print("=" * 70)
    print("TEST: Par en el 3er intento con todas las fichas en cárcel")
    print("=" * 70)
    
    # Crear partida
    partida = Partida("test_sala", max_jugadores=2)
    
    # Agregar jugadores
    jugador1 = partida.agregar_jugador("Jugador1", "player1", "red")
    jugador2 = partida.agregar_jugador("Jugador2", "player2", "blue")
    
    # Iniciar partida
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    jugador1.es_su_turno = True
    partida.turno_actual = 0
    
    print(f"\n🎮 Partida iniciada - Turno de: {jugador1.nombre}")
    print(f"📊 Todas las fichas están en la cárcel")
    
    # Verificar estado inicial
    for i, ficha in enumerate(jugador1.fichas):
        print(f"   Ficha {i}: {ficha.estado.value}")
    
    print(f"\n--- INTENTO 1 ---")
    # Primer intento: NO saca par
    dados1 = (3, 5)
    print(f"🎲 Lanzando dados: {dados1[0]} + {dados1[1]} = {dados1[0] + dados1[1]}")
    print(f"   ¿Es par?: {dados1[0] == dados1[1]}")
    
    resultado1 = partida.procesar_turno(jugador1, dados1)
    print(f"   Resultado: {resultado1.get('accion', 'N/A')}")
    print(f"   Intentos usados: {jugador1.intentos_carcel}/{jugador1.max_intentos_carcel}")
    print(f"   Intentos restantes: {resultado1.get('intentos_restantes', 'N/A')}")
    
    if resultado1.get('cambio_turno'):
        print(f"   ❌ ERROR: Cambió el turno pero el jugador tiene más intentos")
        return False
    
    print(f"\n--- INTENTO 2 ---")
    # Segundo intento: NO saca par
    dados2 = (2, 4)
    print(f"🎲 Lanzando dados: {dados2[0]} + {dados2[1]} = {dados2[0] + dados2[1]}")
    print(f"   ¿Es par?: {dados2[0] == dados2[1]}")
    
    resultado2 = partida.procesar_turno(jugador1, dados2)
    print(f"   Resultado: {resultado2.get('accion', 'N/A')}")
    print(f"   Intentos usados: {jugador1.intentos_carcel}/{jugador1.max_intentos_carcel}")
    print(f"   Intentos restantes: {resultado2.get('intentos_restantes', 'N/A')}")
    
    if resultado2.get('cambio_turno'):
        print(f"   ❌ ERROR: Cambió el turno pero el jugador tiene más intentos")
        return False
    
    print(f"\n--- INTENTO 3 (ÚLTIMO) ---")
    # Tercer intento: ¡SACA PAR!
    dados3 = (4, 4)
    print(f"🎲 Lanzando dados: {dados3[0]} + {dados3[1]} = {dados3[0] + dados3[1]}")
    print(f"   ¿Es par?: {dados3[0] == dados3[1]}")
    print(f"   👉 ¡ESTE ES EL BUG! Debería detectar el par y permitir sacar ficha")
    
    resultado3 = partida.procesar_turno(jugador1, dados3)
    print(f"   Resultado: {resultado3.get('accion', 'N/A')}")
    print(f"   Mensaje: {resultado3.get('mensaje', 'N/A')}")
    print(f"   ¿Cambió turno?: {resultado3.get('cambio_turno', False)}")
    
    # Verificar si detectó el par
    if resultado3.get('accion') == 'intentos_agotados':
        print(f"\n   ❌ BUG CONFIRMADO: No detectó el par en el 3er intento")
        print(f"      El jugador pierde el turno aunque sacó par")
        return False
    
    if resultado3.get('accion') in ['par_sacar_carcel', 'sacar_carcel']:
        print(f"\n   ✅ CORRECTO: Detectó el par y permite sacar ficha")
        print(f"   Intentos reseteados: {jugador1.intentos_carcel}")
        
        # Intentar sacar una ficha
        if resultado3.get('accion') == 'par_sacar_carcel':
            print(f"\n🎯 Sacando ficha 0 de la cárcel...")
            resultado_sacar = partida.procesar_turno(jugador1, dados3, id_ficha=0)
            print(f"   Resultado: {resultado_sacar.get('accion', 'N/A')}")
            
            # Verificar que la ficha salió
            ficha0 = jugador1.fichas[0]
            if ficha0.estado == EstadoFicha.TABLERO:
                print(f"   ✅ Ficha 0 salió de la cárcel a posición {ficha0.posicion}")
                return True
            else:
                print(f"   ❌ ERROR: Ficha 0 no salió ({ficha0.estado.value})")
                return False
        else:
            return True
    
    print(f"\n   ⚠️  Resultado inesperado: {resultado3}")
    return False

if __name__ == "__main__":
    print("\n🧪 EJECUTANDO TEST DEL BUG DEL PAR EN ÚLTIMO INTENTO\n")
    
    exito = test_par_en_tercer_intento()
    
    print("\n\n" + "=" * 70)
    print("RESULTADO DEL TEST")
    print("=" * 70)
    print(f"{'✅ TEST EXITOSO: El par se detecta correctamente' if exito else '❌ TEST FALLIDO: El par NO se detecta en el último intento'}")
    print("=" * 70)

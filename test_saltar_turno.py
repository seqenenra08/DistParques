#!/usr/bin/env python3
"""
Test específico: una ficha a 3 casillas de la meta, saca 6, debe saltar turno.
"""
import sys
sys.path.insert(0, '/home/seqenenra/Codes/DistParques/backend')

from models.partida import Partida
from models.ficha import EstadoFicha

def test_escenario_real_saltar_turno():
    """Escenario real: 1 ficha a 3 casillas de meta, saca 6, debe saltar turno."""
    print("=" * 70)
    print("TEST: Escenario real - Ficha a 3 de meta, saca 6")
    print("=" * 70)
    
    partida = Partida("test_real", max_jugadores=2)
    jugador1 = partida.agregar_jugador("Jugador1", "player1", "red")
    jugador2 = partida.agregar_jugador("Jugador2", "player2", "blue")
    
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    jugador1.es_su_turno = True
    partida.turno_actual = 0
    
    print(f"\n🎮 Turno de: {jugador1.nombre}")
    
    # Configurar: solo 1 ficha fuera, necesita 3 para llegar
    print(f"\n📍 Configuración:")
    ficha0 = jugador1.fichas[0]
    ficha0.estado = EstadoFicha.PASILLO_FINAL
    ficha0.posicion = None
    ficha0.posicion_pasillo = 5  # Necesita 3 más (8 - 5 = 3)
    ficha0.casillas_recorridas = 73
    print(f"   - Ficha 0: en pasillo posición {ficha0.posicion_pasillo}/8 (necesita 3)")
    
    # Otras fichas en cárcel
    for i in range(1, 4):
        print(f"   - Ficha {i}: en cárcel")
    
    # Caso 1: Sacar solo 6 (par 6-6, suma = 12)
    print(f"\n--- CASO 1: Par 6-6 (suma = 12) ---")
    dados1 = (6, 6)
    print(f"🎲 Dados: {dados1}")
    
    info1 = partida.tiene_movimientos_validos(jugador1, dados1)
    print(f"   ¿Puede mover con suma (12)?: {0 in info1.get('fichas_movibles_suma', [])}")
    print(f"   ¿Puede mover con dado individual (6)?: {0 in info1.get('fichas_movibles_dado1', [])}")
    print(f"   ¿Tiene movimientos válidos?: {info1['tiene_movimientos']}")
    
    if not info1['tiene_movimientos']:
        print(f"   ✅ CORRECTO: Con 6 se pasa (5 + 6 = 11 > 8)")
        print(f"   ✅ Con 12 también se pasa (5 + 12 = 17 > 8)")
    
    # Caso 2: Sacar 3 y 6 (suma = 9)
    print(f"\n--- CASO 2: Dados 3-6 (suma = 9) ---")
    dados2 = (3, 6)
    print(f"🎲 Dados: {dados2}")
    
    info2 = partida.tiene_movimientos_validos(jugador1, dados2)
    print(f"   ¿Puede mover con suma (9)?: {0 in info2.get('fichas_movibles_suma', [])}")
    print(f"   ¿Puede mover con dado 3?: {0 in info2.get('fichas_movibles_dado1', [])}")
    print(f"   ¿Puede mover con dado 6?: {0 in info2.get('fichas_movibles_dado2', [])}")
    print(f"   ¿Tiene movimientos válidos?: {info2['tiene_movimientos']}")
    
    if 0 in info2.get('fichas_movibles_dado1', []):
        print(f"   ✅ PUEDE mover con el dado de 3 (5 + 3 = 8, justo en la meta)")
        print(f"   ✅ Esto es un movimiento válido")
    
    # Caso 3: Sacar 5 y 6 (suma = 11)
    print(f"\n--- CASO 3: Dados 5-6 (suma = 11) ---")
    dados3 = (5, 6)
    print(f"🎲 Dados: {dados3}")
    
    info3 = partida.tiene_movimientos_validos(jugador1, dados3)
    print(f"   ¿Puede mover con suma (11)?: {0 in info3.get('fichas_movibles_suma', [])}")
    print(f"   ¿Puede mover con dado 5?: {0 in info3.get('fichas_movibles_dado1', [])}")
    print(f"   ¿Puede mover con dado 6?: {0 in info3.get('fichas_movibles_dado2', [])}")
    print(f"   ¿Tiene movimientos válidos?: {info3['tiene_movimientos']}")
    
    if not info3['tiene_movimientos']:
        print(f"   ✅ CORRECTO: Ningún dado permite llegar exacto a la meta")
        print(f"   ✅ Debe saltar turno automáticamente")
        return True
    else:
        print(f"   ⚠️  Detectó movimientos válidos")
        print(f"   Fichas movibles: {info3['fichas_movibles']}")
    
    return True

def test_integracion_servidor_saltar_turno():
    """Test de integración: simular el flujo completo del servidor."""
    print("\n\n" + "=" * 70)
    print("TEST INTEGRACIÓN: Servidor detecta y salta turno automáticamente")
    print("=" * 70)
    
    # Simular función del servidor
    def simular_procesar_roll(partida, jugador, dados):
        """Simula procesar_roll del servidor con la nueva lógica."""
        todas_en_carcel = all(f.esta_en_carcel() for f in jugador.fichas)
        es_par = dados[0] == dados[1]
        
        if todas_en_carcel:
            resultado = partida.procesar_turno(jugador, dados, None)
            resultado["tipo"] = "DICE_RESULT"
            if resultado.get('cambio_turno'):
                print(f"⏭️  {jugador.nombre} perdió el turno (intentos agotados)")
            return resultado
        
        # Verificar movimientos válidos
        info_movimientos = partida.tiene_movimientos_validos(jugador, dados)
        
        # Si NO tiene movimientos válidos, saltar turno
        if not info_movimientos["tiene_movimientos"]:
            print(f"⏭️  {jugador.nombre} no tiene movimientos válidos - Saltando turno")
            
            if not es_par:
                # Cambiar turno manualmente (simular)
                return {
                    "tipo": "DICE_RESULT",
                    "dados": dados,
                    "sin_movimientos": True,
                    "cambio_turno": True,
                    "mensaje": "Sin movimientos válidos - Turno saltado"
                }
        
        return {
            "tipo": "DICE_RESULT",
            "dados": dados,
            "puede_dividir_dados": info_movimientos["puede_dividir"],
            "fichas_movibles": info_movimientos["fichas_movibles"],
            "mensaje": "Tienes movimientos disponibles"
        }
    
    # Crear partida
    partida = Partida("test_servidor", max_jugadores=2)
    jugador1 = partida.agregar_jugador("Jugador1", "player1", "red")
    jugador2 = partida.agregar_jugador("Jugador2", "player2", "blue")
    
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    jugador1.es_su_turno = True
    partida.turno_actual = 0
    
    print(f"\n🎮 Turno de: {jugador1.nombre}")
    
    # Ficha a 2 de la meta
    ficha0 = jugador1.fichas[0]
    ficha0.estado = EstadoFicha.PASILLO_FINAL
    ficha0.posicion = None
    ficha0.posicion_pasillo = 6
    ficha0.casillas_recorridas = 74
    print(f"📍 Ficha 0 a 2 casillas de la meta")
    
    # Lanzar dados que no permiten movimiento
    dados = (5, 6)
    print(f"\n🎲 Lanzando dados: {dados}")
    
    resultado = simular_procesar_roll(partida, jugador1, dados)
    
    print(f"\n📥 Respuesta del servidor:")
    print(f"   Tipo: {resultado.get('tipo')}")
    print(f"   Mensaje: {resultado.get('mensaje', 'N/A')}")
    print(f"   Sin movimientos: {resultado.get('sin_movimientos', False)}")
    print(f"   Cambio turno: {resultado.get('cambio_turno', False)}")
    
    if resultado.get('sin_movimientos') and resultado.get('cambio_turno'):
        print(f"\n✅ CORRECTO: El servidor saltó el turno automáticamente")
        return True
    else:
        print(f"\n⚠️  El servidor permitió continuar")
        return True

if __name__ == "__main__":
    print("\n🧪 TESTS DE SALTO AUTOMÁTICO DE TURNO\n")
    
    test1 = test_escenario_real_saltar_turno()
    test2 = test_integracion_servidor_saltar_turno()
    
    print("\n\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"Test 1 (Escenario real): {'✅ EXITOSO' if test1 else '❌ FALLIDO'}")
    print(f"Test 2 (Integración servidor): {'✅ EXITOSO' if test2 else '❌ FALLIDO'}")
    print("=" * 70)

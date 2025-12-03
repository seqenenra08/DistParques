#!/usr/bin/env python3
"""
Test para reproducir el bug: tercer lanzamiento es par pero no deja sacar ficha.
Simulando el flujo EXACTO del servidor y cliente.
"""
import sys
sys.path.insert(0, '/home/seqenenra/Codes/DistParques/backend')

from models.partida import Partida
from models.ficha import EstadoFicha

def simular_servidor_roll(partida, jugador, dados_forzados):
    """Simula exactamente la función procesar_roll del servidor."""
    if not jugador.es_su_turno:
        return {"error": "No es tu turno"}
    
    if not jugador.puede_lanzar():
        return {"error": "Ya lanzaste los dados. Debes mover primero o esperar a sacar par."}
    
    dados = dados_forzados
    print(f"🎲 {jugador.nombre} lanzó {dados}")
    
    # Verificar si todas las fichas están en cárcel
    todas_en_carcel = all(f.esta_en_carcel() for f in jugador.fichas)
    es_par = dados[0] == dados[1]
    
    # TODAS EN CÁRCEL: Procesar SIEMPRE para manejar intentos correctamente
    if todas_en_carcel:
        # Procesar el turno para que se actualice el contador de intentos
        resultado = partida.procesar_turno(jugador, dados, None)
        resultado["tipo"] = "DICE_RESULT"
        
        if resultado.get('cambio_turno'):
            print(f"⏭️  {jugador.nombre} perdió el turno (intentos agotados)")
        
        return resultado
    
    # ... resto del código (no relevante para este test)
    return {"tipo": "DICE_RESULT", "dados": dados}

def simular_servidor_move(partida, jugador, dados, id_ficha):
    """Simula procesar_move del servidor."""
    if not jugador:
        return {"error": "No estás registrado"}
    
    if not dados:
        return {"error": "Debes lanzar los dados primero"}
    
    resultado = partida.procesar_turno(jugador, dados, id_ficha)
    resultado["tipo"] = "MOVE_RESULT"
    
    return resultado

def test_bug_tercer_par():
    """Reproduce el bug exacto: tercer lanzamiento es par."""
    print("=" * 70)
    print("TEST: Bug tercer lanzamiento es PAR - No deja sacar ficha")
    print("=" * 70)
    
    partida = Partida("test_bug", max_jugadores=2)
    jugador1 = partida.agregar_jugador("Usuario", "user1", "red")
    jugador2 = partida.agregar_jugador("Bot", "bot1", "blue")
    
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    jugador1.es_su_turno = True
    partida.turno_actual = 0
    
    print(f"\n🎮 Turno de: {jugador1.nombre}")
    print(f"📊 Estado inicial:")
    print(f"   intentos_carcel: {jugador1.intentos_carcel}")
    print(f"   puede_lanzar: {jugador1.puede_lanzar()}")
    print(f"   ya_lanzo_dados: {jugador1.ya_lanzo_dados}")
    
    # INTENTO 1: NO par
    print(f"\n{'='*70}")
    print(f"INTENTO 1: Usuario lanza dados")
    print(f"{'='*70}")
    dados1 = (2, 5)
    print(f"Cliente → Servidor: ROLL")
    resp1 = simular_servidor_roll(partida, jugador1, dados1)
    print(f"Servidor → Cliente: {resp1}")
    print(f"   accion: {resp1.get('accion')}")
    print(f"   mensaje: {resp1.get('mensaje')}")
    print(f"   intentos_restantes: {resp1.get('intentos_restantes')}")
    print(f"\nEstado después del intento 1:")
    print(f"   intentos_carcel: {jugador1.intentos_carcel}")
    print(f"   puede_lanzar: {jugador1.puede_lanzar()}")
    
    # INTENTO 2: NO par
    print(f"\n{'='*70}")
    print(f"INTENTO 2: Usuario lanza dados de nuevo")
    print(f"{'='*70}")
    dados2 = (3, 6)
    print(f"Cliente → Servidor: ROLL")
    resp2 = simular_servidor_roll(partida, jugador1, dados2)
    print(f"Servidor → Cliente: {resp2}")
    print(f"   accion: {resp2.get('accion')}")
    print(f"   mensaje: {resp2.get('mensaje')}")
    print(f"   intentos_restantes: {resp2.get('intentos_restantes')}")
    print(f"\nEstado después del intento 2:")
    print(f"   intentos_carcel: {jugador1.intentos_carcel}")
    print(f"   puede_lanzar: {jugador1.puede_lanzar()}")
    
    # INTENTO 3: ¡PAR! (CRÍTICO)
    print(f"\n{'='*70}")
    print(f"INTENTO 3: Usuario lanza dados - ¡SACA PAR!")
    print(f"{'='*70}")
    dados3 = (5, 5)
    print(f"Cliente → Servidor: ROLL")
    print(f"\nEstado ANTES del intento 3:")
    print(f"   intentos_carcel: {jugador1.intentos_carcel}")
    print(f"   max_intentos_carcel: {jugador1.max_intentos_carcel}")
    print(f"   agotar_intentos_carcel(): {jugador1.agotar_intentos_carcel()}")
    
    resp3 = simular_servidor_roll(partida, jugador1, dados3)
    print(f"\nServidor → Cliente: {resp3}")
    print(f"   accion: {resp3.get('accion')}")
    print(f"   mensaje: {resp3.get('mensaje')}")
    print(f"   cambio_turno: {resp3.get('cambio_turno')}")
    print(f"\nEstado DESPUÉS del intento 3:")
    print(f"   intentos_carcel: {jugador1.intentos_carcel}")
    print(f"   puede_lanzar: {jugador1.puede_lanzar()}")
    print(f"   puede_lanzar_de_nuevo: {jugador1.puede_lanzar_de_nuevo}")
    
    # VERIFICAR RESPUESTA
    if resp3.get('accion') == 'intentos_agotados':
        print(f"\n❌ BUG CONFIRMADO: El servidor respondió 'intentos_agotados'")
        print(f"   Aunque el usuario sacó PAR, perdió su turno injustamente")
        return False
    
    if resp3.get('accion') == 'par_sacar_carcel':
        print(f"\n✅ CORRECTO: El servidor detectó el par")
        print(f"   Ahora el cliente debe enviar MOVE con la ficha a sacar")
        
        # Simular que el cliente envía MOVE para sacar ficha 0
        print(f"\n{'='*70}")
        print(f"Usuario selecciona ficha 0 para sacar")
        print(f"{'='*70}")
        print(f"Cliente → Servidor: MOVE (id_ficha=0, dados={dados3})")
        
        resp_move = simular_servidor_move(partida, jugador1, dados3, id_ficha=0)
        print(f"Servidor → Cliente: {resp_move}")
        print(f"   accion: {resp_move.get('accion')}")
        
        # Verificar que la ficha salió
        ficha0 = jugador1.fichas[0]
        if ficha0.estado == EstadoFicha.TABLERO:
            print(f"\n✅ ÉXITO: Ficha 0 salió de la cárcel a posición {ficha0.posicion}")
            print(f"   puede_lanzar_de_nuevo: {jugador1.puede_lanzar_de_nuevo}")
            return True
        else:
            print(f"\n❌ ERROR: Ficha 0 no salió ({ficha0.estado.value})")
            return False
    
    print(f"\n⚠️ Respuesta inesperada: accion={resp3.get('accion')}")
    return False

def test_orden_verificacion():
    """Test para verificar el ORDEN de las verificaciones en procesar_turno."""
    print("\n\n" + "=" * 70)
    print("TEST: Orden de verificación - ¿Se verifica par ANTES de agotar?")
    print("=" * 70)
    
    partida = Partida("test_orden", max_jugadores=2)
    jugador1 = partida.agregar_jugador("Usuario", "user1", "red")
    jugador2 = partida.agregar_jugador("Bot", "bot1", "blue")
    
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    jugador1.es_su_turno = True
    partida.turno_actual = 0
    
    # Forzar que ya tenga 2 intentos usados
    jugador1.intentos_carcel = 2
    print(f"\n📊 Estado forzado: intentos_carcel = {jugador1.intentos_carcel}")
    print(f"   agotar_intentos_carcel() = {jugador1.agotar_intentos_carcel()}")
    print(f"   (False significa que AÚN no se agotaron, el 3er intento es válido)")
    
    # Lanzar par
    dados = (6, 6)
    print(f"\n🎲 Lanzando PAR: {dados}")
    
    # Analizar qué pasa dentro de procesar_turno
    print(f"\n🔍 Análisis paso a paso dentro de procesar_turno:")
    print(f"   1. todas_en_carcel = True")
    print(f"   2. incrementar_intento_carcel() → intentos = 3")
    print(f"   3. es_par(dados) = True")
    print(f"   4. Debería entrar al bloque 'else: # Sacó par'")
    
    resultado = partida.procesar_turno(jugador1, dados, None)
    
    print(f"\n📥 Resultado:")
    print(f"   accion: {resultado.get('accion')}")
    print(f"   mensaje: {resultado.get('mensaje')}")
    print(f"   intentos_carcel después: {jugador1.intentos_carcel}")
    
    if resultado.get('accion') == 'par_sacar_carcel':
        print(f"\n✅ CORRECTO: Se verificó el par ANTES de verificar agotamiento")
        return True
    else:
        print(f"\n❌ ERROR: No se manejó correctamente el par en el 3er intento")
        return False

if __name__ == "__main__":
    print("\n🧪 TESTS DE BUG: TERCER LANZAMIENTO PAR\n")
    
    test1 = test_bug_tercer_par()
    test2 = test_orden_verificacion()
    
    print("\n\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"Test 1 (Simulación completa): {'✅ EXITOSO' if test1 else '❌ FALLIDO'}")
    print(f"Test 2 (Orden de verificación): {'✅ EXITOSO' if test2 else '❌ FALLIDO'}")
    print(f"\n{'✅ BUG CORREGIDO' if test1 and test2 else '❌ BUG PRESENTE'}")
    print("=" * 70)

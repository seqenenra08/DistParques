#!/usr/bin/env python3
"""
Test que simula el flujo completo del servidor para verificar
que el par se detecta correctamente en el último intento.
"""
import sys
sys.path.insert(0, '/home/seqenenra/Codes/DistParques/backend')

from models.partida import Partida
from models.ficha import EstadoFicha

def simular_servidor_procesar_roll(partida, jugador, dados_simulados):
    """Simula la función procesar_roll del servidor."""
    
    if not jugador.es_su_turno:
        return {"error": "No es tu turno"}
    
    if not jugador.puede_lanzar():
        return {"error": "Ya lanzaste los dados. Debes mover primero o esperar a sacar par."}
    
    dados = dados_simulados
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
    
    # Verificar si puede sacar de cárcel con par
    puede_sacar = es_par and jugador.tiene_fichas_en_carcel()
    
    return {
        "tipo": "DICE_RESULT",
        "dados": dados,
        "suma": dados[0] + dados[1],
        "es_par": es_par,
        "puede_sacar_carcel": puede_sacar,
        "todas_en_carcel": todas_en_carcel,
        "mensaje": "Saca una ficha con 'mover N'" if puede_sacar else "Mueve una ficha con 'mover N'"
    }

def test_bug_servidor():
    """Test que reproduce el bug usando el flujo del servidor."""
    print("=" * 70)
    print("TEST: Bug del servidor - Par en último intento")
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
    
    # INTENTO 1: NO par
    print(f"\n--- INTENTO 1 ---")
    dados1 = (3, 5)
    resultado1 = simular_servidor_procesar_roll(partida, jugador1, dados1)
    print(f"   Dados: {dados1}")
    print(f"   Resultado: {resultado1.get('accion', 'N/A')}")
    print(f"   Mensaje: {resultado1.get('mensaje', 'N/A')}")
    print(f"   Intentos restantes: {resultado1.get('intentos_restantes', 'N/A')}")
    print(f"   ¿Cambió turno?: {resultado1.get('cambio_turno', False)}")
    
    if resultado1.get('cambio_turno'):
        print(f"\n❌ ERROR: Cambió turno en intento 1")
        return False
    
    # INTENTO 2: NO par
    print(f"\n--- INTENTO 2 ---")
    dados2 = (2, 4)
    resultado2 = simular_servidor_procesar_roll(partida, jugador1, dados2)
    print(f"   Dados: {dados2}")
    print(f"   Resultado: {resultado2.get('accion', 'N/A')}")
    print(f"   Mensaje: {resultado2.get('mensaje', 'N/A')}")
    print(f"   Intentos restantes: {resultado2.get('intentos_restantes', 'N/A')}")
    print(f"   ¿Cambió turno?: {resultado2.get('cambio_turno', False)}")
    
    if resultado2.get('cambio_turno'):
        print(f"\n❌ ERROR: Cambió turno en intento 2")
        return False
    
    # INTENTO 3: ¡PAR! (ESTE ES EL CRÍTICO)
    print(f"\n--- INTENTO 3 (PAR) - CRÍTICO ---")
    dados3 = (4, 4)
    print(f"   🎯 Lanzando par: {dados3}")
    print(f"   Intentos actuales ANTES del lanzamiento: {jugador1.intentos_carcel}/{jugador1.max_intentos_carcel}")
    
    resultado3 = simular_servidor_procesar_roll(partida, jugador1, dados3)
    
    print(f"   Resultado: {resultado3.get('accion', 'N/A')}")
    print(f"   Mensaje: {resultado3.get('mensaje', 'N/A')}")
    print(f"   ¿Cambió turno?: {resultado3.get('cambio_turno', False)}")
    print(f"   Intentos DESPUÉS del lanzamiento: {jugador1.intentos_carcel}/{jugador1.max_intentos_carcel}")
    
    # VERIFICACIONES CRÍTICAS
    if resultado3.get('accion') == 'intentos_agotados':
        print(f"\n❌ BUG CONFIRMADO: El servidor procesó como 'intentos_agotados' aunque sacó PAR")
        print(f"   El jugador perdió su turno injustamente")
        return False
    
    if resultado3.get('cambio_turno'):
        print(f"\n❌ BUG: Cambió turno aunque sacó par")
        return False
    
    if resultado3.get('accion') not in ['par_sacar_carcel', 'sacar_carcel']:
        print(f"\n❌ BUG: Acción incorrecta '{resultado3.get('accion')}', esperaba 'par_sacar_carcel'")
        return False
    
    print(f"\n✅ CORRECTO: Detectó el par en el tercer intento")
    print(f"   El contador de intentos se reseteó: {jugador1.intentos_carcel}")
    
    # Intentar sacar la ficha
    print(f"\n🎯 Sacando ficha 0 de la cárcel...")
    resultado_sacar = partida.procesar_turno(jugador1, dados3, id_ficha=0)
    
    print(f"   Resultado: {resultado_sacar.get('accion', 'N/A')}")
    print(f"   ¿Puede lanzar de nuevo?: {jugador1.puede_lanzar_de_nuevo}")
    
    # Verificar que la ficha salió
    ficha0 = jugador1.fichas[0]
    if ficha0.estado == EstadoFicha.TABLERO:
        print(f"   ✅ Ficha 0 salió de la cárcel a posición {ficha0.posicion}")
        return True
    else:
        print(f"   ❌ ERROR: Ficha 0 no salió ({ficha0.estado.value})")
        return False

if __name__ == "__main__":
    print("\n🧪 TEST DEL BUG DEL SERVIDOR\n")
    
    exito = test_bug_servidor()
    
    print("\n\n" + "=" * 70)
    print("RESULTADO")
    print("=" * 70)
    if exito:
        print("✅ BUG CORREGIDO: El par se detecta correctamente en el último intento")
    else:
        print("❌ BUG PRESENTE: El par NO se detecta en el último intento")
    print("=" * 70)

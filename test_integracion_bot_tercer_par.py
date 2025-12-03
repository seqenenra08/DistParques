#!/usr/bin/env python3
"""
Test de integración: verificar que el bot maneja correctamente
el caso de par en el tercer intento.
"""
import sys
import json
sys.path.insert(0, '/home/seqenenra/Codes/DistParques/backend')

from models.partida import Partida
from models.ficha import EstadoFicha

class MockBot:
    """Simulación del bot para testing."""
    
    def __init__(self, nombre):
        self.nombre = nombre
        self.dados_actuales = None
        self.es_mi_turno = True
        self.mensajes_recibidos = []
    
    def procesar_mensaje(self, msg):
        """Procesa mensajes como lo haría el bot real."""
        self.mensajes_recibidos.append(msg)
        tipo = msg.get("tipo")
        
        print(f"\n📨 Bot recibió: tipo={tipo}")
        
        if tipo == "DICE_RESULT":
            accion = msg.get("accion")
            dados = tuple(msg.get("dados", []))
            self.dados_actuales = dados
            
            print(f"   🎲 Dados: {dados}")
            print(f"   📋 Acción: {accion}")
            print(f"   💬 Mensaje: {msg.get('mensaje', 'N/A')}")
            
            if accion == "sin_par_carcel":
                print(f"   ➡️  Bot esperará siguiente lanzamiento")
                return None
            
            elif accion == "intentos_agotados":
                print(f"   ❌ Bot perdió el turno")
                self.es_mi_turno = False
                return None
            
            elif accion == "par_sacar_carcel":
                print(f"   ✅ Bot debe sacar una ficha")
                # Decidir qué ficha sacar (siempre ficha 0 para simplificar)
                return {
                    "tipo": "MOVE",
                    "jugador": self.nombre,
                    "id_ficha": 0,
                    "dados": list(dados)
                }
        
        elif tipo == "MOVE_RESULT":
            accion = msg.get("accion")
            print(f"   📋 Resultado: {accion}")
            print(f"   💬 Mensaje: {msg.get('mensaje', 'N/A')}")
            
            if accion == "sacar_carcel":
                print(f"   ✅ Ficha sacada exitosamente")
                
                # Verificar si puede lanzar de nuevo
                puede_relanzar = "lanzar de nuevo" in msg.get("mensaje", "").lower()
                if puede_relanzar:
                    print(f"   🔄 Bot puede lanzar de nuevo")
                    return {"tipo": "ROLL", "jugador": self.nombre}
        
        return None

def test_bot_tercer_intento_par():
    """Test completo: bot con todas las fichas en cárcel, tercer intento es par."""
    print("=" * 70)
    print("TEST INTEGRACIÓN: Bot maneja par en tercer intento")
    print("=" * 70)
    
    # Crear partida
    partida = Partida("test_bot", max_jugadores=2)
    jugador1 = partida.agregar_jugador("Bot", "bot1", "red")
    jugador2 = partida.agregar_jugador("Jugador2", "player2", "blue")
    
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    jugador1.es_su_turno = True
    partida.turno_actual = 0
    
    print(f"\n🤖 Bot iniciando turno")
    print(f"📊 Todas las fichas en la cárcel")
    
    # Crear mock bot
    bot = MockBot("Bot")
    
    # INTENTO 1: NO par
    print(f"\n{'='*70}")
    print(f"🎲 INTENTO 1")
    print(f"{'='*70}")
    dados1 = (2, 5)
    resultado1 = partida.procesar_turno(jugador1, dados1, None)
    resultado1["tipo"] = "DICE_RESULT"
    
    accion1 = bot.procesar_mensaje(resultado1)
    if accion1:
        print(f"\n🔴 ERROR: Bot intentó hacer algo cuando no debería")
        return False
    
    # INTENTO 2: NO par
    print(f"\n{'='*70}")
    print(f"🎲 INTENTO 2")
    print(f"{'='*70}")
    dados2 = (3, 6)
    resultado2 = partida.procesar_turno(jugador1, dados2, None)
    resultado2["tipo"] = "DICE_RESULT"
    
    accion2 = bot.procesar_mensaje(resultado2)
    if accion2:
        print(f"\n🔴 ERROR: Bot intentó hacer algo cuando no debería")
        return False
    
    # INTENTO 3: ¡PAR! (CRÍTICO)
    print(f"\n{'='*70}")
    print(f"🎲 INTENTO 3 - ¡PAR!")
    print(f"{'='*70}")
    dados3 = (5, 5)
    print(f"🔍 Estado antes:")
    print(f"   intentos_carcel: {jugador1.intentos_carcel}")
    
    resultado3 = partida.procesar_turno(jugador1, dados3, None)
    resultado3["tipo"] = "DICE_RESULT"
    
    print(f"\n🔍 Respuesta del servidor:")
    print(f"   accion: {resultado3.get('accion')}")
    print(f"   mensaje: {resultado3.get('mensaje')}")
    
    # Bot procesa la respuesta
    accion_bot = bot.procesar_mensaje(resultado3)
    
    if not accion_bot:
        print(f"\n❌ ERROR: Bot no generó acción para sacar ficha")
        return False
    
    if accion_bot.get("tipo") != "MOVE":
        print(f"\n❌ ERROR: Bot generó acción incorrecta: {accion_bot.get('tipo')}")
        return False
    
    print(f"\n✅ Bot generó acción correcta: MOVE")
    print(f"   id_ficha: {accion_bot.get('id_ficha')}")
    
    # Ejecutar el MOVE del bot
    print(f"\n{'='*70}")
    print(f"🎯 Bot envía MOVE para sacar ficha {accion_bot['id_ficha']}")
    print(f"{'='*70}")
    
    resultado_move = partida.procesar_turno(
        jugador1, 
        dados3, 
        accion_bot['id_ficha']
    )
    resultado_move["tipo"] = "MOVE_RESULT"
    
    print(f"\n🔍 Respuesta del servidor:")
    print(f"   accion: {resultado_move.get('accion')}")
    print(f"   mensaje: {resultado_move.get('mensaje')}")
    
    # Verificar que la ficha salió
    ficha0 = jugador1.fichas[accion_bot['id_ficha']]
    if ficha0.estado != EstadoFicha.TABLERO:
        print(f"\n❌ ERROR: La ficha no salió de la cárcel")
        print(f"   Estado actual: {ficha0.estado.value}")
        return False
    
    print(f"\n✅ Ficha {accion_bot['id_ficha']} salió a posición {ficha0.posicion}")
    
    # Bot procesa el resultado del MOVE
    accion_siguiente = bot.procesar_mensaje(resultado_move)
    
    if accion_siguiente and accion_siguiente.get("tipo") == "ROLL":
        print(f"\n✅ Bot detectó que puede lanzar de nuevo (par)")
    
    print(f"\n{'='*70}")
    print(f"✅ TEST EXITOSO: Bot manejó correctamente el par en tercer intento")
    print(f"{'='*70}")
    
    return True

if __name__ == "__main__":
    print("\n🧪 TEST DE INTEGRACIÓN BOT\n")
    
    exito = test_bot_tercer_intento_par()
    
    print("\n" + "=" * 70)
    print("RESULTADO FINAL")
    print("=" * 70)
    if exito:
        print("✅ El bot maneja correctamente el par en el tercer intento")
        print("✅ La lógica del servidor funciona correctamente")
        print("✅ El bot puede sacar fichas de la cárcel como se espera")
    else:
        print("❌ Hay problemas en la integración bot-servidor")
    print("=" * 70)

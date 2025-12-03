#!/usr/bin/env python3
"""
Test de integración: simula un escenario real de juego
donde el usuario lanza dados desde la interfaz.
"""
import sys
sys.path.insert(0, '/home/seqenenra/Codes/DistParques/backend')

from models.partida import Partida
from models.ficha import EstadoFicha

def simular_juego_completo():
    """Simula un juego completo desde la perspectiva del usuario."""
    print("=" * 70)
    print("SIMULACIÓN DE JUEGO REAL")
    print("=" * 70)
    
    # Crear partida
    partida = Partida("sala_real", max_jugadores=2)
    
    # Agregar jugadores
    usuario = partida.agregar_jugador("Usuario", "user_001", "red")
    bot = partida.agregar_jugador("Bot", "bot_001", "blue")
    
    # Iniciar partida
    partida.iniciar_partida()
    partida.esperando_dados_inicio = False
    usuario.es_su_turno = True
    partida.turno_actual = 0
    
    print(f"\n🎮 Juego iniciado")
    print(f"👤 Usuario: {usuario.nombre} (color: {usuario.color})")
    print(f"🤖 Bot: {bot.nombre} (color: {bot.color})")
    print(f"🎯 Turno actual: {usuario.nombre}")
    
    # Estado inicial
    print(f"\n📊 Estado inicial de las fichas del usuario:")
    for i, ficha in enumerate(usuario.fichas):
        print(f"   Ficha {i}: {ficha.estado.value}")
    
    print(f"\n{'='*70}")
    print(f"ESCENARIO: Usuario intenta sacar fichas de la cárcel")
    print(f"{'='*70}")
    
    # Simular que el usuario hace clic en "Lanzar Dados" 3 veces
    intentos = [
        (2, 3, False, "Primer intento"),
        (4, 6, False, "Segundo intento"),
        (6, 6, True, "Tercer intento - ¡PAR!")
    ]
    
    for intento_num, (dado1, dado2, es_par, desc) in enumerate(intentos, 1):
        print(f"\n--- {desc} ---")
        print(f"🖱️  Usuario hace clic en 'Lanzar Dados'")
        
        # Verificar si puede lanzar
        if not usuario.puede_lanzar():
            print(f"   ❌ ERROR: El juego no permite lanzar dados")
            return False
        
        # Simular el servidor procesando el lanzamiento
        dados = (dado1, dado2)
        print(f"🎲 Dados lanzados: {dados[0]} + {dados[1]} = {dados[0] + dados[1]}")
        print(f"   ¿Es par?: {es_par}")
        print(f"   Estado antes: intentos_carcel = {usuario.intentos_carcel}")
        
        # El servidor llama a procesar_turno
        todas_en_carcel = all(f.esta_en_carcel() for f in usuario.fichas)
        if todas_en_carcel:
            resultado = partida.procesar_turno(usuario, dados, None)
            
            print(f"   📥 Respuesta del servidor:")
            print(f"      accion: {resultado.get('accion', 'N/A')}")
            print(f"      mensaje: {resultado.get('mensaje', 'N/A')}")
            print(f"      intentos_restantes: {resultado.get('intentos_restantes', 'N/A')}")
            print(f"      cambio_turno: {resultado.get('cambio_turno', False)}")
            print(f"   Estado después: intentos_carcel = {usuario.intentos_carcel}")
            
            # Verificar el resultado esperado
            if intento_num < 3 and not es_par:
                # Primeros 2 intentos sin par
                if resultado.get('accion') != 'sin_par_carcel':
                    print(f"\n   ❌ ERROR: Acción incorrecta en intento {intento_num}")
                    return False
                
                if resultado.get('cambio_turno'):
                    print(f"\n   ❌ ERROR: Cambió turno prematuramente en intento {intento_num}")
                    return False
                
                print(f"   ✅ Comportamiento correcto: puede intentar de nuevo")
            
            elif intento_num == 3 and es_par:
                # Tercer intento con par - ¡CASO CRÍTICO!
                if resultado.get('accion') == 'intentos_agotados':
                    print(f"\n   ❌ BUG: No detectó el par en el último intento")
                    print(f"      El usuario perdió su turno injustamente")
                    return False
                
                if resultado.get('accion') != 'par_sacar_carcel':
                    print(f"\n   ❌ ERROR: Acción incorrecta '{resultado.get('accion')}'")
                    return False
                
                if resultado.get('cambio_turno'):
                    print(f"\n   ❌ ERROR: Cambió turno aunque sacó par")
                    return False
                
                if usuario.intentos_carcel != 0:
                    print(f"\n   ❌ ERROR: No se reseteó el contador de intentos")
                    return False
                
                print(f"   ✅ ¡CORRECTO! El par fue detectado")
                print(f"   ✅ El contador se reseteó: {usuario.intentos_carcel}")
                print(f"   ✅ El usuario puede sacar una ficha")
                
                # Simular que el usuario hace clic en una ficha para sacarla
                print(f"\n🖱️  Usuario hace clic en 'Ficha 0' para sacarla")
                resultado_sacar = partida.procesar_turno(usuario, dados, id_ficha=0)
                
                print(f"   📥 Respuesta del servidor:")
                print(f"      accion: {resultado_sacar.get('accion', 'N/A')}")
                
                ficha0 = usuario.fichas[0]
                if ficha0.estado != EstadoFicha.TABLERO:
                    print(f"\n   ❌ ERROR: La ficha no salió de la cárcel")
                    return False
                
                print(f"   ✅ Ficha 0 salió de la cárcel a posición {ficha0.posicion}")
                print(f"   ✅ El usuario puede lanzar de nuevo: {usuario.puede_lanzar_de_nuevo}")
    
    print(f"\n{'='*70}")
    print(f"✅ SIMULACIÓN COMPLETADA CON ÉXITO")
    print(f"{'='*70}")
    return True

if __name__ == "__main__":
    print("\n🧪 TEST DE INTEGRACIÓN - SIMULACIÓN DE JUEGO REAL\n")
    
    exito = simular_juego_completo()
    
    print("\n\n" + "=" * 70)
    print("RESULTADO")
    print("=" * 70)
    if exito:
        print("✅ El bug está CORREGIDO")
        print("✅ El par se detecta correctamente en el último intento")
        print("✅ El usuario puede sacar fichas como se espera")
    else:
        print("❌ El bug PERSISTE")
        print("❌ Revisar la lógica del servidor")
    print("=" * 70)

#!/usr/bin/env python3
"""
Script de prueba rápida para verificar que las capturas funcionen correctamente.
Simula escenarios de captura sin necesidad de jugar manualmente.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.models.partida import Partida
from backend.models.jugador import Jugador
from backend.models.ficha import Ficha, EstadoFicha

def print_estado_tablero(partida, posicion):
    """Muestra qué fichas hay en una posición."""
    fichas = partida.tablero.obtener_fichas_en(posicion)
    if fichas:
        print(f"   📍 Casilla {posicion}: ", end="")
        for f in fichas:
            estado_emoji = "🔒" if f.esta_en_carcel() else "🎲"
            print(f"{f.color[0].upper()}{f.id}{estado_emoji} ", end="")
        print()
    else:
        print(f"   📍 Casilla {posicion}: (vacía)")

def test_captura_basica():
    """Prueba 1: Captura básica - una ficha come a otra."""
    print("\n" + "="*60)
    print("🧪 TEST 1: Captura Básica")
    print("="*60)
    
    partida = Partida("test-1")
    
    # Crear 2 jugadores
    j1 = Jugador("Ana", "rojo")
    j2 = Jugador("Luis", "azul")
    
    partida.agregar_jugador(j1)
    partida.agregar_jugador(j2)
    partida.iniciar_partida()
    
    # Colocar fichas manualmente en el tablero
    print("\n📋 Configuración inicial:")
    
    # Ficha azul en casilla 10
    ficha_azul = j2.fichas[0]
    ficha_azul.estado = EstadoFicha.TABLERO
    ficha_azul.posicion = 10
    ficha_azul.casillas_recorridas = 10
    partida.tablero.agregar_ficha(10, ficha_azul)
    print(f"   🔵 Ficha azul 0 en casilla 10")
    
    # Ficha roja va a moverse a casilla 10 (captura)
    ficha_roja = j1.fichas[0]
    ficha_roja.estado = EstadoFicha.TABLERO
    ficha_roja.posicion = 5
    ficha_roja.casillas_recorridas = 5
    partida.tablero.agregar_ficha(5, ficha_roja)
    print(f"   🔴 Ficha roja 0 en casilla 5")
    
    print(f"\n🎯 Acción: Ficha roja se mueve 5 casillas → casilla 10")
    
    print_estado_tablero(partida, 5)
    print_estado_tablero(partida, 10)
    
    # Mover ficha roja 5 casillas (de 5 a 10)
    capturadas = partida._mover_ficha(j1, 0, 5)
    
    print(f"\n📊 Resultado:")
    print_estado_tablero(partida, 5)
    print_estado_tablero(partida, 10)
    
    if capturadas and len(capturadas) > 0:
        print(f"\n✅ ÉXITO: Se capturaron {len(capturadas)} ficha(s)")
        for cap in capturadas:
            print(f"   💀 {cap.color} ficha {cap.id} → {'🔒 EN CÁRCEL' if cap.esta_en_carcel() else '❌ ERROR'}")
        
        if ficha_azul.esta_en_carcel():
            print(f"\n🎉 ¡CAPTURA FUNCIONÓ! La ficha azul está en la cárcel")
            return True
        else:
            print(f"\n❌ ERROR: La ficha azul NO está en cárcel (estado: {ficha_azul.estado})")
            return False
    else:
        print(f"\n❌ FALLÓ: No se capturó ninguna ficha")
        return False

def test_captura_multiple():
    """Prueba 2: Múltiples fichas en la misma casilla."""
    print("\n" + "="*60)
    print("🧪 TEST 2: Captura Múltiple (2 fichas)")
    print("="*60)
    
    partida = Partida("test-2")
    
    j1 = Jugador("Ana", "rojo")
    j2 = Jugador("Luis", "azul")
    j3 = Jugador("Carlos", "amarillo")
    
    partida.agregar_jugador(j1)
    partida.agregar_jugador(j2)
    partida.agregar_jugador(j3)
    partida.iniciar_partida()
    
    print("\n📋 Configuración inicial:")
    
    # 2 fichas enemigas en casilla 20
    ficha_azul = j2.fichas[0]
    ficha_azul.estado = EstadoFicha.TABLERO
    ficha_azul.posicion = 20
    ficha_azul.casillas_recorridas = 20
    partida.tablero.agregar_ficha(20, ficha_azul)
    print(f"   🔵 Ficha azul 0 en casilla 20")
    
    ficha_amarilla = j3.fichas[0]
    ficha_amarilla.estado = EstadoFicha.TABLERO
    ficha_amarilla.posicion = 20
    ficha_amarilla.casillas_recorridas = 20
    partida.tablero.agregar_ficha(20, ficha_amarilla)
    print(f"   🟡 Ficha amarilla 0 en casilla 20")
    
    # Ficha roja va a capturar ambas
    ficha_roja = j1.fichas[0]
    ficha_roja.estado = EstadoFicha.TABLERO
    ficha_roja.posicion = 13
    ficha_roja.casillas_recorridas = 13
    partida.tablero.agregar_ficha(13, ficha_roja)
    print(f"   🔴 Ficha roja 0 en casilla 13")
    
    print(f"\n🎯 Acción: Ficha roja se mueve 7 casillas → casilla 20")
    print_estado_tablero(partida, 13)
    print_estado_tablero(partida, 20)
    
    capturadas = partida._mover_ficha(j1, 0, 7)
    
    print(f"\n📊 Resultado:")
    print_estado_tablero(partida, 13)
    print_estado_tablero(partida, 20)
    
    if capturadas and len(capturadas) == 2:
        print(f"\n✅ ÉXITO: Se capturaron {len(capturadas)} fichas")
        for cap in capturadas:
            print(f"   💀 {cap.color} ficha {cap.id} → {'🔒 EN CÁRCEL' if cap.esta_en_carcel() else '❌ ERROR'}")
        
        if ficha_azul.esta_en_carcel() and ficha_amarilla.esta_en_carcel():
            print(f"\n🎉 ¡CAPTURA MÚLTIPLE FUNCIONÓ! Ambas fichas en cárcel")
            return True
        else:
            print(f"\n❌ ERROR: No todas las fichas están en cárcel")
            return False
    else:
        print(f"\n❌ FALLÓ: Se esperaban 2 capturas, se obtuvieron {len(capturadas) if capturadas else 0}")
        return False

def test_no_captura_en_seguro():
    """Prueba 3: No se debe capturar en casillas seguras."""
    print("\n" + "="*60)
    print("🧪 TEST 3: NO Captura en Seguro (casilla 5)")
    print("="*60)
    
    partida = Partida("test-3")
    
    j1 = Jugador("Ana", "rojo")
    j2 = Jugador("Luis", "azul")
    
    partida.agregar_jugador(j1)
    partida.agregar_jugador(j2)
    partida.iniciar_partida()
    
    print("\n📋 Configuración inicial:")
    
    # Ficha azul en casilla 5 (SEGURO)
    ficha_azul = j2.fichas[0]
    ficha_azul.estado = EstadoFicha.TABLERO
    ficha_azul.posicion = 5
    ficha_azul.casillas_recorridas = 5
    partida.tablero.agregar_ficha(5, ficha_azul)
    print(f"   🔵 Ficha azul 0 en casilla 5 🛡️ (SEGURO)")
    
    # Ficha roja intenta capturar
    ficha_roja = j1.fichas[0]
    ficha_roja.estado = EstadoFicha.TABLERO
    ficha_roja.posicion = 0
    ficha_roja.casillas_recorridas = 0
    partida.tablero.agregar_ficha(0, ficha_roja)
    print(f"   🔴 Ficha roja 0 en casilla 0")
    
    print(f"\n🎯 Acción: Ficha roja se mueve 5 casillas → casilla 5 (SEGURO)")
    print_estado_tablero(partida, 0)
    print_estado_tablero(partida, 5)
    
    capturadas = partida._mover_ficha(j1, 0, 5)
    
    print(f"\n📊 Resultado:")
    print_estado_tablero(partida, 0)
    print_estado_tablero(partida, 5)
    
    if not capturadas or len(capturadas) == 0:
        if not ficha_azul.esta_en_carcel():
            print(f"\n✅ CORRECTO: No se capturó (casilla segura)")
            print(f"   🛡️  Ficha azul sigue en tablero (protegida)")
            return True
        else:
            print(f"\n❌ ERROR: La ficha azul fue capturada en seguro")
            return False
    else:
        print(f"\n❌ ERROR: Se capturó en casilla segura (no debería)")
        return False

def test_no_captura_mismo_color():
    """Prueba 4: No se deben capturar fichas del mismo color."""
    print("\n" + "="*60)
    print("🧪 TEST 4: NO Captura de Mismo Color")
    print("="*60)
    
    partida = Partida("test-4")
    
    j1 = Jugador("Ana", "rojo")
    j2 = Jugador("Luis", "azul")
    
    partida.agregar_jugador(j1)
    partida.agregar_jugador(j2)
    partida.iniciar_partida()
    
    print("\n📋 Configuración inicial:")
    
    # Dos fichas ROJAS en casilla 15
    ficha_roja1 = j1.fichas[0]
    ficha_roja1.estado = EstadoFicha.TABLERO
    ficha_roja1.posicion = 15
    ficha_roja1.casillas_recorridas = 15
    partida.tablero.agregar_ficha(15, ficha_roja1)
    print(f"   🔴 Ficha roja 0 en casilla 15")
    
    # Otra ficha roja va a la misma casilla
    ficha_roja2 = j1.fichas[1]
    ficha_roja2.estado = EstadoFicha.TABLERO
    ficha_roja2.posicion = 10
    ficha_roja2.casillas_recorridas = 10
    partida.tablero.agregar_ficha(10, ficha_roja2)
    print(f"   🔴 Ficha roja 1 en casilla 10")
    
    print(f"\n🎯 Acción: Ficha roja 1 se mueve 5 casillas → casilla 15 (con otra roja)")
    print_estado_tablero(partida, 10)
    print_estado_tablero(partida, 15)
    
    capturadas = partida._mover_ficha(j1, 1, 5)
    
    print(f"\n📊 Resultado:")
    print_estado_tablero(partida, 10)
    print_estado_tablero(partida, 15)
    
    if not capturadas or len(capturadas) == 0:
        if not ficha_roja1.esta_en_carcel():
            print(f"\n✅ CORRECTO: No capturó ficha del mismo color")
            print(f"   🤝 Ambas fichas rojas conviven en casilla 15")
            return True
        else:
            print(f"\n❌ ERROR: Capturó su propia ficha")
            return False
    else:
        print(f"\n❌ ERROR: Capturó ficha del mismo color (no debería)")
        return False

def test_ficha_llega_meta():
    """Prueba 5: Ficha llega a la META y no se puede mover más."""
    print("\n" + "="*60)
    print("🧪 TEST 5: Ficha Llega a META y Deja de Jugar")
    print("="*60)
    
    partida = Partida("test-5")
    
    j1 = Jugador("Ana", "rojo")
    j2 = Jugador("Luis", "azul")
    
    partida.agregar_jugador(j1)
    partida.agregar_jugador(j2)
    partida.iniciar_partida()
    
    print("\n📋 Configuración inicial:")
    
    # Ficha roja cerca del final (casilla 65, necesita 3 para llegar a 68)
    ficha_roja = j1.fichas[0]
    ficha_roja.estado = EstadoFicha.TABLERO
    ficha_roja.posicion = 65
    ficha_roja.casillas_recorridas = 65
    partida.tablero.agregar_ficha(65, ficha_roja)
    print(f"   🔴 Ficha roja 0 en casilla 65 (recorridas: 65)")
    print(f"   💭 Necesita recorrer 68 casillas totales para entrar al pasillo")
    
    print(f"\n🎯 Paso 1: Mover 3 casillas → Entra al pasillo (casilla 0 del pasillo)")
    capturadas = partida._mover_ficha(j1, 0, 3)
    
    print(f"\n📊 Resultado Paso 1:")
    print(f"   Estado: {ficha_roja.estado}")
    print(f"   Posición pasillo: {ficha_roja.posicion_pasillo if ficha_roja.estado == EstadoFicha.PASILLO_FINAL else 'N/A'}")
    print(f"   Casillas recorridas: {ficha_roja.casillas_recorridas}")
    
    if ficha_roja.estado != EstadoFicha.PASILLO_FINAL:
        print(f"\n❌ ERROR: No entró al pasillo final")
        return False
    
    print(f"\n✅ Entró al pasillo final")
    print(f"\n🎯 Paso 2: Mover 8 casillas más → Llega EXACTO a la META (casilla 8 del pasillo)")
    capturadas = partida._mover_ficha(j1, 0, 8)
    
    print(f"\n📊 Resultado Paso 2:")
    print(f"   Estado: {ficha_roja.estado}")
    print(f"   Posición pasillo: {ficha_roja.posicion_pasillo if hasattr(ficha_roja, 'posicion_pasillo') else 'N/A'}")
    print(f"   ¿Está en meta?: {ficha_roja.esta_en_meta()}")
    
    if not ficha_roja.esta_en_meta():
        print(f"\n❌ ERROR: No llegó a la META")
        return False
    
    print(f"\n✅ ¡Llegó a la META!")
    
    # Ahora intentar moverla de nuevo (NO debería poder)
    print(f"\n🎯 Paso 3: Intentar mover de nuevo (NO debería poder)")
    
    # Verificar que puede_mover retorna False
    puede = j1.puede_mover(0, 5)
    print(f"   puede_mover(0, 5) = {puede}")
    
    if puede:
        print(f"\n❌ ERROR: puede_mover() retorna True para ficha en META")
        return False
    
    print(f"\n✅ CORRECTO: puede_mover() retorna False para ficha en META")
    
    # Verificar que no aparece en fichas disponibles
    print(f"\n🎯 Paso 4: Verificar que no aparece como disponible")
    fichas_disponibles = partida.obtener_fichas_disponibles(j1)
    
    puede_mover_meta = False
    for info in fichas_disponibles:
        if info["id"] == 0:
            puede_mover_meta = info["puede_mover"]
            print(f"   Ficha 0: puede_mover = {info['puede_mover']}, descripción = '{info['descripcion']}'")
    
    if puede_mover_meta:
        print(f"\n❌ ERROR: Ficha en META aparece como movible")
        return False
    
    print(f"\n✅ CORRECTO: Ficha en META no puede moverse")
    print(f"\n🎉 ¡TEST COMPLETO! Ficha llega a META y deja de jugar correctamente")
    return True

def test_ficha_se_pasa_de_meta():
    """Prueba 6: Ficha que se pasaría de META no debe moverse."""
    print("\n" + "="*60)
    print("🧪 TEST 6: Ficha NO se Mueve si se Pasa de META")
    print("="*60)
    
    partida = Partida("test-6")
    
    j1 = Jugador("Ana", "rojo")
    
    partida.agregar_jugador(j1)
    partida.agregar_jugador(Jugador("Luis", "azul"))
    partida.iniciar_partida()
    
    print("\n📋 Configuración inicial:")
    
    # Ficha en pasillo, posición 6 (faltan 2 para META)
    ficha_roja = j1.fichas[0]
    ficha_roja.estado = EstadoFicha.PASILLO_FINAL
    ficha_roja.posicion_pasillo = 6
    ficha_roja.casillas_recorridas = 74  # 68 (tablero) + 6 (pasillo)
    print(f"   🔴 Ficha roja 0 en pasillo, posición 6")
    print(f"   💭 Necesita EXACTAMENTE 2 casillas para llegar a META (posición 8)")
    
    print(f"\n🎯 Acción: Intentar mover 5 casillas (6 + 5 = 11 > 8, SE PASA)")
    
    posicion_antes = ficha_roja.posicion_pasillo
    estado_antes = ficha_roja.estado
    
    capturadas = partida._mover_ficha(j1, 0, 5)
    
    print(f"\n📊 Resultado:")
    print(f"   Posición pasillo ANTES: {posicion_antes}")
    print(f"   Posición pasillo DESPUÉS: {ficha_roja.posicion_pasillo}")
    print(f"   Estado: {ficha_roja.estado}")
    
    # La ficha NO debe moverse
    if ficha_roja.posicion_pasillo == 6 and not ficha_roja.esta_en_meta():
        print(f"\n✅ CORRECTO: La ficha NO se movió (se pasaría de META)")
        print(f"   🚫 Movimiento bloqueado correctamente")
        return True
    else:
        print(f"\n❌ ERROR: La ficha se movió cuando no debía")
        return False

def test_jugador_gana_con_4_fichas():
    """Prueba 7: Jugador gana cuando las 4 fichas llegan a META."""
    print("\n" + "="*60)
    print("🧪 TEST 7: Jugador GANA con 4 Fichas en META")
    print("="*60)
    
    partida = Partida("test-7")
    
    j1 = Jugador("Ana", "rojo")
    j2 = Jugador("Luis", "azul")
    
    partida.agregar_jugador(j1)
    partida.agregar_jugador(j2)
    partida.iniciar_partida()
    
    print("\n📋 Configuración inicial:")
    print(f"   👤 {j1.nombre} ({j1.color}): 0/4 fichas en meta")
    print(f"   🎯 Objetivo: Llevar las 4 fichas a META")
    
    # Contador de fichas en meta
    fichas_en_meta = 0
    
    # Poner las 4 fichas cerca del final
    for i in range(4):
        ficha = j1.fichas[i]
        ficha.estado = EstadoFicha.TABLERO
        ficha.posicion = 65
        ficha.casillas_recorridas = 65
        partida.tablero.agregar_ficha(65, ficha)
    
    print(f"\n🎯 Proceso: Llevar cada ficha a META una por una")
    
    for i in range(4):
        print(f"\n   ───── Ficha {i} ─────")
        ficha = j1.fichas[i]
        
        # Mover 3 casillas para entrar al pasillo
        print(f"   📍 Paso 1: Casilla 65 → Pasillo posición 0")
        partida._mover_ficha(j1, i, 3)
        
        # Mover 8 casillas para llegar a META
        print(f"   📍 Paso 2: Pasillo 0 → META (posición 8)")
        partida._mover_ficha(j1, i, 8)
        
        if ficha.esta_en_meta():
            fichas_en_meta += 1
            print(f"   ✅ Ficha {i} llegó a META ({fichas_en_meta}/4)")
        else:
            print(f"   ❌ ERROR: Ficha {i} NO llegó a META")
            return False
        
        # Verificar estado del jugador después de cada ficha
        gano = j1.todas_fichas_en_meta()
        print(f"   🏆 todas_fichas_en_meta() = {gano}")
        
        if i == 3:  # Después de la última ficha
            if not gano:
                print(f"\n❌ ERROR: 4 fichas en META pero todas_fichas_en_meta() = False")
                return False
        else:  # Antes de la última ficha
            if gano:
                print(f"\n❌ ERROR: Solo {fichas_en_meta} fichas pero todas_fichas_en_meta() = True")
                return False
    
    print(f"\n📊 Resultado Final:")
    print(f"   🎯 Fichas en META: {fichas_en_meta}/4")
    print(f"   🏆 Jugador ganó: {j1.todas_fichas_en_meta()}")
    
    # Verificar manualmente que todas las fichas están en META
    fichas_meta_manual = sum(1 for f in j1.fichas if f.esta_en_meta())
    print(f"   ✓ Verificación manual: {fichas_meta_manual}/4 en META")
    
    if fichas_en_meta == 4 and j1.todas_fichas_en_meta() and fichas_meta_manual == 4:
        print(f"\n🎉 ¡VICTORIA! Ana ganó la partida con 4 fichas en META")
        return True
    else:
        print(f"\n❌ ERROR: Condición de victoria no se cumplió correctamente")
        return False

def main():
    print("\n" + "🎲"*30)
    print("PRUEBAS AUTOMÁTICAS DEL JUEGO")
    print("🎲"*30)
    
    resultados = []
    
    # Ejecutar todas las pruebas
    resultados.append(("Captura Básica", test_captura_basica()))
    resultados.append(("Captura Múltiple", test_captura_multiple()))
    resultados.append(("NO Captura en Seguro", test_no_captura_en_seguro()))
    resultados.append(("NO Captura Mismo Color", test_no_captura_mismo_color()))
    resultados.append(("Ficha Llega a META", test_ficha_llega_meta()))
    resultados.append(("NO Mover si se Pasa de META", test_ficha_se_pasa_de_meta()))
    resultados.append(("Jugador GANA con 4 en META", test_jugador_gana_con_4_fichas()))
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    
    total = len(resultados)
    exitosas = sum(1 for _, exito in resultados if exito)
    
    for nombre, exito in resultados:
        emoji = "✅" if exito else "❌"
        print(f"{emoji} {nombre}")
    
    print("\n" + "-"*60)
    print(f"Total: {exitosas}/{total} pruebas exitosas")
    
    if exitosas == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! Las capturas funcionan correctamente.")
        return 0
    else:
        print(f"\n⚠️  {total - exitosas} prueba(s) fallaron. Revisar implementación.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

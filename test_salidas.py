#!/usr/bin/env python3
"""
Test para verificar las salidas correctas de cada color.
"""
import sys
sys.path.insert(0, '/home/seqenenra/Codes/DistParques/backend')

from models.partida import Partida

def test_salidas_correctas():
    """Verifica que las salidas de cada color estén en las casillas correctas."""
    print("=" * 70)
    print("TEST: Verificación de casillas de salida")
    print("=" * 70)
    
    # Crear partida
    partida = Partida("test_sala", max_jugadores=4)
    
    # Agregar jugadores de cada color
    rojo = partida.agregar_jugador("Rojo", "player_red", "red")
    azul = partida.agregar_jugador("Azul", "player_blue", "blue")
    amarillo = partida.agregar_jugador("Amarillo", "player_yellow", "yellow")
    verde = partida.agregar_jugador("Verde", "player_green", "green")
    
    print("\n📍 Casillas de salida configuradas:")
    print(f"   🔴 Rojo:     {rojo.casilla_salida}")
    print(f"   🔵 Azul:     {azul.casilla_salida}")
    print(f"   🟡 Amarillo: {amarillo.casilla_salida}")
    print(f"   🟢 Verde:    {verde.casilla_salida}")
    
    print("\n✅ Casillas esperadas (según diseño visual):")
    print(f"   🔴 Rojo:     39 (lado superior izquierdo)")
    print(f"   🔵 Azul:     22 (lado derecho)")
    print(f"   🟡 Amarillo: 5  (lado inferior derecho)")
    print(f"   🟢 Verde:    56 (lado inferior izquierdo)")
    
    # Verificar
    errores = []
    
    if rojo.casilla_salida != 39:
        errores.append(f"❌ Rojo: esperaba 39, obtuvo {rojo.casilla_salida}")
    else:
        print(f"\n✅ Rojo CORRECTO: {rojo.casilla_salida}")
    
    if azul.casilla_salida != 22:
        errores.append(f"❌ Azul: esperaba 22, obtuvo {azul.casilla_salida}")
    else:
        print(f"✅ Azul CORRECTO: {azul.casilla_salida}")
    
    if amarillo.casilla_salida != 5:
        errores.append(f"❌ Amarillo: esperaba 5, obtuvo {amarillo.casilla_salida}")
    else:
        print(f"✅ Amarillo CORRECTO: {amarillo.casilla_salida}")
    
    if verde.casilla_salida != 56:
        errores.append(f"❌ Verde: esperaba 56, obtuvo {verde.casilla_salida}")
    else:
        print(f"✅ Verde CORRECTO: {verde.casilla_salida}")
    
    if errores:
        print("\n" + "=" * 70)
        print("❌ ERRORES ENCONTRADOS:")
        for error in errores:
            print(f"   {error}")
        print("=" * 70)
        return False
    
    print("\n" + "=" * 70)
    print("✅ TODAS LAS SALIDAS SON CORRECTAS")
    print("=" * 70)
    return True

def test_entradas_pasillo():
    """Verifica que las entradas a pasillos estén correctas."""
    print("\n\n" + "=" * 70)
    print("TEST: Verificación de entradas a pasillos finales")
    print("=" * 70)
    
    from models.tablero import Tablero
    
    tablero = Tablero()
    
    print("\n📍 Entradas a pasillos configuradas:")
    print(f"   🔴 Rojo:     {tablero.ENTRADAS_PASILLO['red']}")
    print(f"   🔵 Azul:     {tablero.ENTRADAS_PASILLO['blue']}")
    print(f"   🟡 Amarillo: {tablero.ENTRADAS_PASILLO['yellow']}")
    print(f"   🟢 Verde:    {tablero.ENTRADAS_PASILLO['green']}")
    
    print("\n✅ Entradas esperadas (10 casillas antes de la salida):")
    print(f"   🔴 Rojo:     29 (39 - 10 = 29)")
    print(f"   🔵 Azul:     12 (22 - 10 = 12)")
    print(f"   🟡 Amarillo: 63 (5 - 10 + 68 = 63)")
    print(f"   🟢 Verde:    46 (56 - 10 = 46)")
    
    # Verificar
    errores = []
    
    if tablero.ENTRADAS_PASILLO['red'] != 29:
        errores.append(f"❌ Rojo: esperaba 29, obtuvo {tablero.ENTRADAS_PASILLO['red']}")
    else:
        print(f"\n✅ Rojo CORRECTO: {tablero.ENTRADAS_PASILLO['red']}")
    
    if tablero.ENTRADAS_PASILLO['blue'] != 12:
        errores.append(f"❌ Azul: esperaba 12, obtuvo {tablero.ENTRADAS_PASILLO['blue']}")
    else:
        print(f"✅ Azul CORRECTO: {tablero.ENTRADAS_PASILLO['blue']}")
    
    if tablero.ENTRADAS_PASILLO['yellow'] != 63:
        errores.append(f"❌ Amarillo: esperaba 63, obtuvo {tablero.ENTRADAS_PASILLO['yellow']}")
    else:
        print(f"✅ Amarillo CORRECTO: {tablero.ENTRADAS_PASILLO['yellow']}")
    
    if tablero.ENTRADAS_PASILLO['green'] != 46:
        errores.append(f"❌ Verde: esperaba 46, obtuvo {tablero.ENTRADAS_PASILLO['green']}")
    else:
        print(f"✅ Verde CORRECTO: {tablero.ENTRADAS_PASILLO['green']}")
    
    if errores:
        print("\n" + "=" * 70)
        print("❌ ERRORES ENCONTRADOS:")
        for error in errores:
            print(f"   {error}")
        print("=" * 70)
        return False
    
    print("\n" + "=" * 70)
    print("✅ TODAS LAS ENTRADAS SON CORRECTAS")
    print("=" * 70)
    return True

if __name__ == "__main__":
    print("\n🧪 VERIFICANDO CONFIGURACIÓN DE CASILLAS\n")
    
    test1 = test_salidas_correctas()
    test2 = test_entradas_pasillo()
    
    print("\n\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"Test Salidas: {'✅ EXITOSO' if test1 else '❌ FALLIDO'}")
    print(f"Test Entradas: {'✅ EXITOSO' if test2 else '❌ FALLIDO'}")
    print(f"\n{'✅ CONFIGURACIÓN CORRECTA' if test1 and test2 else '❌ HAY ERRORES EN LA CONFIGURACIÓN'}")
    print("=" * 70)

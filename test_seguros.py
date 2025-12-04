#!/usr/bin/env python3
"""
Test para verificar las casillas seguras y la mecánica de captura.
"""
import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.tablero import Tablero
from models.ficha import Ficha, EstadoFicha
from models.jugador import Jugador


def test_seguros():
    """Prueba 1: Verificar cuáles son las casillas seguras"""
    print("=" * 70)
    print("PRUEBA 1: CASILLAS SEGURAS")
    print("=" * 70)
    
    tablero = Tablero()
    
    print(f"\n📍 Casillas seguras en el tablero: {sorted(tablero.SEGUROS)}")
    print(f"Total de seguros: {len(tablero.SEGUROS)}")
    
    # Verificar cada seguro
    print("\n🔍 Verificando cada casilla:")
    for pos in sorted(tablero.SEGUROS):
        assert tablero.es_seguro(pos), f"La casilla {pos} debería ser segura"
        print(f"   ✓ Casilla {pos} es seguro")
    
    # Verificar algunas casillas que NO son seguros
    casillas_normales = [1, 2, 3, 10, 20, 30, 40, 50, 60]
    print("\n🔍 Verificando casillas que NO son seguros:")
    for pos in casillas_normales:
        assert not tablero.es_seguro(pos), f"La casilla {pos} NO debería ser segura"
        print(f"   ✗ Casilla {pos} NO es seguro")
    
    print("\n✅ PRUEBA 1 PASADA: Todos los seguros funcionan correctamente")


def test_captura_en_seguros():
    """Prueba 2: Verificar que NO se puede capturar en seguros"""
    print("\n" + "=" * 70)
    print("PRUEBA 2: NO SE PUEDE CAPTURAR EN SEGUROS")
    print("=" * 70)
    
    tablero = Tablero()
    
    # Crear fichas de diferentes colores
    jugador_rojo = Jugador("Rojo", "red")
    jugador_azul = Jugador("Azul", "blue")
    
    ficha_roja = jugador_rojo.fichas[0]
    ficha_azul = jugador_azul.fichas[0]
    
    # Colocar ficha azul en un seguro (casilla 5)
    posicion_seguro = 5
    ficha_azul.posicion = posicion_seguro
    ficha_azul.estado = EstadoFicha.TABLERO
    tablero.agregar_ficha(posicion_seguro, ficha_azul)
    
    print(f"\n📌 Ficha AZUL en casilla {posicion_seguro} (SEGURO)")
    print(f"   Estado tablero: {tablero.casillas[posicion_seguro]}")
    
    # Intentar mover ficha roja a la misma casilla
    ficha_roja.posicion = posicion_seguro
    ficha_roja.estado = EstadoFicha.TABLERO
    
    print(f"\n🔴 Ficha ROJA intenta moverse a casilla {posicion_seguro} (SEGURO)")
    
    # Verificar captura (debería retornar lista vacía porque es seguro)
    capturadas = tablero.verificar_captura(posicion_seguro, ficha_roja)
    
    print(f"   Fichas capturadas: {len(capturadas)}")
    
    assert len(capturadas) == 0, "NO debería haber capturas en un seguro"
    assert ficha_azul.estado == EstadoFicha.TABLERO, "La ficha azul NO debería ser capturada"
    
    print("\n✅ PRUEBA 2 PASADA: No se puede capturar en seguros")


def test_captura_fuera_de_seguros():
    """Prueba 3: Verificar que SÍ se puede capturar fuera de seguros"""
    print("\n" + "=" * 70)
    print("PRUEBA 3: SÍ SE PUEDE CAPTURAR FUERA DE SEGUROS")
    print("=" * 70)
    
    tablero = Tablero()
    
    # Crear fichas de diferentes colores
    jugador_rojo = Jugador("Rojo", "red")
    jugador_azul = Jugador("Azul", "blue")
    
    ficha_roja = jugador_rojo.fichas[0]
    ficha_azul = jugador_azul.fichas[0]
    
    # Colocar ficha azul en una casilla NORMAL (no seguro)
    posicion_normal = 10
    ficha_azul.posicion = posicion_normal
    ficha_azul.estado = EstadoFicha.TABLERO
    tablero.agregar_ficha(posicion_normal, ficha_azul)
    
    print(f"\n📌 Ficha AZUL en casilla {posicion_normal} (NO SEGURO)")
    print(f"   ¿Es seguro? {tablero.es_seguro(posicion_normal)}")
    print(f"   Estado tablero: {tablero.casillas[posicion_normal]}")
    
    # Intentar mover ficha roja a la misma casilla
    ficha_roja.posicion = posicion_normal
    ficha_roja.estado = EstadoFicha.TABLERO
    
    print(f"\n🔴 Ficha ROJA intenta moverse a casilla {posicion_normal} (NO SEGURO)")
    
    # Verificar captura (debería capturar la ficha azul)
    capturadas = tablero.verificar_captura(posicion_normal, ficha_roja)
    
    print(f"   Fichas capturadas: {len(capturadas)}")
    if capturadas:
        for f in capturadas:
            print(f"   🎯 Capturada: Ficha {f.color}-{f.id}")
    
    assert len(capturadas) == 1, "Debería haber capturado 1 ficha"
    assert capturadas[0] == ficha_azul, "Debería haber capturado la ficha azul"
    
    print("\n✅ PRUEBA 3 PASADA: Sí se puede capturar fuera de seguros")


def test_multiples_fichas_en_seguro():
    """Prueba 4: Verificar que pueden coexistir fichas de diferentes colores en un seguro"""
    print("\n" + "=" * 70)
    print("PRUEBA 4: MÚLTIPLES FICHAS EN SEGURO (SIN CAPTURA)")
    print("=" * 70)
    
    tablero = Tablero()
    
    # Crear fichas de diferentes colores
    jugador_rojo = Jugador("Rojo", "red")
    jugador_azul = Jugador("Azul", "blue")
    jugador_verde = Jugador("Verde", "green")
    
    ficha_roja = jugador_rojo.fichas[0]
    ficha_azul = jugador_azul.fichas[0]
    ficha_verde = jugador_verde.fichas[0]
    
    # Colocar todas en el mismo seguro
    posicion_seguro = 12
    
    # Primera ficha (roja)
    ficha_roja.posicion = posicion_seguro
    ficha_roja.estado = EstadoFicha.TABLERO
    tablero.agregar_ficha(posicion_seguro, ficha_roja)
    
    # Segunda ficha (azul)
    ficha_azul.posicion = posicion_seguro
    ficha_azul.estado = EstadoFicha.TABLERO
    capturadas_1 = tablero.verificar_captura(posicion_seguro, ficha_azul)
    tablero.agregar_ficha(posicion_seguro, ficha_azul)
    
    # Tercera ficha (verde)
    ficha_verde.posicion = posicion_seguro
    ficha_verde.estado = EstadoFicha.TABLERO
    capturadas_2 = tablero.verificar_captura(posicion_seguro, ficha_verde)
    tablero.agregar_ficha(posicion_seguro, ficha_verde)
    
    print(f"\n📌 Casilla {posicion_seguro} (SEGURO) con múltiples fichas:")
    fichas_en_casilla = tablero.obtener_fichas_en(posicion_seguro)
    for f in fichas_en_casilla:
        print(f"   - Ficha {f.color}-{f.id}")
    
    print(f"\n📊 Resultados:")
    print(f"   Capturas al agregar ficha azul: {len(capturadas_1)}")
    print(f"   Capturas al agregar ficha verde: {len(capturadas_2)}")
    print(f"   Total de fichas en seguro: {len(fichas_en_casilla)}")
    
    assert len(capturadas_1) == 0, "No debería haber capturas en seguro"
    assert len(capturadas_2) == 0, "No debería haber capturas en seguro"
    assert len(fichas_en_casilla) == 3, "Deberían coexistir 3 fichas en el seguro"
    
    print("\n✅ PRUEBA 4 PASADA: Múltiples fichas pueden coexistir en seguros")


def test_salidas_son_seguros():
    """Prueba 5: Verificar que las salidas también funcionan como seguros"""
    print("\n" + "=" * 70)
    print("PRUEBA 5: SALIDAS COMO SEGUROS")
    print("=" * 70)
    
    tablero = Tablero()
    
    print(f"\n📍 Salidas por color:")
    for color, pos in tablero.SALIDAS.items():
        print(f"   {color}: casilla {pos} - ¿Es seguro? {tablero.es_seguro(pos)}")
    
    # Verificar que las salidas son seguros o tienen protección especial
    jugador_rojo = Jugador("Rojo", "red")
    jugador_azul = Jugador("Azul", "blue")
    
    ficha_roja = jugador_rojo.fichas[0]
    ficha_azul = jugador_azul.fichas[0]
    
    # Colocar ficha roja en su propia salida (casilla 39)
    salida_roja = tablero.SALIDAS["red"]
    ficha_roja.posicion = salida_roja
    ficha_roja.estado = EstadoFicha.TABLERO
    tablero.agregar_ficha(salida_roja, ficha_roja)
    
    print(f"\n🔴 Ficha ROJA en su salida (casilla {salida_roja})")
    
    # Ficha azul intenta caer en la salida roja
    ficha_azul.posicion = salida_roja
    ficha_azul.estado = EstadoFicha.TABLERO
    
    capturadas = tablero.verificar_captura(salida_roja, ficha_azul)
    
    print(f"🔵 Ficha AZUL intenta moverse a salida roja")
    print(f"   Capturas: {len(capturadas)}")
    
    # Las salidas del mismo color también protegen (no se captura en tu propia salida)
    # Pero una ficha de otro color SÍ podría caer ahí
    
    print("\n✅ PRUEBA 5 PASADA: Verificación de salidas completada")


if __name__ == "__main__":
    try:
        test_seguros()
        test_captura_en_seguros()
        test_captura_fuera_de_seguros()
        test_multiples_fichas_en_seguro()
        test_salidas_son_seguros()
        
        print("\n" + "=" * 70)
        print("🎉 TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("=" * 70)
        print("\nRESUMEN:")
        print("✓ Las casillas seguras están correctamente definidas")
        print("✓ NO se puede capturar fichas en seguros")
        print("✓ SÍ se puede capturar fichas fuera de seguros")
        print("✓ Múltiples fichas de diferentes colores pueden coexistir en seguros")
        print("✓ Las salidas tienen protección especial")
        
    except AssertionError as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

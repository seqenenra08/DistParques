#!/usr/bin/env python3
"""
Test de división de dados - Verificar que funciona correctamente
"""

import sys
sys.path.append('./backend')

from models.partida import Partida

def test_division_dados():
    """Test: Dividir dados entre dos fichas diferentes."""
    print("\n" + "="*60)
    print("TEST: División de dados entre diferentes fichas")
    print("="*60)
    
    # Crear partida
    partida = Partida("test", 2)
    j1 = partida.agregar_jugador("Jugador1", "s1", "red")
    j2 = partida.agregar_jugador("Jugador2", "s2", "blue")
    
    partida.iniciada = True
    partida.esperando_dados_inicio = False
    j1.es_su_turno = True
    
    # Sacar dos fichas de la cárcel primero
    print("\n1. Sacando fichas de la cárcel...")
    
    # Sacar primera ficha (par 1,1)
    dados_par1 = (1, 1)
    partida.procesar_turno(j1, dados_par1, None)
    partida.procesar_turno(j1, dados_par1, 0)
    print(f"   ✅ Ficha 0 en posición: {j1.fichas[0].posicion}")
    
    # Resetear contador de pares para evitar 3 pares
    j1.pares_consecutivos = 0
    
    # Sacar segunda ficha (par 2,2)
    dados_par2 = (2, 2)
    partida.procesar_turno(j1, dados_par2, None)
    partida.procesar_turno(j1, dados_par2, 1)
    print(f"   ✅ Ficha 1 en posición: {j1.fichas[1].posicion}")
    
    # Resetear contador de nuevo
    j1.pares_consecutivos = 0
    
    # Ahora probar división de dados
    print("\n2. Probando división de dados (2 y 4)...")
    dados = (2, 4)
    
    # Verificar que puede dividir
    info = partida.tiene_movimientos_validos(j1, dados)
    print(f"   - Puede dividir: {info['puede_dividir']}")
    print(f"   - Fichas movibles: {info['fichas_movibles']}")
    
    if not info['puede_dividir']:
        print("   ❌ ERROR: Debería poder dividir dados")
        return False
    
    # Intentar división: ficha 0 con 2, ficha 1 con 4
    movimientos = [
        {"id_ficha": 0, "valor_dado": 2},
        {"id_ficha": 1, "valor_dado": 4}
    ]
    
    pos_antes_0 = j1.fichas[0].posicion
    pos_antes_1 = j1.fichas[1].posicion
    
    resultado = partida.procesar_turno_dividido(j1, dados, movimientos)
    
    if "error" in resultado:
        print(f"   ❌ ERROR: {resultado['error']}")
        return False
    
    pos_despues_0 = j1.fichas[0].posicion
    pos_despues_1 = j1.fichas[1].posicion
    
    print(f"\n3. Resultado de división:")
    print(f"   - Ficha 0: {pos_antes_0} → {pos_despues_0} (avanzó {(pos_despues_0 - pos_antes_0) % 68})")
    print(f"   - Ficha 1: {pos_antes_1} → {pos_despues_1} (avanzó {(pos_despues_1 - pos_antes_1) % 68})")
    print(f"   - Movimientos realizados: {len(resultado['movimientos_realizados'])}")
    
    # Verificar que cada ficha se movió la cantidad correcta
    avance_0 = (pos_despues_0 - pos_antes_0) % 68
    avance_1 = (pos_despues_1 - pos_antes_1) % 68
    
    if avance_0 == 2 and avance_1 == 4:
        print("\n✅ TEST PASADO: División de dados funciona correctamente")
        return True
    else:
        print(f"\n❌ TEST FALLIDO: Avances incorrectos (esperado: 2 y 4, obtenido: {avance_0} y {avance_1})")
        return False

def test_no_puede_mover_misma_ficha():
    """Test: No se puede mover la misma ficha dos veces."""
    print("\n" + "="*60)
    print("TEST: Validación - No mover la misma ficha dos veces")
    print("="*60)
    
    partida = Partida("test2", 2)
    j1 = partida.agregar_jugador("Jugador1", "s1", "red")
    j2 = partida.agregar_jugador("Jugador2", "s2", "blue")
    
    partida.iniciada = True
    partida.esperando_dados_inicio = False
    j1.es_su_turno = True
    
    # Sacar una ficha
    dados_par = (1, 1)
    partida.procesar_turno(j1, dados_par, None)
    partida.procesar_turno(j1, dados_par, 0)
    j1.pares_consecutivos = 0  # Resetear contador
    
    # Intentar mover la misma ficha dos veces con dados diferentes
    dados = (2, 4)
    movimientos = [
        {"id_ficha": 0, "valor_dado": 2},
        {"id_ficha": 0, "valor_dado": 4}  # ❌ Misma ficha
    ]
    
    resultado = partida.procesar_turno_dividido(j1, dados, movimientos)
    
    if "error" in resultado and "misma ficha" in resultado["error"].lower():
        print(f"   ✅ Validación correcta: {resultado['error']}")
        print("\n✅ TEST PASADO: Sistema rechaza mover la misma ficha dos veces")
        return True
    else:
        print(f"   ❌ ERROR: Debería rechazar mover la misma ficha dos veces")
        return False

def test_valores_deben_coincidir():
    """Test: Los valores deben coincidir con los dados."""
    print("\n" + "="*60)
    print("TEST: Validación - Valores deben coincidir con dados")
    print("="*60)
    
    partida = Partida("test3", 2)
    j1 = partida.agregar_jugador("Jugador1", "s1", "red")
    j2 = partida.agregar_jugador("Jugador2", "s2", "blue")
    
    partida.iniciada = True
    partida.esperando_dados_inicio = False
    j1.es_su_turno = True
    
    # Sacar dos fichas
    dados_par1 = (1, 1)
    partida.procesar_turno(j1, dados_par1, None)
    partida.procesar_turno(j1, dados_par1, 0)
    j1.pares_consecutivos = 0  # Resetear
    
    dados_par2 = (2, 2)
    partida.procesar_turno(j1, dados_par2, None)
    partida.procesar_turno(j1, dados_par2, 1)
    j1.pares_consecutivos = 0  # Resetear
    
    # Intentar usar valores que no coinciden con los dados
    dados = (2, 4)
    movimientos = [
        {"id_ficha": 0, "valor_dado": 3},  # ❌ No sacó 3
        {"id_ficha": 1, "valor_dado": 3}   # ❌ No sacó otro 3
    ]
    
    resultado = partida.procesar_turno_dividido(j1, dados, movimientos)
    
    if "error" in resultado:
        print(f"   ✅ Validación correcta: {resultado['error']}")
        print("\n✅ TEST PASADO: Sistema rechaza valores incorrectos")
        return True
    else:
        print(f"   ❌ ERROR: Debería rechazar valores que no coinciden")
        return False

if __name__ == "__main__":
    print("\n" + "🎲"*30)
    print("TESTS DE DIVISIÓN DE DADOS")
    print("🎲"*30)
    
    try:
        resultado1 = test_division_dados()
        resultado2 = test_no_puede_mover_misma_ficha()
        resultado3 = test_valores_deben_coincidir()
        
        print("\n" + "="*60)
        if resultado1 and resultado2 and resultado3:
            print("🎉 TODOS LOS TESTS PASARON")
            print("="*60)
            print("\n✅ La funcionalidad de división de dados funciona correctamente")
            print("✅ Las validaciones previenen uso incorrecto")
            print("\n📝 Ahora el frontend puede implementar la UI para usar esta funcionalidad")
        else:
            print("❌ ALGUNOS TESTS FALLARON")
            print("="*60)
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

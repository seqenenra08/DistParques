#!/usr/bin/env python3
"""
Test: Verificar que no se puede dividir dados con una sola ficha
"""

import sys
sys.path.append('./backend')

from models.partida import Partida

def test_no_dividir_con_una_ficha():
    """Test: No se debe poder dividir dados cuando solo hay 1 ficha disponible"""
    print("\n" + "="*60)
    print("TEST: NO dividir dados con una sola ficha")
    print("="*60)
    
    partida = Partida("test", 2)
    j1 = partida.agregar_jugador("Rojo", "s1", "red")
    j2 = partida.agregar_jugador("Azul", "s2", "blue")
    
    partida.iniciada = True
    partida.esperando_dados_inicio = False
    j1.es_su_turno = True
    
    # Sacar una ficha
    dados_par = (1, 1)
    partida.procesar_turno(j1, dados_par, None)
    partida.procesar_turno(j1, dados_par, 0)
    
    print(f"\n1. Una sola ficha fuera de cárcel:")
    print(f"   - Ficha 0 en posición: {j1.fichas[0].posicion}")
    fichas_carcel = [f.id for f in j1.fichas if f.esta_en_carcel()]
    print(f"   - Fichas en cárcel: {fichas_carcel}")
    
    # Lanzar dados diferentes
    dados = (2, 4)
    info = partida.tiene_movimientos_validos(j1, dados)
    
    print(f"\n2. Lanzando dados {dados}:")
    print(f"   - Fichas movibles: {info['fichas_movibles']}")
    print(f"   - Puede dividir: {info['puede_dividir']}")
    
    if not info['puede_dividir']:
        print(f"\n✅ TEST PASADO: NO puede dividir dados con una sola ficha")
        return True
    else:
        print(f"\n❌ TEST FALLIDO: Permite dividir dados con una sola ficha")
        return False

def test_si_dividir_con_dos_fichas():
    """Test: SÍ se debe poder dividir dados cuando hay 2 fichas disponibles"""
    print("\n" + "="*60)
    print("TEST: SÍ dividir dados con dos fichas")
    print("="*60)
    
    partida = Partida("test2", 2)
    j1 = partida.agregar_jugador("Rojo", "s1", "red")
    j2 = partida.agregar_jugador("Azul", "s2", "blue")
    
    partida.iniciada = True
    partida.esperando_dados_inicio = False
    j1.es_su_turno = True
    
    # Sacar dos fichas
    dados_par1 = (1, 1)
    partida.procesar_turno(j1, dados_par1, None)
    partida.procesar_turno(j1, dados_par1, 0)
    j1.resetear_pares()
    
    dados_par2 = (2, 2)
    partida.procesar_turno(j1, dados_par2, None)
    partida.procesar_turno(j1, dados_par2, 1)
    j1.resetear_pares()
    
    print(f"\n1. Dos fichas fuera de cárcel:")
    print(f"   - Ficha 0 en posición: {j1.fichas[0].posicion}")
    print(f"   - Ficha 1 en posición: {j1.fichas[1].posicion}")
    
    # Lanzar dados diferentes
    dados = (2, 4)
    info = partida.tiene_movimientos_validos(j1, dados)
    
    print(f"\n2. Lanzando dados {dados}:")
    print(f"   - Fichas movibles: {info['fichas_movibles']}")
    print(f"   - Puede dividir: {info['puede_dividir']}")
    
    if info['puede_dividir']:
        print(f"\n✅ TEST PASADO: SÍ puede dividir dados con dos fichas")
        return True
    else:
        print(f"\n❌ TEST FALLIDO: NO permite dividir dados con dos fichas")
        return False

if __name__ == "__main__":
    print("\n" + "✂️"*30)
    print("TESTS: DIVISIÓN REQUIERE MÍNIMO 2 FICHAS")
    print("✂️"*30)
    
    try:
        resultado1 = test_no_dividir_con_una_ficha()
        resultado2 = test_si_dividir_con_dos_fichas()
        
        print("\n" + "="*60)
        if resultado1 and resultado2:
            print("🎉 TODOS LOS TESTS PASARON")
            print("="*60)
            print("\n✅ Se requieren al menos 2 fichas para dividir dados")
        else:
            print("❌ ALGUNOS TESTS FALLARON")
            print("="*60)
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

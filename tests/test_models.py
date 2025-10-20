"""
Tests unitarios para las clases del juego de Parqués

Para ejecutar los tests:
    python -m pytest tests/ -v
    
O simplemente ejecutar este archivo:
    python tests/test_models.py
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.models import Jugador, Ficha, Tablero, Partida
from backend.models import ColorJugador, EstadoFicha, EstadoPartida


def test_crear_jugador():
    """Test: Crear un jugador correctamente."""
    print("🧪 Test: Crear jugador")
    
    jugador = Jugador("Alice", "player_1")
    
    assert jugador.nombre == "Alice"
    assert jugador.id == "player_1"
    assert jugador.color is None
    assert jugador.turno is False
    assert len(jugador.fichas) == 0
    
    print("✅ Jugador creado correctamente")


def test_asignar_color():
    """Test: Asignar color a un jugador."""
    print("\n🧪 Test: Asignar color")
    
    jugador = Jugador("Bob", "player_2")
    jugador.asignar_color(ColorJugador.ROJO)
    
    assert jugador.color == ColorJugador.ROJO
    assert len(jugador.fichas) == 4
    
    # Verificar que todas las fichas tienen el color correcto
    for ficha in jugador.fichas:
        assert ficha.color == ColorJugador.ROJO
        assert ficha.esta_en_carcel()
    
    print("✅ Color asignado correctamente")


def test_crear_ficha():
    """Test: Crear una ficha."""
    print("\n🧪 Test: Crear ficha")
    
    ficha = Ficha(0, ColorJugador.AZUL, "player_1")
    
    assert ficha.id == 0
    assert ficha.color == ColorJugador.AZUL
    assert ficha.posicion == -1
    assert ficha.estado == EstadoFicha.CARCEL
    assert ficha.esta_en_carcel()
    
    print("✅ Ficha creada correctamente")


def test_sacar_ficha_de_carcel():
    """Test: Sacar ficha de la cárcel."""
    print("\n🧪 Test: Sacar ficha de cárcel")
    
    ficha = Ficha(0, ColorJugador.VERDE, "player_1")
    ficha.sacar_de_carcel(5)
    
    assert ficha.posicion == 5
    assert ficha.estado == EstadoFicha.ACTIVA
    assert ficha.esta_activa()
    assert not ficha.esta_en_carcel()
    
    print("✅ Ficha sacada de cárcel correctamente")


def test_mover_ficha():
    """Test: Mover una ficha."""
    print("\n🧪 Test: Mover ficha")
    
    ficha = Ficha(0, ColorJugador.AMARILLO, "player_1")
    ficha.sacar_de_carcel(5)
    ficha.mover(10, es_seguro=False)
    
    assert ficha.posicion == 10
    assert ficha.estado == EstadoFicha.ACTIVA
    
    # Mover a un seguro
    ficha.mover(12, es_seguro=True)
    assert ficha.posicion == 12
    assert ficha.estado == EstadoFicha.SEGURO
    assert ficha.esta_en_seguro()
    
    print("✅ Ficha movida correctamente")


def test_enviar_ficha_a_carcel():
    """Test: Enviar ficha de vuelta a la cárcel (comida)."""
    print("\n🧪 Test: Enviar ficha a cárcel")
    
    ficha = Ficha(0, ColorJugador.ROJO, "player_1")
    ficha.sacar_de_carcel(5)
    ficha.mover(20, es_seguro=False)
    
    # Simular que fue comida
    ficha.enviar_a_carcel()
    
    assert ficha.posicion == -1
    assert ficha.estado == EstadoFicha.CARCEL
    assert ficha.esta_en_carcel()
    
    print("✅ Ficha enviada a cárcel correctamente")


def test_crear_tablero():
    """Test: Crear tablero."""
    print("\n🧪 Test: Crear tablero")
    
    tablero = Tablero()
    
    assert tablero.num_casillas == 68
    assert len(tablero.casillas) == 68
    assert len(tablero.seguros) == 8
    assert len(tablero.salidas) == 4
    
    # Verificar salidas
    assert tablero.salidas[ColorJugador.ROJO] == 5
    assert tablero.salidas[ColorJugador.AZUL] == 22
    assert tablero.salidas[ColorJugador.AMARILLO] == 39
    assert tablero.salidas[ColorJugador.VERDE] == 56
    
    print("✅ Tablero creado correctamente")


def test_casillas_seguras():
    """Test: Verificar casillas seguras."""
    print("\n🧪 Test: Casillas seguras")
    
    tablero = Tablero()
    
    assert tablero.es_casilla_segura(5)
    assert tablero.es_casilla_segura(12)
    assert not tablero.es_casilla_segura(10)
    assert not tablero.es_casilla_segura(0)
    
    print("✅ Casillas seguras verificadas")


def test_crear_partida():
    """Test: Crear una partida."""
    print("\n🧪 Test: Crear partida")
    
    partida = Partida("test_game", max_jugadores=4)
    
    assert partida.id == "test_game"
    assert partida.max_jugadores == 4
    assert partida.estado == EstadoPartida.ESPERANDO
    assert len(partida.jugadores) == 0
    assert partida.ganador is None
    
    print("✅ Partida creada correctamente")


def test_agregar_jugadores():
    """Test: Agregar jugadores a la partida."""
    print("\n🧪 Test: Agregar jugadores")
    
    partida = Partida("test_game")
    
    j1 = partida.agregar_jugador("Alice", "p1")
    assert j1 is not None
    assert j1.color == ColorJugador.ROJO
    assert len(partida.jugadores) == 1
    
    j2 = partida.agregar_jugador("Bob", "p2")
    assert j2 is not None
    assert j2.color == ColorJugador.AZUL
    assert len(partida.jugadores) == 2
    
    j3 = partida.agregar_jugador("Carlos", "p3")
    assert j3.color == ColorJugador.AMARILLO
    
    j4 = partida.agregar_jugador("Diana", "p4")
    assert j4.color == ColorJugador.VERDE
    
    # Intentar agregar un 5to jugador
    j5 = partida.agregar_jugador("Eve", "p5")
    assert j5 is None  # No debe permitir más de 4 jugadores
    
    print("✅ Jugadores agregados correctamente")


def test_iniciar_partida():
    """Test: Iniciar la partida."""
    print("\n🧪 Test: Iniciar partida")
    
    partida = Partida("test_game")
    
    # No se puede iniciar sin jugadores
    assert partida.iniciar_partida() is False
    
    # Agregar jugadores
    partida.agregar_jugador("Alice", "p1")
    partida.agregar_jugador("Bob", "p2")
    
    # Ahora sí se puede iniciar
    assert partida.iniciar_partida() is True
    assert partida.estado == EstadoPartida.EN_CURSO
    
    # Verificar que hay un jugador con turno activo
    jugadores_con_turno = [j for j in partida.jugadores if j.turno]
    assert len(jugadores_con_turno) == 1
    
    print("✅ Partida iniciada correctamente")


def test_lanzar_dado():
    """Test: Lanzar dado."""
    print("\n🧪 Test: Lanzar dado")
    
    partida = Partida("test_game")
    partida.agregar_jugador("Alice", "p1")
    partida.agregar_jugador("Bob", "p2")
    partida.iniciar_partida()
    
    # Lanzar dado 10 veces para verificar rango
    for _ in range(10):
        dado = partida.lanzar_dado()
        assert 1 <= dado <= 6
        assert partida.ultimo_dado == dado
    
    print("✅ Dado lanzado correctamente")


def test_puede_sacar_de_carcel():
    """Test: Verificar si puede sacar de la cárcel."""
    print("\n🧪 Test: Puede sacar de cárcel")
    
    partida = Partida("test_game")
    
    # Se puede sacar con 5
    assert partida.puede_sacar_de_carcel(5) is True
    
    # Se puede sacar con pares
    assert partida.puede_sacar_de_carcel(2) is True
    assert partida.puede_sacar_de_carcel(4) is True
    assert partida.puede_sacar_de_carcel(6) is True
    
    # No se puede sacar con impares (excepto 5)
    assert partida.puede_sacar_de_carcel(1) is False
    assert partida.puede_sacar_de_carcel(3) is False
    
    print("✅ Validación de salida de cárcel correcta")


def test_mover_ficha_partida():
    """Test: Mover ficha en una partida."""
    print("\n🧪 Test: Mover ficha en partida")
    
    partida = Partida("test_game")
    j1 = partida.agregar_jugador("Alice", "p1")
    partida.agregar_jugador("Bob", "p2")
    partida.iniciar_partida()
    
    # Asegurar que Alice tiene el turno
    j1.activar_turno()
    partida.turno_actual = partida.jugadores.index(j1)
    
    # Intentar mover con un 5 (sacar de cárcel)
    resultado = partida.mover_ficha("p1", 0, 5)
    
    assert resultado["exito"] is True
    assert resultado["turno_extra"] is True
    assert j1.fichas[0].esta_activa()
    
    print("✅ Ficha movida en partida correctamente")


def test_pasar_turno():
    """Test: Pasar turno al siguiente jugador."""
    print("\n🧪 Test: Pasar turno")
    
    partida = Partida("test_game")
    j1 = partida.agregar_jugador("Alice", "p1")
    j2 = partida.agregar_jugador("Bob", "p2")
    partida.iniciar_partida()
    
    jugador_inicial = partida.obtener_jugador_actual()
    
    # Pasar turno
    siguiente = partida.pasar_turno()
    
    assert siguiente != jugador_inicial
    assert siguiente.turno is True
    assert jugador_inicial.turno is False
    
    print("✅ Turno pasado correctamente")


def test_serializar_a_dict():
    """Test: Serializar objetos a diccionarios."""
    print("\n🧪 Test: Serialización a dict")
    
    # Test Ficha
    ficha = Ficha(0, ColorJugador.ROJO, "p1")
    ficha_dict = ficha.to_dict()
    assert ficha_dict["id"] == 0
    assert ficha_dict["color"] == "rojo"
    assert ficha_dict["posicion"] == -1
    
    # Test Jugador
    jugador = Jugador("Alice", "p1")
    jugador.asignar_color(ColorJugador.AZUL)
    jugador_dict = jugador.to_dict()
    assert jugador_dict["nombre"] == "Alice"
    assert jugador_dict["color"] == "azul"
    assert len(jugador_dict["fichas"]) == 4
    
    # Test Partida
    partida = Partida("test_game")
    partida.agregar_jugador("Alice", "p1")
    partida_dict = partida.to_dict()
    assert partida_dict["id"] == "test_game"
    assert partida_dict["num_jugadores"] == 1
    
    print("✅ Serialización correcta")


def run_all_tests():
    """Ejecuta todos los tests."""
    print("\n" + "🧪" * 30)
    print(" " * 20 + "EJECUTANDO TESTS")
    print("🧪" * 30 + "\n")
    
    tests = [
        test_crear_jugador,
        test_asignar_color,
        test_crear_ficha,
        test_sacar_ficha_de_carcel,
        test_mover_ficha,
        test_enviar_ficha_a_carcel,
        test_crear_tablero,
        test_casillas_seguras,
        test_crear_partida,
        test_agregar_jugadores,
        test_iniciar_partida,
        test_lanzar_dado,
        test_puede_sacar_de_carcel,
        test_mover_ficha_partida,
        test_pasar_turno,
        test_serializar_a_dict,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} falló: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} error: {e}")
            failed += 1
    
    print("\n" + "🧪" * 30)
    print(f"\n📊 RESULTADOS:")
    print(f"   ✅ Pasados: {passed}/{len(tests)}")
    print(f"   ❌ Fallados: {failed}/{len(tests)}")
    print("\n" + "🧪" * 30 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

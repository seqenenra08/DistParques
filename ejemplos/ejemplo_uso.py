"""
Ejemplo de uso del sistema de Parqués - Fase 1

Este script demuestra cómo usar las clases implementadas
para simular una partida básica de Parqués.
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.models import Partida, ColorJugador, EstadoPartida
import json


def imprimir_separador():
    """Imprime una línea separadora."""
    print("\n" + "=" * 60 + "\n")


def mostrar_estado_partida(partida):
    """Muestra el estado actual de la partida."""
    print(f"📊 Estado de la Partida: {partida.estado.value}")
    print(f"🎲 Último dado: {partida.ultimo_dado}")
    print(f"👥 Jugadores: {len(partida.jugadores)}")
    
    jugador_actual = partida.obtener_jugador_actual()
    if jugador_actual:
        print(f"🎯 Turno actual: {jugador_actual.nombre} ({jugador_actual.color.value})")
    
    print("\n👤 Estado de jugadores:")
    for jugador in partida.jugadores:
        turno_marker = "➡️" if jugador.turno else "  "
        print(f"{turno_marker} {jugador.nombre} ({jugador.color.value}):")
        
        fichas_carcel = sum(1 for f in jugador.fichas if f.esta_en_carcel())
        fichas_activas = sum(1 for f in jugador.fichas if f.esta_activa())
        fichas_meta = sum(1 for f in jugador.fichas if f.esta_en_final())
        
        print(f"      Cárcel: {fichas_carcel} | Activas: {fichas_activas} | Meta: {fichas_meta}")


def ejemplo_crear_partida():
    """Ejemplo 1: Crear una partida y agregar jugadores."""
    imprimir_separador()
    print("🎮 EJEMPLO 1: Crear partida y agregar jugadores")
    imprimir_separador()
    
    # Crear nueva partida
    partida = Partida("partida_ejemplo", max_jugadores=4)
    print(f"✅ Partida creada: {partida.id}")
    print(f"📊 Estado: {partida.estado.value}")
    
    # Agregar jugadores
    jugadores_nombres = ["Alice", "Bob", "Carlos", "Diana"]
    
    for i, nombre in enumerate(jugadores_nombres):
        jugador = partida.agregar_jugador(nombre, f"player_{i+1}")
        if jugador:
            print(f"✅ {nombre} se unió - Color: {jugador.color.value}")
        else:
            print(f"❌ {nombre} no pudo unirse")
    
    return partida


def ejemplo_iniciar_partida(partida):
    """Ejemplo 2: Iniciar la partida."""
    imprimir_separador()
    print("🎮 EJEMPLO 2: Iniciar partida")
    imprimir_separador()
    
    if partida.iniciar_partida():
        print("✅ ¡Partida iniciada!")
        mostrar_estado_partida(partida)
    else:
        print("❌ No se pudo iniciar la partida")


def ejemplo_lanzar_dado_y_mover(partida):
    """Ejemplo 3: Lanzar dado y mover ficha."""
    imprimir_separador()
    print("🎮 EJEMPLO 3: Lanzar dado y mover ficha")
    imprimir_separador()
    
    jugador_actual = partida.obtener_jugador_actual()
    print(f"🎯 Turno de: {jugador_actual.nombre}")
    
    # Lanzar dado
    resultado_dado = partida.lanzar_dado()
    print(f"🎲 Dado lanzado: {resultado_dado}")
    
    # Verificar si puede sacar de la cárcel
    puede_sacar = partida.puede_sacar_de_carcel(resultado_dado)
    print(f"{'✅' if puede_sacar else '❌'} Puede sacar de la cárcel: {puede_sacar}")
    
    # Obtener fichas movibles
    fichas_movibles = jugador_actual.obtener_fichas_movibles(resultado_dado)
    print(f"📍 Fichas movibles: {len(fichas_movibles)}")
    
    if fichas_movibles:
        # Mover la primera ficha movible
        ficha = fichas_movibles[0]
        print(f"\n🔄 Intentando mover ficha #{ficha.id}...")
        
        resultado = partida.mover_ficha(jugador_actual.id, ficha.id, resultado_dado)
        
        print(f"\n{'✅' if resultado['exito'] else '❌'} {resultado['mensaje']}")
        
        if resultado['exito']:
            if resultado['turno_extra']:
                print("🎉 ¡Turno extra otorgado!")
            if resultado['llego_a_meta']:
                print("🏆 ¡Ficha llegó a la meta!")
            if resultado['ficha_comida']:
                print("😈 ¡Ficha enemiga comida!")
        
        return resultado
    else:
        print("⚠️ No hay fichas movibles")
        return None


def ejemplo_serializar_json(partida):
    """Ejemplo 4: Serializar partida a JSON."""
    imprimir_separador()
    print("🎮 EJEMPLO 4: Serializar partida a JSON")
    imprimir_separador()
    
    # Convertir a diccionario
    estado_dict = partida.to_dict()
    
    # Convertir a JSON
    estado_json = json.dumps(estado_dict, indent=2, ensure_ascii=False)
    
    print("📄 Estado de la partida en JSON:")
    print(estado_json[:500] + "..." if len(estado_json) > 500 else estado_json)
    
    return estado_dict


def ejemplo_simular_turno_completo(partida):
    """Ejemplo 5: Simular un turno completo."""
    imprimir_separador()
    print("🎮 EJEMPLO 5: Simular turno completo")
    imprimir_separador()
    
    jugador_actual = partida.obtener_jugador_actual()
    print(f"🎯 Turno de: {jugador_actual.nombre} ({jugador_actual.color.value})")
    
    # Lanzar dado
    dado = partida.lanzar_dado()
    print(f"🎲 Resultado: {dado}")
    
    # Intentar mover
    fichas_movibles = jugador_actual.obtener_fichas_movibles(dado)
    
    if fichas_movibles:
        ficha = fichas_movibles[0]
        resultado = partida.mover_ficha(jugador_actual.id, ficha.id, dado)
        print(f"{'✅' if resultado['exito'] else '❌'} {resultado['mensaje']}")
        
        # Si no hay turno extra, pasar turno
        if not resultado.get('turno_extra', False):
            siguiente = partida.pasar_turno()
            print(f"➡️ Turno pasa a: {siguiente.nombre}")
    else:
        print("⚠️ No hay movimientos posibles")
        siguiente = partida.pasar_turno()
        print(f"➡️ Turno pasa a: {siguiente.nombre}")


def ejemplo_verificar_victoria(partida):
    """Ejemplo 6: Verificar condiciones de victoria."""
    imprimir_separador()
    print("🎮 EJEMPLO 6: Verificar victoria")
    imprimir_separador()
    
    for jugador in partida.jugadores:
        fichas_meta = sum(1 for f in jugador.fichas if f.esta_en_final())
        print(f"{jugador.nombre}: {fichas_meta}/4 fichas en meta")
        
        if jugador.todas_fichas_en_meta():
            print(f"🏆 ¡{jugador.nombre} ha ganado!")
    
    if partida.ganador:
        print(f"\n👑 GANADOR: {partida.ganador.nombre}")
        print(f"🎊 Color: {partida.ganador.color.value}")
    else:
        print("\n⏳ La partida continúa...")


def main():
    """Función principal que ejecuta todos los ejemplos."""
    print("\n" + "🎲" * 30)
    print(" " * 20 + "PARQUÉS - EJEMPLOS DE USO")
    print("🎲" * 30)
    
    # Ejemplo 1: Crear partida
    partida = ejemplo_crear_partida()
    
    # Ejemplo 2: Iniciar partida
    ejemplo_iniciar_partida(partida)
    
    # Ejemplo 3: Lanzar dado y mover
    ejemplo_lanzar_dado_y_mover(partida)
    
    # Mostrar estado
    imprimir_separador()
    mostrar_estado_partida(partida)
    
    # Ejemplo 4: Serializar a JSON
    ejemplo_serializar_json(partida)
    
    # Simular varios turnos
    print("\n" + "🎲" * 30)
    print(" " * 20 + "SIMULANDO 5 TURNOS")
    print("🎲" * 30)
    
    for i in range(5):
        print(f"\n--- Turno {i+1} ---")
        ejemplo_simular_turno_completo(partida)
    
    # Ejemplo 6: Verificar victoria
    ejemplo_verificar_victoria(partida)
    
    # Estado final
    imprimir_separador()
    print("📊 ESTADO FINAL DE LA PARTIDA")
    imprimir_separador()
    mostrar_estado_partida(partida)
    
    print("\n" + "🎲" * 30)
    print(" " * 20 + "FIN DE LOS EJEMPLOS")
    print("🎲" * 30 + "\n")


if __name__ == "__main__":
    main()

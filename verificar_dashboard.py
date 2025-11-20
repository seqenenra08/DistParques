#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificación rápida para el dashboard.
Verifica que curses esté disponible y muestra un preview.
"""

import sys

def check_dependencies():
    """Verifica que todas las dependencias estén disponibles."""
    print("🔍 Verificando dependencias...\n")
    
    # Verificar curses
    try:
        import curses
        print("✅ curses: Disponible")
    except ImportError:
        print("❌ curses: NO disponible")
        print("   Instala con: sudo apt-get install python3-curses (Ubuntu/Debian)")
        return False
    
    # Verificar socket (debería estar siempre)
    try:
        import socket
        print("✅ socket: Disponible")
    except ImportError:
        print("❌ socket: NO disponible (esto es muy raro)")
        return False
    
    # Verificar json (debería estar siempre)
    try:
        import json
        print("✅ json: Disponible")
    except ImportError:
        print("❌ json: NO disponible (esto es muy raro)")
        return False
    
    # Verificar threading (debería estar siempre)
    try:
        import threading
        print("✅ threading: Disponible")
    except ImportError:
        print("❌ threading: NO disponible (esto es muy raro)")
        return False
    
    print("\n✅ Todas las dependencias están disponibles!")
    return True

def test_curses_preview(stdscr):
    """Muestra un preview del dashboard."""
    curses.curs_set(0)
    
    # Inicializar colores
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_YELLOW, -1)
        curses.init_pair(2, curses.COLOR_BLUE, -1)
        curses.init_pair(3, curses.COLOR_RED, -1)
        curses.init_pair(4, curses.COLOR_GREEN, -1)
    
    h, w = stdscr.getmaxyx()
    
    # Título
    title = "🎲 PREVIEW DEL DASHBOARD DE PARQUÉS"
    stdscr.addstr(0, (w - len(title)) // 2, title, curses.A_BOLD | curses.A_REVERSE)
    
    # Info
    stdscr.addstr(2, 2, f"Tamaño de terminal: {w}x{h}")
    stdscr.addstr(3, 2, f"Colores: {'✅ Soportados' if curses.has_colors() else '❌ No soportados'}")
    
    # Tarjeta de ejemplo
    y, x = 5, 5
    card_w, card_h = 32, 11
    
    if w >= card_w + 10 and h >= card_h + 10:
        # Borde
        for i in range(card_w):
            stdscr.addch(y, x+i, ord('═'), curses.color_pair(1))
            stdscr.addch(y+card_h-1, x+i, ord('═'), curses.color_pair(1))
        
        for j in range(1, card_h-1):
            stdscr.addch(y+j, x, ord('║'), curses.color_pair(1))
            stdscr.addch(y+j, x+card_w-1, ord('║'), curses.color_pair(1))
        
        # Esquinas
        stdscr.addch(y, x, ord('╔'), curses.color_pair(1))
        stdscr.addch(y, x+card_w-1, ord('╗'), curses.color_pair(1))
        stdscr.addch(y+card_h-1, x, ord('╚'), curses.color_pair(1))
        stdscr.addch(y+card_h-1, x+card_w-1, ord('╝'), curses.color_pair(1))
        
        # Contenido
        stdscr.addstr(y+1, x+2, "👉 Ana (TÚ)", curses.A_BOLD | curses.color_pair(1))
        stdscr.addstr(y+2, x+2, "🟨 AMARILLO", curses.color_pair(1))
        stdscr.addstr(y+4, x+2, "🏁 En meta:    2/4")
        stdscr.addstr(y+5, x+2, "🎲 En juego:   1")
        stdscr.addstr(y+6, x+2, "🔒 En cárcel:  1")
        stdscr.addstr(y+8, x+2, "[████████░░░░░░░░░░░░░░]")
        stdscr.addstr(y+9, x+2, "50% completado", curses.A_DIM)
        
        stdscr.addstr(y+card_h+2, 2, "✅ La tarjeta se ve correcta!")
    else:
        stdscr.addstr(5, 2, "⚠️  Terminal muy pequeña para mostrar tarjeta completa")
        stdscr.addstr(6, 2, f"    Necesitas al menos 80x24, tienes {w}x{h}")
    
    # Instrucciones
    stdscr.addstr(h-3, 2, "Presiona cualquier tecla para continuar...", curses.A_REVERSE)
    
    stdscr.refresh()
    stdscr.getch()

def main():
    """Función principal."""
    print("="*60)
    print("🎲 VERIFICACIÓN DEL DASHBOARD DE PARQUÉS")
    print("="*60)
    print()
    
    # Verificar dependencias
    if not check_dependencies():
        print("\n❌ Algunas dependencias faltan. Soluciónalas antes de continuar.")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("Abriendo preview del dashboard...")
    print("="*60)
    print()
    input("Presiona ENTER para continuar...")
    
    # Probar curses
    try:
        import curses
        curses.wrapper(test_curses_preview)
        
        print("\n" + "="*60)
        print("✅ ¡Todo está listo!")
        print("="*60)
        print()
        print("Puedes iniciar el dashboard con:")
        print("  ./run_dashboard.sh")
        print()
        print("O iniciar la demo completa con:")
        print("  ./demo_dashboard.sh")
        print()
        
    except Exception as e:
        print(f"\n❌ Error al probar curses: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

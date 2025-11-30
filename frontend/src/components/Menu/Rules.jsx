/**
 * Componente Rules - Muestra las reglas del juego
 */

import React from 'react';
import styles from './Rules.module.css';

const Rules = ({ onClose }) => {
  return (
    <div className={styles.rulesOverlay} onClick={onClose}>
      <div className={styles.rulesCard} onClick={(e) => e.stopPropagation()}>
        <div className={styles.rulesHeader}>
          <h2 className={styles.title}>Reglas del Parcheesi</h2>
          <button className={styles.closeButton} onClick={onClose}>
            ✕
          </button>
        </div>

        <div className={styles.rulesContent}>
          <section className={styles.section}>
            <h3>Objetivo del Juego</h3>
            <p>
              Ser el primero en llevar todas tus fichas desde la cárcel hasta la meta,
              recorriendo el tablero completo.
            </p>
          </section>

          <section className={styles.section}>
            <h3>Configuración Inicial</h3>
            <ul>
              <li>Cada jugador tiene 4 fichas del mismo color</li>
              <li>Todas las fichas comienzan en la cárcel (prisión)</li>
              <li>Se puede jugar con 2, 3 o 4 jugadores</li>
              <li>En cada turno se lanzan 2 dados</li>
            </ul>
          </section>

          <section className={styles.section}>
            <h3>Reglas Básicas</h3>
            <ul>
              <li><strong>Salir de la cárcel:</strong> Para liberar una ficha, ambos dados deben mostrar el mismo número (dobles: 1-1, 2-2, 3-3, 4-4, 5-5 o 6-6). Solo puedes sacar UNA ficha por turno, que tú eliges</li>
              <li><strong>Movimiento:</strong> Cuando tienes fichas en el tablero, puedes moverlas según el número que saques en cada dado (haces dos movimientos por turno)</li>
              <li><strong>Capturas:</strong> Si caes en una casilla ocupada por un oponente, lo envías de vuelta a su cárcel</li>
              <li><strong>Casillas seguras:</strong> Las fichas en casillas seguras no pueden ser capturadas</li>
              <li><strong>Turnos con dobles:</strong> Al sacar dobles, además de poder liberar una ficha, obtienes movimientos adicionales</li>
            </ul>
          </section>

          <section className={styles.section}>
            <h3>Casillas Especiales</h3>
            <ul>
              <li><strong>Casillas de salida:</strong> Donde las fichas entran al tablero</li>
              <li><strong>Casillas seguras:</strong> Protegen tus fichas de capturas</li>
              <li><strong>Pasillo final:</strong> El último tramo antes de llegar a la meta</li>
              <li><strong>Meta:</strong> Destino final de todas las fichas</li>
            </ul>
          </section>

          <section className={styles.section}>
            <h3>Cómo Ganar</h3>
            <p>
              El primer jugador que logre meter todas sus 4 fichas en la meta gana el juego.
            </p>
          </section>

          <section className={styles.section}>
            <h3>Consejos Estratégicos</h3>
            <ul>
              <li>Sacar dobles es crucial para liberar tus fichas de la cárcel</li>
              <li>Decide estratégicamente qué ficha sacar cuando obtengas dobles</li>
              <li>Intenta sacar varias fichas de la cárcel para tener más opciones de movimiento</li>
              <li>Usa las casillas seguras para proteger tus fichas</li>
              <li>Captura las fichas de tus oponentes cuando sea posible para retrasar su avance</li>
              <li>Planifica tus movimientos con ambos dados para maximizar tus oportunidades</li>
            </ul>
          </section>
        </div>

        <div className={styles.rulesFooter}>
          <button className={styles.closeFooterButton} onClick={onClose}>
            Entendido
          </button>
        </div>
      </div>
    </div>
  );
};

export default Rules;

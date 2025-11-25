import { useEffect, useRef, useState } from "react";
import PlayerPieces from "./PlayerPieces";
import "../styles/board.css";

/**
 * Board.jsx
 * - genera una grid 15x15
 * - genera 64 posiciones de tablero (pathPositions) recorriendo un anillo alrededor del centro
 * - posiciona las casas (4 zonas de inicio)
 * - controla movimiento paso-a-paso de las fichas con animación
 */

function generatePathPositions() {
  // Genera posiciones en coordenadas grid (1..15) recorriendo perímetro interior y avanzando
  // hasta obtener 64 posiciones. Es una generación programática (no manual),
  // produce un circuito alrededor del centro utilizable para el juego.
  const size = 15;
  const min = 1;
  const max = size;
  const visited = new Set();
  const coords = [];

  // Empezamos en (1,1) y hacemos capas concéntricas alrededor del centro
  let layer = 0;
  while (coords.length < 64 && layer < 8) {
    const start = 1 + layer;
    const end = size - layer;
    // top row left->right
    for (let c = start; c <= end && coords.length < 64; c++) {
      const key = `${start}-${c}`;
      if (!visited.has(key)) { coords.push({ r: start, c }); visited.add(key); }
    }
    // right col top+1 -> bottom
    for (let r = start + 1; r <= end && coords.length < 64; r++) {
      const key = `${r}-${end}`;
      if (!visited.has(key)) { coords.push({ r, c: end }); visited.add(key); }
    }
    // bottom row right-1 -> left
    for (let c = end - 1; c >= start && coords.length < 64; c--) {
      const key = `${end}-${c}`;
      if (!visited.has(key)) { coords.push({ r: end, c }); visited.add(key); }
    }
    // left col bottom-1 -> top+1
    for (let r = end - 1; r > start && coords.length < 64; r--) {
      const key = `${r}-${start}`;
      if (!visited.has(key)) { coords.push({ r, c: start }); visited.add(key); }
    }
    layer++;
  }

  // Si aún faltan, rellena con posiciones interiores por fila (defensa)
  for (let r = 2; coords.length < 64 && r <= size - 1; r++) {
    for (let c = 2; coords.length < 64 && c <= size - 1; c++) {
      const key = `${r}-${c}`;
      if (!visited.has(key)) { coords.push({ r, c }); visited.add(key); }
    }
  }

  // Normaliza: cada entrada {r,c} con r,c entre 1..15
  return coords.slice(0, 64);
}

export default function Board() {
  const boardRef = useRef();
  const [pathPos] = useState(generatePathPositions); // array de 64 {r,c}
  const [pieces, setPieces] = useState(() => {
    // estado: 4 jugadores x 4 fichas: posición -1 significa en casa
    const players = ["red", "blue", "green", "yellow"];
    const initial = [];
    players.forEach((color, pIdx) => {
      for (let i = 0; i < 4; i++) {
        initial.push({ id: `${color}-${i}`, color, player: pIdx, pos: -1 });
      }
    });
    return initial;
  });

  // piezas absolutas (para animar): map id -> {left, top}
  const piecesRef = useRef({});

  useEffect(() => {
    // inicializamos piezasRef con la ubicación de sus casillas (si pos>=0)
    updateAllPieceDOMPositions();
    // eslint-disable-next-line
  }, []);

  function getCellCenterPosition(gridR, gridC) {
    // Calcula la posición absoluta (en px) del centro de la celda (gridR, gridC)
    // basándose en boardRef y su grid 15x15.
    if (!boardRef.current) return { x: 0, y: 0 };
    const boardRect = boardRef.current.getBoundingClientRect();
    const cellW = boardRect.width / 15;
    const cellH = boardRect.height / 15;
    const left = boardRect.left + (gridC - 1) * cellW + cellW / 2;
    const top = boardRect.top + (gridR - 1) * cellH + cellH / 2;
    return { x: left, y: top, cellW, cellH };
  }

  function updateAllPieceDOMPositions() {
    // actualiza cache de posiciones DOM (no mueve visualmente la ficha)
    pieces.forEach((pc) => {
      if (pc.pos >= 0) {
        const { r, c } = pathPos[pc.pos];
        piecesRef.current[pc.id] = getCellCenterPosition(r, c);
      } else {
        piecesRef.current[pc.id] = null;
      }
    });
  }

  async function movePieceStepByStep(pieceId, steps) {
    // movimiento opción A: paso a paso con delay y animación CSS
    const delay = (ms) => new Promise((res) => setTimeout(res, ms));
    setPieces((prev) => {
      // si no se encuentra la pieza, nada
      const idx = prev.findIndex((p) => p.id === pieceId);
      if (idx === -1) return prev;
      return prev.map((p) => ({ ...p }));
    });

    for (let s = 0; s < steps; s++) {
      setPieces((prev) => {
        const copy = prev.map((p) => ({ ...p }));
        const i = copy.findIndex((p) => p.id === pieceId);
        if (i === -1) return prev;
        // si está en casa (-1), lo sacamos al primer índice del path según su jugador
        if (copy[i].pos === -1) {
          // asignamos una entrada inicial para cada jugador (distribuida)
          const startingOffsets = [0, 16, 32, 48]; // ejemplo: red starts at 0, blue 16, green 32, yellow 48
          copy[i].pos = startingOffsets[copy[i].player] % 64;
        } else {
          copy[i].pos = (copy[i].pos + 1) % 64;
        }
        return copy;
      });

      // Esperamos que el DOM re-renderice, luego dejamos animación CSS mover la ficha.
      await delay(260); // tiempo que coincide con transition en CSS
    }
  }

  function rollDie() {
    return Math.floor(Math.random() * 6) + 1;
  }

  // control simple de UI: seleccionar ficha y tirar dado
  const [selectedPiece, setSelectedPiece] = useState(null);
  const [lastRoll, setLastRoll] = useState(null);
  const [moving, setMoving] = useState(false);

  async function handleRollAndMove() {
    if (!selectedPiece) return alert("Selecciona una ficha primero.");
    if (moving) return;
    const val = rollDie();
    setLastRoll(val);
    setMoving(true);
    await movePieceStepByStep(selectedPiece, val);
    setMoving(false);
  }

  return (
    <div className="boardWrap">
      {/* Contenedor del tablero y overlay */}
      <div className="boardContainer">
        <div ref={boardRef} className="boardGrid">
          {/* Casas (zonas de inicio) */}
          <div className="home home-red"> </div>
          <div className="home home-blue"> </div>
          <div className="home home-green"> </div>
          <div className="home home-yellow"> </div>

          {/* centro */}
          <div className="centerBlock"></div>

          {/* celdas visibles (15x15) */}
          {Array.from({ length: 15 * 15 }).map((_, i) => {
            const r = Math.floor(i / 15) + 1;
            const c = (i % 15) + 1;
            // find if this grid position matches any pathPos index -> label index
            const pathIndex = pathPos.findIndex((p) => p.r === r && p.c === c);
            return (
              <div key={`${r}-${c}`} className={`gridCell`}>
                {pathIndex >= 0 ? <div className="cellLabel">{pathIndex + 1}</div> : null}
              </div>
            );
          })}
        </div>

        {/* piezas absolutas (overlay) */}
        <div className="piecesOverlay">
          {pieces.map((pc) => {
            // compute style for absolute position (if pos>=0)
            let style = {};
            if (pc.pos >= 0 && boardRef.current) {
              const { r, c } = pathPos[pc.pos];
              const { x, y } = getCellCenterPosition(r, c);
              // convert board absolute coordinates to overlay relative coordinates
              const boardRect = boardRef.current.getBoundingClientRect();
              style = {
                left: `${x - boardRect.left}px`,
                top: `${y - boardRect.top}px`,
                transform: "translate(-50%, -50%)",
              };
            } else {
              // pieces in home: show grouped according to player
              // place them near the home corners
              const homePositions = {
                0: { left: "5%", top: "5%" },
                1: { left: "92%", top: "5%" },
                2: { left: "5%", top: "92%" },
                3: { left: "92%", top: "92%" },
              };
              const base = homePositions[pc.player];
              style = { left: base.left, top: base.top, transform: "translate(-50%,-50%)" };
            }

            return (
              <div
                key={pc.id}
                className={`pieceMarker ${pc.color}`}
                style={style}
                onClick={() => setSelectedPiece(pc.id)}
              >
                <div className="pieceDot" />
              </div>
            );
          })}
        </div>
      </div>

      {/* Panel lateral con controles y selector */}
      <div className="rightPanel">
        {/* UI de controles */}
        <div className="controls">
          <div><strong>Ficha seleccionada:</strong> {selectedPiece ?? "ninguna"}</div>
          <div><strong>Última tirada:</strong> {lastRoll ?? "-"}</div>
          <button onClick={handleRollAndMove} disabled={!selectedPiece || moving}>
            Tirar dado y mover
          </button>
          <button
            onClick={() => {
              // poner todas a casa
              setPieces((prev) => prev.map((p) => ({ ...p, pos: -1 })));
              setSelectedPiece(null);
              setLastRoll(null);
            }}
          >
            Reiniciar
          </button>
        </div>

        {/* listado de piezas para seleccionar */}
        <div className="selector">
          <h4>Seleccionar ficha</h4>
          {pieces.map((p) => (
            <button
              key={p.id}
              onClick={() => setSelectedPiece(p.id)}
              className={selectedPiece === p.id ? "sel" : ""}
            >
              {p.id} ({p.pos >= 0 ? `posición ${p.pos + 1}` : "casa"})
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

import { useEffect, useRef, useState } from "react";
import PlayerPieces from "./PlayerPieces";
import "../styles/board.css";

/**
 * TABLERO SERPIENTE SIMPLE
 * 68 casillas en zigzag horizontal claro
 */

function generatePathPositions() {
  const path = [];
  
  // ============================================
  // SERPIENTE SIMPLE: 7 FILAS HORIZONTALES
  // Cada fila tiene ~10 casillas
  // Van alternando izquierda-derecha-izquierda...
  // ============================================
  
  // FILA 1: Casillas 0-9 (de izquierda a derecha, fila 13)
  for (let c = 2; c <= 11; c++) {
    const pos = c - 2;
    path.push({ r: 13, c, safe: pos === 0 || pos === 5 }); // 0-9
  }
  
  // FILA 2: Casillas 10-19 (de derecha a izquierda, fila 11)
  for (let c = 11; c >= 2; c--) {
    const pos = 10 + (11 - c);
    path.push({ r: 11, c, safe: pos === 12 || pos === 17 }); // 10-19
  }
  
  // FILA 3: Casillas 20-29 (de izquierda a derecha, fila 9)
  for (let c = 2; c <= 11; c++) {
    const pos = 20 + (c - 2);
    path.push({ r: 9, c, safe: pos === 22 || pos === 29 }); // 20-29
  }
  
  // FILA 4: Casillas 30-39 (de derecha a izquierda, fila 7)
  for (let c = 11; c >= 2; c--) {
    const pos = 30 + (11 - c);
    path.push({ r: 7, c, safe: pos === 34 || pos === 39 }); // 30-39
  }
  
  // FILA 5: Casillas 40-49 (de izquierda a derecha, fila 5)
  for (let c = 2; c <= 11; c++) {
    const pos = 40 + (c - 2);
    path.push({ r: 5, c, safe: pos === 46 || pos === 49 }); // 40-49
  }
  
  // FILA 6: Casillas 50-59 (de derecha a izquierda, fila 3)
  for (let c = 11; c >= 2; c--) {
    const pos = 50 + (11 - c);
    path.push({ r: 3, c, safe: pos === 51 || pos === 56 }); // 50-59
  }
  
  // FILA 7: Casillas 60-67 (de izquierda a derecha, fila 1)
  for (let c = 2; c <= 9; c++) {
    const pos = 60 + (c - 2);
    path.push({ r: 1, c, safe: pos === 61 || pos === 63 }); // 60-67
  }
  
  return {
    main: path,
    finalPaths: { red: [], blue: [], yellow: [], green: [] }
  };
}

export default function Board() {
  const boardRef = useRef();
  const [pathData] = useState(generatePathPositions);
  const pathPos = pathData.main;
  
  const [pieces, setPieces] = useState(() => {
    const players = ["red", "blue", "green", "yellow"];
    const initial = [];
    players.forEach((color, pIdx) => {
      for (let i = 0; i < 4; i++) {
        initial.push({ id: `${color}-${i}`, color, player: pIdx, pos: -1 });
      }
    });
    return initial;
  });

  const piecesRef = useRef({});

  useEffect(() => {
    updateAllPieceDOMPositions();
    // eslint-disable-next-line
  }, []);

  function getCellCenterPosition(gridR, gridC) {
    if (!boardRef.current) return { x: 0, y: 0 };
    const boardRect = boardRef.current.getBoundingClientRect();
    const cellW = boardRect.width / 15;
    const cellH = boardRect.height / 15;
    const left = boardRect.left + (gridC - 1) * cellW + cellW / 2;
    const top = boardRect.top + (gridR - 1) * cellH + cellH / 2;
    return { x: left, y: top, cellW, cellH };
  }

  function updateAllPieceDOMPositions() {
    pieces.forEach((pc) => {
      if (pc.pos >= 0 && pc.pos < pathPos.length) {
        const { r, c } = pathPos[pc.pos];
        piecesRef.current[pc.id] = getCellCenterPosition(r, c);
      } else {
        piecesRef.current[pc.id] = null;
      }
    });
  }

  async function movePieceStepByStep(pieceId, steps) {
    const delay = (ms) => new Promise((res) => setTimeout(res, ms));
    
    for (let s = 0; s < steps; s++) {
      setPieces((prev) => {
        const copy = prev.map((p) => ({ ...p }));
        const i = copy.findIndex((p) => p.id === pieceId);
        if (i === -1) return prev;
        
        if (copy[i].pos === -1) {
          // Sacar de casa
          copy[i].pos = 0;
        } else {
          // Avanzar
          copy[i].pos = (copy[i].pos + 1) % pathPos.length;
        }
        return copy;
      });
      await delay(200);
    }
  }

  function rollDie() {
    return Math.floor(Math.random() * 6) + 1;
  }

  const [selectedPiece, setSelectedPiece] = useState(null);
  const [lastRoll, setLastRoll] = useState(null);
  const [moving, setMoving] = useState(false);

  async function handleRollAndMove() {
    if (!selectedPiece) {
      alert("Selecciona una ficha");
      return;
    }
    if (moving) return;
    
    const val = rollDie();
    setLastRoll(val);
    setMoving(true);
    await movePieceStepByStep(selectedPiece, val);
    setMoving(false);
  }

  return (
    <div className="boardWrap">
      <div className="boardContainer">
        <div ref={boardRef} className="boardGrid">
          <div className="home home-red">🏠</div>
          <div className="home home-blue">🏠</div>
          <div className="home home-green">🏠</div>
          <div className="home home-yellow">🏠</div>
          <div className="centerBlock"></div>

          {Array.from({ length: 15 * 15 }).map((_, i) => {
            const r = Math.floor(i / 15) + 1;
            const c = (i % 15) + 1;
            
            const pathIndex = pathPos.findIndex((p) => p.r === r && p.c === c);
            const cellData = pathPos[pathIndex];
            const isSafe = cellData?.safe;
            const cellClass = `gridCell ${isSafe ? 'safe' : ''}`;
            
            return (
              <div key={`${r}-${c}`} className={cellClass}>
                {pathIndex >= 0 && <div className="cellLabel">{pathIndex}</div>}
                {isSafe && <div className="safeMarker">★</div>}
              </div>
            );
          })}
        </div>

        <div className="piecesOverlay">
          {pieces.map((pc) => {
            let style = {};
            
            if (pc.pos >= 0 && pc.pos < pathPos.length && boardRef.current) {
              const { r, c } = pathPos[pc.pos];
              const { x, y } = getCellCenterPosition(r, c);
              const boardRect = boardRef.current.getBoundingClientRect();
              style = {
                left: `${x - boardRect.left}px`,
                top: `${y - boardRect.top}px`,
                transform: "translate(-50%, -50%)",
              };
            } else {
              const homePositions = {
                0: { left: "12%", top: "88%" },
                1: { left: "88%", top: "88%" },
                2: { left: "88%", top: "12%" },
                3: { left: "12%", top: "12%" },
              };
              const base = homePositions[pc.player];
              const pieceNum = parseInt(pc.id.split('-')[1]);
              const offsetX = (pieceNum % 2) * 25;
              const offsetY = Math.floor(pieceNum / 2) * 25;
              
              style = { 
                left: `calc(${base.left} + ${offsetX}px)`, 
                top: `calc(${base.top} + ${offsetY}px)`, 
                transform: "translate(-50%,-50%)" 
              };
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

      <div className="rightPanel">
        <div className="controls">
          <div><strong>Ficha:</strong> {selectedPiece ?? "Ninguna"}</div>
          <div><strong>Dado:</strong> {lastRoll ?? "-"}</div>
          <div><strong>Casillas:</strong> {pathPos.length}</div>
          <button onClick={handleRollAndMove} disabled={!selectedPiece || moving}>
            {moving ? "⏳" : "🎲"} Tirar
          </button>
          <button onClick={() => {
            setPieces((prev) => prev.map((p) => ({ ...p, pos: -1 })));
            setSelectedPiece(null);
            setLastRoll(null);
          }}>
            🔄 Reset
          </button>
        </div>

        <div className="selector">
          <h4>Fichas</h4>
          {pieces.map((p) => (
            <button
              key={p.id}
              onClick={() => setSelectedPiece(p.id)}
              className={selectedPiece === p.id ? "sel" : ""}
            >
              <span style={{
                display: 'inline-block',
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                backgroundColor: p.color,
                marginRight: '8px'
              }}></span>
              {p.id}
              <span style={{ float: 'right' }}>
                {p.pos >= 0 ? `#${p.pos}` : "🏠"}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

import "../styles/board.css";
import Piece from "./Piece";

export default function Board() {
  return (
    <div className="board">

      {/* Casas */}
      <div className="home home-red"></div>
      <div className="home home-blue"></div>
      <div className="home home-green"></div>
      <div className="home home-yellow"></div>

      {/* Centro */}
      <div className="center"></div>

      {/* Caminos */}
      {Array.from({ length: 52 }).map((_, i) => (
        <div key={i} className={`cell path-${i}`}></div>
      ))}

    </div>
  );
}

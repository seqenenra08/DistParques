import Piece from "./Piece";

export default function PlayerPieces({ color }) {
  return (
    <div className="pieces-area">
      {[0, 1, 2, 3].map((i) => (
        <Piece key={i} color={color} id={i} />
      ))}
    </div>
  );
}

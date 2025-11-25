export default function PlayerPieces({ color }) {
  return (
    <div className="piecesArea">
      {[0,1,2,3].map(i => (
        <div key={i} className="pieceSmall" style={{ backgroundColor: color }} />
      ))}
    </div>
  );
}

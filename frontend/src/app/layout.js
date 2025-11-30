import './globals.css';

export const metadata = {
  title: 'Parcheesi Game',
  description: 'Juego de Parcheesi multijugador distribuido',
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}

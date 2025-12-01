import './globals.css';

export const metadata = {
  title: 'Parchese Game',
  description: 'Juego de Parchese multijugador distribuido',
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}

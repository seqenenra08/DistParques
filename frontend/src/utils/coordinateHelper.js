/**
 * Utilidad para convertir posiciones de píxeles a porcentajes
 * Útil al ajustar coordenadas del tablero
 */

// Dimensiones de la imagen del tablero (ajusta según tu imagen)
const BOARD_WIDTH = 700;
const BOARD_HEIGHT = 700;

/**
 * Convierte coordenadas de píxeles a porcentajes
 * @param {number} x - Posición X en píxeles
 * @param {number} y - Posición Y en píxeles
 * @param {number} width - Ancho del tablero en píxeles (opcional)
 * @param {number} height - Alto del tablero en píxeles (opcional)
 * @returns {{x: number, y: number}} Coordenadas en porcentajes
 */
export function pixelsToPercentage(x, y, width = BOARD_WIDTH, height = BOARD_HEIGHT) {
  return {
    x: Math.round((x / width) * 100),
    y: Math.round((y / height) * 100)
  };
}

/**
 * Convierte coordenadas de porcentajes a píxeles
 * @param {number} x - Posición X en porcentaje
 * @param {number} y - Posición Y en porcentaje
 * @param {number} width - Ancho del tablero en píxeles (opcional)
 * @param {number} height - Alto del tablero en píxeles (opcional)
 * @returns {{x: number, y: number}} Coordenadas en píxeles
 */
export function percentageToPixels(x, y, width = BOARD_WIDTH, height = BOARD_HEIGHT) {
  return {
    x: Math.round((x / 100) * width),
    y: Math.round((y / 100) * height)
  };
}

/**
 * Genera código JavaScript para una lista de coordenadas
 * @param {Array<{id: string|number, x: number, y: number}>} coordinates
 * @returns {string} Código JavaScript listo para copiar
 */
export function generateCoordinatesCode(coordinates) {
  let code = '{\n';
  coordinates.forEach(coord => {
    const id = typeof coord.id === 'string' ? `'${coord.id}'` : coord.id;
    code += `  ${id}: { x: ${coord.x}, y: ${coord.y} },\n`;
  });
  code += '}';
  return code;
}

/**
 * Calcula coordenadas para una secuencia lineal de casillas
 * @param {number} startX - X inicial en porcentaje
 * @param {number} startY - Y inicial en porcentaje
 * @param {number} endX - X final en porcentaje
 * @param {number} endY - Y final en porcentaje
 * @param {number} count - Número de casillas en la secuencia
 * @returns {Array<{x: number, y: number}>} Array de coordenadas
 */
export function linearSequence(startX, startY, endX, endY, count) {
  const coords = [];
  const stepX = (endX - startX) / (count - 1);
  const stepY = (endY - startY) / (count - 1);
  
  for (let i = 0; i < count; i++) {
    coords.push({
      x: Math.round(startX + stepX * i),
      y: Math.round(startY + stepY * i)
    });
  }
  
  return coords;
}

/**
 * Calcula coordenadas para una curva (útil para esquinas)
 * @param {number} centerX - X del centro de la curva
 * @param {number} centerY - Y del centro de la curva
 * @param {number} radius - Radio de la curva en porcentaje
 * @param {number} startAngle - Ángulo inicial en grados
 * @param {number} endAngle - Ángulo final en grados
 * @param {number} count - Número de puntos
 * @returns {Array<{x: number, y: number}>} Array de coordenadas
 */
export function curveSequence(centerX, centerY, radius, startAngle, endAngle, count) {
  const coords = [];
  const angleStep = (endAngle - startAngle) / (count - 1);
  
  for (let i = 0; i < count; i++) {
    const angle = (startAngle + angleStep * i) * (Math.PI / 180);
    coords.push({
      x: Math.round(centerX + radius * Math.cos(angle)),
      y: Math.round(centerY + radius * Math.sin(angle))
    });
  }
  
  return coords;
}

// Ejemplos de uso (puedes ejecutar esto en la consola del navegador)
if (typeof window !== 'undefined') {
  window.coordinateHelper = {
    pixelsToPercentage,
    percentageToPixels,
    generateCoordinatesCode,
    linearSequence,
    curveSequence,
    
    // Ejemplo: Convertir clic del mouse a coordenadas
    setupClickListener: function() {
      console.log('Haz clic en el tablero para obtener coordenadas...');
      const board = document.querySelector('.board');
      if (!board) {
        console.error('No se encontró el tablero');
        return;
      }
      
      board.addEventListener('click', (e) => {
        const rect = board.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const coords = pixelsToPercentage(x, y, rect.width, rect.height);
        console.log(`Clic en: { x: ${coords.x}, y: ${coords.y} }`);
      });
    }
  };
  
  console.log('Helper de coordenadas cargado. Usa window.coordinateHelper');
}

export default {
  pixelsToPercentage,
  percentageToPixels,
  generateCoordinatesCode,
  linearSequence,
  curveSequence
};
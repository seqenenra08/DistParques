/**
 * Componente de Celebración - Fuegos Artificiales
 * Se muestra cuando un jugador gana la partida
 */

import React, { useEffect, useRef, useState } from 'react';
import styles from './Celebration.module.css';

const Celebration = ({ winner, onClose }) => {
  const canvasRef = useRef(null);
  const [showMessage, setShowMessage] = useState(false);
  const animationRef = useRef(null);
  const fireworksRef = useRef([]);
  const particlesRef = useRef([]);

  useEffect(() => {
    // Mostrar mensaje con delay para efecto dramático
    setTimeout(() => setShowMessage(true), 500);

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Clase para partículas de fuegos artificiales
    class Particle {
      constructor(x, y, color) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.velocity = {
          x: (Math.random() - 0.5) * 8,
          y: (Math.random() - 0.5) * 8
        };
        this.alpha = 1;
        this.decay = Math.random() * 0.015 + 0.015;
        this.size = Math.random() * 3 + 2;
      }

      update() {
        this.velocity.y += 0.1; // Gravedad
        this.x += this.velocity.x;
        this.y += this.velocity.y;
        this.alpha -= this.decay;
      }

      draw(ctx) {
        ctx.save();
        ctx.globalAlpha = this.alpha;
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }
    }

    // Clase para cohetes (antes de explotar)
    class Firework {
      constructor(x, targetY, color) {
        this.x = x;
        this.y = canvas.height;
        this.targetY = targetY;
        this.color = color;
        this.velocity = -8;
        this.exploded = false;
        this.trail = [];
      }

      update() {
        if (!this.exploded) {
          this.trail.push({ x: this.x, y: this.y });
          if (this.trail.length > 10) this.trail.shift();

          this.y += this.velocity;
          this.velocity += 0.1; // Desaceleración

          if (this.y <= this.targetY) {
            this.explode();
          }
        }
      }

      explode() {
        this.exploded = true;
        const particleCount = 50 + Math.random() * 50;
        
        for (let i = 0; i < particleCount; i++) {
          particlesRef.current.push(new Particle(this.x, this.y, this.color));
        }
      }

      draw(ctx) {
        if (!this.exploded) {
          // Dibujar estela
          ctx.save();
          ctx.strokeStyle = this.color;
          ctx.lineWidth = 2;
          ctx.beginPath();
          this.trail.forEach((point, index) => {
            ctx.globalAlpha = index / this.trail.length;
            if (index === 0) {
              ctx.moveTo(point.x, point.y);
            } else {
              ctx.lineTo(point.x, point.y);
            }
          });
          ctx.stroke();
          ctx.restore();

          // Dibujar cohete
          ctx.save();
          ctx.fillStyle = this.color;
          ctx.beginPath();
          ctx.arc(this.x, this.y, 3, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
        }
      }
    }

    // Colores basados en el color del ganador
    const getFireworkColors = () => {
      const baseColors = {
        red: ['#ff0000', '#ff6b6b', '#ff9999', '#ffcccc'],
        blue: ['#0000ff', '#6b6bff', '#9999ff', '#ccccff'],
        green: ['#00ff00', '#6bff6b', '#99ff99', '#ccffcc'],
        yellow: ['#ffff00', '#ffff6b', '#ffff99', '#ffffcc']
      };

      return baseColors[winner.color] || ['#ffffff', '#ffdd00', '#ff00ff', '#00ffff'];
    };

    const colors = getFireworkColors();

    // Función para crear un nuevo fuego artificial
    const createFirework = () => {
      const x = Math.random() * canvas.width;
      const targetY = Math.random() * canvas.height * 0.4 + canvas.height * 0.1;
      const color = colors[Math.floor(Math.random() * colors.length)];
      
      fireworksRef.current.push(new Firework(x, targetY, color));
    };

    // Función de animación
    const animate = () => {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Crear nuevos fuegos artificiales aleatoriamente
      if (Math.random() < 0.15) {
        createFirework();
      }

      // Actualizar y dibujar fuegos artificiales
      fireworksRef.current = fireworksRef.current.filter(firework => {
        firework.update();
        firework.draw(ctx);
        return !firework.exploded;
      });

      // Actualizar y dibujar partículas
      particlesRef.current = particlesRef.current.filter(particle => {
        particle.update();
        particle.draw(ctx);
        return particle.alpha > 0;
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    // Iniciar animación
    animate();

    // Crear fuegos artificiales iniciales
    for (let i = 0; i < 5; i++) {
      setTimeout(() => createFirework(), i * 200);
    }

    // Limpiar al desmontar
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [winner]);

  const getColorName = (color) => {
    const colorNames = {
      red: 'Rojo',
      blue: 'Azul',
      green: 'Verde',
      yellow: 'Amarillo'
    };
    return colorNames[color] || color;
  };

  return (
    <div className={styles.celebrationOverlay}>
      <canvas ref={canvasRef} className={styles.fireworksCanvas} />
      
      {showMessage && (
        <div className={styles.messageContainer}>
          <div className={styles.trophy}>🏆</div>
          <h1 className={styles.title}>¡FELICITACIONES!</h1>
          <h2 className={styles.winner} style={{
            color: winner.color === 'red' ? '#ff4444' :
                   winner.color === 'blue' ? '#4444ff' :
                   winner.color === 'green' ? '#44ff44' : '#ffff44'
          }}>
            {winner.name}
          </h2>
          <p className={styles.subtitle}>
            Jugador {getColorName(winner.color)} ha ganado la partida
          </p>
          
          <div className={styles.confettiEmojis}>
            <span className={styles.confetti}>🎉</span>
            <span className={styles.confetti}>🎊</span>
            <span className={styles.confetti}>✨</span>
            <span className={styles.confetti}>🎆</span>
            <span className={styles.confetti}>🎇</span>
          </div>

          <button className={styles.closeButton} onClick={onClose}>
            Nueva Partida
          </button>
        </div>
      )}
    </div>
  );
};

export default Celebration;

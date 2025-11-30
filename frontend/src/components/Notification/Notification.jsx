/**
 * Componente Notification - Muestra notificaciones estilizadas
 */

import React, { useEffect } from 'react';
import styles from './Notification.module.css';
import audioService from '../../services/audioService';

const Notification = ({ message, type = 'info', onClose, duration = 4000 }) => {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const getIcon = () => {
    switch (type) {
      case 'error':
        return '⚠️';
      case 'success':
        return '✅';
      case 'warning':
        return '⚡';
      case 'info':
      default:
        return 'ℹ️';
    }
  };

  const handleClose = () => {
    audioService.playClick();
    onClose();
  };

  return (
    <div className={`${styles.notificationOverlay}`} onClick={handleClose}>
      <div 
        className={`${styles.notification} ${styles[type]}`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className={styles.icon}>{getIcon()}</div>
        <div className={styles.content}>
          <p className={styles.message}>{message}</p>
        </div>
        <button className={styles.closeButton} onClick={handleClose}>
          ✕
        </button>
      </div>
    </div>
  );
};

export default Notification;

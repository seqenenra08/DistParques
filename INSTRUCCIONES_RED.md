# Instrucciones para Jugar en Red Local

## 🎮 Configuración para jugar distribuido

### En el servidor (tu máquina):

1. **Obtén tu IP local:**
   ```bash
   # En Linux/Mac:
   ip addr show | grep "inet " | grep -v 127.0.0.1
   
   # O más simple:
   hostname -I
   
   # Busca algo como: 192.168.1.XXX o 10.0.0.XXX
   ```

2. **Inicia el backend:**
   ```bash
   cd backend
   python3 servidor_salas.py
   ```
   El servidor escuchará en todas las interfaces (0.0.0.0:5555)

3. **Configura el frontend:**
   
   Edita el archivo `frontend/.env.local` y cambia la línea:
   ```
   NEXT_PUBLIC_WS_URL=ws://192.168.1.XXX:5555
   ```
   Reemplaza `192.168.1.XXX` con tu IP local obtenida en el paso 1.

4. **Inicia el frontend:**
   ```bash
   cd frontend
   npm run dev
   ```
   
   Por defecto, Next.js escucha solo en localhost. Para que otros puedan acceder:
   ```bash
   npm run dev -- -H 0.0.0.0
   ```

### En las otras máquinas (clientes):

**Opción A: Acceder directamente al frontend del servidor**

Abre el navegador en: `http://IP_DEL_SERVIDOR:3000`

Ejemplo: `http://192.168.1.100:3000`

**Opción B: Ejecutar frontend localmente**

1. Copia la carpeta `frontend` a la otra máquina
2. Instala dependencias:
   ```bash
   cd frontend
   npm install
   ```
3. Crea/edita `frontend/.env.local` con la IP del servidor:
   ```
   NEXT_PUBLIC_WS_URL=ws://192.168.1.XXX:5555
   ```
4. Inicia el frontend:
   ```bash
   npm run dev
   ```

## 🔥 Firewall

Asegúrate de que los puertos estén abiertos en el servidor:

**En Linux (Ubuntu/Debian):**
```bash
# Permitir puerto del backend (WebSocket)
sudo ufw allow 5555/tcp

# Permitir puerto del frontend (HTTP)
sudo ufw allow 3000/tcp

# Ver estado
sudo ufw status
```

**En Linux con firewalld (Fedora/RHEL):**
```bash
sudo firewall-cmd --permanent --add-port=5555/tcp
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --reload
```

## 🌐 Verificación de conectividad

Desde otra máquina en la red, verifica:

```bash
# Probar conexión al backend
nc -zv IP_SERVIDOR 5555

# O con telnet
telnet IP_SERVIDOR 5555

# Probar conexión al frontend
curl http://IP_SERVIDOR:3000
```

## 📝 Ejemplo completo

**Servidor (IP: 192.168.1.100):**
1. `cd backend && python3 servidor_salas.py` → WebSocket en 192.168.1.100:5555
2. Editar `frontend/.env.local`: `NEXT_PUBLIC_WS_URL=ws://192.168.1.100:5555`
3. `cd frontend && npm run dev -- -H 0.0.0.0` → HTTP en 192.168.1.100:3000

**Cliente (otra máquina):**
1. Abrir navegador en: `http://192.168.1.100:3000`
2. El juego se conectará automáticamente al WebSocket en 192.168.1.100:5555

## ⚠️ Notas importantes

- Todas las máquinas deben estar en la **misma red local**
- Si usas WiFi, asegúrate de que el router no tenga **aislamiento AP** activado
- La IP local puede cambiar si tu servidor usa DHCP. Considera usar IP estática o reservar la IP en el router
- Después de cambiar `.env.local`, **reinicia** el servidor de Next.js

## 🚀 Comandos rápidos

**Iniciar todo en el servidor:**
```bash
# Terminal 1 - Backend
cd backend && python3 servidor_salas.py

# Terminal 2 - Frontend (accesible en red)
cd frontend && npm run dev -- -H 0.0.0.0
```

**Obtener tu IP rápidamente:**
```bash
ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v 127.0.0.1
```

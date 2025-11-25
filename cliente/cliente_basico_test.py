#!/usr/bin/env python3
"""Cliente básico para testing - solo se conecta y espera."""
import socket
import json

def cliente_basico():
    HOST = "127.0.0.1"
    PORT = 5555
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    print("✅ Conectado al servidor")
    
    # Recibir color
    buffer = ""
    while '\n' not in buffer:
        data = sock.recv(4096).decode('utf-8')
        buffer += data
    
    line = buffer.split('\n')[0]
    msg = json.loads(line.strip())
    print(f"🎨 Color asignado: {msg.get('color')}")
    
    # Enviar START
    start_msg = {"accion": "START"}
    sock.sendall((json.dumps(start_msg) + "\n").encode('utf-8'))
    print("📤 Solicitud de inicio enviada")
    
    # Escuchar mensajes
    buffer = ""
    while True:
        try:
            data = sock.recv(4096).decode('utf-8')
            if not data:
                break
            
            buffer += data
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                if line.strip():
                    msg = json.loads(line)
                    print(f"📩 {msg.get('tipo')}: {msg}")
        except KeyboardInterrupt:
            print("\n👋 Saliendo...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    sock.close()

if __name__ == "__main__":
    cliente_basico()

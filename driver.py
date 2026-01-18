import socket
import struct
import os
from evdev import UInput, ecodes, AbsInfo

# === CONFIGURACIÓN ===
PSM_CTRL = 0x11
PSM_INTR = 0x13

# === DEFINICIÓN DEL JOYSTICK ===
cap = {
    ecodes.EV_KEY: [
        # Botones Principales
        ecodes.BTN_SELECT, ecodes.BTN_START, ecodes.BTN_MODE,
        ecodes.BTN_THUMBL, ecodes.BTN_THUMBR, # L3 y R3
        ecodes.BTN_TL, ecodes.BTN_TR, ecodes.BTN_TL2, ecodes.BTN_TR2, # Gatillos
        ecodes.BTN_A, ecodes.BTN_B, ecodes.BTN_X, ecodes.BTN_Y, # Figuras
    ],
    ecodes.EV_ABS: [
        # Palancas Analógicas (Izquierda y Derecha)
        (ecodes.ABS_X, AbsInfo(value=128, min=0, max=255, fuzz=0, flat=15, resolution=0)),
        (ecodes.ABS_Y, AbsInfo(value=128, min=0, max=255, fuzz=0, flat=15, resolution=0)),
        (ecodes.ABS_RX, AbsInfo(value=128, min=0, max=255, fuzz=0, flat=15, resolution=0)),
        (ecodes.ABS_RY, AbsInfo(value=128, min=0, max=255, fuzz=0, flat=15, resolution=0)),
        
        # CRUCETA (HAT) - Esto arreglará el movimiento en menús
        (ecodes.ABS_HAT0X, AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
        (ecodes.ABS_HAT0Y, AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
    ]
}

def setup_server(psm):
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
    sock.bind(("00:00:00:00:00:00", psm))
    sock.listen(1)
    return sock

def send_magic_packet(sock):
    packet = bytes([0x52, 0x01, 0x53, 0xF4, 0x42, 0x03, 0x00, 0x00])
    try:
        sock.send(packet)
    except:
        pass

def main():
    print("=== DRIVER PS3 CLON: CORRECCIÓN CRUCETA ===")
    
    # Limpieza de entorno
    os.system("sudo killall -9 bluetoothd 2>/dev/null")
    os.system("sudo ip link set hci0 up")
    os.system("sudo btmgmt power on")
    os.system("sudo btmgmt connectable on")
    
    print("[*] Esperando al mando... (Presiona Botón PS)")
    
    s_ctrl = setup_server(PSM_CTRL)
    s_intr = setup_server(PSM_INTR)
    
    c_ctrl, _ = s_ctrl.accept()
    print("   [+] Control OK")
    c_intr, _ = s_intr.accept()
    print("   [+] Datos OK")
    
    send_magic_packet(c_ctrl)
    
    ui = UInput(cap, name="Sony PS3 Clon (Fixed Hat)", version=0x1)
    print("\n[!!!] CRUCETA ARREGLADA. MINIMIZA Y A JUGAR [!!!]")

    try:
        while True:
            data = c_intr.recv(64)
            if not data: break
            
            if len(data) >= 12:
                # === DECODIFICACIÓN DEL BYTE 3 (Tus datos) ===
                # Select(1), L3(2), R3(4), Start(8), Up(16), Right(32), Down(64), Left(128)
                b1 = data[3]
                
                # Botones Simples
                ui.write(ecodes.EV_KEY, ecodes.BTN_SELECT, (b1 & 0x01))       # Bit 0
                ui.write(ecodes.EV_KEY, ecodes.BTN_THUMBL, (b1 & 0x02) >> 1)  # Bit 1 (L3)
                ui.write(ecodes.EV_KEY, ecodes.BTN_THUMBR, (b1 & 0x04) >> 2)  # Bit 2 (R3)
                ui.write(ecodes.EV_KEY, ecodes.BTN_START,  (b1 & 0x08) >> 3)  # Bit 3

                # CRUCETA COMO HAT (Ejes)
                # Arriba (16) y Abajo (64 - Inferred)
                hat_y = 0
                if (b1 & 16): hat_y = -1 # Arriba es negativo en HatY
                elif (b1 & 64): hat_y = 1 # Abajo es positivo
                ui.write(ecodes.EV_ABS, ecodes.ABS_HAT0Y, hat_y)

                # Izquierda (128 - Inferred) y Derecha (32)
                hat_x = 0
                if (b1 & 128): hat_x = -1 # Izquierda es negativo
                elif (b1 & 32): hat_x = 1 # Derecha es positivo
                ui.write(ecodes.EV_ABS, ecodes.ABS_HAT0X, hat_x)

                # === BYTE 4 (Figuras) ===
                # X(64), O(32), etc.
                b2 = data[4]
                ui.write(ecodes.EV_KEY, ecodes.BTN_TL2, (b2 & 0x01))
                ui.write(ecodes.EV_KEY, ecodes.BTN_TR2, (b2 & 0x02) >> 1)
                ui.write(ecodes.EV_KEY, ecodes.BTN_TL,  (b2 & 0x04) >> 2)
                ui.write(ecodes.EV_KEY, ecodes.BTN_TR,  (b2 & 0x08) >> 3)
                ui.write(ecodes.EV_KEY, ecodes.BTN_Y,   (b2 & 0x10) >> 4) 
                ui.write(ecodes.EV_KEY, ecodes.BTN_B,   (b2 & 0x20) >> 5) 
                ui.write(ecodes.EV_KEY, ecodes.BTN_A,   (b2 & 0x40) >> 6) 
                ui.write(ecodes.EV_KEY, ecodes.BTN_X,   (b2 & 0x80) >> 7) 

                # === BOTÓN PS ===
                if len(data) > 5:
                    ui.write(ecodes.EV_KEY, ecodes.BTN_MODE, (data[5] & 0x01))

                # === ANALÓGICOS ===
                ui.write(ecodes.EV_ABS, ecodes.ABS_X, data[7])
                ui.write(ecodes.EV_ABS, ecodes.ABS_Y, data[8])
                ui.write(ecodes.EV_ABS, ecodes.ABS_RX, data[9])
                ui.write(ecodes.EV_ABS, ecodes.ABS_RY, data[10])

                ui.syn()

    except KeyboardInterrupt:
        print("\nApagando...")
    finally:
        try:
            ui.close()
            c_ctrl.close()
            c_intr.close()
            s_ctrl.close()
            s_intr.close()
        except:
            pass

if __name__ == "__main__":
    main()

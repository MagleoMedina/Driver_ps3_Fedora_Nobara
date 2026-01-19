El driver se salta el servicio Bluetooth del sistema operativo, se conecta directamente a los sockets L2CAP (Puertos 17 y 19), realiza el "Handshake" específico que necesitan los clones y mapea los datos crudos a un Joystick Virtual correctamente configurado usando `evdev`.

---

## 📋 Requisitos Previos

Antes de empezar, asegúrate de tener instaladas las dependencias del sistema y de Python.

### 1. Herramientas del Sistema (Fedora/Nobara)

Necesitas las herramientas de compilación, librerías de desarrollo de BlueZ y utilidades de bluetooth deprecadas (para comandos de bajo nivel).

### 2. Python

Fue utilizada la versión 3.14.

```bash
sudo dnf install python3-pip python3-devel bluez git gcc make evdev
```

---

## 🚀 Pasos de Instalación y Uso

1. **Verifica tu controlador Bluetooth:**

   ```bash
   bluetoothctl list
   ```

   Esto te dará una salida similar a:

   ```
   Controller 33:03:30:0A:88:AA nobara-pc [default]
   ```

2. **Aplica máscara al servicio Bluetooth de Nobara:**

   ```bash
   sudo systemctl mask bluetooth
   ```

   Resultado esperado:

   ```
   Created symlink '/etc/systemd/system/bluetooth.service' → '/dev/null'.
   ```

3. **Compila `sixpair.c`:**

   ```bash
   gcc -o sixpair sixpair.c
   ```

4. **Ejecuta `sixpair`:**

   Conecta el mando de PS3 a la PC hasta que las luces estén fijas.

   ```bash
   ./sixpair 33:03:30:0A:88:AA
   ```

   Resultado esperado:

   ```
   ¡Mando actualizado! Ahora desconecta el USB y presiona el botón PS.
   ```

5. Espera a que las luces del mando dejen de parpadear y se apague.

6. **Ejecuta el script de Python:**

   ```bash
   python3 driver.py
   ```

7. Presiona el botón PS y ¡listo! Mando conectado.

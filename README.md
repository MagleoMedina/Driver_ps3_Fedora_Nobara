# Driver_ps3_Fedora_Nobara

# Custom Driver para Mandos PS3 Clones (Shanwan/Gasia) en Linux

Este proyecto contiene un driver en espacio de usuario (Userspace Driver) escrito en Python para mandos de PlayStation 3 "Clones" que no funcionan con el stack estándar de Linux (BlueZ) debido a problemas de *timeout*, desconexiones constantes o mapeos incorrectos.

El driver se salta el servicio Bluetooth del sistema operativo, se conecta directamente a los sockets L2CAP (Puertos 17 y 19), realiza el "Handshake" específico que necesitan los clones y mapea los datos crudos a un Joystick Virtual correctamente configurado usando `evdev`.

## 📋 Requisitos Previos

Antes de empezar, asegúrate de tener instaladas las dependencias del sistema y de Python.

### 1. Herramientas del Sistema (Fedora/Nobara)
Necesitas las herramientas de compilación, librerías de desarrollo de BlueZ y utilidades de bluetooth deprecadas (para comandos de bajo nivel).

### Python
Fue utilizada la version 3.14

```bash
sudo dnf install python3-pip python3-devel bluez git gcc make evdev
```
#Ejecuta los siguientes comandos

bluetoothctl list
Controller 33:03:30:0A:88:AA nobara-pc [default]



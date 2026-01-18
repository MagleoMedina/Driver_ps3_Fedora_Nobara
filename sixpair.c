/* sixpair.c - Herramienta para emparejar DualShock 3 en Linux */
#include <string.h>
#include <unistd.h>
#include <stdio.h>
#include <usb.h>

#define VENDOR 0x054c
#define PRODUCT 0x0268

// Busca la MAC del adaptador Bluetooth en el sistema
char *get_bdaddr() {
    static char bdaddr[18];
    FILE *f = popen("hcitool dev | grep hci0 | cut -f3", "r");
    if(!f) return NULL;
    fgets(bdaddr, 18, f);
    pclose(f);
    return bdaddr;
}

int main(int argc, char *argv[]) {
    struct usb_bus *busses;
    struct usb_bus *bus;
    struct usb_device *dev;
    usb_dev_handle *devh;
    char msg[8];
    int res;
    char *mac_addr;
    unsigned int mac[6];

    // Obtener MAC del Bluetooth local (hci0)
    mac_addr = get_bdaddr();
    if (argc > 1) mac_addr = argv[1]; // Permite pasar MAC manual si falla la auto-deteccion

    if (!mac_addr || strlen(mac_addr) < 17) {
        printf("Error: No se pudo detectar la dirección MAC de tu Bluetooth.\n");
        printf("Uso manual: sudo ./sixpair XX:XX:XX:XX:XX:XX\n");
        return 1;
    }

    sscanf(mac_addr, "%x:%x:%x:%x:%x:%x", 
        &mac[0], &mac[1], &mac[2], &mac[3], &mac[4], &mac[5]);

    printf("Configurando mando para conectar al Host: %02X:%02X:%02X:%02X:%02X:%02X\n",
        mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);

    msg[0] = 0x01;
    msg[1] = 0x00;
    msg[2] = mac[5];
    msg[3] = mac[4];
    msg[4] = mac[3];
    msg[5] = mac[2];
    msg[6] = mac[1];
    msg[7] = mac[0];

    usb_init();
    usb_find_busses();
    usb_find_devices();
    busses = usb_get_busses();

    for (bus = busses; bus; bus = bus->next) {
        for (dev = bus->devices; dev; dev = dev->next) {
            if (dev->descriptor.idVendor == VENDOR && dev->descriptor.idProduct == PRODUCT) {
                devh = usb_open(dev);
                if (!devh) continue;
                // Reclamar interfaz (necesario para enviar comandos)
                usb_claim_interface(devh, 0);
                
                // Comando mágico para establecer la dirección Master
                res = usb_control_msg(devh, USB_TYPE_CLASS | USB_RECIP_INTERFACE | USB_ENDPOINT_IN, 
                                      0x01, 0x03f5, 0, msg, 8, 5000);
                
                if(res < 0) {
                     // Intentar método alternativo para algunos clones
                     res = usb_control_msg(devh, USB_TYPE_CLASS | USB_RECIP_INTERFACE | USB_ENDPOINT_IN, 
                                      0x01, 0x03f2, 0, msg, 8, 5000);
                }
                printf("¡Mando actualizado! Ahora desconecta el USB y presiona el botón PS.\n");
                usb_close(devh);
                return 0;
            }
        }
    }
    printf("No se encontró ningún mando PS3 conectado por USB.\n");
    return 1;
}

import usb.core

dev = usb.core.find(idVendor=0x05ac, idProduct=0x1227)
if dev is None:
    print("Device not found")
else:
    print("Found device:", dev)
    try:
        cfg = dev.get_active_configuration()
        print("Active configuration:", cfg.bConfigurationValue)
    except Exception as e:
        print("Active configuration error:", e)

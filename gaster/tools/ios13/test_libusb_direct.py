import ctypes
import ctypes.util

# Load libusb-1.0
libusb_path = ctypes.util.find_library("usb-1.0")
print(f"libusb library: {libusb_path}")
libusb = ctypes.CDLL(libusb_path)

# Initialize libusb
ctx = ctypes.c_void_p()
ret = libusb.libusb_init(ctypes.byref(ctx))
print(f"libusb_init: {ret}")

# Enumerate devices
devs = ctypes.POINTER(ctypes.c_void_p)()
cnt = libusb.libusb_get_device_list(ctx, ctypes.byref(devs))
print(f"Device count: {cnt}")

class DeviceDescriptor(ctypes.Structure):
    _fields_ = [
        ("bLength", ctypes.c_uint8),
        ("bDescriptorType", ctypes.c_uint8),
        ("bcdUSB", ctypes.c_uint16),
        ("bDeviceClass", ctypes.c_uint8),
        ("bDeviceSubClass", ctypes.c_uint8),
        ("bDeviceProtocol", ctypes.c_uint8),
        ("bMaxPacketSize0", ctypes.c_uint8),
        ("idVendor", ctypes.c_uint16),
        ("idProduct", ctypes.c_uint16),
        ("bcdDevice", ctypes.c_uint16),
        ("iManufacturer", ctypes.c_uint8),
        ("iProduct", ctypes.c_uint8),
        ("iSerialNumber", ctypes.c_uint8),
        ("bNumConfigurations", ctypes.c_uint8),
    ]

for i in range(cnt):
    dev = devs[i]
    desc = DeviceDescriptor()
    libusb.libusb_get_device_descriptor(dev, ctypes.byref(desc))
    print(f"Dev {i}: VID={hex(desc.idVendor)} PID={hex(desc.idProduct)}")
    if desc.idVendor == 0x05ac and desc.idProduct == 0x1227:
        print("  Found Apple DFU device!")
        handle = ctypes.c_void_p()
        open_ret = libusb.libusb_open(dev, ctypes.byref(handle))
        print(f"  libusb_open: {open_ret}")
        if open_ret == 0:
            cfg = ctypes.c_int()
            get_cfg_ret = libusb.libusb_get_configuration(handle, ctypes.byref(cfg))
            print(f"  libusb_get_configuration: ret={get_cfg_ret}, cfg={cfg.value}")
            
            # Read serial number descriptor
            # Control transfer: bmRequestType=0x80, bRequest=6 (GET_DESCRIPTOR), wValue=(3<<8)|iSerialNumber, wIndex=0x409
            buf = (ctypes.c_uint8 * 255)()
            ctrl_ret = libusb.libusb_control_transfer(
                handle, 0x80, 6, (3 << 8) | desc.iSerialNumber, 0x409,
                buf, 255, 2000
            )
            print(f"  libusb_control_transfer (serial): {ctrl_ret}")
            print(f"  buf[0] = {buf[0]}, buf[1] = {buf[1]}")
            if ctrl_ret > 2:
                # String is UTF-16LE
                raw_bytes = bytes(buf[:ctrl_ret])
                serial_str = raw_bytes[2:].decode("utf-16le", errors="replace")
                print(f"  Decoded serial: '{serial_str}'")
            libusb.libusb_close(handle)

libusb.libusb_free_device_list(devs, 1)
libusb.libusb_exit(ctx)

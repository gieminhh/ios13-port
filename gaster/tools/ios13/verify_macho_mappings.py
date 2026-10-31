import struct

kc_path = "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/kernelcache-ipad13-decompressed"

with open(kc_path, "rb") as f:
    magic, cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags, reserved = struct.unpack("<IIIIIIII", f.read(32))
    text_vmaddr = None
    segments = []
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack("<II", f.read(8))
        cmd_data = f.read(cmdsize - 8)
        if cmd == 0x19: # LC_SEGMENT_64
            segname = cmd_data[:16].rstrip(b"\x00").decode("latin1", errors="ignore")
            vmaddr, vmsize, fileoff, filesize = struct.unpack("<QQQQ", cmd_data[16:48])
            if text_vmaddr is None and segname == "__TEXT":
                text_vmaddr = vmaddr
            segments.append((segname, vmaddr, vmsize, fileoff, filesize))

print(f"Base __TEXT vmaddr: {hex(text_vmaddr)}")
print(f"{'Segment':18} {'vmaddr':18} {'vmsize':10} {'fileoff':10} {'filesize':10} {'vmaddr - base':14} {'Contiguous?'}")
print("-" * 90)

prev_end = 0
all_contiguous = True
for segname, vmaddr, vmsize, fileoff, filesize in segments:
    delta = vmaddr - text_vmaddr if text_vmaddr else 0
    is_match = (delta == fileoff)
    if not is_match and filesize > 0:
        all_contiguous = False
    print(f"{segname:18} {hex(vmaddr):18} {hex(vmsize):10} {hex(fileoff):10} {hex(filesize):10} {hex(delta):14} {is_match}")

print("-" * 90)
print(f"All core loaded segments (filesize > 0) contiguous with zero virtual-to-file skew: {all_contiguous}")

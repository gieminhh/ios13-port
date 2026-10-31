import struct
import sys

kc_path = "/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-research/kernelcache-ipad13-decompressed"
with open(kc_path, "rb") as f:
    magic, cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags, reserved = struct.unpack("<IIIIIIII", f.read(32))
    print(f"Magic: {hex(magic)} | CPUType: {hex(cputype)} | CPUSubType: {hex(cpusubtype)}")
    print(f"Commands: {ncmds} | Size: {sizeofcmds}")
    
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack("<II", f.read(8))
        cmd_data = f.read(cmdsize - 8)
        if cmd == 0x19: # LC_SEGMENT_64
            segname = cmd_data[:16].rstrip(b"\x00").decode("latin1", errors="ignore")
            vmaddr, vmsize, fileoff, filesize = struct.unpack("<QQQQ", cmd_data[16:48])
            print(f"  Segment: {segname:16} vmaddr: {hex(vmaddr)} vmsize: {hex(vmsize)} off: {hex(fileoff)} size: {hex(filesize)}")
        elif cmd == 0x80000028: # LC_MAIN
            entryoff, stacksize = struct.unpack("<QQ", cmd_data[:16])
            print(f"  LC_MAIN: entryoff: {hex(entryoff)}")
        elif cmd == 0x2: # LC_SYMTAB
            symoff, nsyms, stroff, strsize = struct.unpack("<IIII", cmd_data[:16])
            print(f"  LC_SYMTAB: nsyms = {nsyms}, stroff = {hex(stroff)}, strsize = {hex(strsize)}")
        elif cmd == 0x5: # LC_UNIXTHREAD
            pc = struct.unpack("<Q", cmd_data[264:272])[0]
            print(f"  LC_UNIXTHREAD: pc = {hex(pc)}")

    # Check _StartIOKit
    start_iokit_off = 0x5f5a20
    f.seek(start_iokit_off)
    code_iokit = f.read(32)
    print(f"_StartIOKit instructions at file offset {hex(start_iokit_off)}: {code_iokit.hex()}")

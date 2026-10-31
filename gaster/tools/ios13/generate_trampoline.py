#!/usr/bin/env python3
"""Generate ARM64 Trampoline bridging iOS 12 iBoot boot_args to Darwin 19 kernel."""
import argparse
from pathlib import Path

TRAMPOLINE_ASM = """/* Trampoline bridging iOS 12 iBoot-4513 boot_args to Darwin 19 xnu-6153 */
.text
.align 2
.global _start

_start:
    /* Input: x0 = old_boot_args physical address */
    mov x19, x0                 /* x19 = old_boot_args */
    add x20, x0, #0x1000        /* x20 = new_boot_args (offset by 4KB) */

    /* 1. Copy first 0x70 bytes (virtBase, physBase, memSize, video, devicetreeP/len) */
    mov x1, #0
copy_header:
    ldr x2, [x19, x1]
    str x2, [x20, x1]
    add x1, x1, #8
    cmp x1, #0x70
    b.lt copy_header

    /* 2. Copy original 256-byte CommandLine (offset 0x70 to 0x170) */
copy_cmdline:
    ldr x2, [x19, x1]
    str x2, [x20, x1]
    add x1, x1, #8
    cmp x1, #0x170
    b.lt copy_cmdline

    /* 3. Zero-fill the expanded 352 bytes of CommandLine (offset 0x170 to 0x2d0) */
    mov x2, #0
zero_cmdline:
    str x2, [x20, x1]
    add x1, x1, #8
    cmp x1, #0x2d0
    b.lt zero_cmdline

    /* 4. Map bootFlags: old offset 0x170 -> new offset 0x2d0 */
    ldr x2, [x19, #0x170]
    str x2, [x20, #0x2d0]

    /* 5. Map memSizeActual: old offset 0x178 -> new offset 0x2d8 */
    ldr x2, [x19, #0x178]
    str x2, [x20, #0x2d8]

    /* 6. Hand off to Darwin 19 Kernel Entry */
    mov x0, x20                 /* x0 = new_boot_args */
    ldr x1, kernel_entry_addr
    br x1

.align 3
kernel_entry_addr:
    .quad 0x0                   /* Filled at runtime or patch time */
"""

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entry', type=lambda x: int(x, 0), default=0, help="Kernel entry physical address")
    parser.add_argument('--out', type=Path, default=Path('trampoline.S'), help="Output assembly file")
    args = parser.parse_args()

    content = TRAMPOLINE_ASM.replace('.quad 0x0', f'.quad {hex(args.entry)}')
    args.out.write_text(content)
    print(f"Generated {args.out} with kernel entry: {hex(args.entry)}")

if __name__ == '__main__':
    main()

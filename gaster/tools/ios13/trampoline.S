/* Trampoline bridging iOS 12 iBoot-4513 boot_args to Darwin 19 xnu-6153 */
.text
.align 2
.global _start

_start:
    /* Input: x0 = old_boot_args physical address */
    mov x19, x0                 /* x19 = old_boot_args */
    add x20, x0, #0x1000        /* x20 = new_boot_args (offset by 4KB in physical DRAM) */

    /* 1. Copy first 0x70 bytes (virtBase, physBase, memSize, video, devicetree) */
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

    /* 6. Calculate Physical Kernel Entry Point: physBase + 0xbd490 */
    ldr x1, [x20, #0x10]        /* x1 = physBase (offset 0x10 in boot_args) */
    add x1, x1, #0xbd, lsl #12  /* x1 += 0xbd000 */
    add x1, x1, #0x490          /* x1 += 0x490 -> x1 = physBase + 0xbd490 */

    /* 7. Hand off to Darwin 19 Kernel Entry in Physical Memory */
    mov x0, x20                 /* x0 = new_boot_args physical address */
    br x1

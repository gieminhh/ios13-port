.text
.align 2
.global _start

_start:
    /* Compute PE_Video address relative to current PC using adrp/add */
    /* Virtual address of this hook: 0xfffffff0075f9a20 */
    /* Target PE_Video virtual address: 0xfffffff0070b2bb8 */
    /* Offset: 0x70b2bb8 - 0x75f9a20 = -0x546e68 */
    /* PC page = 0x75f9000, Target page = 0x70b2000 -> page diff = -0x547000 (-1351 pages) */
    adrp x8, -0x547000
    add x8, x8, #0xbb8
    ldr x0, [x8]            /* x0 = v_baseAddr */
    cbz x0, halt

    /* Fill 256,000 pixels (0x3E800: 750 x ~341 lines) with Solid Green: 0x0000FF00 */
    movz w1, #0xff00
    movz x2, #0xe800
    movk x2, #0x3, lsl #16

paint_loop:
    str w1, [x0], #4
    subs x2, x2, #1
    b.ne paint_loop

halt:
    wfe
    b halt

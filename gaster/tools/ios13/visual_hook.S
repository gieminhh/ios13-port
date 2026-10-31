.text
.align 2
.global _start

_start:
    /* Load PE_Video address: 0xfffffff0070b2bb8 */
    ldr x8, pe_video_addr
    ldr x0, [x8]            /* x0 = v_baseAddr (framebuffer) */
    cbz x0, halt            /* if NULL, just halt */

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

.align 3
pe_video_addr:
    .quad 0xfffffff0070b2bb8

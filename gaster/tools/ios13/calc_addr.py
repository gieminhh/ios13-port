# Calculate PE_Video address
pc = 0xfffffff007644474
insn = 0xd0ffd368
immhi = (insn >> 5) & 0x7ffff
immlo = (insn >> 29) & 0x3
imm = (immhi << 2) | immlo
if imm & (1 << 20):
    imm -= (1 << 21)
page_addr = (pc & ~0xfff) + (imm << 12)
addr = page_addr + 0xbb8
print("Target address of PE_Video:", hex(addr))

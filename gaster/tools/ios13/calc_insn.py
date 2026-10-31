imm = -1351
if imm < 0:
    imm += (1 << 21)
immlo = imm & 3
immhi = imm >> 2
insn = 0x90000000 | (immlo << 29) | (immhi << 5) | 8
print("Instruction hex:", hex(insn))

p_imm = (insn >> 5) & 0x7ffff
p_lo = (insn >> 29) & 3
p_val = (p_imm << 2) | p_lo
if p_val & (1 << 20):
    p_val -= (1 << 21)
print("Decoded page difference:", p_val, "(expected -1351)")

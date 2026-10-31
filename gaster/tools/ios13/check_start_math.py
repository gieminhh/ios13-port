# Check XNU start.s logic for ARM64
# In XNU (osfmk/arm64/start.s):
# Ldr x22, [x20, kBootArgsVirtBase]
# Ldr x23, [x20, kBootArgsPhysBase]
#
# But wait, how does XNU compute physical address of a symbol before MMU is on?
# Let's inspect the math!
print("Inspecting start_cpu arithmetic...")

import subprocess

p = subprocess.Popen(
    ["git", "credential", "fill"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
out, err = p.communicate("protocol=https\nhost=github.com\n\n")
print("Output:", out)
print("Error:", err)
print("Code:", p.returncode)

import json

with open("/mnt/c/Users/cmjnh/Desktop/ios13-port/ios13-analysis/native-baseline.json") as f:
    d = json.load(f)
print("Keys in baseline:", list(d.keys()))
if "components" in d:
    for k, v in d["components"].items():
        print(f"Component: {k} -> {v}")
elif "kbags" in d:
    print("kbags:", d["kbags"])
else:
    print("Full json:", d)

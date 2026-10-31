import urllib.request
import re

url = "https://raw.githubusercontent.com/apple-oss-distributions/xnu/xnu-6153.11.26/osfmk/arm64/start.s"
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode("utf-8")
        print(f"Downloaded xnu-6153 start.s ({len(content)} bytes)")
        with open("/mnt/c/Users/cmjnh/Desktop/ios13-port/gaster/tools/ios13/xnu_start.s", "w") as out:
            out.write(content)
        for line in content.splitlines()[:50]:
            print(line)
except Exception as e:
    print("Error:", e)

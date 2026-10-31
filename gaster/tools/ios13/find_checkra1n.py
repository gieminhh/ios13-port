import urllib.request
import re

url = "https://checkra.in/releases/0.12.4-beta"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        matches = re.findall(r'https://assets\.checkra\.in/downloads/[^"\'>\s]+', html)
        for m in set(matches):
            print(m)
except Exception as e:
    print("Error:", e)

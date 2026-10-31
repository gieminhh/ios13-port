import urllib.request
import json

url = "https://api.github.com/users/gieminhh/repos"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req) as resp:
        repos = json.loads(resp.read().decode())
        print(f"Total public repos: {len(repos)}")
        for r in repos:
            print(f"  {r['name']}: {r['clone_url']}")
except Exception as e:
    print("Error:", e)

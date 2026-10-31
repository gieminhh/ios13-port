import urllib.request
import json

# Token retrieved from Git Credential Manager
token = "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"

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Mozilla/5.0"
}

# 1. Check user info and scopes
req = urllib.request.Request("https://api.github.com/user", headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        scopes = resp.headers.get("X-OAuth-Scopes", "")
        data = json.loads(resp.read().decode())
        print(f"Authenticated as: {data.get('login')}")
        print(f"Token Scopes: {scopes}")
except Exception as e:
    print("User check error:", e)

# 2. Check if ios13-port exists
req2 = urllib.request.Request("https://api.github.com/repos/gieminhh/ios13-port", headers=headers)
try:
    with urllib.request.urlopen(req2) as resp:
        data = json.loads(resp.read().decode())
        print(f"Repo ios13-port exists: {data.get('html_url')} (private={data.get('private')})")
except urllib.error.HTTPError as e:
    if e.code == 404:
        print("Repo ios13-port does not exist yet. We can create it.")
    else:
        print("Repo check error:", e)

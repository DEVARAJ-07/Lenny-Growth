import urllib.request
import json

boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="growth_notes.txt"\r\n'
    f"Content-Type: text/plain\r\n\r\n"
    f"Lenny podcast growth principles: retention is the foundation of growth.\r\n"
    f"--{boundary}--\r\n"
).encode("utf-8")

req = urllib.request.Request(
    "http://127.0.0.1:8000/chats/5a1a54b0-6d3e-48f4-aefb-0cd61654d2cb/upload",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
)

with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode())

print("Upload Result:", json.dumps(res, indent=2))

import urllib.request
import json
try:
    req = urllib.request.Request('https://resort-inventory.vercel.app/chat/api/room/1/messages/?after=2020-01-01T00:00:00Z', headers={'Content-Type': 'application/json'})
    print(urllib.request.urlopen(req).read().decode('utf-8'))
except Exception as e:
    print(e)

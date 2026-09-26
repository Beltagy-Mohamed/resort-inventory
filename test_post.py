import urllib.request
import json
try:
    req = urllib.request.Request('https://resort-inventory.vercel.app/chat/api/room/1/messages/', method='POST', data=json.dumps({'content':'hello'}).encode('utf-8'), headers={'Content-Type': 'application/json'})
    print(urllib.request.urlopen(req).read().decode('utf-8'))
except Exception as e:
    print(e)

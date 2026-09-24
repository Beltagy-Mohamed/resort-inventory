import re
path = r'E:\خاص مشروع\client_delivery\inventory\urls.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = re.sub(r'\n\s*path\("remote-setup-db/".*?\),', '', c)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

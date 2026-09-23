import re
path = r'E:\خاص مشروع\client_delivery\inventory\urls.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

new_pattern = '    path("remote-setup-db/", views.remote_setup, name="remote_setup"),\n]'
c = c.replace(']', new_pattern)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

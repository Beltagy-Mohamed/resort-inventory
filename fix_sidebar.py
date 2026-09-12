import os

path = r'g:\client_delivery\templates\layout\sidebar.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('{% if perms.inventory.add_product %}\n        {% if perms.inventory.add_product %}', '{% if perms.inventory.add_product %}')
c = c.replace('target="_blank"', '')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

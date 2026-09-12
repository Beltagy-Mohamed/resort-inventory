import os

path = r'g:\client_delivery\inventory\views\dashboard.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('F("price")', 'F("cost_price")')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

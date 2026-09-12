import os

path = r'g:\client_delivery\inventory\views\dashboard.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('order_by("-price")', 'order_by("-selling_price")')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

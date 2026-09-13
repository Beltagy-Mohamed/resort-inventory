import os

path = r'g:\client_delivery\inventory\views\__init__.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

if 'from .management import *' not in c:
    c += '\nfrom .management import *\n'

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

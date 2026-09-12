import os

path = r'g:\client_delivery\inventory\admin.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('from .models import Category, Color, Size, Product, CodeSequence',
              'from .models import Category, Color, Size, Product, CodeSequence, Warehouse, Partner, Stock')

c += '\nadmin.site.register(Warehouse)\nadmin.site.register(Partner)\nadmin.site.register(Stock)\n'

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

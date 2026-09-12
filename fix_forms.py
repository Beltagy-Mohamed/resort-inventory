import os

path = r'g:\client_delivery\inventory\forms.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace("'price'", "'cost_price', 'selling_price'")
# In labels, replace Price with Cost Price & Selling Price
# We have a dictionary of labels in forms.py
c = c.replace("'price': 'السعر',", "'cost_price': 'سعر الشراء / التكلفة',\n            'selling_price': 'سعر البيع / التوريد',")

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

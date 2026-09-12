import os

path = r'g:\client_delivery\templates\transactions\list.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target = '''<td style="background:red;color:white;">
    {{ t.product.name }}
</td>

<td style="background:blue;color:white;">
    {{ t.product.product_code }}
</td>'''

repl = '''<td data-label="{% trans 'Product' %}">{{ t.product.name }}</td>
<td data-label="{% trans 'User' %}">{% if t.user %}{{ t.user.username }}{% else %}-{% endif %}</td>
<td data-label="{% trans 'Code' %}">{{ t.product.product_code }}</td>'''

c = c.replace(target, repl)

c = c.replace('<td colspan="5">', '<td colspan="6">')
c = c.replace('<td colspan="7">', '<td colspan="6">')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

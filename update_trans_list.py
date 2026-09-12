import os

path = r'g:\client_delivery\templates\transactions\list.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target_th = '''<th>{% trans "Type" %}</th>

<th>{% trans "Quantity" %}</th>'''

repl_th = '''<th>{% trans "Type" %}</th>
<th>الجهة</th>
<th>المخزن</th>
<th>{% trans "Quantity" %}</th>'''

c = c.replace(target_th, repl_th)

target_td = '''<td>{{ t.get_transaction_type_display }}</td>

<td>{{ t.quantity }}</td>'''

repl_td = '''<td data-label="{% trans 'Type' %}">{{ t.get_transaction_type_display }}</td>
<td data-label="الجهة">{% if t.partner %}{{ t.partner.name }}{% else %}-{% endif %}</td>
<td data-label="المخزن">{% if t.warehouse %}{{ t.warehouse.name }}{% else %}-{% endif %}</td>
<td data-label="{% trans 'Quantity' %}">{{ t.quantity }}</td>'''

c = c.replace(target_td, repl_td)

c = c.replace('colspan="6"', 'colspan="8"')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

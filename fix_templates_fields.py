import os

# warehouses_list.html
path1 = r'g:\client_delivery\templates\management\warehouses_list.html'
with open(path1, 'r', encoding='utf-8') as f:
    c1 = f.read()

c1 = c1.replace('<th>الحالة</th>', '<th>أمين المخزن</th>')
c1 = c1.replace('<td>{% if w.is_active %}<span style="color: green;">نشط</span>{% else %}<span style="color: red;">غير نشط</span>{% endif %}</td>', '<td>{{ w.manager|default:"-" }}</td>')

with open(path1, 'w', encoding='utf-8') as f:
    f.write(c1)

# partners_list.html
path2 = r'g:\client_delivery\templates\management\partners_list.html'
with open(path2, 'r', encoding='utf-8') as f:
    c2 = f.read()

c2 = c2.replace('<th>الهاتف</th>\n                <th>الحالة</th>', '<th>بيانات التواصل</th>')
c2 = c2.replace('<td>{{ p.phone|default:"-" }}</td>\n                <td>{% if p.is_active %}<span style="color: green;">نشط</span>{% else %}<span style="color: red;">غير نشط</span>{% endif %}</td>', '<td>{{ p.contact_info|default:"-" }}</td>')
c2 = c2.replace('colspan="5"', 'colspan="4"')

with open(path2, 'w', encoding='utf-8') as f:
    f.write(c2)

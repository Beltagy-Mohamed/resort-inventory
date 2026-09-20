import io

path = 'e:/خاص مشروع/client_delivery/templates/products/list.html'
with io.open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace("<th>سعر الشراء</th>\n                <th>سعر البيع</th>", "{% if user.is_superuser or is_leadership %}<th>سعر الشراء</th>{% endif %}\n                <th>سعر البيع</th>")
c = c.replace("<td>{{ p.cost_price }}</td>\n                <td>{{ p.selling_price }}</td>", "{% if user.is_superuser or is_leadership %}<td>{{ p.cost_price }}</td>{% endif %}\n                <td>{{ p.selling_price }}</td>")

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(c)

import os

path = r'g:\client_delivery\templates\dashboard\index.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    '<a href="{% url \'add_product\' %}" class="quick-btn">',
    '{% if perms.inventory.add_product %}\n        <a href="{% url \'add_product\' %}" class="quick-btn">'
)
c = c.replace(
    '&#10133; {% trans "Add Product" %}\n        </a>',
    '&#10133; {% trans "Add Product" %}\n        </a>\n        {% endif %}'
)

c = c.replace(
    '<a href="{% url \'inventory_report\' %}" class="quick-btn">',
    '{% if perms.inventory.view_inventorytransaction %}\n        <a href="{% url \'inventory_report\' %}" class="quick-btn">'
)
c = c.replace(
    '&#128200; {% trans "Inventory Report" %}\n        </a>',
    '&#128200; {% trans "Inventory Report" %}\n        </a>\n        {% endif %}'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

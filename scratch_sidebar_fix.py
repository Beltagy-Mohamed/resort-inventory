import os

path = r'g:\client_delivery\templates\layout\sidebar.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Protect Add Product
c = c.replace(
    '<a href="{% url \'add_product\' %}"',
    '{% if perms.inventory.add_product %}\n        <a href="{% url \'add_product\' %}"'
)
c = c.replace(
    '<span class="label">{% trans "Add Product" %}</span>\n        </a>',
    '<span class="label">{% trans "Add Product" %}</span>\n        </a>\n        {% endif %}'
)

# Protect Reports section
c = c.replace('<h5>{% trans "Reports" %}</h5>', '{% if perms.inventory.view_inventorytransaction %}\n        <h5>{% trans "Reports" %}</h5>')

# Protect end of Reports section (Activity Log)
c = c.replace(
    '<a href="{% url \'activity_logs\' %}" class="{% if request.resolver_match.url_name == \'activity_logs\' %}active{% endif %}">\n            <i class="bi bi-clock-history"></i>\n            <span class="label">{% trans "Activity Log" %}</span>\n        </a>',
    '<a href="{% url \'activity_logs\' %}" class="{% if request.resolver_match.url_name == \'activity_logs\' %}active{% endif %}">\n            <i class="bi bi-clock-history"></i>\n            <span class="label">{% trans "Activity Log" %}</span>\n        </a>\n        {% endif %}'
)

# Protect Add Product in mobile nav
c = c.replace(
    '<a href="{% url \'add_product\' %}" class="{% if request.resolver_match.url_name == \'add_product\' %}active{% endif %}">\n        <i class="bi bi-plus-circle" aria-hidden="true"></i>\n        <span>{% trans "Add" %}</span>\n    </a>',
    '{% if perms.inventory.add_product %}\n    <a href="{% url \'add_product\' %}" class="{% if request.resolver_match.url_name == \'add_product\' %}active{% endif %}">\n        <i class="bi bi-plus-circle" aria-hidden="true"></i>\n        <span>{% trans "Add" %}</span>\n    </a>\n    {% endif %}'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

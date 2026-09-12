import os

path = r'g:\client_delivery\templates\layout\sidebar.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Protect activity log
if '{% if user.is_superuser %}\n        <a href="{% url \'activity_logs\'' not in c:
    c = c.replace(
        '<a href="{% url \'activity_logs\' %}"',
        '{% if user.is_superuser %}\n        <a href="{% url \'activity_logs\' %}"'
    )
    c = c.replace(
        '<span class="label">{% trans "Activity Log" %}</span>\n        </a>',
        '<span class="label">{% trans "Activity Log" %}</span>\n        </a>\n        {% endif %}'
    )

# Protect transactions in desktop nav
if '{% if perms.inventory.view_inventorytransaction %}\n        <a href="{% url \'transactions_list\'' not in c:
    c = c.replace(
        '<a href="{% url \'transactions_list\' %}" class="{% if request.resolver_match.url_name == \'transactions_list\' \nor request.resolver_match.url_name == \'add_transaction\' %}active{% endif %}">',
        '{% if perms.inventory.view_inventorytransaction %}\n        <a href="{% url \'transactions_list\' %}" class="{% if request.resolver_match.url_name == \'transactions_list\' \nor request.resolver_match.url_name == \'add_transaction\' %}active{% endif %}">'
    )
    c = c.replace(
        '<span class="label">{% trans "Transactions" %}</span>\n        </a>',
        '<span class="label">{% trans "Transactions" %}</span>\n        </a>\n        {% endif %}'
    )

# Protect transactions in mobile nav
if '{% if perms.inventory.view_inventorytransaction %}\n    <a href="{% url \'transactions_list\'' not in c:
    c = c.replace(
        '<a href="{% url \'transactions_list\' %}" class="{% if request.resolver_match.url_name == \'transactions_list\' \n%}active{% endif %}">',
        '{% if perms.inventory.view_inventorytransaction %}\n    <a href="{% url \'transactions_list\' %}" class="{% if request.resolver_match.url_name == \'transactions_list\' \n%}active{% endif %}">'
    )
    c = c.replace(
        '<span>{% trans "Transactions" %}</span>\n    </a>',
        '<span>{% trans "Transactions" %}</span>\n    </a>\n    {% endif %}'
    )

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

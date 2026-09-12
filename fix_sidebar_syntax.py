import os

path = r'g:\client_delivery\templates\layout\sidebar.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Fix desktop transactions_list
target1 = '''        <a href="{% url 'transactions_list' %}" class="{% if request.resolver_match.url_name == 'transactions_list' or request.resolver_match.url_name == 'add_transaction' %}active{% endif %}">
            <i class="bi bi-arrow-left-right"></i>
            <span class="label">{% trans "Transactions" %}</span>
        </a>
        {% endif %}'''

repl1 = '''        {% if perms.inventory.view_inventorytransaction %}
        <a href="{% url 'transactions_list' %}" class="{% if request.resolver_match.url_name == 'transactions_list' or request.resolver_match.url_name == 'add_transaction' %}active{% endif %}">
            <i class="bi bi-arrow-left-right"></i>
            <span class="label">{% trans "Transactions" %}</span>
        </a>
        {% endif %}'''

c = c.replace(target1, repl1)

# Fix mobile transactions_list
target2 = '''    <a href="{% url 'transactions_list' %}" class="{% if request.resolver_match.url_name == 'transactions_list' %}active{% endif %}">
        <i class="bi bi-arrow-left-right" aria-hidden="true"></i>
        <span>{% trans "Transactions" %}</span>
    </a>
    {% endif %}'''

repl2 = '''    {% if perms.inventory.view_inventorytransaction %}
    <a href="{% url 'transactions_list' %}" class="{% if request.resolver_match.url_name == 'transactions_list' %}active{% endif %}">
        <i class="bi bi-arrow-left-right" aria-hidden="true"></i>
        <span>{% trans "Transactions" %}</span>
    </a>
    {% endif %}'''

c = c.replace(target2, repl2)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

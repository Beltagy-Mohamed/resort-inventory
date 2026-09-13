import os

path = r'g:\client_delivery\templates\layout\sidebar.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target = '''        {% if perms.inventory.view_inventorytransaction %}
        <a href="{% url 'transactions_list' %}" class="{% if request.resolver_match.url_name == 'transactions_list' or request.resolver_match.url_name == 'add_transaction' %}active{% endif %}">
            <i class="bi bi-arrow-left-right"></i>
            <span class="label">{% trans "Transactions" %}</span>
        </a>
        {% endif %}'''

repl = '''        {% if perms.inventory.view_inventorytransaction %}
        <a href="{% url 'add_transaction' %}?action=IN" class="{% if request.GET.action == 'IN' %}active{% endif %}" style="color: #10B981;">
            <i class="bi bi-box-arrow-in-down"></i>
            <span class="label">إذن استلام (توريد)</span>
        </a>

        <a href="{% url 'add_transaction' %}?action=OUT" class="{% if request.GET.action == 'OUT' %}active{% endif %}" style="color: #EF4444;">
            <i class="bi bi-box-arrow-up"></i>
            <span class="label">إذن صرف (بيع/توزيع)</span>
        </a>

        <a href="{% url 'transactions_list' %}" class="{% if request.resolver_match.url_name == 'transactions_list' %}active{% endif %}">
            <i class="bi bi-arrow-left-right"></i>
            <span class="label">سجل الحركات</span>
        </a>
        {% endif %}'''

c = c.replace(target, repl)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

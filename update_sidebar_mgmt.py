import os

path = r'g:\client_delivery\templates\layout\sidebar.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target = '''        <h5>{% trans "Management" %}</h5>'''

repl = '''        <h5>{% trans "Management" %}</h5>

        <a href="{% url 'warehouses_list' %}" class="{% if request.resolver_match.url_name == 'warehouses_list' or request.resolver_match.url_name == 'add_warehouse' or request.resolver_match.url_name == 'edit_warehouse' %}active{% endif %}">
            <i class="bi bi-building"></i>
            <span class="label">المخازن (فروع)</span>
        </a>

        <a href="{% url 'partners_list' %}" class="{% if request.resolver_match.url_name == 'partners_list' or request.resolver_match.url_name == 'add_partner' or request.resolver_match.url_name == 'edit_partner' %}active{% endif %}">
            <i class="bi bi-people"></i>
            <span class="label">جهات التعامل (مورد/عميل)</span>
        </a>'''

if 'warehouses_list' not in c.split('<h5>{% trans "Management" %}</h5>')[1]:
    c = c.replace(target, repl)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

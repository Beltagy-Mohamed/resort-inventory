import os

path = r'g:\client_delivery\templates\layout\sidebar.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target = '''        <a href="{% url 'inventory_report' %}" class="{% if request.resolver_match.url_name == 'inventory_report' %}active{% endif %}">
            <i class="bi bi-file-earmark-bar-graph"></i>
            <span class="label">{% trans "Inventory Report" %}</span>
        </a>'''

repl = '''        <a href="{% url 'inventory_report' %}" class="{% if request.resolver_match.url_name == 'inventory_report' %}active{% endif %}">
            <i class="bi bi-file-earmark-bar-graph"></i>
            <span class="label">{% trans "Inventory Report" %}</span>
        </a>

        <a href="{% url 'warehouse_stock_report' %}" class="{% if request.resolver_match.url_name == 'warehouse_stock_report' %}active{% endif %}">
            <i class="bi bi-building"></i>
            <span class="label">جرد المخازن التفصيلي</span>
        </a>

        <a href="{% url 'partner_statement_report' %}" class="{% if request.resolver_match.url_name == 'partner_statement_report' %}active{% endif %}">
            <i class="bi bi-person-lines-fill"></i>
            <span class="label">كشف حساب الجهات</span>
        </a>

        <a href="{% url 'profit_report' %}" class="{% if request.resolver_match.url_name == 'profit_report' %}active{% endif %}">
            <i class="bi bi-graph-up-arrow"></i>
            <span class="label">تقرير الأرباح والمبيعات</span>
        </a>'''

if 'warehouse_stock_report' not in c:
    c = c.replace(target, repl)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

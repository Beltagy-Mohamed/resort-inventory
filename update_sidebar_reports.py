import os

path = r'g:\client_delivery\templates\layout\sidebar.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target = '''        <a href="{% url 'inventory_report' %}" class="nav-item {% if request.resolver_match.url_name == 'inventory_report' %}active{% endif %}">
            <i class="bi bi-file-earmark-spreadsheet"></i>
            <span>التقارير</span>
        </a>'''

repl = '''        <a href="{% url 'inventory_report' %}" class="nav-item {% if request.resolver_match.url_name == 'inventory_report' %}active{% endif %}">
            <i class="bi bi-file-earmark-spreadsheet"></i>
            <span>جرد المنتجات العام</span>
        </a>
        <a href="{% url 'warehouse_stock_report' %}" class="nav-item {% if request.resolver_match.url_name == 'warehouse_stock_report' %}active{% endif %}">
            <i class="bi bi-building"></i>
            <span>جرد المخازن التفصيلي</span>
        </a>
        <a href="{% url 'partner_statement_report' %}" class="nav-item {% if request.resolver_match.url_name == 'partner_statement_report' %}active{% endif %}">
            <i class="bi bi-person-lines-fill"></i>
            <span>كشف حساب الجهات</span>
        </a>
        <a href="{% url 'profit_report' %}" class="nav-item {% if request.resolver_match.url_name == 'profit_report' %}active{% endif %}">
            <i class="bi bi-graph-up-arrow"></i>
            <span>تقرير الأرباح والمبيعات</span>
        </a>'''

c = c.replace(target, repl)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

import os

path = r'g:\client_delivery\templates\layout\sidebar.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Replace Add Product
old_add = '''        <a href="{% url 'add_product' %}" class="{% if request.resolver_match.url_name == 'add_product' %}active{% endif %}">
            <i class="bi bi-plus-circle"></i>
            <span class="label">{% trans "Add Product" %}</span>
        </a>'''
new_add = '''        {% if perms.inventory.add_product %}
''' + old_add + '''
        {% endif %}'''
c = c.replace(old_add, new_add)

# Replace Reports
old_reports = '''        <h5>{% trans "Reports" %}</h5>

        <a href="{% url 'inventory_report' %}" class="{% if request.resolver_match.url_name == 'inventory_report' %}active{% endif %}">
            <i class="bi bi-file-earmark-bar-graph"></i>
            <span class="label">{% trans "Inventory Report" %}</span>
        </a>

        <a href="{% url 'low_stock_products' %}" class="{% if request.resolver_match.url_name == 'low_stock_products' %}active{% endif %}">
            <i class="bi bi-exclamation-triangle"></i>
            <span class="label">{% trans "Low Stock" %}</span>
        </a>

        <a href="{% url 'activity_logs' %}" class="{% if request.resolver_match.url_name == 'activity_logs' %}active{% endif %}">
            <i class="bi bi-clock-history"></i>
            <span class="label">{% trans "Activity Log" %}</span>
        </a>'''
new_reports = '''        {% if perms.inventory.view_inventorytransaction %}
''' + old_reports + '''
        {% endif %}'''
c = c.replace(old_reports, new_reports)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

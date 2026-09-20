import io

path = 'e:/خاص مشروع/client_delivery/templates/layout/sidebar.html'
with io.open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old = """        {% if perms.inventory.view_inventorytransaction %}
        <h5>الصلاحيات</h5>"""

new = """        {% if perms.inventory.view_inventorytransaction %}
        <h5>التقارير</h5>"""

c = c.replace(old, new)

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(c)

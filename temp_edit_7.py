import os

paths = [
    r'E:\خاص مشروع\client_delivery\templates\products\list.html',
    r'E:\خاص مشروع\client_delivery\templates\leadership\list.html'
]

for path in paths:
    if not os.path.exists(path): continue
    
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # Change p.quantity to p.display_quantity inside the table body
    c = c.replace('{% if p.quantity == 0 %}', '{% if p.display_quantity == 0 %}')
    c = c.replace('{{ p.quantity }}</strong></td>', '{{ p.display_quantity }}</strong></td>')
    
    # Add Warehouse filter to form
    wh_html = '''
        <select name="warehouse">
            <option value="">كل المخازن</option>
            {% for w in warehouses %}
            <option value="{{ w.id }}" {% if warehouse_id == w.id|stringformat:"s" %}selected{% endif %}>{{ w.name }}</option>
            {% endfor %}
        </select>
        '''
    if '<select name="warehouse">' not in c:
        c = c.replace('<select name="status">', wh_html + '<select name="status">')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

print("Updated list.html logic")

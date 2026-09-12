import os

path = r'g:\client_delivery\templates\layout\sidebar.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old_mob_add = '''    <a href="{% url 'add_product' %}" class="{% if request.resolver_match.url_name == 'add_product' %}active{% endif %}">
        <i class="bi bi-plus-circle" aria-hidden="true"></i>
        <span>{% trans "Add" %}</span>
    </a>'''

new_mob_add = '''    {% if perms.inventory.add_product %}
''' + old_mob_add + '''
    {% endif %}'''

if '{% if perms.inventory.add_product %}\n    <a href="{% url \'add_product\' %}"' not in c:
    c = c.replace(old_mob_add, new_mob_add)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

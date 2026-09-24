import re

path = r'E:\خاص مشروع\client_delivery\templates\layout\navbar.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    '''<div class="logo">
Ordinance
</div>''',
    '''<div class="logo" style="display: flex; align-items: center; gap: 10px;">
<img src="{% static 'images/logo.jpg' %}" alt="Ordinance Logo" style="height: 40px; width: 40px; border-radius: 50%; object-fit: cover;">
Ordinance
</div>'''
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

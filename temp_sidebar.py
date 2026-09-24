import re

path = r'E:\خاص مشروع\client_delivery\templates\layout\sidebar.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    '<h2>Ordinance</h2>',
    '''<h2 style="display: flex; align-items: center; gap: 10px; font-size: 1.2rem;">
    <img src="{% static 'images/logo.jpg' %}" alt="Ordinance Logo" style="height: 35px; width: 35px; border-radius: 50%; object-fit: cover;">
    Ordinance
</h2>'''
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

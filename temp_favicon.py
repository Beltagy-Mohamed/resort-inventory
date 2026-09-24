import re

path = r'E:\خاص مشروع\client_delivery\templates\layout\base.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = re.sub(
    r'<head>',
    '''<head>
    <link rel="icon" type="image/jpeg" href="{% static 'images/logo.jpg' %}">
    <link rel="apple-touch-icon" href="{% static 'images/logo.jpg' %}">''',
    c
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

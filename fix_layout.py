import os

path = r'g:\client_delivery\templates\layout\base.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Remove navbar from outside container
c = c.replace("    {% include 'layout/navbar.html' %}\n    <div class=\"container\">", '    <div class="container">')

# Insert navbar inside main, just before messages
c = c.replace("        <main>\n{% if messages %}", "        <main>\n            {% include 'layout/navbar.html' %}\n{% if messages %}")

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

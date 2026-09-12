import os
import re

path = r'g:\client_delivery\templates\transactions\list.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target = '''        <button class="btn-save">

            {% trans "Search" %}

        </button>'''

repl = '''        <input type="date" name="date_from" value="{{ date_from }}" title="من تاريخ">
        <input type="date" name="date_to" value="{{ date_to }}" title="إلى تاريخ">
        <button class="btn-save">
            {% trans "Search" %}
        </button>'''

c = c.replace(target, repl)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

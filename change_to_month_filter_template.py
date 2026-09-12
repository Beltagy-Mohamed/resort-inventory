import os

path = r'g:\client_delivery\templates\transactions\list.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target = '''        <input type="date" name="date_from" value="{{ date_from }}" title="من تاريخ">
        <input type="date" name="date_to" value="{{ date_to }}" title="إلى تاريخ">'''

repl = '''        <input type="month" name="month_filter" value="{{ month_filter }}" title="{% trans 'Select Month' %}" style="min-width: 170px;">'''

c = c.replace(target, repl)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

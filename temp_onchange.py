paths = [
    r'E:\خاص مشروع\client_delivery\templates\products\list.html',
    r'E:\خاص مشروع\client_delivery\templates\leadership\list.html'
]
for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('<select name="warehouse">', '<select name="warehouse" onchange="this.form.submit()">')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

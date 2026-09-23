import os

paths = [
    r'E:\خاص مشروع\client_delivery\templates\products\list.html',
    r'E:\خاص مشروع\client_delivery\templates\leadership\list.html'
]

for path in paths:
    if not os.path.exists(path): continue
    
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # Headers
    c = c.replace('<th>الكمية</th>', '<th>ما تم توريده</th>\n                <th>المتبقي (الكمية)</th>')
    
    # Cells
    c = c.replace('<td><strong class="{% if p.quantity == 0 %}out-of-stock{% endif %}">{{ p.quantity }}</strong></td>', 
                  '<td>{{ p.total_supplied }}</td>\n                    <td><strong class="{% if p.quantity == 0 %}out-of-stock{% endif %}">{{ p.quantity }}</strong></td>')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

print("Modified list.html templates")

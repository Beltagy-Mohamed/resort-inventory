import re

paths = [
    r'E:\خاص مشروع\client_delivery\templates\products\list.html',
    r'E:\خاص مشروع\client_delivery\templates\leadership\list.html'
]

for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # Replace classes for buttons
    c = c.replace('class="btn-icon btn-info"', 'class="action-btn view-btn"')
    c = c.replace('class="btn-icon btn-primary"', 'class="action-btn edit-btn"')
    c = c.replace('class="btn-icon btn-danger"', 'class="action-btn delete-btn"')

    # Fix the actions cell wrapper styling just in case it needs flex
    c = c.replace('<td class="actions">', '<td class="actions" style="display: flex; gap: 8px; justify-content: center; align-items: center; padding: 10px;">')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

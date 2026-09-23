import re

paths = [
    r'E:\خاص مشروع\client_delivery\templates\products\list.html',
    r'E:\خاص مشروع\client_delivery\templates\leadership\list.html'
]

for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # We need to change the Status column badge calculation
    old_status = '''                {% if p.remaining_target <= 0 %}
                    <span class="badge" style="background-color: #198754; color: white;">مكتمل</span>
                {% elif p.total_supplied == 0 %}
                    <span class="badge" style="background-color: #dc3545; color: white;">لم يورد</span>
                {% else %}
                    <span class="badge" style="background-color: #ffc107; color: black;">جاري التوريد</span>
                {% endif %}'''
    
    # We will use display_quantity to determine stock status, and use minimum_stock for low stock comparison
    new_status = '''                {% if p.display_quantity <= 0 %}
                    <span class="badge" style="background-color: #dc3545; color: white;">نفد</span>
                {% elif p.display_quantity <= p.minimum_stock %}
                    <span class="badge" style="background-color: #ffc107; color: black;">منخفض</span>
                {% else %}
                    <span class="badge" style="background-color: #198754; color: white;">متوفر</span>
                {% endif %}'''
    
    c = c.replace(old_status, new_status)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

# Now update the Python views for Excel export!
paths = [
    r'E:\خاص مشروع\client_delivery\inventory\views\products.py',
    r'E:\خاص مشروع\client_delivery\inventory\views\leadership.py'
]

for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
        
    old_export = '''"مكتمل" if getattr(p, 'remaining_target', 0) <= 0 else ("لم يورد" if getattr(p, 'total_supplied', 0) == 0 else "جاري التوريد")'''
    new_export = '''"نفد" if getattr(p, 'display_quantity', 0) <= 0 else ("منخفض" if getattr(p, 'display_quantity', 0) <= getattr(p, 'minimum_stock', 0) else "متوفر")'''
    
    c = c.replace(old_export, new_export)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

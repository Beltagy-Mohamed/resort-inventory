paths = [
    r'E:\خاص مشروع\client_delivery\templates\products\list.html',
    r'E:\خاص مشروع\client_delivery\templates\leadership\list.html'
]
import re
for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('<th>المتبقي الحالة</th>', '<th>المتبقي</th>\n            <th>الحالة</th>')
    
    old_cell = '''            <td>
                <!-- To subtract in django templates we can add negative. But unfortunately we can't easily do A - B -->
                <!-- We will do it in python view or just do A|add:"-"|add:B but that's concat. 
                     Wait! add filter with string parses to int! So value|add:"-5" subtracts 5! 
                     But we can't do value|add:"-"|add:B -->
                <!-- Let's just create a custom template tag or calculate it in python! -->
                {{ product.remaining_target }}
            </td>'''
    
    new_cell = '''            <td>{{ product.remaining_target }}</td>
            <td>
                {% if product.remaining_target <= 0 %}
                    <span class="badge bg-success" style="font-size:12px; padding:6px; border-radius:15px; color:white; background-color:#198754;">مكتمل</span>
                {% elif product.total_supplied == 0 %}
                    <span class="badge bg-danger" style="font-size:12px; padding:6px; border-radius:15px; color:white; background-color:#dc3545;">لم يورد</span>
                {% else %}
                    <span class="badge bg-warning" style="font-size:12px; padding:6px; border-radius:15px; color:black; background-color:#ffc107;">جاري التوريد</span>
                {% endif %}
            </td>'''
            
    c = c.replace(old_cell, new_cell)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

import re

paths = [
    r'E:\خاص مشروع\client_delivery\templates\products\list.html',
    r'E:\خاص مشروع\client_delivery\templates\leadership\list.html'
]

for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
        
    # Replace Table Headers
    # We will search for <thead> and replace its content
    thead_replacement = '''    <thead>
        <tr>
            <th>الكود</th>
            <th>اسم الصنف</th>
            <th>التنميط</th>
            <th>ما تم توريده</th>
            <th>المتبقي الحالة</th>
            <th>اسم الشركة</th>
            <th>الإجراءات</th>
        </tr>
    </thead>'''
    c = re.sub(r'\s*<thead>.*?</thead>', '\n' + thead_replacement, c, flags=re.DOTALL)
    
    # Replace Table Cells
    # Inside tbody loop
    tcell_replacement = '''        <tr>
            <td>{{ product.barcode|default:"-" }}</td>
            <td>
                <strong>{{ product.name }}</strong>
                {% if product.description %}<br><small class="text-muted">{{ product.description|truncatechars:50 }}</small>{% endif %}
            </td>
            <td>{{ product.target_quantity }}</td>
            <td>{{ product.total_supplied|default:0 }}</td>
            <td>
                <!-- To subtract in django templates we can add negative. But unfortunately we can't easily do A - B -->
                <!-- We will do it in python view or just do A|add:"-"|add:B but that's concat. 
                     Wait! add filter with string parses to int! So value|add:"-5" subtracts 5! 
                     But we can't do value|add:\"-\"|add:B -->
                <!-- Let's just create a custom template tag or calculate it in python! -->
                {{ product.remaining_target }}
            </td>
            <td>{{ product.latest_supplier|default:"-" }}</td>
            <td class="actions">'''
    
    # Let's fix the python view to annotate remaining_target first!
    c = re.sub(r'        <tr>\s*<td>{{ product\.barcode.*?<td class="actions">', tcell_replacement, c, flags=re.DOTALL)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

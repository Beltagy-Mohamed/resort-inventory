import re

paths = [
    r'E:\خاص مشروع\client_delivery\templates\products\list.html',
    r'E:\خاص مشروع\client_delivery\templates\leadership\list.html'
]

products_period_filter_regex = r'<!-- Period filter for everyone -->.*?<button type="submit">بحث و تصفية</button>'
leadership_period_filter_regex = r'<!-- Period filter for everyone -->.*?<button type="submit" class="btn-primary">بحث و تصفية</button>'

for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Remove period filter from the form
    c = re.sub(r'<!-- Period filter for everyone -->.*?<button type="submit".*?>بحث و تصفية</button>', '<button type="submit" class="btn-primary" style="margin-top:10px;">بحث و تصفية</button>', c, flags=re.DOTALL)

    # 2. Replace tbody completely
    # Let's find the inner loop 
    # For products/list.html: {% for p in page_obj %} ... {% endfor %}
    # For leadership/list.html: {% for product in page_obj %} ... {% empty %} ... {% endfor %}
    
    # We'll use a regex to match from <tbody> to </tbody>
    # and replace the content.
    
    new_tbody = '''<tbody>
    {% for p in page_obj %}
        <tr>
            <td>{{ p.barcode|default:"-" }}</td>
            <td><strong>{{ p.name }}</strong></td>
            <td>{{ p.target_quantity }}</td>
            <td>{{ p.total_supplied }}</td>
            <td>{{ p.remaining_target }}</td>
            <td>
                {% if p.remaining_target <= 0 %}
                    <span class="badge" style="background-color: #198754; color: white;">مكتمل</span>
                {% elif p.total_supplied == 0 %}
                    <span class="badge" style="background-color: #dc3545; color: white;">لم يورد</span>
                {% else %}
                    <span class="badge" style="background-color: #ffc107; color: black;">جاري التوريد</span>
                {% endif %}
            </td>
            <td>{{ p.latest_supplier|default:"-" }}</td>
            <td class="actions">
                {% if is_leadership %}
                    <a href="{% url 'leadership_item_detail' p.id %}" class="btn-icon btn-info" title="عرض التفاصيل"><i class="bi bi-eye"></i></a>
                    <a href="{% url 'leadership_item_edit' p.id %}" class="btn-icon btn-primary" title="تعديل"><i class="bi bi-pencil"></i></a>
                    <a href="{% url 'leadership_item_delete' p.id %}" class="btn-icon btn-danger" title="حذف"><i class="bi bi-trash"></i></a>
                {% else %}
                    <a href="{% url 'product_detail' p.id %}" class="btn-icon btn-info" title="عرض التفاصيل"><i class="bi bi-eye"></i></a>
                    <a href="{% url 'edit_product' p.id %}" class="btn-icon btn-primary" title="تعديل"><i class="bi bi-pencil"></i></a>
                    <a href="{% url 'delete_product' p.id %}" class="btn-icon btn-danger" title="حذف"><i class="bi bi-trash"></i></a>
                {% endif %}
            </td>
        </tr>
    {% empty %}
        <tr><td colspan="8" style="text-align: center; padding: 20px;">لا توجد منتجات مطابقة للبحث.</td></tr>
    {% endfor %}
</tbody>'''

    c = re.sub(r'<tbody>.*?</tbody>', new_tbody, c, flags=re.DOTALL)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

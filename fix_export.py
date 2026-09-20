import io
import sys

path = 'e:/خاص مشروع/client_delivery/templates/products/list.html'
with io.open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old_block = """{% else %}
            <a href="{% url 'add_product' %}" class="btn-primary">
                <i class="bi bi-plus"></i> إضافة صنف
            </a>
        {% endif %}"""

new_block = """{% else %}
            <a href="?search={{ search }}&category={{ category_id }}&color={{ color_id }}&size={{ size_id }}&status={{ status }}&export=xlsx" class="btn-secondary" style="margin-inline-end: 10px;">
                <i class="bi bi-file-earmark-excel"></i> تصدير Excel
            </a>
            <a href="{% url 'add_product' %}" class="btn-primary">
                <i class="bi bi-plus"></i> إضافة صنف
            </a>
        {% endif %}"""

c = c.replace(old_block, new_block)

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(c)

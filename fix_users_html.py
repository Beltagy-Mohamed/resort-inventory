import io

path = 'e:/خاص مشروع/client_delivery/templates/users/list.html'
with io.open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old = """                        <a href="{% url 'edit_user' u.id %}" class="apple-btn-icon" title="تعديل"><i class="bi bi-pencil"></i></a>"""

new = """                        <a href="{% url 'edit_user' u.id %}" class="apple-btn-icon" title="تعديل"><i class="bi bi-pencil"></i></a>
                        <a href="{% url 'delete_user' u.id %}" class="apple-btn-icon text-danger" title="حذف" onclick="return confirm('هل أنت متأكد من تعطيل/حذف هذا المستخدم؟');"><i class="bi bi-trash"></i></a>"""

c = c.replace(old, new)

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(c)

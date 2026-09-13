import os

os.makedirs(r'g:\client_delivery\templates\management', exist_ok=True)

# 1. warehouses_list.html
with open(r'g:\client_delivery\templates\management\warehouses_list.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends "layout/base.html" %}
{% load static %}
{% block title %}المخازن{% endblock %}
{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/products.css' %}">
{% endblock %}
{% block content %}
<div class="page-header">
    <h1>المخازن</h1>
    <a href="{% url 'add_warehouse' %}" class="btn-primary">إضافة مخزن جديد</a>
</div>
<div class="table-responsive">
    <table class="data-table">
        <thead>
            <tr>
                <th>الاسم</th>
                <th>الموقع</th>
                <th>الحالة</th>
                <th>إجراءات</th>
            </tr>
        </thead>
        <tbody>
            {% for w in warehouses %}
            <tr>
                <td>{{ w.name }}</td>
                <td>{{ w.location|default:"-" }}</td>
                <td>{% if w.is_active %}<span style="color: green;">نشط</span>{% else %}<span style="color: red;">غير نشط</span>{% endif %}</td>
                <td>
                    <a href="{% url 'edit_warehouse' w.id %}" class="btn-icon"><i class="bi bi-pencil"></i> تعديل</a>
                </td>
            </tr>
            {% empty %}
            <tr><td colspan="4" style="text-align: center;">لا توجد مخازن</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''')

# 2. warehouse_form.html
with open(r'g:\client_delivery\templates\management\warehouse_form.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends "layout/base.html" %}
{% load static %}
{% block title %}{{ action }}{% endblock %}
{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/products.css' %}">
{% endblock %}
{% block content %}
<div class="page-header">
    <h1>{{ action }}</h1>
</div>
<div class="form-container">
    <form method="post" class="product-form">
        {% csrf_token %}
        {{ form.as_p }}
        <div class="form-actions" style="margin-top: 20px;">
            <button type="submit" class="btn-primary">حفظ</button>
            <a href="{% url 'warehouses_list' %}" class="btn-secondary" style="margin-right: 10px; padding: 10px; text-decoration: none; border-radius: 4px; border: 1px solid #ccc; color: #333;">إلغاء</a>
        </div>
    </form>
</div>
{% endblock %}''')

# 3. partners_list.html
with open(r'g:\client_delivery\templates\management\partners_list.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends "layout/base.html" %}
{% load static %}
{% block title %}جهات التعامل (مورد / عميل){% endblock %}
{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/products.css' %}">
{% endblock %}
{% block content %}
<div class="page-header">
    <h1>جهات التعامل</h1>
    <a href="{% url 'add_partner' %}" class="btn-primary">إضافة جهة جديدة</a>
</div>
<div class="table-responsive">
    <table class="data-table">
        <thead>
            <tr>
                <th>الاسم</th>
                <th>النوع</th>
                <th>الهاتف</th>
                <th>الحالة</th>
                <th>إجراءات</th>
            </tr>
        </thead>
        <tbody>
            {% for p in partners %}
            <tr>
                <td>{{ p.name }}</td>
                <td>{{ p.get_partner_type_display }}</td>
                <td>{{ p.phone|default:"-" }}</td>
                <td>{% if p.is_active %}<span style="color: green;">نشط</span>{% else %}<span style="color: red;">غير نشط</span>{% endif %}</td>
                <td>
                    <a href="{% url 'edit_partner' p.id %}" class="btn-icon"><i class="bi bi-pencil"></i> تعديل</a>
                </td>
            </tr>
            {% empty %}
            <tr><td colspan="5" style="text-align: center;">لا توجد جهات تعامل</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''')

# 4. partner_form.html
with open(r'g:\client_delivery\templates\management\partner_form.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends "layout/base.html" %}
{% load static %}
{% block title %}{{ action }}{% endblock %}
{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/products.css' %}">
{% endblock %}
{% block content %}
<div class="page-header">
    <h1>{{ action }}</h1>
</div>
<div class="form-container">
    <form method="post" class="product-form">
        {% csrf_token %}
        {{ form.as_p }}
        <div class="form-actions" style="margin-top: 20px;">
            <button type="submit" class="btn-primary">حفظ</button>
            <a href="{% url 'partners_list' %}" class="btn-secondary" style="margin-right: 10px; padding: 10px; text-decoration: none; border-radius: 4px; border: 1px solid #ccc; color: #333;">إلغاء</a>
        </div>
    </form>
</div>
{% endblock %}''')


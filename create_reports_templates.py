import os

os.makedirs(r'g:\client_delivery\templates\reports', exist_ok=True)

# 1. Warehouse Stock Template
with open(r'g:\client_delivery\templates\reports\warehouse_stock.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends "layout/base.html" %}
{% load static %}

{% block title %}جرد المخازن التفصيلي{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/products.css' %}">
{% endblock %}

{% block content %}
<div class="page-header">
    <h1>جرد المخازن التفصيلي</h1>
</div>

<div class="search-bar">
    <form method="get">
        <select name="warehouse_id" class="form-control" style="min-width: 200px;">
            <option value="">-- كل المخازن --</option>
            {% for w in warehouses %}
            <option value="{{ w.id }}" {% if selected_warehouse == w.id %}selected{% endif %}>{{ w.name }}</option>
            {% endfor %}
        </select>
        <button type="submit" class="btn-primary" style="padding: 10px 15px; background: #3A5457; color: white; border: none; border-radius: 4px;">بحث</button>
    </form>
</div>

<div class="table-responsive">
    <table class="data-table">
        <thead>
            <tr>
                <th>المخزن</th>
                <th>كود المنتج</th>
                <th>اسم المنتج</th>
                <th>الكمية المتاحة</th>
                <th>سعر التكلفة</th>
                <th>سعر البيع</th>
            </tr>
        </thead>
        <tbody>
            {% for stock in stocks %}
            <tr>
                <td>{{ stock.warehouse.name }}</td>
                <td>{{ stock.product.product_code }}</td>
                <td>{{ stock.product.name }}</td>
                <td>{{ stock.quantity }}</td>
                <td>{{ stock.product.cost_price }}</td>
                <td>{{ stock.product.selling_price }}</td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="6" style="text-align: center;">لا توجد أرصدة مطابقة للبحث</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
''')

# 2. Partner Statement Template
with open(r'g:\client_delivery\templates\reports\partner_statement.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends "layout/base.html" %}
{% load static %}

{% block title %}كشف حساب جهة تعامل{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/products.css' %}">
{% endblock %}

{% block content %}
<div class="page-header">
    <h1>كشف حساب جهة تعامل (مورد / عميل)</h1>
</div>

<div class="search-bar">
    <form method="get">
        <select name="partner_id" class="form-control" style="min-width: 200px;" required>
            <option value="">-- اختر الجهة --</option>
            {% for p in partners %}
            <option value="{{ p.id }}" {% if selected_partner == p.id %}selected{% endif %}>{{ p.name }} ({{ p.get_partner_type_display }})</option>
            {% endfor %}
        </select>
        <input type="month" name="month_filter" value="{{ month_filter }}" class="form-control" style="min-width: 170px;">
        <button type="submit" class="btn-primary" style="padding: 10px 15px; background: #3A5457; color: white; border: none; border-radius: 4px;">بحث</button>
    </form>
</div>

{% if selected_partner %}
<div class="table-responsive">
    <table class="data-table">
        <thead>
            <tr>
                <th>التاريخ</th>
                <th>نوع الحركة</th>
                <th>المنتج</th>
                <th>الكمية</th>
                <th>سعر الوحدة</th>
                <th>الإجمالي</th>
                <th>المخزن</th>
                <th>ملاحظات</th>
            </tr>
        </thead>
        <tbody>
            {% for trans in transactions %}
            <tr>
                <td>{{ trans.created_at|date:"Y-m-d H:i" }}</td>
                <td>{{ trans.get_transaction_type_display }}</td>
                <td>{{ trans.product.name }}</td>
                <td>{{ trans.quantity }}</td>
                <td>{{ trans.unit_price }}</td>
                <td>{% widthratio trans.unit_price 1 trans.quantity %}</td>
                <td>{{ trans.warehouse.name|default:"-" }}</td>
                <td>{{ trans.notes|default:"-" }}</td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="8" style="text-align: center;">لا توجد حركات لهذه الجهة في الفترة المحددة</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% else %}
<p style="text-align: center; margin-top: 50px;">يرجى اختيار جهة تعامل للبدء</p>
{% endif %}
{% endblock %}
''')

# 3. Profit Report Template
with open(r'g:\client_delivery\templates\reports\profit.html', 'w', encoding='utf-8') as f:
    f.write('''{% extends "layout/base.html" %}
{% load static %}

{% block title %}تقرير الأرباح والمبيعات{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/products.css' %}">
<style>
    .summary-cards { display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }
    .summary-card { flex: 1; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); text-align: center; border-right: 4px solid #3A5457; }
    .summary-card h3 { margin: 0 0 10px 0; font-size: 14px; color: #666; }
    .summary-card .value { font-size: 24px; font-weight: bold; color: #111; }
    .profit-positive { color: #10B981 !important; }
    .profit-negative { color: #EF4444 !important; }
</style>
{% endblock %}

{% block content %}
<div class="page-header">
    <h1>تقرير الأرباح والمبيعات (الحركات الصادرة فقط)</h1>
</div>

<div class="search-bar">
    <form method="get">
        <input type="month" name="month_filter" value="{{ month_filter }}" class="form-control" style="min-width: 170px;">
        <button type="submit" class="btn-primary" style="padding: 10px 15px; background: #3A5457; color: white; border: none; border-radius: 4px;">عرض التقرير</button>
    </form>
</div>

<div class="summary-cards">
    <div class="summary-card">
        <h3>إجمالي المبيعات (قيمة البضاعة المنصرفة)</h3>
        <div class="value">{{ total_sales|floatformat:2 }}</div>
    </div>
    <div class="summary-card">
        <h3>إجمالي التكلفة</h3>
        <div class="value">{{ total_cost|floatformat:2 }}</div>
    </div>
    <div class="summary-card">
        <h3>صافي الربح</h3>
        <div class="value {% if total_profit > 0 %}profit-positive{% elif total_profit < 0 %}profit-negative{% endif %}">
            {{ total_profit|floatformat:2 }}
        </div>
    </div>
</div>

<div class="table-responsive">
    <table class="data-table">
        <thead>
            <tr>
                <th>التاريخ</th>
                <th>المنتج</th>
                <th>الكمية المنصرفة</th>
                <th>تكلفة الوحدة</th>
                <th>سعر البيع الفعلي</th>
                <th>إجمالي التكلفة</th>
                <th>إجمالي البيع</th>
                <th>الربح</th>
            </tr>
        </thead>
        <tbody>
            {% for trans in transactions %}
            <tr>
                <td>{{ trans.created_at|date:"Y-m-d H:i" }}</td>
                <td>{{ trans.product.name }}</td>
                <td>{{ trans.quantity }}</td>
                <td>{{ trans.product.cost_price }}</td>
                <td>{{ trans.unit_price }}</td>
                <td>{% widthratio trans.product.cost_price 1 trans.quantity %}</td>
                <td>{% widthratio trans.unit_price 1 trans.quantity %}</td>
                <td class="{% if trans.profit > 0 %}profit-positive{% elif trans.profit < 0 %}profit-negative{% endif %}">
                    {{ trans.profit|floatformat:2 }}
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="8" style="text-align: center;">لا توجد مبيعات (حركات منصرفة) في الفترة المحددة</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
''')


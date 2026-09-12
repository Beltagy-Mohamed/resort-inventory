import os

path = r'g:\client_delivery\templates\transactions\add.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target = '''        <div class="form-group">

            <label>{% trans "Transaction type" %}</label>

            {{ form.transaction_type }}

        </div>'''

repl = '''        <div class="form-group">
            <label>المخزن (Warehouse)</label>
            {{ form.warehouse }}
        </div>
        <div class="form-group">
            <label>الجهة (Partner)</label>
            {{ form.partner }}
        </div>
        <div class="form-group">
            <label>{% trans "Transaction type" %}</label>
            {{ form.transaction_type }}
        </div>
        <div class="form-group">
            <label>سعر الوحدة (Unit Price)</label>
            {{ form.unit_price }}
        </div>'''

c = c.replace(target, repl)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

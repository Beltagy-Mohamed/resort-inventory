import os

for filename in ['add.html', 'edit.html']:
    path = rf'g:\client_delivery\templates\products\{filename}'
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    target = '''        <div class="form-group">
            <label>{{ form.price.label }}</label>
            {{ form.price }}
        </div>'''
        
    repl = '''        <div class="form-group">
            <label>{{ form.cost_price.label }}</label>
            {{ form.cost_price }}
        </div>
        <div class="form-group">
            <label>{{ form.selling_price.label }}</label>
            {{ form.selling_price }}
        </div>'''
        
    c = c.replace(target, repl)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

import os

for filename in ['list.html', 'detail.html']:
    path = rf'g:\client_delivery\templates\products\{filename}'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            c = f.read()
        
        c = c.replace('<th>{% trans "Price" %}</th>', '<th>سعر الشراء</th><th>سعر البيع</th>')
        c = c.replace('<td data-label="{% trans \'Price\' %}">{{ product.price }} {{ system_settings.currency }}</td>', 
                      '<td data-label="سعر الشراء">{{ product.cost_price }} {{ system_settings.currency }}</td>\n<td data-label="سعر البيع">{{ product.selling_price }} {{ system_settings.currency }}</td>')
        
        c = c.replace('<strong>{% trans "Price" %}:</strong> {{ product.price }}', 
                      '<strong>سعر الشراء:</strong> {{ product.cost_price }}<br><strong>سعر البيع:</strong> {{ product.selling_price }}')

        with open(path, 'w', encoding='utf-8') as f:
            f.write(c)

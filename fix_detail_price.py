import io

path = 'e:/خاص مشروع/client_delivery/templates/products/detail.html'
with io.open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old = """        <div class="info-row">
            <span>سعر التكلفة</span>
            <strong>{{ product.cost_price }} {{ system_settings.currency }}</strong>
        </div>"""

new = """        {% if user.is_superuser or is_leadership %}
        <div class="info-row">
            <span>سعر التكلفة</span>
            <strong>{{ product.cost_price }} {{ system_settings.currency }}</strong>
        </div>
        {% endif %}"""

c = c.replace(old, new)

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(c)

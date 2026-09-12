import os

path = r'g:\client_delivery\templates\layout\sidebar.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Desktop sidebar settings link:
old_settings = '''        <a href="{% url 'system_settings' %}" class="{% if request.resolver_match.url_name == 'system_settings' %}active{% endif %}">
            <i class="bi bi-gear"></i>
            <span class="label">{% trans "Settings" %}</span>
        </a>'''

new_settings = '''        {% if user.is_superuser %}
        <a href="{% url 'system_settings' %}" class="{% if request.resolver_match.url_name == 'system_settings' %}active{% endif %}">
            <i class="bi bi-gear"></i>
            <span class="label">{% trans "Settings" %}</span>
        </a>
        {% endif %}'''

c = c.replace(old_settings, new_settings)

# Mobile navbar settings link (More):
old_mobile_settings = '''    <a href="{% url 'system_settings' %}" class="{% if request.resolver_match.url_name == 'system_settings' %}active{% endif %}">
        <i class="bi bi-three-dots" aria-hidden="true"></i>
        <span>{% trans "More" %}</span>
    </a>'''

new_mobile_settings = '''    {% if user.is_superuser %}
    <a href="{% url 'system_settings' %}" class="{% if request.resolver_match.url_name == 'system_settings' %}active{% endif %}">
        <i class="bi bi-three-dots" aria-hidden="true"></i>
        <span>{% trans "More" %}</span>
    </a>
    {% endif %}'''

c = c.replace(old_mobile_settings, new_mobile_settings)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

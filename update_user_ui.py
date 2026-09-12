import os

# 1. Update activity list HTML
path_act = r'g:\client_delivery\templates\activity\list.html'
with open(path_act, 'r', encoding='utf-8') as f:
    c_act = f.read()

if '{% trans "User" %}' not in c_act:
    c_act = c_act.replace('<th>{% trans "Time" %}</th>', '<th>{% trans "Time" %}</th>\n            <th>{% trans "User" %}</th>')
    c_act = c_act.replace('<td data-label="{% trans \'Date\' %}">{{ log.created_at|date:"Y-m-d H:i" }}</td>', '<td data-label="{% trans \'Date\' %}">{{ log.created_at|date:"Y-m-d H:i" }}</td>\n            <td data-label="المستخدم">{% if log.user %}{{ log.user.username }}{% else %}-{% endif %}</td>')
    c_act = c_act.replace('<td colspan="4">', '<td colspan="5">')
    with open(path_act, 'w', encoding='utf-8') as f:
        f.write(c_act)

# 2. Update transactions list HTML
path_trans = r'g:\client_delivery\templates\transactions\list.html'
with open(path_trans, 'r', encoding='utf-8') as f:
    c_trans = f.read()

if '{% trans "User" %}' not in c_trans:
    c_trans = c_trans.replace('<th>{% trans "Product" %}</th>', '<th>{% trans "Product" %}</th>\n                <th>{% trans "User" %}</th>')
    c_trans = c_trans.replace('<td>{{ t.product.name }}</td>', '<td>{{ t.product.name }}</td>\n                <td data-label="المستخدم">{% if t.user %}{{ t.user.username }}{% else %}-{% endif %}</td>')
    c_trans = c_trans.replace('<td colspan="6">', '<td colspan="7">')
    with open(path_trans, 'w', encoding='utf-8') as f:
        f.write(c_trans)

# 3. Protect Activity view to superuser only
path_view_act = r'g:\client_delivery\inventory\views\activity.py'
with open(path_view_act, 'r', encoding='utf-8') as f:
    c_va = f.read()

if 'user_passes_test' not in c_va:
    c_va = c_va.replace('from django.contrib.auth.decorators import login_required', 'from django.contrib.auth.decorators import login_required, user_passes_test\n\ndef is_superuser(u):\n    return u.is_superuser\n')
    c_va = c_va.replace('@login_required', '@login_required\n@user_passes_test(is_superuser, login_url="/")')
    with open(path_view_act, 'w', encoding='utf-8') as f:
        f.write(c_va)

# 4. Protect Transactions view to those with 'view_inventorytransaction'
path_view_trans = r'g:\client_delivery\inventory\views\transactions.py'
with open(path_view_trans, 'r', encoding='utf-8') as f:
    c_vt = f.read()

if 'permission_required("inventory.view_inventorytransaction"' not in c_vt:
    c_vt = c_vt.replace('from django.contrib.auth.decorators import login_required', 'from django.contrib.auth.decorators import login_required, permission_required')
    c_vt = c_vt.replace('@login_required\ndef transactions_list', '@login_required\n@permission_required("inventory.view_inventorytransaction", raise_exception=True)\ndef transactions_list')
    with open(path_view_trans, 'w', encoding='utf-8') as f:
        f.write(c_vt)


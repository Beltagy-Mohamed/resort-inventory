import os

path = r'g:\client_delivery\inventory\urls.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

new_urls = '''
    path("management/warehouses/", views.warehouses_list, name="warehouses_list"),
    path("management/warehouses/add/", views.add_warehouse, name="add_warehouse"),
    path("management/warehouses/<int:pk>/edit/", views.edit_warehouse, name="edit_warehouse"),

    path("management/partners/", views.partners_list, name="partners_list"),
    path("management/partners/add/", views.add_partner, name="add_partner"),
    path("management/partners/<int:pk>/edit/", views.edit_partner, name="edit_partner"),
'''

if 'warehouses_list' not in c:
    c = c.replace('path(\n    "settings/",', new_urls + '\n    path(\n    "settings/",')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

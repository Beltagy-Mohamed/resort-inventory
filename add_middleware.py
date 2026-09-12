import os

path = r'g:\client_delivery\config\settings.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

middleware_str = "'django.contrib.auth.middleware.AuthenticationMiddleware',"
if "'inventory.middleware.CurrentUserMiddleware'" not in c:
    c = c.replace(
        middleware_str,
        middleware_str + "\n    'inventory.middleware.CurrentUserMiddleware',"
    )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

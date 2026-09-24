import re

path = r'E:\خاص مشروع\client_delivery\config\settings.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    "CSRF_TRUSTED_ORIGINS = ['https://resort-inventory.vercel.app'] + [",
    "CSRF_TRUSTED_ORIGINS = ['https://resort-inventory.vercel.app', 'https://*.vercel.app'] + ["
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

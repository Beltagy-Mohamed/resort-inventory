import re
path = r'E:\خاص مشروع\client_delivery\config\wsgi.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

migration_script = '''
import os
import sys
# Automatically run migrations on Vercel cold boot
try:
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
except Exception as e:
    print("Migration failed during WSGI boot:", e)
'''

if 'execute_from_command_line' not in c:
    c = c.replace('application = get_wsgi_application()', migration_script + '\napplication = get_wsgi_application()')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

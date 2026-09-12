import os

path = r'g:\client_delivery\config\wsgi.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

if 'call_command(\'migrate\'' not in c:
    c += '''

# Auto-apply migrations on Vercel boot (cold start)
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
except Exception as e:
    print(f"Migration failed: {e}")
'''
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

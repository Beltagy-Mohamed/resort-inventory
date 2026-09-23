"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


import os
import sys
# Automatically run migrations on Vercel cold boot
try:
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
except Exception as e:
    print("Migration failed during WSGI boot:", e)

application = get_wsgi_application()

# Vercel requires 'app' variable
app = application


# Auto-apply migrations on Vercel boot (cold start)
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
except Exception as e:
    print(f"Migration failed: {e}")

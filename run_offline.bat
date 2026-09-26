@echo off
echo ==============================================
echo      Starting Ordinance Offline Server
echo ==============================================

IF EXIST "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) ELSE IF EXIST ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo [1/3] Checking Database Migrations...
python manage.py migrate

echo [2/3] Creating Default Admin User...
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings'); django.setup(); from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@admin.com', 'admin')"

echo [3/3] Starting Django Server...
echo ==============================================
echo.
echo [SUCCESS] Server is running! 
echo Open your browser and go to this link:
echo http://127.0.0.1:8080
echo.
echo (Username: admin / Password: admin)
echo.
echo ==============================================
python manage.py runserver 0.0.0.0:8080
pause

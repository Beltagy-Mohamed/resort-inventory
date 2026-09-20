@echo off
echo Starting Logix Inventory Server...
waitress-serve --port=8000 --threads=10 config.wsgi:application
pause

# Gunicorn config. Run with: gunicorn -c deploy/gunicorn.conf.py config.wsgi:application

bind = "127.0.0.1:8000"
workers = 3
timeout = 60
accesslog = "-"
errorlog = "-"

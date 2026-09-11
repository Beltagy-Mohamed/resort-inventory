# دليل النشر — Inventory System

## 1. تجهيز السيرفر (Ubuntu VPS / Hostinger مثلًا)

```bash
sudo apt update
sudo apt install python3-venv python3-pip nginx postgresql -y   # postgresql اختياري لو هتستخدم SQLite
```

## 2. رفع المشروع

```bash
sudo mkdir -p /var/www/inventory
sudo chown $USER:$USER /var/www/inventory
# انسخ ملفات المشروع هنا (git clone أو scp)

cd /var/www/inventory
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. متغيرات البيئة

```bash
cp .env.example .env
nano .env   # عبّي القيم الحقيقية (SECRET_KEY, ALLOWED_HOSTS, بيانات قاعدة البيانات...)
```

لتوليد `SECRET_KEY` عشوائي وآمن:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

## 4. قاعدة البيانات

**SQLite (نظام صغير، مستخدم واحد أو اتنين):** ما تحتاجش تعمل حاجة زيادة، سيب `DJANGO_DB_ENGINE` فاضي في `.env`.

**PostgreSQL (لو أكتر من مستخدم هيشتغلوا في نفس الوقت — الأفضل للإنتاج):**
```bash
sudo -u postgres psql -c "CREATE DATABASE inventory_db;"
sudo -u postgres psql -c "CREATE USER inventory_user WITH PASSWORD 'كلمة_سر_قوية';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;"
```
وحط `DJANGO_DB_ENGINE=postgres` + بيانات الاتصال في `.env`.

> **ملاحظة:** لو كنت شغّال بـ SQLite وعايز تنقل بياناتك الحقيقية لـ PostgreSQL، استخدم:
> ```bash
> python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.permission > backup.json
> # بعد التبديل لـ Postgres في .env:
> python manage.py migrate
> python manage.py loaddata backup.json
> ```

## 5. Migrations + Static + Superuser

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py setup_groups          # ينشئ Group باسم Admin و Staff
python manage.py createsuperuser
python manage.py generate_missing_codes   # لو عندك منتجات قديمة من غير باركود
```

## 6. Gunicorn كـ systemd service

```bash
sudo cp deploy/inventory.service /etc/systemd/system/inventory.service
# عدّل المسارات جوّه الملف لو مختلفة عندك
sudo systemctl daemon-reload
sudo systemctl enable --now inventory
sudo systemctl status inventory
```

## 7. Nginx + HTTPS

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/inventory
sudo ln -s /etc/nginx/sites-available/inventory /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# HTTPS مجاني عبر Let's Encrypt:
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 8. اختبار نهائي بعد النشر

- افتح `https://yourdomain.com/accounts/login/` وسجّل دخول
- جرّب: إضافة منتج، حركة IN/OUT، طباعة باركود/QR/ملصق، التقارير
- تأكد إن الموقع بيتحول تلقائيًا لـ HTTPS
- شغّل `python manage.py check --deploy` وتأكد مفيش تحذيرات حرجة

## تحديث المشروع لاحقًا

```bash
cd /var/www/inventory
git pull   # أو ارفع الملفات الجديدة
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart inventory
```

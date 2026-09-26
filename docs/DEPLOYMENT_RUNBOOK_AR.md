# دليل التشغيل والنشر الإنتاجي — Ordinance

هذا الدليل يوصي بـ **Ubuntu VPS + Gunicorn + Nginx + PostgreSQL**. لا تستخدم Vercel لهذه النسخة: التطبيق Django stateful ويحتاج قاعدة بيانات دائمة، كما لا توجد قاعدة بيانات خارجية ضمن المشروع.

> تنبيه حاسم: الحزمة الحالية ليست إصداراً قابلاً للتشغيل. `inventory/services/inventory_service.py` مفقود، وستفشل إضافة حركة مخزون. لا تبدأ أي خطوة نشر حتى تحصل على الإصدار المرخّص الكامل من مالك النظام، ثم تمرّ خطوات التحقق أدناه.

## 0. قرار قبل البدء

يجب أن تتوافر البنود الآتية قبل فتح الموقع للمستخدمين:

- نسخة كاملة تتضمن `inventory/services/inventory_service.py` واختبارات منطق المخزون.
- نطاق DNS، مثل `inventory.example.com`، موجّه إلى عنوان الـ VPS.
- PostgreSQL مخصص للإنتاج؛ لا تستخدم SQLite مع عدة مستخدمين أو لتخزين بيانات إنتاجية.
- نسخة احتياطية من البيانات الحالية، وتجربة استرجاعها في بيئة منفصلة.
- حساب Admin أولي، وسياسة أدوار معلنة: Admin / Staff / Viewer إن كان مطلوباً.
- معالجة بنود P0 في `QA_AUDIT_REPORT_AR.md`: سجل الفاعل، منع حذف حركات التاريخ، واختبارات آلية وmigration clean.

## 1. تجهيز خادم Ubuntu

نفّذ الأوامر بحساب له `sudo`. استبدل `deployuser` باسم المستخدم الإداري لديك، و`inventory.example.com` بنطاقك الفعلي.

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip nginx postgresql postgresql-contrib git ufw certbot python3-certbot-nginx
sudo adduser --system --group --home /var/www/inventory inventory
sudo mkdir -p /var/www/inventory
sudo chown deployuser:inventory /var/www/inventory
sudo chmod 750 /var/www/inventory
```

افتح المنافذ العامة اللازمة فقط:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

لا تفتح المنفذ 8000 للعالم؛ Gunicorn يستمع على `127.0.0.1` وNginx فقط هو الواجهة العامة.

## 2. رفع المصدر بأمان

يفضل Git repository خاص، أو انسخ مجلد الإصدار الكامل عبر SFTP/SCP إلى `/var/www/inventory`. لا ترفع أو تلتزم بهذه الأشياء: `.env`، `db.sqlite3` الحقيقية، مجلدات `media/` الخاصة بعملاء، أو ملفات النسخ الاحتياطي.

```bash
cd /var/www/inventory
git clone <PRIVATE_REPOSITORY_URL> .
test -f inventory/services/inventory_service.py
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

أمر `test` في السطر الثالث يجب أن ينجح. إذا فشل، أوقف النشر: لا تستبدل الملف بمنطق مرتجل لأن ذلك قد يفسد أرصدة المخزون.

## 3. إنشاء PostgreSQL

استخدم كلمة مرور طويلة فريدة محفوظة في مدير أسرار. لا تضعها في أمر shell history إن كان الخادم مشتركاً؛ أدخلها بشكل تفاعلي عند ظهور prompt.

```bash
sudo -u postgres createuser --pwprompt inventory_user
sudo -u postgres createdb --owner=inventory_user --encoding=UTF8 --template=template0 inventory_db
sudo -u postgres psql -d inventory_db -c "REVOKE ALL ON DATABASE inventory_db FROM PUBLIC;"
```

تحقق من الاتصال من بيئة Python بعد إعداد `.env` في القسم التالي. اجعل PostgreSQL يستمع محلياً فقط ما لم يكن مزوداً مُداراً؛ لا تفتح 5432 للعامة.

## 4. إعداد أسرار وبيئة الإنتاج

أنشئ مفتاح Django حقيقياً، مرة واحدة فقط:

```bash
cd /var/www/inventory
. .venv/bin/activate
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

انسخ `.env.example` إلى `.env` وعدّله. المثال التالي يوضح البنية فقط؛ ضع القيم الحقيقية محلياً ولا تشاركها:

```dotenv
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<generated-secret>
DJANGO_ALLOWED_HOSTS=inventory.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://inventory.example.com
DJANGO_SITE_URL=https://inventory.example.com
DJANGO_TIME_ZONE=Africa/Cairo

DJANGO_DB_ENGINE=postgres
DJANGO_DB_NAME=inventory_db
DJANGO_DB_USER=inventory_user
DJANGO_DB_PASSWORD=<database-password>
DJANGO_DB_HOST=127.0.0.1
DJANGO_DB_PORT=5432

DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_HSTS_SECONDS=31536000
```

اقفل الملف فوراً:

```bash
sudo chown inventory:inventory /var/www/inventory/.env
sudo chmod 600 /var/www/inventory/.env
```

قبل تفعيل HTTPS لأول مرة، يمكن مؤقتاً ضبط `DJANGO_SECURE_SSL_REDIRECT=False` لتفادي إعادة توجيه مبكرة، ثم أعده `True` فور حصول Certbot على الشهادة.

## 5. تصحيح إعداد reverse proxy المطلوب

أضف إلى `config/settings.py` بعد التحقق من أن Gunicorn غير مكشوف للعامة:

```python
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
```

هذا يتوافق مع `X-Forwarded-Proto` الذي يرسله Nginx في `deploy/nginx.conf`، ويمنع حلقة إعادة توجيه HTTPS خلف الـ proxy. راجع هذا التغيير واختبره قبل الإطلاق.

## 6. فحوصات قاعدة البيانات والملفات الثابتة

نفّذ كل الأوامر من بيئة الإنتاج بعد قراءة `.env`:

```bash
cd /var/www/inventory
. .venv/bin/activate
set -a
. ./.env
set +a
python manage.py makemigrations --check --dry-run
python manage.py check --deploy
python manage.py test
python manage.py migrate --plan
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py setup_groups
python manage.py createsuperuser
```

قواعد قرار صارمة:

- إذا أظهر `makemigrations --check` ملف migration جديداً: لا تتجاوزه. أنشئ migration في بيئة التطوير، راجعه، التزم به في Git، ثم أعد الرفع.
- إذا قال `test` إن عدد الاختبارات صفر، لا تسمح بالإطلاق التجاري؛ أضف اختبارات P0 أولاً.
- `migrate --plan` للمراجعة فقط. لا تشغّل `migrate` على قاعدة حية قبل backup ونافذة صيانة إذا كان التغيير حساساً.

جهز مسارات التشغيل التي يحتاجها Nginx وGunicorn:

```bash
sudo mkdir -p /var/www/inventory/media /var/www/inventory/staticfiles
sudo chown -R inventory:inventory /var/www/inventory/media /var/www/inventory/staticfiles
sudo chmod -R u=rwX,g=rX,o= /var/www/inventory/media /var/www/inventory/staticfiles
```

إن أضيفت ملفات مرفوعة مستقبلاً، استخدم تخزيناً دائماً مع backup ولا تعتمد نظام ملفات خادم واحد عند التوسع.

## 7. تشغيل Gunicorn عبر systemd

راجع `deploy/inventory.service`: في الملف الحالي مستخدم الخدمة هو `www-data`، بينما الخطوات أعلاه تنشئ `inventory`. عدّل `User` و`Group` إلى `inventory`، واترك `WorkingDirectory` و`EnvironmentFile` كما هما. ثم:

```bash
sudo cp deploy/inventory.service /etc/systemd/system/inventory.service
sudo systemctl daemon-reload
sudo systemctl enable --now inventory
sudo systemctl status inventory --no-pager
sudo journalctl -u inventory -n 100 --no-pager
```

إذا فشلت الخدمة، لا تنتقل إلى Nginx. افحص أولاً أن الملف المفقود موجود، وأن permissions تسمح للمستخدم `inventory` بقراءة المشروع و`.env` وكتابة `media`.

اختبر من نفس الخادم:

```bash
curl -I http://127.0.0.1:8000/accounts/login/
```

ينبغي أن تحصل على استجابة HTTP، وليس `502` أو traceback.

## 8. تهيئة Nginx وHTTPS

انسخ الملف المرجعي وعدل `server_name` إلى نطاقك:

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/inventory
sudo ln -s /etc/nginx/sites-available/inventory /etc/nginx/sites-enabled/inventory
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

بعد تأكد DNS ووصول HTTP:

```bash
sudo certbot --nginx -d inventory.example.com
sudo certbot renew --dry-run
```

بعد الشهادة، تأكد من أن `.env` يعيد `DJANGO_SECURE_SSL_REDIRECT=True` ثم:

```bash
sudo systemctl restart inventory
sudo systemctl reload nginx
curl -I https://inventory.example.com/accounts/login/
```

النتيجة المطلوبة: HTTPS صحيح، لا حلقة redirect، ولا رؤوس أو صفحات Debug تكشف تفاصيل داخلية.

## 9. تهيئة المستخدمين والصلاحيات

1. سجل دخولك بالحساب الذي أنشأته عبر `createsuperuser`.
2. افتح `/admin/`، أنشئ مستخدم Staff منفصلاً للاختبار، وأضفه إلى مجموعة `Staff` فقط.
3. أنشئ Admin أعمال، وأضفه إلى مجموعة `Admin`. لا تمنحه `is_staff` أو `is_superuser` إلا إذا كان مسؤولاً تقنياً يحتاج Django Admin؛ فصل حساب الإدارة التقنية عن الحساب اليومي أفضل.
4. اختبر بحساب Staff: لا إعدادات، لا حذف، لا إدارة مستخدمين، ولا عرض سجل نشاط كل الموظفين بعد تنفيذ الإصلاح المطلوب.
5. اختبر بحساب Admin: التقارير والسجل الكامل وإدارة صلاحيات الأعمال حسب السياسة المعتمدة.

## 10. اختبار قبول ما بعد النشر

نفّذ هذه القائمة في بيئة staging أولاً ثم الإنتاج بعد backup:

- تسجيل دخول صحيح وخاطئ، ثم تسجيل خروج ومنع الرجوع للصفحات المحمية.
- إضافة منتج والتحقق من بياناته ورصيده في المخزن الصحيح.
- حركة استلام IN والتحقق من زيادة الرصيد وإنشاء سجل تدقيق يحوي الفاعل.
- حركة صرف OUT، ومنع الصرف فوق الرصيد، وتجربة طلبين متزامنين على نفس المنتج.
- وصول الرصيد إلى الحد الأدنى ثم الصفر: التقرير والجرس والداشبورد متسقة.
- محاولة Staff تعديل/حذف/فتح إعدادات عبر رابط مباشر: 403 آمن ولا تغيير في البيانات.
- تبديل العربية/الإنجليزية، RTL/LTR، الموبايل، Chrome/Firefox/Edge.
- استعادة نسخة backup في قاعدة مؤقتة ومقارنة عدد المنتجات والحركات وقيمة المخزون.

سجل النتائج مقابل [مصفوفة الاختبار](outputs/resort_inventory_test_plan/test_cases.json)، ولا تطلق الإصدار إذا فشلت حالة High.

## 11. نسخ احتياطي واسترجاع

أنشئ backup مشفراً خارج الخادم يومياً. مثال منطقي (لا تضع كلمة المرور في السطر):

```bash
pg_dump -Fc -h 127.0.0.1 -U inventory_user inventory_db > /secure-backups/inventory_YYYY-MM-DD.dump
```

جرب الاسترجاع إلى قاعدة جديدة في بيئة غير إنتاجية:

```bash
createdb inventory_restore_test
pg_restore -d inventory_restore_test /secure-backups/inventory_YYYY-MM-DD.dump
```

انسخ أي ملفات مرفوعة مستقبلاً إذا أضيفت ميزة تعتمد عليها؛ قاعدة البيانات وحدها لا تستعيدها.

## 12. تحديث إصدار لاحق بأمان

1. اختبر الإصدار في staging على نسخة بيانات منزوعة الحساسية.
2. خذ backup موثقاً من الإنتاج وأعلن نافذة الصيانة إذا وجدت migrations.
3. اسحب كود الإصدار، حدّث الاعتماديات، شغّل migration check/tests/check --deploy، ثم راجع migration plan.
4. شغّل migrations وcollectstatic، وأعد تشغيل Gunicorn فقط بعد نجاحها.
5. نفّذ smoke suite وراقب logs وSentry لمدة لا تقل عن أول يوم تشغيلي.

```bash
cd /var/www/inventory
git pull --ff-only
. .venv/bin/activate
pip install -r requirements.txt
set -a; . ./.env; set +a
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py check --deploy
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart inventory
sudo systemctl status inventory --no-pager
```

## متى تتوقف وتطلب معالجة؟

أوقف النشر فوراً إذا كان أي مما يلي صحيحاً: ملف `InventoryService` غير موجود، migration غير ملتزم بها، اختبار High فاشل، خطأ 500 في IN/OUT، استخدام SQLite لأكثر من مستخدم، أو لا توجد backup قابلة للاسترجاع. هذه ليست تحذيرات تجميلية؛ هي مخاطر مباشرة على رصيد المخزون وسجل التدقيق.

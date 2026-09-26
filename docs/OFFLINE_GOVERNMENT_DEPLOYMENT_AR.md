# دليل تشغيل نظام Ordinance داخل مؤسسة حكومية معزولة

تاريخ المراجعة: 2026-09-14  
النطاق: تشغيل نظام المخازن الحالي على شبكة داخلية لا تملك إنترنت، لأكثر من 14 مخزناً، الكانتين، ومحطات عمل متعددة. هذا الدليل مبني على مراجعة الكود والملفات الحالية، وليس افتراضاً أن كل ميزة موجودة أو مكتملة.

## 1. القرار التنفيذي

الحل الموصى به هو تطبيق واحد مركزي داخل الشبكة الداخلية، مع قاعدة PostgreSQL مركزية. كل جهاز في المخازن والكانتين يفتح النظام من المتصفح عبر اسم داخلي مثل:

`https://inventory.gov.local`

أي استلام أو صرف أو جرد يُحفظ في قاعدة البيانات المركزية نفسها؛ لذلك تظهر النتيجة فوراً عند فتح أو تحديث الصفحة على أي جهاز آخر. لا تنشئ نسخة مستقلة لكل مخزن ولا تستخدم SQLite في الإنتاج، وإلا ستنقسم البيانات ولن تتزامن.

الهيكل الأدنى المقترح باستخدام الخادمين الرئيسيين هو:

```text
أجهزة المخازن والكانتين والقائد
              │ HTTPS داخل الشبكة
              ▼
Server A: Nginx + Gunicorn + Django
              │ منفذ PostgreSQL داخلي فقط
              ▼
Server B: PostgreSQL + نسخ احتياطية
              │
              ▼
مخزن نسخ احتياطية داخلي منفصل/مشفّر
```

Server A لا يحتوي بيانات المخزون الأساسية. Server B لا يقدم الموقع للمستخدمين. إن كانت السياسة تسمح، يوضع خادم نسخ احتياطية منفصل أو مساحة تخزين شبكية محمية؛ لا يكفي نسخ backup بجوار قاعدة البيانات نفسها.

## 2. ما يفعله المشروع فعلياً

النظام الحالي يدعم المنتجات، الفئات والألوان والمقاسات، أرصدة موزعة حسب المخزن، الموردين والعملاء، حركات الاستلام والصرف والجرد، لوحة متابعة، تنبيهات نقص المخزون، تقارير مخزون وجرد مخازن وكشف حساب جهة وأرباح، تصدير Excel، مستخدمين وصلاحيات، وسجل نشاطات.

عند حركة IN أو OUT أو ADJUST، يعدل التطبيق رصيد المنتج في المخزن المحدد ثم يحسب الرصيد الإجمالي للمنتج من كل المخازن. ومنطق الصرف يمنع الصرف فوق رصيد المخزن. تم تطبيق قفل قاعدة بيانات على المنتج أثناء الحركة لتقليل تعارض الحركات المتزامنة؛ اعتمد PostgreSQL واختبره تحت الحمل قبل الإطلاق.

أصناف القائد لها قسم منفصل وسجل وصول وتصدير مستقل. لكن **لا تعتمدها لسرية أصناف القائد في الوضع الحالي** قبل تنفيذ بند العزل في القسم 5، لأن الحركات والتقارير ولوحة التحكم العامة قد تكشف بيانات الصنف المقيد لمن يملك الوصول العام. هذا بند حظر P0 وليس تحسيناً تجميلياً.

QR والباركود والطباعة ليست ميزات فعالة حالياً، رغم وجود آثار قديمة في بعض الوثائق وCSS.

## 3. المتطلبات الفنية الموصى بها

| الطبقة | الحد الأدنى العملي | الموصى به للمؤسسة |
|---|---|---|
| Server A التطبيق | 4 vCPU، 8 GB RAM، 80 GB SSD | 8 vCPU، 16 GB RAM، 150 GB SSD، نظام Linux مدعوم |
| Server B القاعدة | 4 vCPU، 16 GB RAM، 200 GB SSD | 8 vCPU، 32 GB RAM، أقراص RAID10/SSD، مساحة للنسخ |
| نظام التشغيل | Ubuntu Server LTS أو RHEL/AlmaLinux مدعوم | التزم بالنسخة المعتمدة من إدارة البنية التحتية |
| Python | نفس إصدار الحزمة المعتمدة بعد اختبار offline | Python 3.12 أو أحدث معتمد من المؤسسة |
| قاعدة البيانات | PostgreSQL | PostgreSQL 16 أو النسخة المعتمدة داخلياً |
| المتصفح | Chrome/Edge/Firefox حديث | Edge/Chrome موزع مركزياً ومحدّث داخلياً |
| الشبكة | LAN ثابتة | VLAN منفصل للتطبيق + ACLs وDNS داخلي وشهادة CA داخلية |

لا تعتمد أجهزة الكانتين أو المخازن على تثبيت Python أو تشغيل نسخ محلية. يكفي متصفح ومفتاح وصول داخلي.

## 4. اختيار أسلوب النشر

### الحل A — الموصى به: Linux Native

Nginx وGunicorn وDjango على Server A، وPostgreSQL على Server B. هذا أبسط حل تشغيلي، واضح لإدارة الأنظمة، ويعمل بلا إنترنت بعد تجهيز حزم offline.

### الحل B — Docker/Podman Offline

مناسب فقط إذا كانت المؤسسة لديها سجل صور داخلي وإدارة حاويات وموافقات أمنية. يجب نقل صور Python/Nginx/PostgreSQL المعتمدة بالوسيط الآمن، وفحصها ثم تحميلها في Registry داخلي. لا تستخدم `docker pull` من الخادم المعزول. لا يوجد Dockerfile أو compose في المشروع الآن؛ يتطلب ذلك بناء مراجع deployment واختبارها قبل الاعتماد.

### الحل C — Windows Server/IIS أو Waitress

بديل عندما تمنع السياسة Linux. ضع التطبيق على Windows Server مع Python وWaitress كخدمة Windows، وPostgreSQL على الخادم الآخر. استخدم IIS Reverse Proxy أو Nginx for Windows إن كان معتمداً. هذا ممكن لكنه أقل تفضيلاً من Linux Native للمشروع الحالي، ويحتاج إعداد خدمة ومراقبة Windows منفصلين.

**لا تستخدم Vercel أو استضافة خارجية أو أي SaaS عام**: المؤسسة معزولة، والتطبيق يحتاج قاعدة داخلية دائمة وبيانات حساسة.

## 5. قبل النشر: إجراءات حظر إلزامية

1. نفّذ `python manage.py test` و`python manage.py check` و`python manage.py makemigrations --check --dry-run` على نسخة الإصدار. لا تنشر إذا فشل أي منها.
2. طبّق كل migrations، وأهمها 0024 و0025، أولاً على staging ثم الإنتاج بعد backup.
3. أصلح العزل الكامل لأصناف القائد قبل إدخال بياناته. يجب أن تستخدم جميع الاستعلامات التالية قاعدة فلترة واحدة تمنع المنتجات المقيدة لغير حامل الصلاحية: dashboard، كل التقارير، سجل الحركات، تنبيهات navbar، البحث، تصدير Excel، Activity Log، وDjango Admin.
4. اجعل عمليات أصناف القائد تستخدم `Product.all_objects` فقط بعد التحقق الصريح من حامل الصلاحية، وأضف اختباراً يؤكد أن موظفاً عادياً وsuperuser غير المعيّن لا يرى الاسم أو الكمية أو الحركة أو التصدير. حالياً التعيين يسمح لحامل واحد فقط عبر `LeadershipAccessConfig`.
5. لا تحذف المنتج أو الحركة تاريخياً. يوجد منع لحذف منتج له حركات، وهذا جيد. طبّق الأرشفة `is_active` لاحقاً إن كان العمل يحتاج إخفاء المنتج مع بقاء السجل.
6. أضف اختبار ضغط PostgreSQL لحركات OUT المتزامنة من جهازين على نفس المنتج والمخزن؛ يجب ألا يصبح الرصيد سالباً أو تضيع حركة.
7. راجع سياسة الاحتفاظ بالسجلات: سجل النشاط وLeadershipAccessLog مهمان للمراجعة الإدارية، ويجب عدم حذفه من الواجهة العادية.

## 6. تجهيز حزمة غير متصلة بالإنترنت

لا تنقل المشروع عبر USB مباشرة إلى الإنتاج دون موافقة وأداة فحص المؤسسة. استخدم محطة وسيطة معتمدة، افحص المصدر والوسيط ببرنامج الحماية، وسجل hash وتاريخ واسم المستلم.

### 6.1 ما يجب تحضيره خارج المنطقة المعزولة

- نسخة مصدر محددة بالإصدار، مثل ملف ZIP يحتوي المشروع فقط بلا `.env` أو قاعدة بيانات حقيقية.
- SHA-256 للحزمة.
- حزم نظام التشغيل المناسبة لنفس التوزيعة والإصدار والمعمارية المستهدفة: Python، venv، Nginx، PostgreSQL client، build prerequisites إن لزم.
- wheelhouse مخصص لـ **Linux المستهدف** أو Windows المستهدف.
- شهادة CA الداخلية وملف CRL إن كانت السياسة تستخدمها.
- حزم/وسائط PostgreSQL المعتمدة إذا لم تكن في repository داخلي.

المجلد الحالي `offline_packages/` لا يكفي لخادم Linux: بعض الحزم تحمل علامة `win_amd64`، أي أنها مخصصة لويندوز. لا تنسخها لخادم Linux وتتوقع نجاح التثبيت.

### 6.2 إنشاء wheelhouse لنظام Linux مطابق

شغل التالي على جهاز متصل أو mirror داخلي يطابق **Linux + Python + architecture** الخاص بالخادم المستهدف، ثم انقل الناتج عبر الإجراء المعتمد:

```bash
python3 -m venv /tmp/inventory-wheel-build
. /tmp/inventory-wheel-build/bin/activate
python -m pip install --upgrade pip
mkdir -p wheelhouse-linux
pip download --dest wheelhouse-linux -r requirements.txt
python -m pip wheel --wheel-dir wheelhouse-linux -r requirements.txt
sha256sum wheelhouse-linux/* > wheelhouse-linux/SHA256SUMS.txt
```

إذا تعذر استخدام جهاز خارجي، أنشئ Repository داخلياً (APT/YUM/PyPI proxy معتمد) ثم أعط الخوادم المعزولة وصولاً إليه فقط. لا تضف استثناء إنترنت للخادم الإنتاجي لمجرد تثبيت المكتبات.

### 6.3 التحقق عند الاستلام

```bash
sha256sum -c SHA256SUMS.txt
find wheelhouse-linux -type f -name '*.whl' | wc -l
```

احتفظ بنسخة القراءة فقط من حزمة الإصدار وhash في سجل تغيير المؤسسة.

## 7. التنفيذ التفصيلي للحل الموصى به (Linux)

الأمثلة تستخدم الأسماء التالية؛ استبدلها قبل التنفيذ:

```text
اسم الخدمة: inventory
اسم DNS الداخلي: inventory.gov.local
IP Server A: 10.20.10.20
IP Server B: 10.20.10.21
اسم القاعدة: inventory_db
مستخدم القاعدة: inventory_app
مسار المشروع: /opt/inventory
```

### 7.1 DNS والشبكة

1. أنشئ سجل A داخلي: `inventory.gov.local → 10.20.10.20`.
2. في firewall اسمح للمستخدمين بالوصول إلى Server A فقط على TCP/443.
3. اسمح من Server A إلى Server B على TCP/5432 فقط.
4. امنع كل جهاز مستخدم من الوصول المباشر إلى TCP/5432.
5. اسمح للإداريين المعتمدين فقط بـ SSH إلى الخادمين عبر VLAN الإدارة أو jump host.
6. لا تفتح المنافذ 8000 أو 5432 لأي subnet عام.

### 7.2 إعداد PostgreSQL على Server B

ثبت PostgreSQL من مصدر المؤسسة. على Ubuntu كمثال:

```bash
sudo apt install ./packages/postgresql-16*.deb ./packages/postgresql-client-16*.deb
sudo systemctl enable --now postgresql
sudo -u postgres psql
```

داخل `psql`:

```sql
CREATE ROLE inventory_app LOGIN PASSWORD 'ضع-كلمة-مرور-عشوائية-داخل-مدير-الأسرار';
CREATE DATABASE inventory_db OWNER inventory_app ENCODING 'UTF8' TEMPLATE template0;
REVOKE ALL ON DATABASE inventory_db FROM PUBLIC;
\q
```

في `postgresql.conf`:

```conf
listen_addresses = '10.20.10.21,127.0.0.1'
password_encryption = scram-sha-256
```

وفي `pg_hba.conf` أضف سطراً مقيداً لخادم التطبيق فقط:

```conf
hostssl inventory_db inventory_app 10.20.10.20/32 scram-sha-256
```

إذا لم يتوفر TLS بين التطبيق والقاعدة، ضع الخادمين في VLAN محمية واتبع سياسة أمن المؤسسة؛ الأفضل شهادة CA داخلية و`sslmode=verify-full` في `DATABASE_URL`. أعد تشغيل القاعدة بعد التحقق:

```bash
sudo systemctl restart postgresql
sudo -u postgres psql -c '\l'
```

### 7.3 إنشاء حساب خدمة ومسار تطبيق على Server A

```bash
sudo groupadd --system inventory
sudo useradd --system --gid inventory --home /opt/inventory --shell /usr/sbin/nologin inventory
sudo mkdir -p /opt/inventory /var/lib/inventory /var/log/inventory
sudo chown -R inventory:inventory /opt/inventory /var/lib/inventory /var/log/inventory
sudo chmod 750 /opt/inventory /var/lib/inventory /var/log/inventory
```

انقل حزمة المصدر المعتمدة إلى `/opt/inventory` ثم:

```bash
cd /opt/inventory
sudo -u inventory python3 -m venv .venv
sudo -u inventory .venv/bin/pip install --no-index --find-links=/opt/inventory/wheelhouse-linux -r requirements.txt
```

لا تشغل `pip install` بلا `--no-index` داخل البيئة المعزولة، كي لا يحاول الوصول إلى الإنترنت أو يثبت إصداراً غير معتمد.

### 7.4 ملف بيئة الإنتاج

أنشئ `/etc/inventory/inventory.env` واجعله ملكاً لـ root ومقروءاً فقط لحساب الخدمة. مثال:

```dotenv
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<مفتاح-فريد-بطول-50-بايت-على-الأقل>
DJANGO_ALLOWED_HOSTS=inventory.gov.local,10.20.10.20
DJANGO_CSRF_TRUSTED_ORIGINS=https://inventory.gov.local
DJANGO_SITE_URL=https://inventory.gov.local
DJANGO_TIME_ZONE=Africa/Cairo
DATABASE_URL=postgresql://inventory_app:<url-encoded-password>@10.20.10.21:5432/inventory_db?sslmode=verify-full
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_HSTS_SECONDS=31536000
```

أنشئ المفتاح على Server A ولا ترسله بالبريد أو chat:

```bash
/opt/inventory/.venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(50))'
sudo install -d -m 750 /etc/inventory
sudoedit /etc/inventory/inventory.env
sudo chown root:inventory /etc/inventory/inventory.env
sudo chmod 640 /etc/inventory/inventory.env
```

يجب إضافة هذا الإعداد إلى `config/settings.py` عند العمل خلف Nginx TLS termination، بعد مراجعة فريق الأمن أن Gunicorn غير مكشوف إلا محلياً:

```python
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
```

### 7.5 قاعدة البيانات وملفات static

قبل تطبيق أي migration على بيانات حية، خذ backup. ثم نفّذ بترتيب:

```bash
cd /opt/inventory
set -a
. /etc/inventory/inventory.env
set +a
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py test
.venv/bin/python manage.py migrate --plan
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/python manage.py createsuperuser
```

لا تنشئ بيانات وهمية في قاعدة الإنتاج. أنشئ 14 مخزناً حقيقياً من الواجهة أو Django Admin بعد تحديد أمين وموقع كل مخزن. لا تدخل رصيداً افتتاحياً قبل التأكد من المخزن المستهدف.

### 7.6 خدمة Gunicorn

أنشئ `/etc/systemd/system/inventory.service`:

```ini
[Unit]
Description=Inventory Django application
After=network-online.target
Wants=network-online.target

[Service]
Type=exec
User=inventory
Group=inventory
WorkingDirectory=/opt/inventory
EnvironmentFile=/etc/inventory/inventory.env
ExecStart=/opt/inventory/.venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 --timeout 60 --access-logfile - --error-logfile - config.wsgi:application
Restart=on-failure
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ReadWritePaths=/opt/inventory/staticfiles /opt/inventory/media /var/log/inventory

[Install]
WantedBy=multi-user.target
```

ثم:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now inventory
sudo systemctl status inventory --no-pager
curl -I http://127.0.0.1:8000/accounts/login/
sudo journalctl -u inventory -n 100 --no-pager
```

اضبط workers بعد اختبار تحميل فعلي. البداية `2 × عدد vCPU + 1` حد نظري، لكن Django/قاعدة البيانات يجب قياسهما؛ لا ترفع العدد بلا مراقبة.

### 7.7 Nginx وشهادة داخلية

استخدم شهادة صادرة من CA الداخلية باسم `inventory.gov.local`. لا تستخدم Let's Encrypt لأن البيئة معزولة. انسخ الشهادة والمفتاح إلى مسار محمي، ثم أنشئ `/etc/nginx/sites-available/inventory`:

```nginx
server {
    listen 80;
    server_name inventory.gov.local;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name inventory.gov.local;

    ssl_certificate     /etc/nginx/tls/inventory.gov.local.crt;
    ssl_certificate_key /etc/nginx/tls/inventory.gov.local.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_session_timeout 1d;

    client_max_body_size 10m;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header Referrer-Policy same-origin always;

    location /static/ {
        alias /opt/inventory/staticfiles/;
        access_log off;
        expires 7d;
    }

    location /media/ {
        alias /opt/inventory/media/;
        autoindex off;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_read_timeout 60s;
    }
}
```

ثم:

```bash
sudo ln -s /etc/nginx/sites-available/inventory /etc/nginx/sites-enabled/inventory
sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl reload nginx
curl -Ik https://inventory.gov.local/accounts/login/
```

يجب تثبيت CA الداخلية على كل أجهزة Windows عبر GPO أو آلية المؤسسة؛ لا تطلب من كل موظف قبول تحذير الشهادة يدوياً.

## 8. التشغيل دون إنترنت: ملفات الواجهة

القوالب الحالية تحمل خطوط Google Fonts وأيقونات Bootstrap Icons وChart.js من CDN. في شبكة بلا إنترنت ستظهر الصفحة غالباً، لكن الخطوط/الأيقونات/الرسوم قد تفشل. قبل الإطلاق:

1. نزّل الملفات المرخصة من المصدر الموثوق على محطة معتمدة.
2. افحصها وانقلها إلى `static/vendor/` داخل المشروع.
3. بدّل روابط CDN في `templates/layout/base.html` و`templates/dashboard/index.html` إلى `{% static %}`.
4. شغّل `collectstatic --noinput` واختبر من جهاز لا يملك route للإنترنت.

لا يكفي القول إن الخادم لا يحتاج إنترنت؛ المتصفح يحاول CDN من جهاز المستخدم نفسه.

## 9. تصميم المستخدمين والصلاحيات للمؤسسة

| الدور | أمثلة الصلاحيات | لا يمنح |
|---|---|---|
| قائد المؤسسة | قسم أصناف القائد فقط، التصدير الخاص، قراءة ما تقرره السياسة | لا تشارك حسابه، ولا تمنح الصلاحية لأكثر من شخص دون إجراء نقل موثق |
| مدير النظام التقني | إدارة الحسابات والتكوين ومراجعة السجل، بحساب إداري منفصل | لا يستخدم الحساب اليومي للقائد |
| مدير مخزن | رؤية منتجات/حركات مخزنه، استلام وجرد حسب التفويض | تقارير القائد وأصنافه |
| موظف كانتين | صرف فقط من مخزن الكانتين، وإدخال المستلم/الجهة | حذف، إعدادات، إدارة مستخدمين، تعديل أسعار التكلفة |
| محاسب/مراجع | تقارير مصرح بها وقراءة فقط | حركات تعديل أو حذف |

المشروع الحالي يملك صلاحيات عامة أكثر من كونه مقيداً بكل مخزن. لفرض أن موظف الكانتين يعمل على مخزنه فقط، أضف نموذج `UserWarehouseAccess` واربط كل استعلام وحركة بالمخازن المسموحة له، وتحقق من ذلك على الخادم وليس فقط في قائمة الاختيار. هذه ضرورة لمؤسسة فيها 14 مخزناً.

لا تستخدم حساباً مشتركاً للكانتين. لكل موظف حساب شخصي كي يسجل `InventoryTransaction.user` و`ActivityLog.user` الفاعل الحقيقي.

## 10. تفعيل أصناف القائد بطريقة صحيحة

بعد إكمال العزل P0 واختباره، نفّذ:

```bash
cd /opt/inventory
set -a; . /etc/inventory/inventory.env; set +a
.venv/bin/python manage.py transfer_leadership_access --user-id 42 --note "قرار إداري رقم 2026/15"
```

استبدل `42` بمعرف المستخدم الذي تم التحقق من هويته. الأمر يعيّن حاملاً واحداً لصلاحية القيادة ويسجل سبب النقل. عند تغيير القائد لا تعدل قاعدة البيانات يدوياً؛ استخدم الأمر نفسه مع أمر إداري موثق.

اختبار القبول الضروري:

1. افتح قائمة ومنتج وحركة وتقرير وصادرات مستخدماً عادياً وتأكد من عدم ظهور أي بيانات قائد.
2. افعل ذلك بحساب مدير نظام غير حامل الصلاحية أيضاً، إذا كانت سياسة المؤسسة تشترط حجبها عنه.
3. افتح نفس الصفحات بالحساب المعيّن للقائد وتأكد من التوثيق في `LeadershipAccessLog`.
4. افحص export Excel، ملفات logs، cache، وإدارة Django؛ لا يجوز تسريب اسم الصنف فيها.

## 11. النسخ الاحتياطي والاستعادة

### نسخ يومي

على Server B، باستخدام حساب نظام مخصص، خزن النسخ في مسار منفصل أو NAS آمن. مثال:

```bash
sudo install -d -m 750 -o postgres -g postgres /srv/inventory-backups
sudo -u postgres pg_dump -Fc -d inventory_db -f /srv/inventory-backups/inventory_$(date +%F).dump
sudo -u postgres sha256sum /srv/inventory-backups/inventory_$(date +%F).dump > /srv/inventory-backups/inventory_$(date +%F).sha256
```

جدولة مقترحة: backup يومي، احتفاظ 30 يوماً يومياً و12 شهراً شهرياً حسب سياسة الأرشفة. انسخ النسخ إلى موقع داخلي ثانٍ. شفر النسخ إذا كانت الوسائط قابلة للنقل.

### اختبار الاستعادة الشهري

لا تعتبر backup صالحاً ما لم تستعده. على خادم اختبار منفصل:

```bash
createdb inventory_restore_test
pg_restore --clean --if-exists -d inventory_restore_test /srv/inventory-backups/inventory_YYYY-MM-DD.dump
psql -d inventory_restore_test -c 'SELECT COUNT(*) FROM inventory_inventorytransaction;'
dropdb inventory_restore_test
```

وثّق وقت الاستعادة وعدد المنتجات والحركات والنتيجة. RPO مناسب كبداية: 24 ساعة مع WAL/نسخ إضافية عند حاجة أقل. RTO يحدده فريق المؤسسة بعد تجربة استعادة فعلية.

## 12. الاستمرارية والتعافي باستخدام خادمين

التوزيع A/B السابق يرفع الاعتمادية لكنه ليس high availability تلقائياً؛ توقف Server B يعني توقف الكتابة. الخيارات:

- **أساسي:** Server B قاعدة رئيسية + backup يومي. مناسب كبداية.
- **أفضل:** PostgreSQL streaming replication إلى خادم standby ثالث/VM ثالث، مع تمرين failover يدوي موثق.
- **HA كامل:** Patroni/repmgr + etcd/Consul + VIP/load balancer. لا تنفذه دون فريق Linux/DBA وخطة اختبار failover؛ التعقيد عالي.

ابدأ بالأساسي، ثم اعتمد standby بعد اختبار القدرة التشغيلية والحاجة الفعلية. لا تعد المستخدمين بـ zero downtime قبل اختبار واضح.

## 13. مراقبة وتشغيل يومي

- راقب حالة `inventory.service` وNginx وPostgreSQL، ومساحة الأقراص والـ RAM ووقت backup.
- راجع `journalctl -u inventory` وسجل Nginx يومياً أو عبر منصة SIEM داخلية.
- أنشئ health check داخلياً لا يكشف بيانات حساسة، ثم راقبه من نظام مراقبة المؤسسة.
- راقب أخطاء 401/403 وطلبات دخول فاشلة والنشاط غير المعتاد في LeadershipAccessLog.
- راجع صلاحيات المستخدمين شهرياً، وعطل حساب الموظف فور نقله أو انتهاء تكليفه.
- طبّق تحديثات النظام والحزم عبر نافذة صيانة ووسيط داخلي معتمد، لا من الإنترنت.

## 14. اختبار قبول قبل الإطلاق

نفذ على staging يطابق الإنتاج:

1. إنشاء 14 مخزناً وحسابات مسؤول/موظف كانتين/مدير مخزن/محاسب/قائد.
2. إضافة منتج ورصيد افتتاحي للمخزن الصحيح.
3. استلام في مخزن وصرف من مخزن آخر، وتأكد أن الرصيد الإجمالي وتقرير كل مخزن صحيحان.
4. حاول OUT أكبر من رصيد المخزن وتأكد من الرفض وعدم تسجيل حركة جزئية.
5. نفّذ طلبين OUT متزامنين على آخر كمية من جهازين.
6. تحقق من التقارير، Excel، السجل، والتنبيهات بعد كل حركة.
7. اختبر 20-50 مستخدماً متزامناً ثم حمّل بيانات تمثيلية بمئات الأصناف و14 مخزناً.
8. افصل إنترنت محطة المستخدم عمداً وتأكد أن كل الواجهة والرسوم والأيقونات تعمل من static المحلي.
9. اختبر الشهادة الداخلية من أجهزة ضمن كل VLAN.
10. نفّذ restore من نسخة backup على خادم اختبار.
11. نفذ اختبار العزل الكامل للقائد المشار إليه في القسم 10.

لا تنقل النظام إلى الإنتاج حتى تمر الحالات العالية في ملف خطة الاختبار، وتعتمد النتائج Ordinance والأمن وإدارة الشبكات.

## 15. تشغيل أول يوم

1. جمّد التغييرات، خذ backup أخيراً، وسجل رقم الإصدار وSHA-256.
2. فعّل DNS وNginx والخدمة، ثم أجر اختبار smoke بحساب منفصل.
3. أنشئ المخازن والجهات والمستخدمين والصلاحيات الفعلية.
4. أدخل/رحّل الأرصدة الافتتاحية مرة واحدة فقط، مع توقيع مسؤول كل مخزن على العدد والقيمة.
5. شغّل الكانتين على مخزن مخصص له، ولا تسمح له بالصرف من بقية المخازن.
6. راقب الأداء والسجلات أول يوم تشغيلي، ثم راجع النتائج في نهاية الأسبوع الأول.

## 16. تحديث الإصدار لاحقاً بلا إنترنت

```bash
# 1. قبل التحديث: backup للقاعدة وتأكيد نجاحه
# 2. انقل حزمة إصدار موقعة ومفحوصة إلى الخادم
cd /opt/inventory
sudo systemctl stop inventory
# استبدل الكود مع الاحتفاظ بـ .venv وstaticfiles وملف البيئة خارج المشروع
sudo -u inventory .venv/bin/pip install --no-index --find-links=/opt/inventory/wheelhouse-linux -r requirements.txt
set -a; . /etc/inventory/inventory.env; set +a
sudo -u inventory .venv/bin/python manage.py check
sudo -u inventory .venv/bin/python manage.py test
sudo -u inventory .venv/bin/python manage.py makemigrations --check --dry-run
sudo -u inventory .venv/bin/python manage.py migrate --plan
sudo -u inventory .venv/bin/python manage.py migrate
sudo -u inventory .venv/bin/python manage.py collectstatic --noinput
sudo systemctl start inventory
sudo systemctl status inventory --no-pager
```

نفذ التحديث أولاً على staging. إذا فشل migration أو smoke test، توقف واستعد قاعدة البيانات/الإصدار وفق خطة rollback الموثقة؛ لا تحذف migrations ولا تعدل جداول الإنتاج يدوياً.

## 17. قائمة التسليم لإدارة المؤسسة

- وثيقة اعتماد المعمارية وIPs وVLAN وDNS.
- حسابات تشغيل منفصلة: Linux service، PostgreSQL app، backup، وadmin شخصي.
- شهادات CA داخلية وخطة تجديدها.
- نسخة مصدر موقعة وwheelhouse مطابقة للمنصة وhashes.
- ملف الأسرار في مدير الأسرار، لا داخل Git أو ملف مشارك.
- backup يومي + تقرير restore شهري.
- سجل صلاحيات لكل مستخدم ومخزن، وإجراء نقل صلاحية القائد.
- نتائج UAT واختبار الأداء وعزل أصناف القائد.
- runbook للحوادث: توقف التطبيق، تعطل DB، فشل backup، وتسريب حساب.

## 18. ملاحظات صادقة من مراجعة الكود

- `manage.py check` و`makemigrations --check --dry-run` كانا نظيفين أثناء المراجعة، والاختبارات الموجودة تعمل محلياً. لا تكفي الاختبارات الحالية وحدها لتصديق جاهزية مؤسسة كبيرة؛ أضف اختبارات للعزل حسب المخزن والقائد، للتزامن، وrestore.
- توجد ملفات وREADME قديمة تشير إلى QR/Barcode وإلى غياب InventoryService رغم وجوده الآن. نظفها وحدث الوثائق قبل التسليم.
- يجب استبدال CDN assets بملفات static داخلية لضمان عدم تعطل الواجهة في الشبكة المعزولة.
- استخدم PostgreSQL حصراً للإنتاج. SQLite مناسب للتجربة الفردية فقط.
- سياسة القائد الحالية تعتمد مستخدماً واحداً فقط، وتخفي القسم عن الآخرين عبر 404. هذا تصميم جيد كبداية لكنه غير كافٍ وحده لمنع التسريب من جميع شاشات النظام كما أوضحنا.

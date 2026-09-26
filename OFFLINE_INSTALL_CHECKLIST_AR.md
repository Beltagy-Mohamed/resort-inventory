# قائمة تجهيز وتثبيت سريعة — بيئة حكومية بلا إنترنت

هذه القائمة مرافقة للدليل الكامل `OFFLINE_GOVERNMENT_DEPLOYMENT_AR.md`.
الحل المعتمد: خادم تطبيق Linux واحد (A) وخادم PostgreSQL واحد (B)، وكل أجهزة
المخازن والكانتين تستخدم المتصفح فقط عبر `https://inventory.gov.local`.

## 1. قبل الذهاب إلى المؤسسة: جهّز هذه الحزمة على جهاز متصل ومعتمد

1. **ملف إصدار المشروع**: أرشيف ZIP من مصدر نظيف، بلا `.env` وبلا
   `db.sqlite3` وبلا ملفات مستخدمين.
2. **نظام تشغيل خادمي المؤسسة**: ISO أو مستودع داخلي معتمد لنفس النسخة
   والمعمارية التي ستثبت فعلياً (يفضل Ubuntu Server LTS أو RHEL/AlmaLinux
   المعتمدين لديهم).
3. **حزم نظام التشغيل offline** للخادم A: `python3` و`python3-venv` و`nginx`
   و`postgresql-client` و`ca-certificates` و`openssl` و`rsync`.
4. **حزم PostgreSQL offline** للخادم B: `postgresql-server` و`postgresql-client`
   وأي تبعياتها لنفس إصدار النظام. يفضل PostgreSQL 16 أو الإصدار الذي توافق
   عليه إدارة البنية.
5. **Wheelhouse Python لنفس Linux والخادم**. لا تستخدم مجلد
   `offline_packages/` الحالي لخادم Linux؛ فيه wheels لـ Windows (`win_amd64`).
   على جهاز Linux مطابق للخادم، ومن جذر المشروع، نفّذ:

   ```bash
   python3 -m venv /tmp/inventory-wheel-build
   . /tmp/inventory-wheel-build/bin/activate
   python -m pip download --dest wheelhouse-linux -r requirements.txt
   python -m pip wheel --wheel-dir wheelhouse-linux -r requirements.txt
   sha256sum wheelhouse-linux/* > wheelhouse-linux/SHA256SUMS.txt
   ```

6. شهادة السلطة الداخلية CA (والـCRL إن كانت السياسة تتطلبه)، وملف شهادة
   `inventory.gov.local` ومفتاحه من فريق البنية؛ لا تستخدم Let's Encrypt لأنه
   يحتاج إنترنت.
7. ملف hash للإصدار:

   ```bash
   sha256sum resort-inventory-release.zip > SHA256SUMS.txt
   ```

افحص كل وسيط نقل وفق سياسة المؤسسة وسجل الـhash قبل وبعد النقل. لا توصل أي
USB مباشرةً بخادم الإنتاج قبل الفحص والموافقة.

## 2. تسلسل التنفيذ داخل المؤسسة

1. ثبّت النظام والحزم offline، ثم اضبط DNS الداخلي ليشير
   `inventory.gov.local` إلى Server A.
2. أنشئ قاعدة PostgreSQL ومستخدم التطبيق على Server B، وافتح TCP/5432 من
   Server A فقط. لا تفتح هذا المنفذ لأجهزة المستخدمين.
3. على Server A انسخ الإصدار إلى `/opt/inventory` وأنشئ البيئة الافتراضية:

   ```bash
   sudo mkdir -p /opt/inventory
   sudo unzip resort-inventory-release.zip -d /opt/inventory
   sudo python3 -m venv /opt/inventory/.venv
   sudo /opt/inventory/.venv/bin/pip install --no-index \
     --find-links /media/approved/wheelhouse-linux \
     -r /opt/inventory/requirements.txt
   ```

4. أنشئ `/opt/inventory/.env` من `.env.example`، وضع كلمة سر قوية وبيانات
   PostgreSQL واسم DNS الداخلي. اجعل المالك مستخدم الخدمة فقط والصلاحية `600`.
5. نفّذ على Server A:

   ```bash
   cd /opt/inventory
   sudo -u inventoryapp .venv/bin/python manage.py migrate --noinput
   sudo -u inventoryapp .venv/bin/python manage.py collectstatic --noinput
   sudo -u inventoryapp .venv/bin/python manage.py check --deploy
   sudo -u inventoryapp .venv/bin/python manage.py createsuperuser
   ```

6. فعّل Gunicorn كخدمة وNginx كـ reverse proxy باستخدام ملفات `deploy/`، ثم
   ضع شهادة CA الداخلية، وافتح TCP/443 للمستخدمين. لا تعرض Gunicorn مباشرةً.
7. من جهازين مختلفين: سجّل نفس حركة مخزون أو أضف/اصرف صنفاً وتحقق أن الرصيد
   يتحدث من الصفحة الثانية بعد التحديث. اختبر كذلك مستخدماً عادياً وحامل
   صلاحية القائد: لا يجوز للأول رؤية أي صنف قائد أو اسمه في أي تقرير أو بحث.
8. جهز مهمة نسخ احتياطي يومية لـ PostgreSQL إلى موقع داخلي منفصل، واختبر
   الاستعادة مرة واحدة قبل الإطلاق.

التفاصيل الكاملة لإعداد Nginx وGunicorn وPostgreSQL والجدار الناري والنسخ
الاحتياطي موجودة في `OFFLINE_GOVERNMENT_DEPLOYMENT_AR.md`.

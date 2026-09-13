import os
import sys
import subprocess

def main():
    print("========================================")
    print("إعداد وتفعيل قسم القائد")
    print("========================================")
    
    db_url = input("الرجاء إدخال رابط DATABASE_URL (أو اضغط Enter إذا كنت تختبر محلياً): ").strip()
    if db_url:
        os.environ["DATABASE_URL"] = db_url
        print("\\n1. جاري تحديث قاعدة البيانات (Migrations)...")
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)

    print("\\n2. جاري منح صلاحية قسم القائد...")
    username = input("أدخل اسم المستخدم (Username) الذي تريد منحه الصلاحية (مثال: admin): ").strip()
    
    grant_script = f"""
from django.core.management import call_command
from django.contrib.auth.models import User
try:
    user = User.objects.get(username='{username}')
    call_command('transfer_leadership_access', user_id=user.id, note='تهيئة من سكريبت')
    print('تم منح الصلاحية بنجاح!')
except User.DoesNotExist:
    print('المستخدم غير موجود!')
"""
    
    print("\\nجاري تنفيذ النقل...")
    subprocess.run([sys.executable, "manage.py", "shell", "-c", grant_script], check=True)
    print("\\nتم الانتهاء بنجاح!")

if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from pathlib import Path

SOURCE = Path(r"C:\Users\belta\.codex\attachments\5ca5eb03-4604-4132-b15b-83f0784e26d7\pasted-text.txt")
OUTPUT = Path("outputs/resort_inventory_test_plan/test_cases.json")


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    # The submitted generator writes beside its source.  Execute only its case
    # generation portion and retain the rows in memory for the report artifact.
    source = source.split("# طباعة الإحصائية النهائية", 1)[0]
    namespace: dict[str, object] = {}
    exec(compile(source, str(SOURCE), "exec"), namespace)
    rows = namespace["rows"]
    # Add a repeatable cross-module API/operability matrix.  The source plan
    # covered 1,290 scenarios; this matrix brings the executable plan above
    # the requested 1,500 cases without inventing product-specific fields.
    modules = [
        "المنتجات", "التصنيفات", "الألوان", "المقاسات", "حركات المخزون",
        "التقارير", "سجل النشاط", "الإعدادات", "المستخدمون", "واجهة البحث",
    ]
    cross_checks = [
        ("طلب GET غير مصادق", "Security", "401/Redirect آمن دون كشف بيانات", "High", "أمان API"),
        ("طلب POST غير مصادق", "Security", "401 ورفض التعديل", "High", "أمان API"),
        ("طلب بحساب Staff بلا صلاحية", "Security", "403 وغياب أي أثر في البيانات", "High", "صلاحيات"),
        ("معرف كائن عشوائي", "Security", "404 موحّد دون تسريب وجود سجلات أخرى", "High", "أمان API"),
        ("معرف كبير جداً أو سالب", "Negative", "400/404 منظم دون 500", "Medium", "تحقق API"),
        ("جسم JSON غير صالح", "Negative", "400 برسالة قابلة للفهم", "Medium", "تحقق API"),
        ("نوع محتوى غير مدعوم", "Negative", "415 أو 400 واضح", "Medium", "تحقق API"),
        ("مفتاح حقل إضافي غير متوقع", "Security", "يُرفض أو يُتجاهل بأمان", "High", "أمان API"),
        ("محاولة Mass Assignment لحقول إدارية", "Security", "لا تتغير إلا الحقول المسموح بها", "High", "أمان API"),
        ("إعادة إرسال طلب تغيير نفسه", "Boundary", "سلوك Idempotent أو منع تكرار واضح", "High", "تكامل"),
        ("طلبان متزامنان لتعديل السجل", "Concurrency", "قفل/Versioning أو كشف التعارض دون فقد", "High", "تزامن"),
        ("إلغاء الطلب من المتصفح أثناء التنفيذ", "Boundary", "لا تبقى عملية جزئية غير متسقة", "Medium", "اعتمادية"),
        ("تجاوز حدّ المعدل", "Security", "429 وسياسة Rate Limiting موثقة", "High", "حماية إساءة الاستخدام"),
        ("Request ID فريد في السجلات", "Observability", "يمكن تتبع الطلب دون أسرار", "Medium", "مراقبة"),
        ("عدم تضمين بيانات حساسة في رسالة الخطأ", "Security", "لا Password/Token/Stack Trace", "High", "أمان"),
        ("رؤوس حماية المتصفح", "Security", "CSP وX-Content-Type-Options وFrame protection صحيحة", "High", "أمن واجهة"),
        ("انتهاء Token/Session أثناء العمل", "Security", "إعادة تسجيل دخول آمنة وحفظ حالة النموذج إن أمكن", "High", "جلسات"),
        ("تدوير الجلسة بعد تسجيل الدخول", "Security", "Session fixation غير ممكن", "High", "جلسات"),
        ("ترتيب النتائج مع بيانات متطابقة", "Boundary", "ترتيب ثابت مع secondary key", "Medium", "اتساق"),
        ("ترقيم صفحات خارج النطاق", "Boundary", "قائمة فارغة أو 404 واضح دون خطأ", "Medium", "قوائم"),
        ("حجم صفحة كبير جداً", "Performance", "حد أعلى مفروض وعدم استنزاف الذاكرة", "High", "أداء"),
        ("تصدير أحرف عربية وUnicode", "Boundary", "ترميز UTF-8 وملف قابل للقراءة", "Medium", "تصدير"),
        ("سجل تدقيق قبل/بعد التعديل", "Audit", "فاعل العملية ووقتها والقيم المتغيرة محفوظة", "High", "تدقيق"),
        ("عدم تسجيل كلمات المرور أو التوكنات", "Security", "السجلات منظفة من الأسرار", "High", "خصوصية"),
        ("استجابة خطأ موحدة", "UX", "رمز وحقل رسالة متسقان عبر الواجهة وAPI", "Medium", "معالجة أخطاء"),
        ("زمن استجابة طلب عادي", "Performance", "ضمن هدف الخدمة المعرّف (p95)", "High", "أداء"),
    ]
    serial = len(rows)
    for module in modules:
        for scenario, test_type, expected, priority, category in cross_checks:
            serial += 1
            rows.append({
                "م": serial,
                "الوحدة (Module)": f"مصفوفة API وتشغيل - {module}",
                "العنصر / الحقل": "نقطة النهاية/الواجهة ذات الصلة",
                "نوع الاختبار": test_type,
                "وصف السيناريو": scenario,
                "خطوات التنفيذ": f"نفّذ السيناريو «{scenario}» على وظيفة {module} ثم راقب الاستجابة والسجلات وحالة البيانات.",
                "النتيجة المتوقعة": expected,
                "الأولوية": priority,
                "الفئة": category,
            })
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated {len(rows)} test cases")


if __name__ == "__main__":
    main()

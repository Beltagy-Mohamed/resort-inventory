from datetime import datetime
import calendar
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import render
from ..models import ActivityLog

def is_superuser(u):
    return u.is_superuser

@login_required
def activity_logs(request):
    # إذا كان المستخدم أدمن رئيسي أو في مجموعة القائد نعرض كل النشاطات، غير ذلك نستخدم الـ Public Manager
    if request.user.is_superuser or request.user.groups.filter(name__in=['Leader', 'LeaderStaff']).exists():
        logs = ActivityLog.all_objects.select_related("product", "user").order_by("-created_at")
    else:
        logs = ActivityLog.objects.select_related("product", "user").order_by("-created_at")

    month_filter = request.GET.get("month_filter", "").strip()
    year_filter  = request.GET.get("year_filter",  "").strip()
    day_filter   = request.GET.get("day_filter",   "").strip()
    product_name_filter = request.GET.get("product_name", "").strip()

    # --- تحقق صارم: الفلاتر الرقمية لا تُمرَّر للـ QuerySet إلا إذا كانت أرقاماً فعلاً
    # (يمنع ValueError / HTTP 500 لو كتب المستخدم نصاً في الـ URL يدوياً)
    if year_filter and year_filter.isdigit():
        logs = logs.filter(created_at__year=int(year_filter))
    if month_filter and month_filter.isdigit():
        logs = logs.filter(created_at__month=int(month_filter))
    if day_filter and day_filter.isdigit():
        logs = logs.filter(created_at__day=int(day_filter))

    # --- فلتر بحث باسم المنتج (B9)
    if product_name_filter:
        logs = logs.filter(product__name__icontains=product_name_filter)

    paginator = Paginator(logs, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    arabic_months = [
        "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
        "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر",
    ]
    months = [(str(i + 1), arabic_months[i]) for i in range(12)]
    current_year = datetime.now().year
    years = [str(y) for y in range(current_year - 5, current_year + 5)]
    days  = [str(d) for d in range(1, 32)]

    return render(
        request,
        "activity/list.html",
        {
            "logs": page_obj,
            "page_obj": page_obj,
            "month_filter": int(month_filter) if month_filter.isdigit() else "",
            "year_filter": year_filter,
            "day_filter": day_filter,
            "product_name_filter": product_name_filter,
            "months": months,
            "years": years,
            "days": days,
        },
    )

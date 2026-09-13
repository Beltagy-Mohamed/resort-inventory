from datetime import datetime
import calendar
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import render
from ..models import ActivityLog

def is_superuser(u):
    return u.is_superuser

@login_required
@user_passes_test(is_superuser, login_url="/")
def activity_logs(request):
    logs = ActivityLog.objects.select_related("product", "user").order_by("-created_at")

    month_filter = request.GET.get('month_filter')
    year_filter = request.GET.get('year_filter')
    day_filter = request.GET.get('day_filter')

    if year_filter:
        logs = logs.filter(created_at__year=year_filter)
    if month_filter:
        logs = logs.filter(created_at__month=month_filter)
    if day_filter:
        logs = logs.filter(created_at__day=day_filter)

    paginator = Paginator(logs, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    arabic_months = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
    months = [(str(i+1), arabic_months[i]) for i in range(12)]
    
    current_year = datetime.now().year
    years = [str(y) for y in range(current_year - 5, current_year + 5)]
    days = [str(d) for d in range(1, 32)]

    return render(
        request,
        "activity/list.html",
        {
            "logs": page_obj,
            "page_obj": page_obj,
            "month_filter": month_filter,
            "year_filter": year_filter,
            "day_filter": day_filter,
            "months": months,
            "years": years,
            "days": days,
        }
    )

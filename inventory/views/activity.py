from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

from ..models import ActivityLog


@login_required
def activity_logs(request):

    logs = ActivityLog.objects.select_related(
        "product"
    ).order_by("-created_at")

    paginator = Paginator(logs, 20)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "activity/list.html",
        {
            "logs": page_obj,
            "page_obj": page_obj,
        }
    )
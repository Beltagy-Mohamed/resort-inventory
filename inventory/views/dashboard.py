from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, F, Avg, Count, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
import datetime

from ..models import (
    Product,
    Category,
    InventoryTransaction,
)


@login_required
def dashboard(request):

    products = Product.objects.all()

    categories = Category.objects.all()

    today = timezone.localdate()
    period = request.GET.get("period", "month")
    if period not in {"month", "year"}:
        period = "month"

    category_id = request.GET.get("category", "")
    try:
        category_id = int(category_id) if category_id else None
    except (TypeError, ValueError):
        category_id = None

    if category_id and not Category.objects.filter(id=category_id).exists():
        category_id = None

    products = products.filter(category_id=category_id) if category_id else products
    categories = categories.filter(id=category_id) if category_id else categories

    if period == "year":
        period_start = today.replace(month=1, day=1)
        period_end = period_start.replace(year=period_start.year + 1)
        previous_start = period_start.replace(year=period_start.year - 1)
    else:
        period_start = today.replace(day=1)
        if period_start.month == 12:
            period_end = period_start.replace(
                year=period_start.year + 1,
                month=1,
            )
        else:
            period_end = period_start.replace(month=period_start.month + 1)
        if period_start.month == 1:
            previous_start = period_start.replace(
                year=period_start.year - 1,
                month=12,
            )
        else:
            previous_start = period_start.replace(month=period_start.month - 1)

    inventory_value = products.aggregate(
        total=Sum(F("price") * F("quantity"))
    )["total"] or 0

    # One grouped query instead of one .count() per category.
    category_counts_qs = Product.objects.values(
        "category__id", "category__name"
    ).annotate(
        product_count=Count("id")
    )

    counts_by_category_id = {
        row["category__id"]: row["product_count"]
        for row in category_counts_qs
    }
    category_color_map = {
        category.id: category.color
        for category in categories
    }

    transactions_in_period = InventoryTransaction.objects.filter(
        created_at__date__gte=period_start,
        created_at__date__lt=period_end,
    )
    previous_transactions = InventoryTransaction.objects.filter(
        created_at__date__gte=previous_start,
        created_at__date__lt=period_start,
    )
    if category_id:
        transactions_in_period = transactions_in_period.filter(
            product__category_id=category_id
        )
        previous_transactions = previous_transactions.filter(
            product__category_id=category_id
        )

    transaction_totals = transactions_in_period.aggregate(
        received=Sum("quantity", filter=Q(transaction_type="IN")),
        issued=Sum("quantity", filter=Q(transaction_type="OUT")),
        adjusted=Sum("quantity", filter=Q(transaction_type="ADJUST")),
    )
    received_quantity = transaction_totals["received"] or 0
    issued_quantity = transaction_totals["issued"] or 0
    adjusted_quantity = transaction_totals["adjusted"] or 0

    current_transaction_count = transactions_in_period.count()
    previous_transaction_count = previous_transactions.count()
    if previous_transaction_count:
        activity_change = round(
            ((current_transaction_count - previous_transaction_count)
             / previous_transaction_count) * 100,
            1,
        )
    elif current_transaction_count:
        activity_change = 100
    else:
        activity_change = 0

    active_product_ids = transactions_in_period.values("product_id").distinct()
    active_products_count = active_product_ids.count()

    if period == "year":
        chart_labels = [
            datetime.date(today.year, month, 1).strftime("%b")
            for month in range(1, 13)
        ]
        grouped_counts_qs = transactions_in_period.annotate(
            period=TruncMonth("created_at")
        ).values("period").annotate(
            total=Count("id")
        )
        counts_by_period = {
            row["period"].month: row["total"]
            for row in grouped_counts_qs
        }
        chart_counts = [
            counts_by_period.get(month, 0)
            for month in range(1, 13)
        ]
    else:
        day_count = (today - period_start).days + 1
        chart_labels = [
            (period_start + datetime.timedelta(days=offset)).strftime("%d")
            for offset in range(day_count)
        ]
        grouped_counts_qs = transactions_in_period.annotate(
            period=TruncDate("created_at")
        ).values("period").annotate(
            total=Count("id")
        )
        counts_by_period = {
            row["period"]: row["total"]
            for row in grouped_counts_qs
        }
        chart_counts = [
            counts_by_period.get(
                period_start + datetime.timedelta(days=offset),
                0,
            )
            for offset in range(day_count)
        ]

    category_value_qs = products.values(
        "category__name"
    ).annotate(
        total=Sum(F("price") * F("quantity"))
    ).order_by("category__name")

    top_active_products = Product.objects.filter(
        id__in=active_product_ids
    ).annotate(
        movement_count=Count(
            "transactions",
            filter=Q(transactions__created_at__date__gte=period_start,
                      transactions__created_at__date__lt=period_end),
        ),
    ).order_by("-movement_count", "name")[:5]

    context = {
        "products_count": products.count(),
        "categories_count": categories.count(),
        "total_quantity": products.aggregate(
            Sum("quantity")
        )["quantity__sum"] or 0,
        "inventory_value": inventory_value,
        "low_stock": products.filter(
            quantity__lte=F("minimum_stock"),
            quantity__gt=0,
        ).count(),
        "out_of_stock": products.filter(quantity=0).count(),
        "today_transactions": InventoryTransaction.objects.filter(
            created_at__date=today
        ).count(),
        "average_price": products.aggregate(Avg("price"))["price__avg"] or 0,
        "most_expensive": products.order_by("-price").first(),
        "lowest_stock": products.exclude(quantity=0).order_by("quantity").first(),
        "period_transactions": current_transaction_count,
        "previous_transactions": previous_transaction_count,
        "activity_change": activity_change,
        "received_quantity": received_quantity,
        "issued_quantity": issued_quantity,
        "adjusted_quantity": adjusted_quantity,
        "net_movement": received_quantity - issued_quantity,
        "active_products_count": active_products_count,
        "period_start": period_start,
        "period_end": period_end,
        "low_stock_products": products.filter(
            quantity__lte=F("minimum_stock"),
            quantity__gt=0,
        ).order_by("quantity")[:5],
        "out_of_stock_products": products.filter(quantity=0)[:5],
        "latest_products": products.order_by("-created_at")[:5],
        "latest_transactions": InventoryTransaction.objects.select_related(
            "product"
        ).order_by("-created_at")[:5],
        "category_labels": [
            category.name
            for category in categories
        ],
        "category_counts": [
            counts_by_category_id.get(category.id, 0)
            for category in categories
        ],
        "category_colors": [
            category_color_map.get(category.id, "#3A5457")
            for category in categories
        ],
        "category_value_labels": [
            row["category__name"] or "Uncategorized"
            for row in category_value_qs
        ],
        "category_value_counts": [
            float(row["total"] or 0)
            for row in category_value_qs
        ],
        "category_value_colors": [
            category_color_map.get(
                next(
                    (
                        category.id
                        for category in categories
                        if category.name == row["category__name"]
                    ),
                    None,
                ),
                "#3A5457",
            )
            for row in category_value_qs
        ],
        "transactions_labels": chart_labels,
        "transactions_counts": chart_counts,
        "dashboard_period": period,
        "dashboard_category": category_id,
        "dashboard_categories": Category.objects.order_by("name"),
        "top_active_products": top_active_products,
    }

    return render(
        request,
        "dashboard/index.html",
        context,
    )
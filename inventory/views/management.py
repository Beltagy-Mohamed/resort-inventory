from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

from ..models import Warehouse, Partner
from ..forms import WarehouseForm, PartnerForm


def _is_leader_or_staff(user):
    """Returns True if the user can see leader-only resources."""
    return (
        user.is_superuser
        or user.groups.filter(name__in=['Leader', 'LeaderStaff']).exists()
    )


@login_required
@permission_required("inventory.view_warehouse", raise_exception=True)
def warehouses_list(request):
    location_query = request.GET.get('location', '').strip()
    
    if request.user.is_superuser or request.user.groups.filter(name__in=['Leader', 'LeaderStaff']).exists():
        warehouses = Warehouse.all_objects.all()
    else:
        warehouses = Warehouse.objects.all()

    # Get distinct locations for the dropdown
    locations = warehouses.exclude(location__isnull=True).exclude(location='').values_list('location', flat=True).distinct()
    
    if location_query:
        warehouses = warehouses.filter(location__icontains=location_query)
        
    return render(request, "management/warehouses_list.html", {
        "warehouses": warehouses,
        "locations": locations,
        "selected_location": location_query
    })

@login_required
@permission_required("inventory.add_warehouse", raise_exception=True)
def add_warehouse(request):
    if request.method == "POST":
        form = WarehouseForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "تمت إضافة المخزن بنجاح.")
            return redirect("warehouses_list")
    else:
        form = WarehouseForm(user=request.user)
    return render(request, "management/warehouse_form.html", {"form": form, "action": "إضافة مخزن"})

@login_required
@permission_required("inventory.change_warehouse", raise_exception=True)
def edit_warehouse(request, pk):
    warehouse = get_object_or_404(Warehouse.all_objects, pk=pk)
    if request.method == "POST":
        form = WarehouseForm(request.POST, instance=warehouse, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تعديل المخزن بنجاح.")
            return redirect("warehouses_list")
    else:
        form = WarehouseForm(instance=warehouse, user=request.user)
    return render(request, "management/warehouse_form.html", {"form": form, "action": "تعديل مخزن"})


@login_required
@permission_required("inventory.view_partner", raise_exception=True)
def partners_list(request):
    if _is_leader_or_staff(request.user):
        partners = Partner.all_objects.all().order_by('id')
    else:
        partners = Partner.objects.all().order_by('id')
    return render(request, "management/partners_list.html", {"partners": partners})

@login_required
@permission_required("inventory.add_partner", raise_exception=True)
def add_partner(request):
    if request.method == "POST":
        form = PartnerForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "تمت إضافة الجهة بنجاح.")
            return redirect("partners_list")
    else:
        form = PartnerForm(user=request.user)
    return render(request, "management/partner_form.html", {"form": form, "action": "إضافة جهة تعامل"})

@login_required
@permission_required("inventory.change_partner", raise_exception=True)
def edit_partner(request, pk):
    partner = get_object_or_404(Partner.all_objects, pk=pk)
    if request.method == "POST":
        form = PartnerForm(request.POST, instance=partner, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تعديل الجهة بنجاح.")
            return redirect("partners_list")
    else:
        form = PartnerForm(instance=partner, user=request.user)
    return render(request, "management/partner_form.html", {"form": form, "action": "تعديل جهة تعامل"})

@login_required
@permission_required("inventory.delete_warehouse", raise_exception=True)
def delete_warehouse(request, pk):
    warehouse = get_object_or_404(Warehouse.all_objects, pk=pk)
    if request.method == "POST":
        if warehouse.stocks.filter(quantity__gt=0).exists() or warehouse.transactions.exists():
            messages.error(request, "لا يمكن حذف هذا المخزن لأنه يحتوي على أرصدة أو حركات سابقة.")
        else:
            warehouse.delete()
            messages.success(request, "تم حذف المخزن بنجاح.")
    return redirect("warehouses_list")

@login_required
@permission_required("inventory.delete_partner", raise_exception=True)
def delete_partner(request, pk):
    partner = get_object_or_404(Partner.all_objects, pk=pk)
    if request.method == "POST":
        # Check if partner has any transactions
        if hasattr(partner, 'inventorytransaction_set') and partner.inventorytransaction_set.exists():
            messages.error(request, "لا يمكن حذف هذه الجهة لوجود حركات مالية ومخزنية مرتبطة بها.")
        else:
            partner.delete()
            messages.success(request, "تم حذف الجهة بنجاح.")
    return redirect("partners_list")

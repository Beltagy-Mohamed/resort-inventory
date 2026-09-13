from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Warehouse, Partner
from ..forms import WarehouseForm, PartnerForm


@login_required
def warehouses_list(request):
    warehouses = Warehouse.objects.all().order_by('id')
    return render(request, "management/warehouses_list.html", {"warehouses": warehouses})

@login_required
def add_warehouse(request):
    if request.method == "POST":
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "تمت إضافة المخزن بنجاح.")
            return redirect("warehouses_list")
    else:
        form = WarehouseForm()
    return render(request, "management/warehouse_form.html", {"form": form, "action": "إضافة مخزن"})

@login_required
def edit_warehouse(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == "POST":
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تعديل المخزن بنجاح.")
            return redirect("warehouses_list")
    else:
        form = WarehouseForm(instance=warehouse)
    return render(request, "management/warehouse_form.html", {"form": form, "action": "تعديل مخزن"})


@login_required
def partners_list(request):
    partners = Partner.objects.all().order_by('id')
    return render(request, "management/partners_list.html", {"partners": partners})

@login_required
def add_partner(request):
    if request.method == "POST":
        form = PartnerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "تمت إضافة الجهة بنجاح.")
            return redirect("partners_list")
    else:
        form = PartnerForm()
    return render(request, "management/partner_form.html", {"form": form, "action": "إضافة جهة تعامل"})

@login_required
def edit_partner(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    if request.method == "POST":
        form = PartnerForm(request.POST, instance=partner)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تعديل الجهة بنجاح.")
            return redirect("partners_list")
    else:
        form = PartnerForm(instance=partner)
    return render(request, "management/partner_form.html", {"form": form, "action": "تعديل جهة تعامل"})

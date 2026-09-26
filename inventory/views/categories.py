from django.contrib.auth.decorators import login_required, permission_required
from ..forms import CategoryForm
from ..models import Category
from .crud import generic_list, generic_add, generic_edit, generic_delete

@login_required
def categories_list(request):
    return generic_list(request, Category, "categories/list.html", "categories")

@login_required
@permission_required("inventory.add_category", raise_exception=True)
def add_category(request):
    return generic_add(request, CategoryForm, "categories/add.html", "categories_list", "تمت إضافة الفئة بنجاح.")

@login_required
@permission_required("inventory.change_category", raise_exception=True)
def edit_category(request, pk):
    return generic_edit(request, Category, CategoryForm, pk, "categories/edit.html", "category", "categories_list", "تم تعديل الفئة بنجاح.")

@login_required
@permission_required("inventory.delete_category", raise_exception=True)
def delete_category(request, pk):
    return generic_delete(request, Category, pk, "categories/delete.html", "category", "categories_list", "تم حذف الفئة.")

from django.contrib.auth.decorators import login_required, permission_required
from ..forms import ColorForm
from ..models import Color
from .crud import generic_list, generic_add, generic_edit, generic_delete

@login_required
def colors_list(request):
    return generic_list(request, Color, "colors/list.html", "colors")

@login_required
@permission_required("inventory.add_color", raise_exception=True)
def add_color(request):
    return generic_add(request, ColorForm, "colors/add.html", "colors_list", "تمت إضافة اللون بنجاح.")

@login_required
@permission_required("inventory.change_color", raise_exception=True)
def edit_color(request, pk):
    return generic_edit(request, Color, ColorForm, pk, "colors/edit.html", "color", "colors_list", "تم تعديل اللون بنجاح.")

@login_required
@permission_required("inventory.delete_color", raise_exception=True)
def delete_color(request, pk):
    return generic_delete(request, Color, pk, "colors/delete.html", "color", "colors_list", "تم حذف اللون.")

from django.contrib.auth.decorators import login_required, permission_required
from ..forms import SizeForm
from ..models import Size
from .crud import generic_list, generic_add, generic_edit, generic_delete

@login_required
def sizes_list(request):
    return generic_list(request, Size, "sizes/list.html", "sizes")

@login_required
@permission_required("inventory.add_size", raise_exception=True)
def add_size(request):
    return generic_add(request, SizeForm, "sizes/add.html", "sizes_list", "تمت إضافة المقاس بنجاح.")

@login_required
@permission_required("inventory.change_size", raise_exception=True)
def edit_size(request, pk):
    return generic_edit(request, Size, SizeForm, pk, "sizes/edit.html", "size", "sizes_list", "تم تعديل المقاس بنجاح.")

@login_required
@permission_required("inventory.delete_size", raise_exception=True)
def delete_size(request, pk):
    return generic_delete(request, Size, pk, "sizes/delete.html", "size", "sizes_list", "تم حذف المقاس.")

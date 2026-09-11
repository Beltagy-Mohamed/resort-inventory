from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

from ..models import Size
from ..forms import SizeForm


@login_required
def sizes_list(request):

    sizes = Size.objects.all().order_by("name")

    return render(
        request,
        "sizes/list.html",
        {
            "sizes": sizes
        }
    )


@login_required
@permission_required("inventory.add_size", raise_exception=True)
def add_size(request):

    if request.method == "POST":

        form = SizeForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "تم إضافة المقاس."
            )

            return redirect("sizes_list")

    else:

        form = SizeForm()

    return render(
        request,
        "sizes/add.html",
        {
            "form": form
        }
    )


@login_required
@permission_required("inventory.change_size", raise_exception=True)
def edit_size(request, pk):

    size = get_object_or_404(
        Size,
        pk=pk
    )

    if request.method == "POST":

        form = SizeForm(
            request.POST,
            instance=size
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "تم تعديل المقاس."
            )

            return redirect("sizes_list")

    else:

        form = SizeForm(instance=size)

    return render(
        request,
        "sizes/edit.html",
        {
            "form": form
        }
    )


@login_required
@permission_required("inventory.delete_size", raise_exception=True)
def delete_size(request, pk):

    size = get_object_or_404(
        Size,
        pk=pk
    )

    if request.method == "POST":

        size.delete()

        messages.success(
            request,
            "تم حذف المقاس."
        )

        return redirect("sizes_list")

    return render(
        request,
        "sizes/delete.html",
        {
            "size": size
        }
    )
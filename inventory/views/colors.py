from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404

from ..forms import ColorForm
from ..models import Color


@login_required
def colors_list(request):

    colors = Color.objects.all().order_by("name")

    return render(
        request,
        "colors/list.html",
        {
            "colors": colors
        }
    )


@login_required
@permission_required("inventory.add_color", raise_exception=True)
def add_color(request):

    if request.method == "POST":

        form = ColorForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "تم إضافة اللون بنجاح."
            )

            return redirect("colors_list")

    else:

        form = ColorForm()

    return render(
        request,
        "colors/add.html",
        {
            "form": form
        }
    )


@login_required
@permission_required("inventory.change_color", raise_exception=True)
def edit_color(request, pk):

    color = get_object_or_404(
        Color,
        pk=pk
    )

    if request.method == "POST":

        form = ColorForm(
            request.POST,
            instance=color
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "تم تعديل اللون بنجاح."
            )

            return redirect("colors_list")

    else:

        form = ColorForm(instance=color)

    return render(
        request,
        "colors/edit.html",
        {
            "form": form,
            "color": color
        }
    )


@login_required
@permission_required("inventory.delete_color", raise_exception=True)
def delete_color(request, pk):

    color = get_object_or_404(
        Color,
        pk=pk
    )

    if request.method == "POST":

        color.delete()

        messages.success(
            request,
            "تم حذف اللون."
        )

        return redirect("colors_list")

    return render(
        request,
        "colors/delete.html",
        {
            "color": color
        }
    )
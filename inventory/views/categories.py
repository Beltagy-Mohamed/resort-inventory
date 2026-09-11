from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from ..forms import CategoryForm
from ..models import Category


@login_required
def categories_list(request):

    categories = Category.objects.all().order_by("name")

    return render(
        request,
        "categories/list.html",
        {
            "categories": categories
        }
    )


@login_required
@permission_required("inventory.add_category", raise_exception=True)
def add_category(request):

    if request.method == "POST":

        form = CategoryForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "تم إضافة التصنيف بنجاح."
            )

            return redirect("categories_list")

    else:

        form = CategoryForm()

    return render(
        request,
        "categories/add.html",
        {
            "form": form
        }
    )


@login_required
@permission_required("inventory.change_category", raise_exception=True)
def edit_category(request, pk):

    category = get_object_or_404(
        Category,
        pk=pk
    )

    if request.method == "POST":

        form = CategoryForm(
            request.POST,
            instance=category
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "تم تعديل التصنيف بنجاح."
            )

            return redirect("categories_list")

    else:

        form = CategoryForm(
            instance=category
        )

    return render(
        request,
        "categories/edit.html",
        {
            "form": form,
            "category": category
        }
    )


@login_required
@permission_required("inventory.delete_category", raise_exception=True)
def delete_category(request, pk):

    category = get_object_or_404(
        Category,
        pk=pk
    )

    if request.method == "POST":

        category.delete()

        messages.success(
            request,
            "تم حذف التصنيف بنجاح."
        )

        return redirect("categories_list")

    return render(
        request,
        "categories/delete.html",
        {
            "category": category
        }
    )
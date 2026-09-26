from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

def generic_list(request, model, template, context_name, sort_field="name"):
    items = model.objects.all().order_by(sort_field)
    return render(request, template, {context_name: items})

def generic_add(request, form_class, template, redirect_url, success_msg):
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, success_msg)
            return redirect(redirect_url)
    else:
        form = form_class()
    return render(request, template, {"form": form})

def generic_edit(request, model, form_class, pk, template, context_name, redirect_url, success_msg):
    obj = get_object_or_404(model, pk=pk)
    if request.method == "POST":
        form = form_class(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, success_msg)
            return redirect(redirect_url)
    else:
        form = form_class(instance=obj)
    return render(request, template, {"form": form, context_name: obj})

def generic_delete(request, model, pk, template, context_name, redirect_url, success_msg):
    obj = get_object_or_404(model, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, success_msg)
        return redirect(redirect_url)
    return render(request, template, {context_name: obj})

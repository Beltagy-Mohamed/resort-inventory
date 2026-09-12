from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Permission
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from inventory.models import Product, InventoryTransaction
from inventory.forms import CustomUserCreationForm, CustomUserEditForm

def superuser_required(user):
    return user.is_superuser

@user_passes_test(superuser_required, login_url='/')
def users_list(request):
    users = User.objects.all().order_by('-is_superuser', 'username')
    return render(request, 'users/list.html', {'users': users})

def assign_permissions(user, cleaned_data):
    user.user_permissions.clear()
    
    # We assign standard django permissions based on checkboxes
    prod_ct = ContentType.objects.get_for_model(Product)
    trans_ct = ContentType.objects.get_for_model(InventoryTransaction)
    
    if cleaned_data.get('perm_inventory'):
        user.user_permissions.add(
            Permission.objects.get(content_type=prod_ct, codename='add_product'),
            Permission.objects.get(content_type=prod_ct, codename='change_product'),
            Permission.objects.get(content_type=prod_ct, codename='view_product')
        )
    if cleaned_data.get('perm_sales'):
        user.user_permissions.add(
            Permission.objects.get(content_type=trans_ct, codename='add_inventorytransaction'),
            Permission.objects.get(content_type=trans_ct, codename='change_inventorytransaction'),
            Permission.objects.get(content_type=trans_ct, codename='view_inventorytransaction')
        )
    if cleaned_data.get('perm_delete'):
        user.user_permissions.add(
            Permission.objects.get(content_type=prod_ct, codename='delete_product'),
            Permission.objects.get(content_type=trans_ct, codename='delete_inventorytransaction')
        )
    # perm_reports can be a custom permission or just mapped to viewing reports.
    # We can just check user.has_perm('inventory.view_inventorytransaction') for reports, 
    # but let's create a custom permission check or use view_inventorytransaction.
    # Actually, let's assign view_inventorytransaction if they have reports.
    if cleaned_data.get('perm_reports'):
        user.user_permissions.add(
            Permission.objects.get(content_type=trans_ct, codename='view_inventorytransaction')
        )

@user_passes_test(superuser_required, login_url='/')
def add_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False # They shouldn't access /admin
            user.save()
            assign_permissions(user, form.cleaned_data)
            messages.success(request, 'تمت إضافة الموظف بنجاح.')
            return redirect('users_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/form.html', {'form': form, 'title': 'إضافة موظف جديد'})

@user_passes_test(superuser_required, login_url='/')
def edit_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            assign_permissions(user, form.cleaned_data)
            messages.success(request, 'تم تحديث بيانات الموظف.')
            return redirect('users_list')
    else:
        # Pre-fill checkboxes based on current permissions
        initial = {
            'perm_inventory': user.has_perm('inventory.add_product'),
            'perm_sales': user.has_perm('inventory.add_inventorytransaction'),
            'perm_delete': user.has_perm('inventory.delete_product'),
            # Since both perm_reports and perm_sales use view_trans, distinguish if needed,
            # or just set it to True if they have view_trans.
            'perm_reports': user.has_perm('inventory.view_inventorytransaction'),
        }
        form = CustomUserEditForm(instance=user, initial=initial)
        
    return render(request, 'users/form.html', {'form': form, 'title': 'تعديل بيانات الموظف'})

@user_passes_test(superuser_required, login_url='/')
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if not user.is_superuser: # Prevent deleting superuser
        user.delete()
        messages.success(request, 'تم حذف الموظف بنجاح.')
    return redirect('users_list')

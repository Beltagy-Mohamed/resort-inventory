from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Permission
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from inventory.models import Product, InventoryTransaction, Category, Color, Size, Warehouse, Partner
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
    cat_ct = ContentType.objects.get_for_model(Category)
    col_ct = ContentType.objects.get_for_model(Color)
    size_ct = ContentType.objects.get_for_model(Size)
    wh_ct = ContentType.objects.get_for_model(Warehouse)
    part_ct = ContentType.objects.get_for_model(Partner)
    
    if cleaned_data.get('perm_inventory'):
        user.user_permissions.add(
            Permission.objects.get(content_type=prod_ct, codename='add_product'),
            Permission.objects.get(content_type=prod_ct, codename='change_product'),
            Permission.objects.get(content_type=prod_ct, codename='view_product'),
            Permission.objects.get(content_type=cat_ct, codename='add_category'),
            Permission.objects.get(content_type=cat_ct, codename='change_category'),
            Permission.objects.get(content_type=cat_ct, codename='view_category'),
            Permission.objects.get(content_type=col_ct, codename='add_color'),
            Permission.objects.get(content_type=col_ct, codename='change_color'),
            Permission.objects.get(content_type=col_ct, codename='view_color'),
            Permission.objects.get(content_type=size_ct, codename='add_size'),
            Permission.objects.get(content_type=size_ct, codename='change_size'),
            Permission.objects.get(content_type=size_ct, codename='view_size'),
            Permission.objects.get(content_type=wh_ct, codename='add_warehouse'),
            Permission.objects.get(content_type=wh_ct, codename='change_warehouse'),
            Permission.objects.get(content_type=wh_ct, codename='view_warehouse'),
            Permission.objects.get(content_type=part_ct, codename='add_partner'),
            Permission.objects.get(content_type=part_ct, codename='change_partner'),
            Permission.objects.get(content_type=part_ct, codename='view_partner')
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
            Permission.objects.get(content_type=trans_ct, codename='delete_inventorytransaction'),
            Permission.objects.get(content_type=cat_ct, codename='delete_category'),
            Permission.objects.get(content_type=col_ct, codename='delete_color'),
            Permission.objects.get(content_type=size_ct, codename='delete_size'),
            Permission.objects.get(content_type=wh_ct, codename='delete_warehouse'),
            Permission.objects.get(content_type=part_ct, codename='delete_partner')
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
            user.is_superuser = form.cleaned_data.get('is_superadmin', False)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            
            from django.contrib.auth.models import Group
            if form.cleaned_data.get('is_leader'):
                leader_group, _ = Group.objects.get_or_create(name='Leader')
                user.groups.add(leader_group)
            else:
                leader_group = Group.objects.filter(name='Leader').first()
                if leader_group:
                    user.groups.remove(leader_group)
                    
            assign_permissions(user, form.cleaned_data)
            messages.success(request, 'تمت إضافة الموظف بنجاح.')
            return redirect('users_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/form.html', {'form': form, 'title': 'إضافة موظف جديد'})

@user_passes_test(superuser_required, login_url='/')
def edit_user(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=target_user)
        if form.is_valid():
            # --- حماية Self-Lockout (A6): المدير لا يستطيع تعطيل نفسه
            if target_user == request.user and not form.cleaned_data.get('is_active', True):
                messages.error(request, 'لا يمكنك تعطيل حسابك الشخصي. اطلب من مدير آخر القيام بذلك.')
                return redirect('users_list')
            user = form.save(commit=False)
            
            # Prevent removing superadmin from oneself
            if target_user == request.user and target_user.is_superuser and not form.cleaned_data.get('is_superadmin', False):
                messages.error(request, 'لا يمكنك إزالة صلاحيات الإدارة الرئيسية عن نفسك.')
                form.cleaned_data['is_superadmin'] = True
                
            user.is_superuser = form.cleaned_data.get('is_superadmin', False)
            new_password = form.cleaned_data.get('new_password')
            if new_password:
                user.set_password(new_password)
            user.save()
            
            from django.contrib.auth.models import Group
            if form.cleaned_data.get('is_leader'):
                leader_group, _ = Group.objects.get_or_create(name='Leader')
                user.groups.add(leader_group)
            else:
                leader_group = Group.objects.filter(name='Leader').first()
                if leader_group:
                    user.groups.remove(leader_group)
                    
            assign_permissions(user, form.cleaned_data)
            messages.success(request, 'تم تحديث بيانات الموظف.')
            return redirect('users_list')
    else:
        # Pre-fill checkboxes based on current permissions
        initial = {
            'perm_inventory': target_user.has_perm('inventory.add_product'),
            'perm_sales': target_user.has_perm('inventory.add_inventorytransaction'),
            'perm_delete': target_user.has_perm('inventory.delete_product'),
            'perm_reports': target_user.has_perm('inventory.view_inventorytransaction'),
            'is_superadmin': target_user.is_superuser,
            'is_leader': target_user.groups.filter(name='Leader').exists(),
        }
        form = CustomUserEditForm(instance=target_user, initial=initial)

    return render(request, 'users/form.html', {'form': form, 'title': 'تعديل بيانات الموظف'})


@user_passes_test(superuser_required, login_url='/')
def delete_user(request, pk):
    """
    لا نحذف المستخدمين فيزيائياً — نعطّلهم فقط (Soft Deactivation).
    يحافظ على سلامة السجل التاريخي (ActivityLog, LeadershipAccessLog)
    ويتجنب انهيار HTTP 500 الناتج عن ProtectedError.
    """
    target_user = get_object_or_404(User, pk=pk)

    # --- منع حذف/تعطيل المدير الأعلى
    if target_user.is_superuser:
        messages.error(request, 'لا يمكن تعطيل حساب المدير الرئيسي للنظام.')
        return redirect('users_list')

    # --- منع الشخص من تعطيل نفسه (A6)
    if target_user == request.user:
        messages.error(request, 'لا يمكنك تعطيل حسابك الشخصي.')
        return redirect('users_list')

    target_user.is_active = False
    target_user.save(update_fields=['is_active'])
    messages.success(request, f'تم تعطيل حساب "{target_user.username}" بنجاح. يمكنك إعادة تفعيله لاحقاً من صفحة التعديل.')
    return redirect('users_list')

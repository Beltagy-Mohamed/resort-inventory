import io

path = 'e:/خاص مشروع/client_delivery/inventory/views/users.py'
with io.open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old = """            user.is_superuser = form.cleaned_data.get('is_superadmin', False)
            new_password = form.cleaned_data.get('new_password')
            if new_password:
                user.set_password(new_password)
            user.save()"""

new = """            user.is_superuser = form.cleaned_data.get('is_superadmin', False)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()"""

# Replace ONLY the first occurrence (which is in add_user)
c = c.replace(old, new, 1)

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(c)

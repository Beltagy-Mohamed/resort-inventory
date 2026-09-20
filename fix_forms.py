import io

path = 'e:/خاص مشروع/client_delivery/inventory/forms.py'
with io.open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old = """class CustomUserEditForm(forms.ModelForm):"""
new = """class CustomUserEditForm(forms.ModelForm):
    new_password = forms.CharField(label='كلمة مرور جديدة (اتركها فارغة إذا لم ترد التغيير)', required=False, widget=forms.PasswordInput(attrs={'class': 'form-control'}))"""

c = c.replace(old, new)

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(c)

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Product
from .models import Category
from .models import Color
from .models import InventoryTransaction
from .models import Size
from .models import SystemSettings
class ProductForm(forms.ModelForm):

    class Meta:

        model = Product

        fields = [
            "name",
            "category",
            "color",
            "size",
            "price",
            "quantity",
            "minimum_stock",
            "description",
        ]

        labels = {
            "name": _("Product name"),
            "category": _("Category"),
            "color": _("Color"),
            "size": _("Size"),
            "price": _("Price"),
            "quantity": _("Quantity"),
            "description": _("Description"),
            "minimum_stock": _("Minimum stock"),
        }

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "category": forms.Select(
                attrs={"class": "form-control"}
            ),
            "color": forms.Select(
                attrs={"class": "form-control"}
            ),
            "size": forms.Select(
                attrs={"class": "form-control"}
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "quantity": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "minimum_stock": forms.NumberInput(
            attrs={"class": "form-control"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4
                }
            ),
        }
class CategoryForm(forms.ModelForm):

    class Meta:

        model = Category

        fields = [
            "name",
            "color",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Category name")
                }
            ),
            "color": forms.TextInput(
                attrs={
                    "class": "form-control category-color-input",
                    "type": "color",
                }
            ),

        }        
        
class ColorForm(forms.ModelForm):

    class Meta:

        model = Color

        fields = [
            "name",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Color name")
                }
            )

        }        
        
class InventoryTransactionForm(forms.ModelForm):

    class Meta:

        model = InventoryTransaction

        fields = [

            "product",

            "transaction_type",

            "quantity",

            "notes",

        ]

        widgets = {

            "product": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "transaction_type": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4
                }
            )

        }
        
class SizeForm(forms.ModelForm):

    class Meta:

        model = Size

        fields = [
            "name",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Size name")
                }
            )

        }        

class SystemSettingsForm(forms.ModelForm):

    class Meta:

        model = SystemSettings

        fields = [
            "company_name",
            "currency",
        ]

        labels = {
            "company_name": "اسم الشركة",
            "currency": "العملة",
        }

        widgets = {
            "company_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "currency": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "مثال: EGP"}
            ),
        }

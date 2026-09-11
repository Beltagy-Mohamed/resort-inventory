from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from ..forms import ProductForm
from ..models import Product, ActivityLog
from ..services.code_generator import CodeGenerator
from ..services.qr_service import QRService
from ..services.barcode_service import BarcodeService
@login_required
def products_list(request):

    search = request.GET.get("search", "")

    status = request.GET.get("status", "")

    products = Product.objects.select_related(
        "category",
        "color",
        "size",
    )

    if search:

        products = products.filter(

            Q(name__icontains=search) |

            Q(product_code__icontains=search)

        )

    if status == "available":

        products = products.filter(
            quantity__gt=F("minimum_stock")
        )

    elif status == "low":

        products = products.filter(
            quantity__gt=0,
            quantity__lte=F("minimum_stock")
        )

    elif status == "out":

        products = products.filter(
            quantity=0
        )

    products = products.order_by("-id")

    paginator = Paginator(products, 10)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(

        request,

        "products/list.html",

        {

            "page_obj": page_obj,

            "search": search,

            "status": status,

        }

    )
    
    
@login_required
@permission_required("inventory.add_product", raise_exception=True)
def add_product(request):

    if request.method == "POST":

        form = ProductForm(request.POST)

        if form.is_valid():

            product = form.save(commit=False)

            product.product_code = CodeGenerator.generate()

            product.save()
            ActivityLog.objects.create(

    action="ADD",

    product=product,

    description=f"تم إضافة {product.name}"

)
            QRService.generate(product)
            BarcodeService.generate(product)

            messages.success(
            request,
            "تم إضافة المنتج بنجاح."
            )
            return redirect("products_list")

    else:

        form = ProductForm()

    return render(
        request,
        "products/add.html",
        {
            "form": form
        }
    )


@login_required
@permission_required("inventory.change_product", raise_exception=True)
def edit_product(request, product_code):

    product = get_object_or_404(
        Product,
        product_code=product_code
    )

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            instance=product
        )

        if form.is_valid():

            form.save()
            ActivityLog.objects.create(

    action="EDIT",

    product=product,

    description=f"تم تعديل {product.name}"

)
            messages.success(
                request,
                "تم تعديل المنتج بنجاح."
            )

            return redirect(
                "product_detail",
                product.product_code
            )

    else:

        form = ProductForm(instance=product)

    return render(
        request,
        "products/edit.html",
        {
            "form": form,
            "product": product
        }
    )    
    
@login_required
@permission_required("inventory.delete_product", raise_exception=True)
def delete_product(request, product_code):

    product = get_object_or_404(
        Product,
        product_code=product_code
    )

    if request.method == "POST":
       
        ActivityLog.objects.create(

    action="DELETE",

    description=f"تم حذف {product.name}"

)
        product.delete()

        messages.success(
            request,
            "تم حذف المنتج بنجاح."
        )

        return redirect("products_list")

    return render(
        request,
        "products/delete.html",
        {
            "product": product
        }
    )
    
@login_required
def print_qr(request, product_code):

    product = get_object_or_404(
        Product,
        product_code=product_code
    )

    QRService.get_or_generate(product)

    return render(
        request,
        "products/print.html",
        {
            "product": product
        }
    )    
@login_required
def product_detail(request, product_code):

    product = get_object_or_404(
        Product,
        product_code=product_code
    )

    transactions = product.transactions.all()[:10]

    return render(
        request,
        "products/detail.html",
        {
            "product": product,
            "transactions": transactions,
        }
    )


@login_required
def low_stock_products(request):

    products = Product.objects.filter(
        quantity__lte=F("minimum_stock")
    ).order_by("quantity")

    return render(
        request,
        "products/low_stock.html",
        {
            "products": products
        }
    )    
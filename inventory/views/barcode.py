from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)

from ..models import Product


@login_required
def print_barcode(request, product_code):

    product = get_object_or_404(
        Product,
        product_code=product_code
    )

    
    return render(
        request,
        "products/barcode.html",
        {
            "product": product
        }
    )


@login_required
def print_label(request, product_code):
    """
    A single printable label combining name, code, price, barcode and
    QR — the "one clean label" requested, not a label designer.
    """

    
    product = get_object_or_404(
        Product,
        product_code=product_code
    )

        
    return render(
        request,
        "products/label.html",
        {
            "product": product
        }
    )
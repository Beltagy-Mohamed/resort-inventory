from django.http import HttpResponse
from django.conf import settings
import barcode
from barcode.writer import ImageWriter
from io import BytesIO



def dynamic_barcode(request, product_code):
    try:
        code = barcode.get("code128", product_code, writer=ImageWriter())
        response = HttpResponse(content_type="image/png")
        code.write(response)
        return response
    except Exception as e:
        return HttpResponse(status=404)

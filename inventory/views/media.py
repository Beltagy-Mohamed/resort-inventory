from django.http import HttpResponse
from django.conf import settings
import qrcode
import barcode
from barcode.writer import ImageWriter
from io import BytesIO

def dynamic_qr(request, product_code):
    product_url = settings.SITE_URL + f"/products/{product_code}/"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(product_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response

def dynamic_barcode(request, product_code):
    try:
        code = barcode.get("code128", product_code, writer=ImageWriter())
        response = HttpResponse(content_type="image/png")
        code.write(response)
        return response
    except Exception as e:
        return HttpResponse(status=404)

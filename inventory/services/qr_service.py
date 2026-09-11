import os

import qrcode

from django.conf import settings


class QRService:
    """
    Generates a QR code image for a product that points to its detail
    page. Kept intentionally simple.
    """

    @staticmethod
    def generate(product):
        filename = f"{product.product_code}.png"

        folder = os.path.join(
            settings.MEDIA_ROOT,
            "qrcodes"
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

        filepath = os.path.join(
            folder,
            filename
        )

        product_url = (
            settings.SITE_URL +
            f"/products/{product.product_code}/"
        )

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )

        qr.add_data(product_url)

        qr.make(fit=True)

        img = qr.make_image(
            fill_color="black",
            back_color="white"
        )

        img.save(filepath)

        product.qr_code = f"qrcodes/{filename}"

        product.save(update_fields=["qr_code"])

        return product.qr_code

    @staticmethod
    def get_or_generate(product):
        """
        Returns a usable QR code for this product, generating one first
        if it's missing or the file was lost from disk. Mirrors
        BarcodeService.get_or_generate for consistency. Never
        regenerates a QR code that's already present on disk.
        """
        if product.qr_code and product.qr_code.name:
            existing_path = os.path.join(settings.MEDIA_ROOT, product.qr_code.name)
            if os.path.exists(existing_path):
                return product.qr_code

        QRService.generate(product)
        product.refresh_from_db(fields=["qr_code"])
        return product.qr_code

import os

import barcode
from barcode.writer import ImageWriter

from django.conf import settings


class BarcodeService:
    """
    Generates a Code128 barcode image for a product, named after its
    product_code. Kept intentionally simple — one format, one job.
    """

    @staticmethod
    def generate(product):
        folder = os.path.join(
            settings.MEDIA_ROOT,
            "barcodes"
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

        filename = product.product_code

        filepath = os.path.join(
            folder,
            filename
        )

        code = barcode.get(
            "code128",
            product.product_code,
            writer=ImageWriter()
        )

        code.save(filepath)

        product.barcode = f"barcodes/{filename}.png"

        product.save(update_fields=["barcode"])

        return product.barcode

    @staticmethod
    def get_or_generate(product):
        """
        Returns a usable barcode for this product, generating one first
        if it's missing or if the file was lost from disk (e.g. an old
        product created before BarcodeService existed). Safe to call
        from any view that needs to display/print a barcode — it will
        never raise just because the barcode wasn't made yet, and it
        will never regenerate a barcode that already exists on disk.
        """
        if product.barcode and product.barcode.name:
            existing_path = os.path.join(settings.MEDIA_ROOT, product.barcode.name)
            if os.path.exists(existing_path):
                return product.barcode

        BarcodeService.generate(product)
        product.refresh_from_db(fields=["barcode"])
        return product.barcode

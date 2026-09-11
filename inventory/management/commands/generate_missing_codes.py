from django.core.management.base import BaseCommand

from inventory.models import Product
from inventory.services.barcode_service import BarcodeService
from inventory.services.qr_service import QRService


class Command(BaseCommand):
    """
    One-time / repeatable fix for older products that were created
    before BarcodeService (and possibly QRService) existed, or whose
    generated image files were lost from media/.

    Safe to run multiple times: get_or_generate() only creates a file
    when one is genuinely missing, so it never regenerates or
    overwrites codes that already exist.

    Usage:
        python manage.py generate_missing_codes
    """

    help = "Generate barcode/QR images for any product that is missing one."

    def handle(self, *args, **options):
        products = Product.objects.all()

        barcodes_created = 0
        qrs_created = 0

        for product in products:
            had_barcode = bool(product.barcode)
            had_qr = bool(product.qr_code)

            BarcodeService.get_or_generate(product)
            QRService.get_or_generate(product)

            product.refresh_from_db(fields=["barcode", "qr_code"])

            if not had_barcode and product.barcode:
                barcodes_created += 1
                self.stdout.write(f"  + barcode generated for {product.product_code}")

            if not had_qr and product.qr_code:
                qrs_created += 1
                self.stdout.write(f"  + qr code generated for {product.product_code}")

        self.stdout.write(self.style.SUCCESS(
            f"Done. {barcodes_created} barcode(s) and {qrs_created} QR code(s) "
            f"generated out of {products.count()} product(s)."
        ))

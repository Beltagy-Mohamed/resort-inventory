from django.db import transaction
from django.core.exceptions import ValidationError
from inventory.models import Product, Stock

class InventoryService:
    @staticmethod
    @transaction.atomic
    def process(inventory_transaction):
        """
        Process an inventory transaction and update the product's quantity in the specified warehouse,
        as well as the product's total global quantity.
        """
        # Serialize movements per product so concurrent OUT requests cannot
        # independently read the same available balance.
        product = Product.objects.select_for_update().get(
            pk=inventory_transaction.product_id
        )
        qty = inventory_transaction.quantity
        t_type = inventory_transaction.transaction_type
        warehouse = inventory_transaction.warehouse
        
        if not warehouse:
            raise ValidationError("يجب تحديد المخزن لإتمام الحركة.")

        # Get or create stock record for this warehouse
        stock, created = Stock.objects.select_for_update().get_or_create(
            product=product,
            warehouse=warehouse,
            defaults={'quantity': 0}
        )
        
        # Update stock quantity based on transaction type
        if t_type == 'IN':
            stock.quantity += qty
        elif t_type == 'OUT':
            if stock.quantity < qty:
                raise ValidationError(f"الكمية المتاحة في '{warehouse.name}' لا تكفي لهذه العملية.")
            stock.quantity -= qty
        elif t_type == 'ADJUST':
            # For ADJUST, the 'quantity' field represents the NEW physical count in that specific warehouse.
            stock.quantity = qty
            
        stock.save()
        
        # Save the transaction
        inventory_transaction.product = product
        inventory_transaction.save()
        
        # Update global product quantity (Cache total quantity from all warehouses)
        from django.db.models import Sum
        total_qty = Stock.objects.filter(product=product).aggregate(total=Sum('quantity'))['total']
        product.quantity = total_qty or 0
        product.save()
        
        return product

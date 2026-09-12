from django.db import transaction
from django.core.exceptions import ValidationError

class InventoryService:
    @staticmethod
    @transaction.atomic
    def process(inventory_transaction):
        """
        Process an inventory transaction and update the product's quantity.
        """
        product = inventory_transaction.product
        qty = inventory_transaction.quantity
        t_type = inventory_transaction.transaction_type
        
        # Save the transaction first
        inventory_transaction.save()
        
        # Update product quantity based on transaction type
        if t_type == 'IN':
            product.quantity += qty
        elif t_type == 'OUT':
            if product.quantity < qty:
                raise ValidationError("الكمية المتاحة في المخزن لا تكفي لهذه العملية.")
            product.quantity -= qty
        elif t_type == 'ADJUST':
            # For ADJUST, the 'quantity' field represents the NEW physical count.
            product.quantity = qty
            
        product.save()
        return product

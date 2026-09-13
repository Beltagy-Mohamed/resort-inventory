import os

path = r'g:\client_delivery\inventory\views\transactions.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target = '''    if request.method == "POST":
        # Force the transaction type based on the action parameter to ensure data integrity
        post_data = request.POST.copy()
        post_data['transaction_type'] = action
        form = InventoryTransactionForm(post_data)'''

repl = '''    from ..models import Partner
    
    if request.method == "POST":
        # Force the transaction type based on the action parameter to ensure data integrity
        post_data = request.POST.copy()
        post_data['transaction_type'] = action
        form = InventoryTransactionForm(post_data)
        
        # Enforce partner filtering on POST
        if action == "IN":
            form.fields['partner'].queryset = Partner.objects.filter(partner_type="SUPPLIER")
        elif action == "OUT":
            form.fields['partner'].queryset = Partner.objects.filter(partner_type__in=["CLIENT", "OTHER"])'''

c = c.replace(target, repl)

target2 = '''    else:

        form = InventoryTransactionForm()'''

repl2 = '''    else:
        form = InventoryTransactionForm()
        
        # Enforce partner filtering on GET
        if action == "IN":
            form.fields['partner'].queryset = Partner.objects.filter(partner_type="SUPPLIER")
        elif action == "OUT":
            form.fields['partner'].queryset = Partner.objects.filter(partner_type__in=["CLIENT", "OTHER"])'''

c = c.replace(target2, repl2)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

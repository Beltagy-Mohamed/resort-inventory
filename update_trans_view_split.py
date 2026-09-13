import os

path = r'g:\client_delivery\inventory\views\transactions.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target = '''@login_required
@permission_required("inventory.add_inventorytransaction", raise_exception=True)
def add_transaction(request):

    if request.method == "POST":

        form = InventoryTransactionForm(request.POST)'''

repl = '''import json
from ..models import Product

@login_required
@permission_required("inventory.add_inventorytransaction", raise_exception=True)
def add_transaction(request):
    action = request.GET.get("action", "IN").upper()
    if action not in ["IN", "OUT", "ADJUST"]:
        action = "IN"

    if request.method == "POST":
        # Force the transaction type based on the action parameter to ensure data integrity
        post_data = request.POST.copy()
        post_data['transaction_type'] = action
        form = InventoryTransactionForm(post_data)'''

c = c.replace(target, repl)

target2 = '''    return render(

        request,

        "transactions/add.html",

        {

            "form": form

        }

    )'''

repl2 = '''    
    # Create dictionary mapping product ID to its prices for JS autofill
    products_data = {
        p.id: {
            "cost_price": float(p.cost_price), 
            "selling_price": float(p.selling_price)
        } for p in Product.objects.all()
    }
    
    return render(
        request,
        "transactions/add.html",
        {
            "form": form,
            "action": action,
            "products_data_json": json.dumps(products_data)
        }
    )'''

c = c.replace(target2, repl2)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

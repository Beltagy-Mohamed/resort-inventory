import os

path = r'g:\client_delivery\inventory\views\transactions.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target1 = '''    search = request.GET.get("search", "")

    transaction_type = request.GET.get("type", "")'''

repl1 = '''    search = request.GET.get("search", "")
    transaction_type = request.GET.get("type", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")'''

c = c.replace(target1, repl1)

target2 = '''    if transaction_type:

        transactions = transactions.filter(
            transaction_type=transaction_type
        )'''

repl2 = '''    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
        
    if date_from:
        transactions = transactions.filter(created_at__date__gte=date_from)
        
    if date_to:
        transactions = transactions.filter(created_at__date__lte=date_to)'''

c = c.replace(target2, repl2)

target3 = '''        {

            "page_obj": page_obj,

            "search": search,

            "transaction_type": transaction_type,

        }'''

repl3 = '''        {
            "page_obj": page_obj,
            "search": search,
            "transaction_type": transaction_type,
            "date_from": date_from,
            "date_to": date_to,
        }'''

c = c.replace(target3, repl3)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

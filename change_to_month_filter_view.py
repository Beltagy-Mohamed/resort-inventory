import os
import re

path = r'g:\client_delivery\inventory\views\transactions.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Replace date_from/date_to logic with month_filter
c = c.replace('date_from = request.GET.get("date_from", "")', 'month_filter = request.GET.get("month_filter", "")')
c = c.replace('    date_to = request.GET.get("date_to", "")\n', '')

filter_target = '''    if date_from:
        transactions = transactions.filter(created_at__date__gte=date_from)
        
    if date_to:
        transactions = transactions.filter(created_at__date__lte=date_to)'''

filter_repl = '''    if month_filter:
        try:
            year, month = month_filter.split("-")
            transactions = transactions.filter(created_at__year=year, created_at__month=month)
        except ValueError:
            pass'''

c = c.replace(filter_target, filter_repl)

ctx_target = '''            "transaction_type": transaction_type,
            "date_from": date_from,
            "date_to": date_to,
        }'''

ctx_repl = '''            "transaction_type": transaction_type,
            "month_filter": month_filter,
        }'''

c = c.replace(ctx_target, ctx_repl)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

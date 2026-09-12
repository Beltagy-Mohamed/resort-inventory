import os

path = r'g:\client_delivery\inventory\views\analytics.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Fix partner_statement_report
target = '''    if partner_id:
        transactions = InventoryTransaction.objects.select_related("product", "partner", "warehouse").filter(partner_id=partner_id)
        
        year_filter = request.GET.get("year_filter", "")'''

repl = '''    year_filter = request.GET.get("year_filter", "")
    
    if partner_id:
        transactions = InventoryTransaction.objects.select_related("product", "partner", "warehouse").filter(partner_id=partner_id)'''

c = c.replace(target, repl)

# 2. Fix profit_report context
target_profit = '''    context = {
        "transactions": transactions,
        "month_filter": month_filter,
        "total_profit": total_profit,
        "total_sales": total_sales,
        "total_cost": total_cost,
    }'''

repl_profit = '''    context = {
        "transactions": transactions,
        "month_filter": int(month_filter) if month_filter.isdigit() else "",
        "year_filter": int(year_filter) if year_filter.isdigit() else "",
        "months": [(1, "يناير"), (2, "فبراير"), (3, "مارس"), (4, "أبريل"), (5, "مايو"), (6, "يونيو"), (7, "يوليو"), (8, "أغسطس"), (9, "سبتمبر"), (10, "أكتوبر"), (11, "نوفمبر"), (12, "ديسمبر")],
        "years": range(2025, 2035),
        "total_profit": total_profit,
        "total_sales": total_sales,
        "total_cost": total_cost,
    }'''

c = c.replace(target_profit, repl_profit)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

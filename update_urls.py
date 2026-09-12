import os

path = r'g:\client_delivery\inventory\urls.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

new_urls = '''
path(
    "reports/warehouse-stock/",
    views.warehouse_stock_report,
    name="warehouse_stock_report",
),
path(
    "reports/partner-statement/",
    views.partner_statement_report,
    name="partner_statement_report",
),
path(
    "reports/profit/",
    views.profit_report,
    name="profit_report",
),
'''

c = c.replace('path(\n    "reports/inventory/",', new_urls + 'path(\n    "reports/inventory/",')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

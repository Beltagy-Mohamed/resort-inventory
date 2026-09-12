import os
import datetime

MONTHS = [
    (1, "يناير"), (2, "فبراير"), (3, "مارس"), (4, "أبريل"),
    (5, "مايو"), (6, "يونيو"), (7, "يوليو"), (8, "أغسطس"),
    (9, "سبتمبر"), (10, "أكتوبر"), (11, "نوفمبر"), (12, "ديسمبر")
]

# Update transactions.py
path_trans = r'g:\client_delivery\inventory\views\transactions.py'
with open(path_trans, 'r', encoding='utf-8') as f:
    c = f.read()

target = '''    if month_filter:
        try:
            year, month = month_filter.split("-")
            transactions = transactions.filter(created_at__year=year, created_at__month=month)
        except ValueError:
            pass'''

repl = '''    year_filter = request.GET.get("year_filter", "")
    
    if month_filter and month_filter.isdigit():
        transactions = transactions.filter(created_at__month=int(month_filter))
    
    if year_filter and year_filter.isdigit():
        transactions = transactions.filter(created_at__year=int(year_filter))'''

c = c.replace(target, repl)

target_ctx = '''            "month_filter": month_filter,
        }'''
        
repl_ctx = '''            "month_filter": int(month_filter) if month_filter.isdigit() else "",
            "year_filter": int(year_filter) if year_filter.isdigit() else "",
            "months": [(1, "يناير"), (2, "فبراير"), (3, "مارس"), (4, "أبريل"), (5, "مايو"), (6, "يونيو"), (7, "يوليو"), (8, "أغسطس"), (9, "سبتمبر"), (10, "أكتوبر"), (11, "نوفمبر"), (12, "ديسمبر")],
            "years": range(2025, 2035),
        }'''
        
c = c.replace(target_ctx, repl_ctx)

with open(path_trans, 'w', encoding='utf-8') as f:
    f.write(c)


# Update analytics.py
path_analytics = r'g:\client_delivery\inventory\views\analytics.py'
with open(path_analytics, 'r', encoding='utf-8') as f:
    c = f.read()

target2 = '''        if month_filter:
            try:
                year, month = month_filter.split("-")
                transactions = transactions.filter(created_at__year=year, created_at__month=month)
            except ValueError:
                pass'''
                
repl2 = '''        year_filter = request.GET.get("year_filter", "")
        if month_filter and month_filter.isdigit():
            transactions = transactions.filter(created_at__month=int(month_filter))
        if year_filter and year_filter.isdigit():
            transactions = transactions.filter(created_at__year=int(year_filter))'''

c = c.replace(target2, repl2)

target3 = '''    if month_filter:
        try:
            year, month = month_filter.split("-")
            transactions = transactions.filter(created_at__year=year, created_at__month=month)
        except ValueError:
            pass'''
            
repl3 = '''    year_filter = request.GET.get("year_filter", "")
    if month_filter and month_filter.isdigit():
        transactions = transactions.filter(created_at__month=int(month_filter))
    if year_filter and year_filter.isdigit():
        transactions = transactions.filter(created_at__year=int(year_filter))'''
        
c = c.replace(target3, repl3)

target_ctx2 = '''        "month_filter": month_filter,
    }'''
    
repl_ctx2 = '''        "month_filter": int(month_filter) if month_filter.isdigit() else "",
        "year_filter": int(year_filter) if year_filter.isdigit() else "",
        "months": [(1, "يناير"), (2, "فبراير"), (3, "مارس"), (4, "أبريل"), (5, "مايو"), (6, "يونيو"), (7, "يوليو"), (8, "أغسطس"), (9, "سبتمبر"), (10, "أكتوبر"), (11, "نوفمبر"), (12, "ديسمبر")],
        "years": range(2025, 2035),
    }'''

c = c.replace(target_ctx2, repl_ctx2)

with open(path_analytics, 'w', encoding='utf-8') as f:
    f.write(c)

# HTML templates updates
# 1. transactions/list.html
path_html = r'g:\client_delivery\templates\transactions\list.html'
with open(path_html, 'r', encoding='utf-8') as f:
    html = f.read()

target_html = '''<input type="month" name="month_filter" value="{{ month_filter }}" title="{% trans 'Select Month' %}" style="min-width: 170px;">'''

repl_html = '''<select name="month_filter" class="form-control" style="min-width: 120px;">
            <option value="">-- الشهر --</option>
            {% for m_id, m_name in months %}
            <option value="{{ m_id }}" {% if month_filter == m_id %}selected{% endif %}>{{ m_name }}</option>
            {% endfor %}
        </select>
        <select name="year_filter" class="form-control" style="min-width: 100px;">
            <option value="">-- السنة --</option>
            {% for y in years %}
            <option value="{{ y }}" {% if year_filter == y %}selected{% endif %}>{{ y }}</option>
            {% endfor %}
        </select>'''

html = html.replace(target_html, repl_html)
with open(path_html, 'w', encoding='utf-8') as f:
    f.write(html)

# 2. partner_statement.html
path_html = r'g:\client_delivery\templates\reports\partner_statement.html'
with open(path_html, 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('''<input type="month" name="month_filter" value="{{ month_filter }}" class="form-control" style="min-width: 170px;">''', repl_html)
with open(path_html, 'w', encoding='utf-8') as f:
    f.write(html)

# 3. profit.html
path_html = r'g:\client_delivery\templates\reports\profit.html'
with open(path_html, 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('''<input type="month" name="month_filter" value="{{ month_filter }}" class="form-control" style="min-width: 170px;">''', repl_html)
with open(path_html, 'w', encoding='utf-8') as f:
    f.write(html)

import re

path_leadership = r'E:\خاص مشروع\client_delivery\inventory\views\leadership.py'
with open(path_leadership, 'r', encoding='utf-8') as f:
    c = f.read()

# Add inline export to leadership_items_list right before paginator
export_block = '''
    if request.GET.get("export") == "xlsx":
        import openpyxl
        from django.http import HttpResponse
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "المقرات والقيادات"
        
        headers = [
            "الكود",
            "اسم الصنف",
            "التنميط",
            "ما تم توريده",
            "المتبقي الحالة",
            "اسم الشركة",
        ]
        ws.append(headers)
        
        for p in products:
            row = [
                p.barcode or "",
                p.name,
                p.target_quantity,
                getattr(p, 'total_supplied', 0),
                getattr(p, 'remaining_target', 0),
                getattr(p, 'latest_supplier', "") or "",
            ]
            ws.append(row)
            
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="leadership_items.xlsx"'
        wb.save(response)
        return response

    paginator = Paginator(products, 12)'''

c = re.sub(r'    paginator = Paginator\(products, 12\)', export_block, c)

with open(path_leadership, 'w', encoding='utf-8') as f:
    f.write(c)

# Now, update templates to use HTML5 form="search-form"
path_products_tpl = r'E:\خاص مشروع\client_delivery\templates\products\list.html'
path_leadership_tpl = r'E:\خاص مشروع\client_delivery\templates\leadership\list.html'

for path in [path_products_tpl, path_leadership_tpl]:
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    html = html.replace('<form method="get">', '<form method="get" id="search-form">')
    
    # products list HTML replacement
    if path == path_products_tpl:
        old_export1 = '''<a href="{% url 'leadership_items_export' %}" class="btn-secondary" style="margin-inline-end: 10px;">
                <i class="bi bi-file-earmark-excel"></i> تصدير Excel
            </a>'''
        new_export1 = '''<button type="submit" form="search-form" name="export" value="xlsx" class="btn-secondary" style="margin-inline-end: 10px;">
                <i class="bi bi-file-earmark-excel"></i> تصدير Excel
            </button>'''
        
        old_export2 = '''<a href="?search={{ search }}&category={{ category_id }}&color={{ color_id }}&size={{ size_id }}&status={{ status }}&export=xlsx" class="btn-secondary" style="margin-inline-end: 10px;">
                <i class="bi bi-file-earmark-excel"></i> تصدير Excel
            </a>'''
        new_export2 = '''<button type="submit" form="search-form" name="export" value="xlsx" class="btn-secondary" style="margin-inline-end: 10px;">
                <i class="bi bi-file-earmark-excel"></i> تصدير Excel
            </button>'''
        
        html = html.replace(old_export1, new_export1).replace(old_export2, new_export2)
    
    # leadership list HTML replacement
    elif path == path_leadership_tpl:
        old_export3 = '''<a href="{% url 'leadership_items_export' %}" class="btn-secondary" style="margin-inline-end: 10px;">
                <i class="bi bi-file-earmark-excel"></i> تصدير Excel
            </a>'''
        new_export3 = '''<button type="submit" form="search-form" name="export" value="xlsx" class="btn-secondary" style="margin-inline-end: 10px;">
                <i class="bi bi-file-earmark-excel"></i> تصدير Excel
            </button>'''
        html = html.replace(old_export3, new_export3)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

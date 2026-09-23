import re

paths = [
    r'E:\خاص مشروع\client_delivery\inventory\views\products.py',
    r'E:\خاص مشروع\client_delivery\inventory\views\leadership.py'
]

for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    bad_export = '''        headers = [
            "الكود",
            "اسم المنتج",
            "الفئة",
            "اللون",
            "المقاس",
            "سعر التكلفة",
            "سعر البيع",
            "ما تم توريده",
            "المتبقي (الكمية)",
            "الحد الأدنى",
        ]'''
        
    good_export = '''        headers = [
            "الكود",
            "اسم الصنف",
            "التنميط",
            "ما تم توريده",
            "المتبقي الحالة",
            "اسم الشركة",
        ]'''
    
    bad_row = '''            row = [
                p.barcode or "",
                p.name,
                p.category.name if p.category else "",
                p.color.name if p.color else "",
                p.size.name if p.size else "",
                float(p.cost_price),
                float(p.selling_price),
                getattr(p, 'total_supplied', 0),
                getattr(p, 'display_quantity', p.quantity),
                p.minimum_stock,
            ]'''
            
    good_row = '''            row = [
                p.barcode or "",
                p.name,
                p.target_quantity,
                getattr(p, 'total_supplied', 0),
                getattr(p, 'remaining_target', 0),
                getattr(p, 'latest_supplier', "") or "",
            ]'''

    c = c.replace(bad_export, good_export).replace(bad_row, good_row)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

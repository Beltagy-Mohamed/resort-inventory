paths = [
    r'E:\خاص مشروع\client_delivery\inventory\views\products.py',
    r'E:\خاص مشروع\client_delivery\inventory\views\leadership.py'
]
for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace('"المتبقي الحالة",', '"المتبقي",\n            "الحالة",')
    
    bad_row = '''                getattr(p, 'remaining_target', 0),
                getattr(p, 'latest_supplier', "") or "",'''
                
    good_row = '''                getattr(p, 'remaining_target', 0),
                "مكتمل" if getattr(p, 'remaining_target', 0) <= 0 else ("لم يورد" if getattr(p, 'total_supplied', 0) == 0 else "جاري التوريد"),
                getattr(p, 'latest_supplier', "") or "",'''
    
    c = c.replace(bad_row, good_row)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

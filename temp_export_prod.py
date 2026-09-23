import re
path = r'E:\خاص مشروع\client_delivery\inventory\views\products.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

bad_headers = r'        headers = \["الكود", "اسم الصنف", "التصنيف", "اللون", "المقاس", "سعر التكلفة", "سعر البيع", "ما تم توريده", "المتبقي \(الكمية\)"\]'
good_headers = '''        headers = [
            "الكود",
            "اسم الصنف",
            "التنميط",
            "ما تم توريده",
            "المتبقي",
            "الحالة",
            "اسم الشركة",
        ]'''

bad_row = r'''            ws\.append\(\[
                p\.barcode or "-",
                p\.name,
                p\.category\.name if p\.category else "-",
                p\.color\.name if p\.color else "-",
                p\.size\.name if p\.size else "-",
                p\.cost_price,
                p\.selling_price,
                p\.total_supplied,
                p\.quantity
            \]\)'''

good_row = '''            ws.append([
                p.barcode or "",
                p.name,
                p.target_quantity,
                getattr(p, 'total_supplied', 0),
                getattr(p, 'remaining_target', 0),
                "مكتمل" if getattr(p, 'remaining_target', 0) <= 0 else ("لم يورد" if getattr(p, 'total_supplied', 0) == 0 else "جاري التوريد"),
                getattr(p, 'latest_supplier', "") or "",
            ])'''

c = re.sub(bad_headers, good_headers, c)
c = re.sub(bad_row, good_row, c)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

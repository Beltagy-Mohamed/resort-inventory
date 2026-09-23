import os

paths = [
    r'E:\خاص مشروع\client_delivery\inventory\views\products.py',
    r'E:\خاص مشروع\client_delivery\inventory\views\leadership.py'
]

for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # Replace headers
    c = c.replace('["الكود", "اسم الصنف", "الفئة", "اللون", "المقاس", "سعر التكلفة", "سعر البيع", "الكمية الحالية"]',
                  '["الكود", "اسم الصنف", "التصنيف", "اللون", "المقاس", "سعر التكلفة", "سعر البيع", "ما تم توريده", "المتبقي (الكمية)"]')
    
    # Replace row append
    c = c.replace('p.selling_price,\n                p.quantity',
                  'p.selling_price,\n                p.total_supplied,\n                p.quantity')
                  
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

print("Updated export in views")

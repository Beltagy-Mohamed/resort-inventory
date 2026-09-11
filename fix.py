import codecs

filepath = r'g:\client_delivery\inventory\views\reports.py'
with codecs.open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Replace corrupted headers
content = content.replace(\"['^ \".ŝ', '\".', '\"S?', '\"', '\".S', ' \"%', '\"\"', '\"'S. \".\"S']\", \"['كود المنتج', 'الاسم', 'التصنيف', 'السعر', 'الكمية', 'الحد الأدنى', 'الحالة', 'القيمة الإجمالية']\")

content = content.replace(\"'^ S?'\", \"'بدون تصنيف'\")

with codecs.open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed!')

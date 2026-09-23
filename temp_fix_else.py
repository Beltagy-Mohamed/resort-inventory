path = r'E:\خاص مشروع\client_delivery\inventory\views\products.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Delete lines 49 to 59 inclusive
del lines[49:60]

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

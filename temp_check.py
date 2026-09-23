with open(r'E:\خاص مشروع\client_delivery\inventory\views\leadership.py', 'r', encoding='utf-8') as f:
    c = f.read()
    import re
    m = re.search(r'def leadership_items_list.*?return render.*?"(.*?)"', c, re.DOTALL)
    print(m.group(1) if m else 'Not found')

import os

path = r'g:\client_delivery\static\css\products.css'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

target = '''.search-bar {
    display: flex;
    gap: 10px;
    margin: 18px 0;
    flex-wrap: wrap;
}'''

repl = '''.search-bar {
    margin: 18px 0;
}
.search-bar form {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    width: 100%;
}'''

c = c.replace(target, repl)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

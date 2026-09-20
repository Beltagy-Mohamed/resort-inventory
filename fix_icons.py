import io
import os

files = [
    "templates/management/partners_list.html",
    "templates/management/warehouses_list.html",
    "templates/products/list.html",
    "templates/settings/import_excel.html",
    "templates/users/list.html"
]

for filepath in files:
    path = os.path.join("e:/خاص مشروع/client_delivery", filepath)
    with io.open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = content.replace("fas fa-edit", "bi bi-pencil")
    content = content.replace("fas fa-trash", "bi bi-trash")
    content = content.replace("fas fa-filter", "bi bi-funnel")
    content = content.replace("fas fa-times", "bi bi-x-lg")
    content = content.replace("fas fa-lock", "bi bi-lock-fill")
    content = content.replace("fas fa-file-excel", "bi bi-file-earmark-excel")
    content = content.replace("fas fa-search", "bi bi-search")
    content = content.replace("fas fa-plus", "bi bi-plus")
    
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(content)

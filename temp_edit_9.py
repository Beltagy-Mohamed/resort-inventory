import os
import re

directory = r'E:\خاص مشروع\client_delivery'
replace_map = {
    'Ordinance': 'Ordinance',
    'Ordinance': 'Ordinance',
    'Ordinance': 'Ordinance'
}

for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith(('.html', '.py', '.txt', '.md', '.json', '.env.example')):
            filepath = os.path.join(root, file)
            # Skip venv, git, node_modules etc
            if 'venv' in filepath or '.git' in filepath or 'offline_packages' in filepath:
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    c = f.read()
                    
                modified = False
                for k, v in replace_map.items():
                    if k in c:
                        c = c.replace(k, v)
                        modified = True
                        
                if modified:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(c)
                    print(f"Updated {filepath}")
            except Exception as e:
                pass

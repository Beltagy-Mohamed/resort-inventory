import re
with open('chat/models.py', 'r', encoding='utf-8') as f: content = f.read()
content = re.sub(r'\s*image = models\.TextField\(blank=True, null=True\).*?\n', '\n', content)
content = re.sub(r'\s*file = models\.TextField\(blank=True, null=True\).*?\n', '\n', content)
content = re.sub(r'\s*file_name = models\.CharField\(max_length=255, blank=True\)\n', '\n', content)
content = re.sub(r'\s*''image_url'': self\.image,\n', '\n', content)
content = re.sub(r'\s*''file_url'': self\.file,\n', '\n', content)
content = re.sub(r'\s*''file_name'': self\.file_name,\n', '\n', content)
with open('chat/models.py', 'w', encoding='utf-8') as f: f.write(content)

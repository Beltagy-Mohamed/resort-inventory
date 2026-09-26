import re
with open('templates/chat/room.html', 'r', encoding='utf-8') as f: content = f.read()
content = re.sub(r'\s*const imgHtml.*?;', '', content)
content = re.sub(r'\s*const fileHtml.*?;', '', content)
content = content.replace('', '')
with open('templates/chat/room.html', 'w', encoding='utf-8') as f: f.write(content)

import re
with open('templates/chat/room.html', 'r', encoding='utf-8') as f: content = f.read()
content = re.sub(r'const imgHtml = m\.image_url \? .*?;', '', content)
content = re.sub(r'const fileHtml = m\.file_url \? .*?;', '', content)
content = re.sub(r'\$\{imgHtml\}\$\{fileHtml\}', '', content)
content = re.sub(r'function toBase64.*?\}\s*\}\s*async function sendMessage\(\) \{.*?clearImage\(\);', 'async function sendMessage() { const input = document.getElementById('chatInput'); const content = input.value.trim(); if (!content) return; input.value = ''; input.style.height = 'auto'; const body = JSON.stringify({ content }); const headers = { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN };', content, flags=re.DOTALL)
with open('templates/chat/room.html', 'w', encoding='utf-8') as f: f.write(content)

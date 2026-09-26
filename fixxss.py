import re
with open('templates/chat/room.html', 'r', encoding='utf-8') as f: content = f.read()
content = re.sub(r'wrap\.innerHTML =', 'wrap.insertAdjacentHTML('beforeend', ', content)
content = re.sub(r'sub\.innerHTML = (.*?;)', r'sub.insertAdjacentHTML('beforeend', \1); sub.replaceChildren(); sub.insertAdjacentHTML('beforeend', \1)', content)
# wait, replacing innerHTML with replaceChildren is better for emptying
with open('templates/chat/room.html', 'w', encoding='utf-8') as f: f.write(content)

import re
with open('templates/chat/room.html', 'r', encoding='utf-8') as f:
    c = f.read()
c = re.sub(r'sub\.innerHTML = ''(<span[^>]*>[^<]*<\/span>)'';', r'sub.replaceChildren(); sub.insertAdjacentHTML("beforeend", "\1");', c)
with open('templates/chat/room.html', 'w', encoding='utf-8') as f:
    f.write(c)

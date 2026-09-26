import re
with open('templates/chat/home.html', 'r', encoding='utf-8') as f:
    c = f.read()
c = re.sub(r'list\.innerHTML = ''(<li[^>]*>.*?<\/li>)'';', r'list.replaceChildren(); list.insertAdjacentHTML("beforeend", "\1");', c, flags=re.DOTALL)
c = re.sub(r'list\.innerHTML = data\.users\.map\(u => (.*?)\)\.join\(''''\);', r'list.replaceChildren(); list.insertAdjacentHTML("beforeend", data.users.map(u => \1).join(""));', c, flags=re.DOTALL)
with open('templates/chat/home.html', 'w', encoding='utf-8') as f:
    f.write(c)

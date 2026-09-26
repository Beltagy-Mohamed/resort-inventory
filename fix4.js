const fs = require('fs');
let c = fs.readFileSync('templates/chat/home.html', 'utf8');
c = c.replace(/list\.innerHTML = '([^']+)';/g, "list.replaceChildren(); list.insertAdjacentHTML('beforeend', '');");
c = c.replace(/list\.innerHTML = data\.users\.map\([\s\S]*?\}\);/, (match) => {
    return match.replace("list.innerHTML = ", "list.replaceChildren(); list.insertAdjacentHTML('beforeend', ").replace(").join('');", ").join(''));");
});
fs.writeFileSync('templates/chat/home.html', c);

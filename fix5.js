const fs = require('fs');
let c = fs.readFileSync('templates/layout/base.html', 'utf8');
c = c.replace(/\.innerHTML = '([^']+)';/g, ".replaceChildren(); .insertAdjacentHTML('beforeend', '');".replace(/\$\$/g, '')); // wait, I can't easily backref the object.
// I will replace specific lines
c = c.replace(/document\.getElementById\('fcw-rooms'\)\.innerHTML = '([^']+)';/, "const el = document.getElementById('fcw-rooms'); el.replaceChildren(); el.insertAdjacentHTML('beforeend', '');");
c = c.replace(/container\.innerHTML = '([^']+)';/, "container.replaceChildren(); container.insertAdjacentHTML('beforeend', '');");
c = c.replace(/container\.innerHTML = rooms\.map\([\s\S]*?\}\)\.join\(''\);/, (match) => {
    return match.replace("container.innerHTML = ", "container.replaceChildren(); container.insertAdjacentHTML('beforeend', ").replace(").join('');", ").join(''));");
});
c = c.replace(/document\.getElementById\('fcw-msgs-area'\)\.innerHTML = '';/, "document.getElementById('fcw-msgs-area').replaceChildren();");
c = c.replace(/backBtn\.innerHTML = '([^']+)';/, "backBtn.replaceChildren(); backBtn.insertAdjacentHTML('beforeend', '');");
c = c.replace(/wrap\.innerHTML = ([\s\S]*?);/, "wrap.insertAdjacentHTML('beforeend', $1);");
fs.writeFileSync('templates/layout/base.html', c);

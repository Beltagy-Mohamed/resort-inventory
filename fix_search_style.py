import os
import re

path = r'g:\client_delivery\static\css\base.css'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Replace the gold styling for topbar-search
target = '''html[data-theme="dark"] .topbar-search input,
html[data-theme="dark"] .topbar-search-btn {
    background: var(--resort-gold);
    border-color: rgba(255, 255, 255, .34);
    color: #203638;
    box-shadow: 0 6px 16px rgba(0, 0, 0, .16), inset 0 1px 0 rgba(255, 255, 255, .28);
}'''

replacement = '''html[data-theme="dark"] .topbar-search input,
html[data-theme="dark"] .topbar-search-btn {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.05);
    color: #b0b8c4;
    box-shadow: none;
}
html[data-theme="dark"] .topbar-search input:focus {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.15);
    color: #fff;
}
html[data-theme="dark"] .topbar-search-btn:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
    border-color: rgba(255, 255, 255, 0.15);
}'''

c = c.replace(target, replacement)

# Let's also check if there is any other block turning it gold
c = c.replace(
    '''html[data-theme="dark"] .language-toggle:hover,
html[data-theme="dark"] .theme-toggle:hover,
html[data-theme="dark"] .notif-bell:hover,
html[data-theme="dark"] .logout-btn:hover,
html[data-theme="dark"] .topbar-search-btn:hover {
    background: #d1ad80;
    border-color: #e2c49b;
    color: #203638;
}''',
    '''html[data-theme="dark"] .language-toggle:hover,
html[data-theme="dark"] .theme-toggle:hover,
html[data-theme="dark"] .notif-bell:hover,
html[data-theme="dark"] .logout-btn:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.1);
    color: #fff;
}'''
)

# Fix light mode as well (make it look like the language button)
light_target = '''
.topbar-search input {
    padding: 11px 16px;
    border-radius: 999px;
}
'''
light_repl = '''
.topbar-search input {
    padding: 11px 16px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.42);
    border: 1px solid var(--glass-border);
    color: var(--text);
}
.topbar-search-btn {
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.42);
    border: 1px solid var(--glass-border);
    color: var(--text);
}
.topbar-search-btn:hover {
    background: rgba(255, 255, 255, 0.7);
}
'''
if 'background: rgba(255, 255, 255, 0.42)' not in c:
    c = c.replace(light_target, light_repl)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

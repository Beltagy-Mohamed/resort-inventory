import os

path = r'g:\client_delivery\static\css\base.css'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Make sidebar full height
c = c.replace(
    '.sidebar {\n    margin-top: 16px;\n    border-radius: 0 24px 24px 0;\n    height: calc(100vh - 32px);\n}',
    '.sidebar {\n    margin-top: 0;\n    border-radius: 0;\n    height: 100vh;\n}'
)
c = c.replace(
    '[dir="rtl"] .sidebar {\n    border-radius: 24px 0 0 24px;\n}',
    '[dir="rtl"] .sidebar {\n    border-radius: 0;\n}'
)

# And remove margin/radius in media query if any
c = c.replace(
    '    .sidebar {\n        border: 1px solid rgba(255, 255, 255, .2);\n        border-inline-end: 2px solid rgba(255, 255, 255, .34);\n        border-inline-start: 0;\n        border-radius: 28px 0 0 28px;\n        box-shadow: 8px 0 26px rgba(41, 64, 67, .16);\n',
    '    .sidebar {\n        border-inline-end: 1px solid rgba(0, 0, 0, .1);\n        border-radius: 0;\n        box-shadow: 2px 0 10px rgba(0, 0, 0, .05);\n'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

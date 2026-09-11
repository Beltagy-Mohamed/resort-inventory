import io
import re
with io.open('g:/client_delivery/inventory/views/reports.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
content = re.sub(r"headers = \[.*?\]", "headers = ['\u0643\u0648\u062f \u0627\u0644\u0645\u0646\u062a\u062c', '\u0627\u0644\u0627\u0633\u0645', '\u0627\u0644\u062a\u0635\u0646\u064a\u0641', '\u0627\u0644\u0633\u0639\u0631', '\u0627\u0644\u0643\u0645\u064a\u0629', '\u0627\u062d\u062f \u0627\u0644\u0623\u062f\u0646\u0649', '\u0627\u0644\u062d\u0627\u0644\u0629', '\u0627\u0644\u0642\u064a\u0645\u0629 \u0627\u0644\u0625\u062c\u0645\u0627\u0644\u064a\u0629']", content)
content = re.sub(r"else: '.*?'", "else: '\u0628\u062f\u0648\u0646 \u062a\u0635\u0646\u064a\u0641'", content)
with io.open('g:/client_delivery/inventory/views/reports.py', 'w', encoding='utf-8') as f:
    f.write(content)

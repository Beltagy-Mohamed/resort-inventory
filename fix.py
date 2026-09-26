import re
with open('templates/chat/room.html', 'r', encoding='utf-8') as f: content = f.read()
content = re.sub(r'<div class="chat-input-wrap">.*?</div>\s*</div>\s*\{% endblock %\}', '<div class="chat-input-wrap">\n        <textarea\n            class="chat-textarea"\n            id="chatInput"\n            placeholder="???? ?????..."\n            rows="1"\n            dir="auto"\n        ></textarea>\n        <button class="send-btn" id="sendBtn" onclick="sendMessage()">\n            <i class="bi bi-send-fill"></i>\n        </button>\n    </div>\n</div>\n{% endblock %}', content, flags=re.DOTALL)
with open('templates/chat/room.html', 'w', encoding='utf-8') as f: f.write(content)

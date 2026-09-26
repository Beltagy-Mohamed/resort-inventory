
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const ROOM_ID = 1;
const CURRENT_USER_ID = 1;
const CSRF_TOKEN = getCookie('csrftoken') || "1";
const API_URL = `/chat/api/room/${ROOM_ID}/messages/`;
const IS_GROUP = "1" === "GROUP";

let lastTimestamp = "1";
let polling = null;
let notifPermission = false;
let lastSenderId = null;
let selectedImageFile = null; let selectedFile = null;

function previewFile() { const fi = document.getElementById("fileUpload"); if(fi.files && fi.files[0]) { selectedFile = fi.files[0]; selectedImageFile = null; document.getElementById("imageUpload").value = ""; document.getElementById("imagePreview").style.display = "none"; document.getElementById("filePreviewName").style.display = "inline"; document.getElementById("filePreviewName").innerText = selectedFile.name; document.getElementById("imagePreviewContainer").style.display = "block"; document.getElementById("chatInput").focus(); } } function previewImage() {
    const fileInput = document.getElementById('imageUpload');
    if (fileInput.files && fileInput.files[0]) {
        selectedImageFile = fileInput.files[0]; selectedFile = null; document.getElementById("fileUpload").value = "";
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById("imagePreview").src = e.target.result; document.getElementById("imagePreview").style.display = "inline"; document.getElementById("filePreviewName").style.display = "none";
            document.getElementById('imagePreviewContainer').style.display = 'block';
            document.getElementById('chatInput').focus();
        };
        reader.readAsDataURL(selectedImageFile);
    }
}
function clearImage() { selectedFile = null; document.getElementById("fileUpload").value = "";
    selectedImageFile = null; document.getElementById("imageUpload").value = "";
    document.getElementById('imageUpload').value = '';
    document.getElementById('imagePreviewContainer').style.display = 'none';
}

// ===== Scroll =====
function scrollBottom(smooth = true) {
    const area = document.getElementById('messagesArea');
    area.scrollTo({ top: area.scrollHeight, behavior: smooth ? 'smooth' : 'instant' });
}
scrollBottom(false);

// ===== Notifications =====
async function requestNotif(interactive = false) {
    if (!('Notification' in window)) return;
    
    if (Notification.permission === 'granted') {
        notifPermission = true;
        document.getElementById('enableNotifBtn').style.display = 'none';
    } else if (Notification.permission !== 'denied') {
        if (interactive) {
            if(window.playNotifSound) window.playNotifSound(); const p = await Notification.requestPermission();
            notifPermission = p === 'granted';
            if (notifPermission) document.getElementById('enableNotifBtn').style.display = 'none';
        } else {
            document.getElementById('enableNotifBtn').style.display = 'block';
        }
    }
}
requestNotif(false);

function showNotif(senderName, content) { if(window.playNotifSound) window.playNotifSound();
    if (!notifPermission || document.visibilityState === 'visible') return;
    new Notification(`💬 ${senderName}`, {
        body: content.length > 80 ? content.slice(0, 80) + '…' : content,
        icon: '/static/pwa/icons/icon-192.png',
    });
}

window.downloadDataUri = function(e, uri, name) { e.preventDefault(); try { const arr = uri.split(","); const mime = arr[0].match(/:(.*?);/)[1]; const bstr = atob(arr[1]); let n = bstr.length; const u8arr = new Uint8Array(n); while(n--){ u8arr[n] = bstr.charCodeAt(n); } const blob = new Blob([u8arr], {type:mime}); const blobUrl = URL.createObjectURL(blob); const a = document.createElement("a"); a.href = blobUrl; a.download = name; document.body.appendChild(a); a.click(); document.body.removeChild(a); setTimeout(() => URL.revokeObjectURL(blobUrl), 100); } catch(err) { window.open(uri, "_blank"); } }; // ===== Append message =====
function appendMessage(m) {
    const area = document.getElementById('messagesArea');
    const empty = area.querySelector('.chat-empty');
    if (empty) empty.remove();

    const isMine = m.is_mine || (m.sender_id === CURRENT_USER_ID);
    const isNewSender = (m.sender_id !== lastSenderId);
    lastSenderId = m.sender_id;

    const wrap = document.createElement('div');
    wrap.className = `msg-row ${isMine ? "mine" : "theirs"}${isNewSender ? " first-in-group" : ""}`; wrap.setAttribute("data-ts", m.created_at_full);
    wrap.id = `msg-${m.id}`;

    const avatarHtml = !isMine ? `
        <div class="msg-avatar-small${isNewSender ? '' : ' hidden'}" style="background:${m.avatar_color};">
            ${m.sender_name[0].toUpperCase()}
        </div>` : '';

    const nameHtml = (!isMine && isNewSender) ? `
        <div class="msg-sender-name" style="color:${m.avatar_color};">${m.sender_name}</div>
    ` : '';

    const checkHtml = isMine ? `
        <i class="bi ${m.is_read ? 'bi-check2-all' : 'bi-check2'}"
           style="font-size:.85rem;color:${m.is_read ? '#4FC3F7' : '#999'};"></i>` : '';

    wrap.innerHTML = `
        ${avatarHtml}
        <div class="msg-bubble-wrap">
            ${nameHtml}
            <div class="msg-bubble">${escapeHtml(m.content)}</div>
            <div class="msg-time-row">
                <span class="msg-time">${m.created_at}</span>
                ${checkHtml}
            </div>
        </div>
    `;
    area.appendChild(wrap);

    const nearBottom = area.scrollTop + area.clientHeight >= area.scrollHeight - 150;
    if (nearBottom || isMine) scrollBottom(true);
}

function escapeHtml(t) {
    return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ===== Poll =====
async function pollMessages() {
    if (!lastTimestamp) return;
    try {
        const resp = await fetch(`${API_URL}?after=${encodeURIComponent(lastTimestamp)}`);
        if (!resp.ok) return;
        const data = await resp.json();
        (data.messages || []).forEach(m => {
            if (!document.getElementById(`msg-${m.id}`)) {
                appendMessage(m);
                if (!m.is_mine) showNotif(m.sender_name, m.content);
            } else if (m.is_mine && m.is_read) {
                // Update checkmarks to blue if read
                const msgEl = document.getElementById(`msg-${m.id}`);
                const checks = msgEl.querySelector('.bi-check2');
                if (checks) {
                    checks.classList.remove('bi-check2');
                    checks.classList.add('bi-check2-all');
                    checks.style.color = '#4FC3F7';
                }
            }
            lastTimestamp = m.created_at_full;
        });

        if (data.other_read_up_to) {
            document.querySelectorAll('.msg-row.mine:not(.read)').forEach(row => {
                const ts = row.getAttribute('data-ts');
                if (ts && ts <= data.other_read_up_to) {
                    row.classList.add('read');
                    const checks = row.querySelector('.bi-check2');
                    if (checks) {
                        checks.classList.remove('bi-check2');
                        checks.classList.add('bi-check2-all');
                        checks.style.color = '#4FC3F7';
                    }
                }
            });
        }
        
        if (data.other_is_online !== undefined) {
            const sub = document.querySelector('.chat-room-title .sub');
            if (sub && sub.innerText.indexOf('قناة') === -1) {
                if (data.other_is_online) {
                    sub.innerHTML = '<span style="color: #4CAF50;">● متصل الآن</span>';
                } else {
                    sub.innerHTML = '<span style="color: #bbb;">غير متصل</span>';
                }
            }
        }
    } catch(e) { alert("Network Error: " + e.message); }
}
function startPolling() {
    if (polling) clearInterval(polling);
    polling = setInterval(pollMessages, 2000);
}
startPolling();

// ===== Send =====
async function sendMessage() {
    try { const dummyCtx = new (window.AudioContext || window.webkitAudioContext)(); dummyCtx.resume(); }catch(e){}
    const input = document.getElementById('chatInput');
    const content = input.value.trim();
    if (!content) return;
    input.value = '';
    input.style.height = 'auto';
    const body = JSON.stringify({ content });
    const headers = { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN };

    if (!lastTimestamp) lastTimestamp = new Date(0).toISOString();

    try {
        const resp = await fetch(API_URL, { method: 'POST', headers, body });
        if (resp.ok) {
            const data = await resp.json();
            if (!document.getElementById(`msg-${data.message.id}`)) {
                appendMessage(data.message);
            }
            lastTimestamp = data.message.created_at_full;
        }
    } catch(e) {
        alert("Network Error: " + e.message);
    }
}

// Enter = send, Shift+Enter = newline
document.getElementById('chatInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Auto-resize textarea
document.getElementById('chatInput').addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 130) + 'px';
});

// Pause poll when hidden
document.addEventListener('visibilitychange', () => {
    document.hidden ? clearInterval(polling) : startPolling();
});

// Focus input on load (desktop)
if (window.innerWidth > 768) {
    document.getElementById('chatInput').focus();
}


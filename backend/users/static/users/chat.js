(() => {
    const script = document.currentScript;
    const tokenUrl = script.dataset.tokenUrl;
    const myId = Number(script.dataset.currentUserId);
    const colleagues = JSON.parse(document.getElementById('colleagues-data').textContent);

    const colleaguesEl = document.getElementById('chat-colleagues');
    const messagesEl = document.getElementById('chat-messages');
    const form = document.getElementById('chat-form');
    const input = document.getElementById('chat-input');

    let activeConversationId = null;
    let ws = null;

    // Записка-пропуск живёт 5 минут на сервере — проще каждый раз спросить свежую,
    // чем следить за временем её жизни на фронте.
    async function getToken() {
        const resp = await fetch(tokenUrl);
        return resp.text();
    }

    function conversationStorageKey(otherUserId) {
        const pair = [myId, otherUserId].sort((a, b) => a - b);
        return `messenger_conv_${pair[0]}_${pair[1]}`;
    }

    async function findOrCreateConversation(token, otherUserId) {
        const key = conversationStorageKey(otherUserId);
        const cached = localStorage.getItem(key);
        if (cached) {
            return Number(cached);
        }

        const resp = await fetch('/messenger-api/conversations', {
            method: 'POST',
            headers: {
                Authorization: 'Bearer ' + token,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_ids: [myId, otherUserId] }),
        });
        const conv = await resp.json();
        localStorage.setItem(key, conv.id);
        return conv.id;
    }

    function renderMessage(msg) {
        const div = document.createElement('div');
        div.className = 'chat-message' + (msg.sender_id === myId ? ' mine' : '');
        div.textContent = msg.text;
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    async function openChat(otherUserId, colleagueEl) {
        document.querySelectorAll('.chat-colleague').forEach((el) => el.classList.remove('active'));
        colleagueEl.classList.add('active');

        messagesEl.innerHTML = '';
        if (ws) {
            ws.close();
        }

        const token = await getToken();
        activeConversationId = await findOrCreateConversation(token, otherUserId);

        const historyResp = await fetch(`/messenger-api/conversations/${activeConversationId}/messages`, {
            headers: { Authorization: 'Bearer ' + token },
        });
        const history = (await historyResp.json()) || [];
        history.forEach(renderMessage);

        const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
        ws = new WebSocket(
            `${protocol}://${location.host}/messenger-api/conversations/${activeConversationId}/ws?token=${token}`
        );
        ws.onmessage = (event) => renderMessage(JSON.parse(event.data));
    }

    function renderColleagues() {
        colleagues.forEach((colleague) => {
            const el = document.createElement('a');
            el.className = 'chat-colleague';
            el.textContent = colleague.full_name;
            el.addEventListener('click', () => openChat(colleague.id, el));
            colleaguesEl.appendChild(el);
        });
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const text = input.value.trim();
        if (!text || !activeConversationId) {
            return;
        }

        const token = await getToken();
        await fetch('/messenger-api/messages', {
            method: 'POST',
            headers: {
                Authorization: 'Bearer ' + token,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ conversation_id: activeConversationId, text }),
        });
        input.value = '';
    });

    renderColleagues();
})();

CHAT_HTML = """<!DOCTYPE html>
<html lang="ca">
<head>
<meta charset="UTF-8">
<title>Centro Médico IMPULS</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
html, body {
    margin: 0;
    padding: 0;
    height: 100vh;
    font-family: Arial, sans-serif;
    background: #f4f4f4;
    overflow: hidden;
}
.chat-container {
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: white;
}
.chat-header {
    background: #4CAF50;
    color: white;
    padding: 15px;
    text-align: center;
    flex-shrink: 0;
}
.chat-body {
    flex: 1;
    overflow-y: auto;
    padding: 15px;
    background: #f9f9f9;
}
.chat-message {
    margin-bottom: 10px;
    padding: 10px;
    border-radius: 10px;
    max-width: 80%;
    word-wrap: break-word;
}
.chat-message.user {
    background: #DCF8C6;
    margin-left: auto;
}
.chat-message.assistant {
    background: #EEE;
    margin-right: auto;
}
.language-buttons {
    display: flex;
    justify-content: center;
    gap: 10px;
    padding: 10px;
    flex-wrap: wrap;
    flex-shrink: 0;
}
.language-button {
    background: #4CAF50;
    color: white;
    border: none;
    padding: 10px 16px;
    border-radius: 20px;
    cursor: pointer;
    font-size: 16px;
}
.language-button:hover {
    background: #45a049;
}
.chat-footer {
    display: none;
    padding: 10px;
    border-top: 1px solid #ddd;
    background: white;
    display: flex;
    flex-shrink: 0;
}
.chat-footer input {
    flex: 1;
    padding: 10px;
    border-radius: 20px;
    border: 1px solid #ccc;
    margin-right: 10px;
    font-size: 16px;
    outline: none;
}
.chat-footer button {
    padding: 10px 16px;
    border-radius: 20px;
    background: #4CAF50;
    color: white;
    border: none;
    font-size: 16px;
    cursor: pointer;
}
.chat-footer button:hover {
    background: #45a049;
}
</style>
</head>
<body>
<div class="chat-container">
    <div class="chat-header">Centro Médico IMPULS</div>
    <div class="chat-body" id="chat-body">
        <div class="chat-message assistant">👋 Choose languge please:<br>1. Español<br>2. Русский<br>3. English<br>4. Català</div>
    </div>
    <div class="language-buttons" id="language-selection">
        <button class="language-button" onclick="selectLanguage('Español')">Español</button>
        <button class="language-button" onclick="selectLanguage('Русский')">Русский</button>
        <button class="language-button" onclick="selectLanguage('English')">English</button>
        <button class="language-button" onclick="selectLanguage('Català')">Català</button>
    </div>
    <div class="chat-footer" id="chat-input">
        <input type="text" id="message-input" placeholder="Escriu el teu missatge..." onkeypress="if(event.keyCode==13) sendMessage()">
        <button onclick="sendMessage()">➤</button>
    </div>
</div>

<script>
function selectLanguage(language) {
    document.getElementById('language-selection').style.display = 'none';
    document.getElementById('chat-input').style.display = 'flex';
    sendMessageToServer(language);
}

function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    if (!message) return;
    appendMessage('user', message);
    input.value = '';
    sendMessageToServer(message);
}

function appendMessage(role, message) {
    const div = document.createElement('div');
    div.className = 'chat-message ' + role;
    div.textContent = message;
    const body = document.getElementById('chat-body');
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
}

function sendMessageToServer(message) {
    fetch('/chat-message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
    })
    .then(res => res.json())
    .then(data => {
        setTimeout(() => {
            appendMessage('assistant', data.response);
        }, 600); // Имитируем задержку ответа
    })
    .catch(err => appendMessage('assistant', '⚠️ Ошибка. Попробуйте еще раз.'));
}
</script>
</body>
</html>"""
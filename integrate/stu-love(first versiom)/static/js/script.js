function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const messageText = messageInput.value.trim();

    if (messageText) {
        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `message=${encodeURIComponent(messageText)}`
        }).then(response => response.json()).then(data => {
            if (data.success) {
                messageInput.value = ''; // 清空输入框
                loadMessages(); // 刷新消息列表
            }
        });
    }
}

function loadMessages() {
    fetch('/get_messages')
        .then(response => response.json())
        .then(data => {
            const messagesContainer = document.getElementById('messages');
            messagesContainer.innerHTML = ''; // 清空当前消息

            data.messages.forEach(msg => {
                const messageElement = document.createElement('div');
                messageElement.className = 'message';
                messageElement.textContent = msg;
                messagesContainer.appendChild(messageElement);
            });

            // 滚动到最新消息
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        });
}

// 定时刷新消息
setInterval(loadMessages, 1000); // 每秒刷新一次

let currentReceiverId = null;  // 当前接收消息的用户 ID  
let currentUserId = null;      // 当前用户的 ID

// 获取当前用户的 ID（假设从 API 中获取）
function fetchCurrentUserId() {
    fetch('/get_current_user')
        .then(response => response.json())
        .then(data => {
            currentUserId = data.user_id;  // 设置当前用户的 ID
            console.log('当前用户 ID:', currentUserId);  // 调试输出
        })
        .catch(error => {
            console.error('获取当前用户 ID 失败:', error);
        });
}

// 页面加载时获取当前用户的 ID
document.addEventListener('DOMContentLoaded', function() {
    fetchCurrentUserId();  // 获取当前用户的 ID
    setupFriendClickListener(); // 确保好友点击事件绑定
});

function setupFriendClickListener() {
    const friendListItems = document.querySelectorAll('.friend-list li');
    
    friendListItems.forEach(item => {
        item.addEventListener('click', function() {
            // 获取选中的好友 ID
            const receiverId = this.getAttribute('data-chat-id');
            const receiverName = this.textContent.trim();
            
            console.log('Receiver ID:', receiverId);  // 输出调试信息
            
            if (!receiverId || receiverId === 'null') {
                console.log('Error: Invalid receiver ID');
                return;
            }
            
            // 更新聊天区的标题
            const chatHeader = document.getElementById('chat-header');
            chatHeader.textContent = `与 ${receiverName} 聊天中...`;
            chatHeader.setAttribute('data-chat-id', receiverId);  // 设置正确的 receiverId
            console.log('Updated Receiver ID in chat header:', receiverId);  // 输出更新后的 receiverId

            // 设置选中的好友项的样式
            friendListItems.forEach(friend => friend.classList.remove('active'));
            this.classList.add('active');
            
            // 清空聊天记录区域（如果需要）
            const chatMessages = document.getElementById('chat-messages');
            chatMessages.innerHTML = ''; // 清空历史消息

            // 加载聊天记录
            loadChat(receiverId, receiverName);
        });
    });
}

// 发送消息
function sendMessage(event) {
    event.preventDefault();  // 阻止表单默认提交

    let messageInput = document.getElementById('message-input');
    let message = messageInput.value.trim();
    
    if (message === "") {
        alert("请输入消息！");
        return;
    }

    // 获取接收者 ID
    let receiverId = document.getElementById('chat-header').getAttribute('data-chat-id');
    console.log('Receiver ID from chat header:', receiverId);  // 调试输出 receiverId

    if (!receiverId) {
        alert("请选择一个好友进行聊天！");
        return;
    }

    // 发送消息到后端
    fetch('/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            receiver_id: receiverId,  // 确保发送正确的 receiver_id
            message: message
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            messageInput.value = '';  // 清空输入框

            // 显示发送的消息
            addMessageToChat('my-message', message);
        } else {
            console.log('消息发送失败');
        }
    })
    .catch(error => {
        console.error('发送消息时出现错误:', error);
    });
}

// 添加好友的函数
function addFriend(receiverId) {
    if (!currentUserId) {
        alert('当前用户未登录');
        return;
    }

    fetch('/add_friend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',  // 确保请求头正确
        },
        body: JSON.stringify({
            current_user_id: currentUserId,  // 当前用户的 ID
            friend_id: receiverId            // 对方的 ID
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('服务器错误');
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            alert('好友添加成功');
        } else {
            alert('好友添加失败: ' + data.message);
        }
    })
    .catch(error => {
        console.error('添加好友时发生错误:', error);
        alert('添加好友失败，请稍后重试');
    });
}

// 表情选择器相关
function toggleEmojiPicker() {
    const emojiPicker = document.getElementById('emoji-picker');
    emojiPicker.style.display = emojiPicker.style.display === 'block' ? 'none' : 'block';
}

function addEmoji(emoji) {
    const messageInput = document.getElementById('message-input');
    messageInput.value += emoji;
    toggleEmojiPicker();  // 关闭表情选择器
}

function uploadEmoji(event) {
    const file = event.target.files[0];
    if (file) {
        const formData = new FormData();
        formData.append("image", file);  // 确保字段名与后端一致

        // 发送图片到后端
        fetch('/upload_image', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === "图片上传成功！") {
                const messageInput = document.getElementById('message-input');
                const messageContainer = document.getElementById('chat-messages');  // 假设消息区域的 id 为 chat-messages

                // 创建 img 元素来显示图片
                const imgElement = document.createElement('img');
                imgElement.src = data.file_url;  // 返回的图片路径
                //imgElement.style.width = '80px';
                //imgElement.style.height = '80px';

                // 将图片添加到聊天区域
                const newMessage = document.createElement('div');
                newMessage.classList.add('my-message');  // 假设这是当前用户的消息
                newMessage.appendChild(imgElement);  // 将图片插入消息框

                // 将新消息添加到消息区域
                messageContainer.appendChild(newMessage);

                // 滚动到消息底部
                messageContainer.scrollTop = messageContainer.scrollHeight;
            } else {
                alert('图片上传失败');
            }
        })
        .catch(error => {
            console.error('图片上传出错:', error);
            alert('图片上传失败');
        });
    }
}

function loadChat(receiverId, receiverName) {
    fetch(`/get_messages?receiver_id=${receiverId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const messages = data.messages;
                const chatMessages = document.getElementById('chat-messages');
                chatMessages.innerHTML = '';  // 清空当前聊天记录

                // 按照时间戳升序排序消息（最旧的在前，最新的在后）
                messages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

                // 按顺序将所有消息添加到底部
                messages.forEach(message => {
                    // 判断发送者 ID 来决定是我发的消息还是好友发的消息
                    const messageClass = message.sender_id === 1 ? 'my-message' : 'other-message';  // 假设 1 是我的 ID
                    addMessageToChat(messageClass, message.message);
                });

                // 让聊天区域滚动到底部
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } else {
                console.log('无法加载历史消息');
            }
        })
        .catch(error => {
            console.error('加载聊天记录时出错:', error);
        });
}

// 添加消息到聊天区域
function addMessageToChat(messageClass, message) {
    const chatMessages = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    messageElement.classList.add(messageClass);

    // 创建一个包含文本的 div 元素，限制每行最多 10 个字符
    const textElement = document.createElement('div');
    textElement.classList.add('message-text');
    textElement.textContent = message;

    // 将文本添加到消息框中
    messageElement.appendChild(textElement);

    // 将消息框添加到聊天区域
    chatMessages.appendChild(messageElement);

    // 让聊天区域滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
}


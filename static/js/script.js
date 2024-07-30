document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

function sendMessage() {
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();
    if (message) {
        document.getElementById('intro-box').style.display = 'none'; // Hide intro box when a message is sent
        appendMessage('user', message);

        // Simulate bot response
        var formData = {
            question: userInput.value
        };
         fetch('/submit-form', {
            method: 'POST', // 或者 'GET'
            headers: {
                'Content-Type': 'application/json', // 告诉服务器我们发送的是JSON格式的数据
            },
            body: JSON.stringify(formData) // 将JavaScript对象转换为JSON字符串
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // 解析JSON格式的响应体
        })
        .then(data => {
            console.log('Success:', data);
            // 在这里处理成功响应，比如更新页面元素
            //
            //
            //
            //   // 使用Fetch API请求数据
            fetch('/get-data')
                .then(response => {
                    // 确保请求成功
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    // 解析JSON数据
                    return response.json();
                })
                .then(data => {
                    // 处理数据

                    setTimeout(() => {appendMessage('bot', getBotResponse(data.message));}, 500);

                })
                .catch(error => {
                    console.error('There was a problem with your fetch operation:', error);
                });
            //
            //
            //
            //
        })
        .catch(error => {
            console.error('There was a problem with your fetch operation:', error);
        });
        userInput.value = '';
    }
}

function appendMessage(sender, message) {
    const chatWindow = document.getElementById('chat-window');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    messageElement.innerText = message;
    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function getBotResponse(message) {
    // Placeholder bot response logic
    return "AI: " + message;
}

// Sidebar toggle functionality
const openBtn = document.getElementById('open-sidebar');
const closeBtn = document.getElementById('close-sidebar');
const sidebar = document.getElementById('sidebar');
const chatContainer = document.getElementById('chat-container');
const inputContainer = document.querySelector('.input-container');

openBtn.addEventListener('click', () => {
    sidebar.classList.remove('hidden-sidebar');
    chatContainer.classList.remove('hidden-chat-container');
    inputContainer.classList.remove('hidden-input-container');
});

closeBtn.addEventListener('click', () => {
    sidebar.classList.add('hidden-sidebar');
    chatContainer.classList.add('hidden-chat-container');
    inputContainer.classList.add('hidden-input-container');
});

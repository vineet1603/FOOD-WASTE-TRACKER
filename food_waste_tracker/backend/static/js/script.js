const uploadForm = document.getElementById('uploadForm');
const chatbox = document.getElementById('chatbox');

uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    // User message
    const userMsg = document.createElement('div');
    userMsg.className = 'user';
    userMsg.innerText = "📤 Uploading food image...";
    chatbox.appendChild(userMsg);

    const response = await fetch('/analyze', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();

    // Bot response
    const botMsg = document.createElement('div');
    botMsg.className = 'bot';
    botMsg.innerText = "🤖 Bot: " + result.message;
    chatbox.appendChild(botMsg);

    chatbox.scrollTop = chatbox.scrollHeight;
});

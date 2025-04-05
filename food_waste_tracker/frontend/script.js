// Handle Upload
document.getElementById('uploadForm').onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    document.getElementById('foodResult').innerText = `Food: ${data.foodName}, Expiry: ${data.expiry}`;
};

// Handle Chat
async function sendMessage() {
    const input = document.getElementById('userInput').value;
    if (!input) return;
    const chatbox = document.getElementById('chatbox');
    chatbox.innerHTML += `<div>User: ${input}</div>`;
    
    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
    });
    const data = await response.json();
    chatbox.innerHTML += `<div>Bot: ${data.response}</div>`;
    document.getElementById('userInput').value = '';
}

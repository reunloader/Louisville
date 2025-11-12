// Derby City Watch Chatbot Frontend

const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const buttonText = document.getElementById('buttonText');
const buttonLoader = document.getElementById('buttonLoader');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    messageInput.focus();
});

// Handle form submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();

    if (!message) return;

    // Add user message to chat
    addMessage(message, 'user');

    // Clear input
    messageInput.value = '';

    // Disable input while processing
    setLoading(true);

    // Show typing indicator
    const typingId = addTypingIndicator();

    try {
        // Send message to backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator(typingId);

        if (data.success) {
            // Add bot response
            addMessage(data.response, 'bot');
        } else {
            addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            console.error('Error:', data.error);
        }
    } catch (error) {
        removeTypingIndicator(typingId);
        addMessage('Sorry, I could not connect to the server. Please try again later.', 'bot');
        console.error('Fetch error:', error);
    }

    setLoading(false);
});

// Add message to chat
function addMessage(content, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Convert markdown-style formatting to HTML
    let formattedContent = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');

    contentDiv.innerHTML = formattedContent;

    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    scrollToBottom();
}

// Add typing indicator
function addTypingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.id = 'typing-indicator';

    const typingDiv = document.createElement('div');
    typingDiv.className = 'message-content typing-indicator';
    typingDiv.innerHTML = '<span></span><span></span><span></span>';

    messageDiv.appendChild(typingDiv);
    chatMessages.appendChild(messageDiv);

    scrollToBottom();

    return 'typing-indicator';
}

// Remove typing indicator
function removeTypingIndicator(id) {
    const indicator = document.getElementById(id);
    if (indicator) {
        indicator.remove();
    }
}

// Scroll to bottom of chat
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Set loading state
function setLoading(isLoading) {
    if (isLoading) {
        sendButton.disabled = true;
        messageInput.disabled = true;
        buttonText.style.display = 'none';
        buttonLoader.style.display = 'inline-block';
    } else {
        sendButton.disabled = false;
        messageInput.disabled = false;
        buttonText.style.display = 'inline';
        buttonLoader.style.display = 'none';
        messageInput.focus();
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        if (data.success) {
            document.getElementById('incident-count').textContent =
                `${data.total_incidents} incidents loaded`;
            document.getElementById('ai-provider').textContent =
                `AI: ${data.ai_provider.toUpperCase()}`;
        }

        // Check auto-reload status
        const reloadResponse = await fetch('/api/auto-reload-status');
        const reloadData = await reloadResponse.json();

        if (reloadData.success && reloadData.enabled) {
            const statsDiv = document.getElementById('stats');
            const autoReloadSpan = document.createElement('span');
            autoReloadSpan.id = 'auto-reload-status';
            autoReloadSpan.textContent = '🔄 Auto-update ON';
            autoReloadSpan.title = `Checking for new files every ${reloadData.check_interval}s`;
            statsDiv.appendChild(autoReloadSpan);
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// Clear chat
async function clearChat() {
    if (confirm('Clear all chat messages?')) {
        try {
            await fetch('/api/clear', { method: 'POST' });

            // Clear UI
            chatMessages.innerHTML = '';

            // Add welcome message back
            addMessage(
                "👋 Hi! I'm your Derby City Watch assistant. I can help you find information about recent emergency incidents, traffic, and public safety events in Louisville, KY.\n\n" +
                "**Try asking me:**\n" +
                "• \"What's happening around Bardstown Road?\"\n" +
                "• \"Any traffic incidents on I-65?\"\n" +
                "• \"Are there any recent fire calls in downtown?\"\n" +
                "• \"What incidents happened today?\"",
                'bot'
            );
        } catch (error) {
            console.error('Failed to clear chat:', error);
            alert('Failed to clear chat. Please try again.');
        }
    }
}

// Reload data
async function reloadData() {
    try {
        const response = await fetch('/api/reload', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            alert(data.message);
            loadStats();
        } else {
            alert('Failed to reload data: ' + data.error);
        }
    } catch (error) {
        console.error('Failed to reload data:', error);
        alert('Failed to reload data. Please try again.');
    }
}

// Allow Enter to send, Shift+Enter for new line
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

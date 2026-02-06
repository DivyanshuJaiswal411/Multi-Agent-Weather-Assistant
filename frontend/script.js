const API_URL = "https://weather-backend-236535001785.us-central1.run.app/chat";

// Session Persistence
let sessionId = localStorage.getItem("weather_session_id") || null;

document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("user-input");
    
    // Enter key support
    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    // Focus input on load
    input.focus();
});

async function sendMessage() {
    const input = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const message = input.value.trim();
    
    if (!message) return;

    // UI Updates
    appendMessage("user", message);
    input.value = "";
    input.disabled = true; // Disable while loading
    sendBtn.style.opacity = "0.5";
    
    // Show loading
    const typingId = showTypingIndicator();

    try {
        const res = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message,
                session_id: sessionId
            })
        });

        if (!res.ok) throw new Error("API Error");

        const data = await res.json();
        
        // Remove loader
        removeTypingIndicator(typingId);

        // Update Session
        if (data.session_id) {
            sessionId = data.session_id;
            localStorage.setItem("weather_session_id", sessionId);
        }

        appendMessage("agent", data.reply);

    } catch (error) {
        removeTypingIndicator(typingId);
        appendMessage("agent", "⚠️ I'm having trouble connecting to the weather network. Please try again in a moment.");
        console.error(error);
    } finally {
        input.disabled = false;
        sendBtn.style.opacity = "1";
        input.focus();
    }
}

function appendMessage(sender, text) {
    const box = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = `message ${sender}`;
    
    const avatar = sender === 'agent' ? `<div class="avatar-icon"><i class="fa-solid fa-robot"></i></div>` : '';
    
    // Enhanced Markdown Parsing
    let formattedText = text
        // Bold
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Italic
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // Lists
        .replace(/^- (.*)$/gm, '• $1') 
        // Newlines to breaks
        .replace(/\n/g, '<br>');

    div.innerHTML = `
        ${avatar}
        <div class="bubble">${formattedText}</div>
    `;
    
    box.appendChild(div);
    scrollToBottom();
}

function showTypingIndicator() {
    const box = document.getElementById("chat-box");
    const id = "typing-" + Date.now();
    const div = document.createElement("div");
    div.id = id;
    div.className = "message agent";
    div.innerHTML = "
        <div class=\"avatar-icon\"><i class=\"fa-solid fa-robot\"></i></div>
        <div class=\"typing-container\">
            <div class=\"dot\"></div>
            <div class=\"dot\"></div>
            <div class=\"dot\"></div>
        </div>
    ";
    box.appendChild(div);
    scrollToBottom();
    return id;
}

function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) {
        element.style.opacity = '0';
        setTimeout(() => element.remove(), 200); // Fade out effect
    }
}

function scrollToBottom() {
    const box = document.getElementById("chat-box");
    // Small timeout to ensure DOM is rendered
    setTimeout(() => {
        box.scrollTop = box.scrollHeight;
    }, 10);
}

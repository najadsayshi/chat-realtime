// app.js
const API_URL = "http://localhost:8000";
const WS_URL = "ws://localhost:8000/ws";

// State
let token = localStorage.getItem("chat_token") || "";
let activeRoom = null;
let socket = null;
let joinedRooms = new Set(); // Store joined room numbers

// DOM Elements
const els = {
    authScreen: document.getElementById("auth-screen"),
    chatScreen: document.getElementById("chat-screen"),
    loginForm: document.getElementById("login-form"),
    signupForm: document.getElementById("signup-form"),
    goSignup: document.getElementById("go-to-signup"),
    goLogin: document.getElementById("go-to-login"),
    logoutBtn: document.getElementById("logout-btn"),
    
    roomInput: document.getElementById("room-id-input"),
    joinBtn: document.getElementById("join-room-btn"),
    roomsList: document.getElementById("rooms-list"),
    activeRoomName: document.getElementById("active-room-name"),
    connStatus: document.getElementById("connection-status"),
    messagesContainer: document.getElementById("messages-container"),
    messageForm: document.getElementById("message-form"),
    messageInput: document.getElementById("message-input"),
    toastContainer: document.getElementById("toast-container")
};

// Initialize
init();

function init() {
    setupEventListeners();
    if (token) {
        showScreen("chat");
    } else {
        showScreen("auth");
    }
}

function showScreen(screen) {
    els.authScreen.classList.remove("active");
    els.chatScreen.classList.remove("active");
    
    if (screen === "auth") els.authScreen.classList.add("active");
    if (screen === "chat") els.chatScreen.classList.add("active");
}

function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    els.toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3300);
}

function setupEventListeners() {
    // Auth Toggle
    els.goSignup.addEventListener("click", (e) => {
        e.preventDefault();
        els.loginForm.classList.remove("active");
        els.loginForm.classList.add("slide-left");
        els.signupForm.classList.add("active");
    });
    
    els.goLogin.addEventListener("click", (e) => {
        e.preventDefault();
        els.signupForm.classList.remove("active");
        els.loginForm.classList.remove("slide-left");
        els.loginForm.classList.add("active");
    });

    // Login
    els.loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("login-email").value;
        const password = document.getElementById("login-password").value;
        await login(email, password);
    });

    // Signup
    els.signupForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("signup-name").value;
        const email = document.getElementById("signup-email").value;
        const password = document.getElementById("signup-password").value;
        await signup(name, email, password);
    });

    // Logout
    els.logoutBtn.addEventListener("click", logout);

    // Join Room
    els.joinBtn.addEventListener("click", () => {
        const roomId = parseInt(els.roomInput.value);
        if(!roomId || isNaN(roomId)) return;
        els.roomInput.value = "";
        joinRoom(roomId);
    });
    
    // Send Message
    els.messageForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const content = els.messageInput.value.trim();
        if(!content || !socket || !activeRoom) {
            if(!activeRoom) showToast("Select a room first", "error");
            return;
        }
        
        socket.send(JSON.stringify({
            type: "MESSAGE",
            room_id: activeRoom,
            content: content
        }));
        
        els.messageInput.value = "";
    });
}

async function login(email, password) {
    try {
        const res = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        
        if (!res.ok) throw new Error(data.detail || "Login failed");
        
        token = data.access_token;
        localStorage.setItem("chat_token", token);
        showToast("Login successful!", "success");
        showScreen("chat");
    } catch (err) {
        showToast(err.message, "error");
    }
}

async function signup(name, email, password) {
    try {
        const res = await fetch(`${API_URL}/signup`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, email, password })
        });
        const data = await res.json();
        
        if (!res.ok) throw new Error(data.detail || "Signup failed");
        
        showToast("Account created! Please log in.", "success");
        els.goLogin.click();
    } catch (err) {
        showToast(err.message, "error");
    }
}

function logout() {
    token = "";
    localStorage.removeItem("chat_token");
    if (socket) socket.close();
    socket = null;
    activeRoom = null;
    els.messagesContainer.innerHTML = `
        <div class="empty-state">
            <svg viewBox="0 0 24 24" width="48" height="48" stroke="currentColor" stroke-width="1.5" fill="none" class="empty-icon"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            <p>No messages here yet.<br>Start the conversation!</p>
        </div>
    `;
    els.roomsList.innerHTML = "";
    joinedRooms.clear();
    els.activeRoomName.textContent = "Select a Room";
    els.connStatus.textContent = "Disconnected";
    els.connStatus.classList.remove("connected");
    showScreen("auth");
}

async function joinRoom(roomId) {
    activeRoom = roomId;
    els.activeRoomName.textContent = `Room ${roomId}`;
    
    if(!joinedRooms.has(roomId)) {
        joinedRooms.add(roomId);
        renderRoomItem(roomId);
    }
    
    document.querySelectorAll(".room-item").forEach(el => el.classList.remove("active"));
    const activeItem = document.getElementById(`room-item-${roomId}`);
    if(activeItem) activeItem.classList.add("active");

    await loadMessages(roomId);
    connectWebSocket(roomId);
}

function renderRoomItem(roomId) {
    const li = document.createElement("li");
    li.className = "room-item";
    li.id = `room-item-${roomId}`;
    li.innerHTML = `<span class="hashtag">#</span> Room ${roomId}`;
    li.onclick = () => joinRoom(roomId);
    els.roomsList.appendChild(li);
}

async function loadMessages(roomId) {
    try {
        const res = await fetch(`${API_URL}/messages?room_id=${roomId}`);
        const data = await res.json();
        
        els.messagesContainer.innerHTML = ""; 
        
        if(!data.messages || data.messages.length === 0) {
            els.messagesContainer.innerHTML = `
                <div class="empty-state">
                    <svg viewBox="0 0 24 24" width="48" height="48" stroke="currentColor" stroke-width="1.5" fill="none" class="empty-icon"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                    <p>No messages here yet.<br>Start the conversation!</p>
                </div>
            `;
            return;
        }

        data.messages.forEach(msg => appendMessage(msg));
        scrollToBottom();
    } catch(err) {
        showToast("Error loading messages", "error");
    }
}

function connectWebSocket(roomId) {
    if(!socket || socket.readyState !== WebSocket.OPEN) {
        els.connStatus.textContent = "Connecting...";
        els.connStatus.classList.remove("connected");
        
        if(socket) socket.close();
        
        socket = new WebSocket(`${WS_URL}?token=${token}`);
        
        socket.onopen = () => {
            els.connStatus.textContent = "Connected";
            els.connStatus.classList.add("connected");
            
            socket.send(JSON.stringify({
                type: "JOIN_ROOM",
                room_id: roomId
            }));
        };
        
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === "MESSAGE") {
                if (data.room_id === activeRoom) {
                    appendMessage(data);
                    scrollToBottom();
                }
            } else if (data.type === "ERROR") {
                showToast(data.detail || "Error", "error");
            }
        };
        
        socket.onclose = () => {
            els.connStatus.textContent = "Disconnected";
            els.connStatus.classList.remove("connected");
        };
        
        socket.onerror = () => {
            showToast("Connection error", "error");
            els.connStatus.textContent = "Error";
            els.connStatus.classList.remove("connected");
        };
    } else {
        socket.send(JSON.stringify({
            type: "JOIN_ROOM",
            room_id: roomId
        }));
    }
}

function appendMessage(data) {
    const emptyState = els.messagesContainer.querySelector(".empty-state");
    if (emptyState) emptyState.remove();

    const div = document.createElement("div");
    
    // Determine sender identity and parse token for own user ID
    let isMe = false;
    try {
        if(token) {
            const payload = JSON.parse(atob(token.split('.')[1]));
            if(payload.user_id && String(data.user_id) === String(payload.user_id)) {
                isMe = true;
            }
        }
    } catch(e) {
        console.error("Token decode error", e);
    }

    const senderName = data.name || (data.user_id ? `User ${data.user_id}` : "Unknown");
    div.className = `message ${isMe ? 'msg-sent' : 'msg-recv'}`;
    
    const senderEl = `<div class="msg-sender">${escapeHTML(senderName)}</div>`;
    const bubbleEl = `<div class="msg-bubble">${escapeHTML(data.content || JSON.stringify(data))}</div>`;
    
    div.innerHTML = isMe ? bubbleEl : (senderEl + bubbleEl);
    els.messagesContainer.appendChild(div);
}

function scrollToBottom() {
    els.messagesContainer.scrollTop = els.messagesContainer.scrollHeight;
}

function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

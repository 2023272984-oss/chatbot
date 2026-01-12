/* static/script.js */
let chatSessions = [];
let currentChatId = null;

/* ---------- INIT ---------- */
function initializeApp() {
  loadChatSessions();
  if (chatSessions.length === 0) createNewChat();
  else switchToChat(chatSessions[0].id);
  renderChatSessions();
}

/* ---------- CHAT CREATION ---------- */
function createNewChat() {
  const newChat = {
    id: Date.now(),
    title: `Chat ${chatSessions.length + 1}`,
    messages: [],
    createdAt: new Date().toISOString(),
    preview: 'New conversation'
  };
  chatSessions.unshift(newChat);
  saveChatSessions();
  switchToChat(newChat.id);
  
  // On mobile, close menu after creating new chat
  if (window.innerWidth <= 768) {
      document.getElementById('history-panel').classList.remove('open');
      document.getElementById('overlay').classList.remove('active');
  }
}

/* ---------- SWITCH CHAT ---------- */
function switchToChat(chatId) {
  currentChatId = chatId;
  const chat = chatSessions.find(c => c.id === chatId);
  if (!chat) return;

  const chatBox = document.getElementById('chat-box');
  chatBox.innerHTML = '';

  if (chat.messages.length === 0) {
    // Re-render welcome screen
    chatBox.innerHTML = `
      <div class="welcome-message">
        <h3>Hello, User</h3>
        <p>How can I help you be healthier today?</p>
        <div class="suggestion-chips">
          <div class="chip" onclick="sendSuggestion('Give me a 10-minute workout routine')">10-min workout</div>
          <div class="chip" onclick="sendSuggestion('Tips for better sleep hygiene')">Sleep better</div>
          <div class="chip" onclick="sendSuggestion('Healthy breakfast ideas')">Healthy breakfast</div>
          <div class="chip" onclick="sendSuggestion('How to manage stress')">Manage stress</div>
        </div>
      </div>`;
  } else {
    chat.messages.forEach(m => addMessageToUI(m.text, m.isUser));
  }

  renderChatSessions();
  
  // Mobile: close sidebar on selection
  if (window.innerWidth <= 768) {
     toggleHistoryPanel(); 
  }
}

/* ---------- RESET CURRENT CHAT ---------- */
function resetCurrentChat() {
  if (!currentChatId) return;
  // Gemini doesn't usually confirm for reset, but we can keep it for safety
  if (!confirm('Clear this chat?')) return;

  const chat = chatSessions.find(c => c.id === currentChatId);
  if (!chat) return;

  chat.messages = [];
  chat.preview = 'New conversation';
  saveChatSessions();
  switchToChat(currentChatId);
}

/* ---------- CLEAR ALL ---------- */
function clearAllChats() {
  if (!confirm('Delete all history?')) return;
  chatSessions = [];
  saveChatSessions();
  createNewChat();
}

/* ---------- DELETE CHAT ---------- */
function deleteChat(chatId, event) {
  event.stopPropagation();
  if (!confirm('Delete this chat?')) return;

  chatSessions = chatSessions.filter(c => c.id !== chatId);
  saveChatSessions();

  if (currentChatId === chatId) {
    chatSessions.length ? switchToChat(chatSessions[0].id) : createNewChat();
  }
  renderChatSessions();
}

/* ---------- SIDEBAR ---------- */
function renderChatSessions() {
  const container = document.getElementById('chat-sessions');
  container.innerHTML = '<h3>Recent</h3>'; // Add "Recent" label like Gemini

  chatSessions.forEach(chat => {
    const div = document.createElement('div');
    div.className = `chat-session ${chat.id === currentChatId ? 'active' : ''}`;
    div.onclick = () => switchToChat(chat.id);

    div.innerHTML = `
      <div class="chat-session-title">${chat.title}</div>
      <button class="delete-chat-btn" onclick="deleteChat(${chat.id}, event)">×</button>`;
    container.appendChild(div);
  });
}

/* ---------- MESSAGE UI ---------- */
function addMessageToUI(text, isUser) {
  const chatBox = document.getElementById('chat-box');
  chatBox.querySelector('.welcome-message')?.remove();

  const div = document.createElement('div');
  div.className = `message ${isUser ? 'user' : 'bot'}`;

  // Use Gemini/Google icons
  const icon = isUser ? 'person' : 'smart_toy'; 

  div.innerHTML = `
    <div class="avatar">
        <span class="material-symbols-outlined" style="font-size: 20px;">${icon}</span>
    </div>
    <div class="message-content">${formatMessage(text)}</div>`;

  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

/* ---------- FORMAT ---------- */
function formatMessage(text) {
  let f = text.replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>');
  f = f.replace(/(<li>.*<\/li>\s*)+/gs, m => `<ol>${m}</ol>`);
  f = f.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  return f;
}

/* ---------- TYPING ---------- */
function showTyping() {
  const box = document.getElementById('chat-box');
  if (document.getElementById('typing-indicator')) return;
  
  box.insertAdjacentHTML('beforeend', `
    <div class="message bot" id="typing-indicator">
      <div class="avatar">
        <span class="material-symbols-outlined" style="font-size: 20px;">smart_toy</span>
      </div>
      <div class="typing-indicator" style="display:flex; gap:4px; padding:10px;">
        <span></span><span></span><span></span>
      </div>
    </div>`);
  box.scrollTop = box.scrollHeight;
}

function removeTyping() {
  document.getElementById('typing-indicator')?.remove();
}

/* ---------- SEND ---------- */
async function sendMessage(messageText) {
  const input = document.getElementById('user-input');
  const text = messageText ? messageText.trim() : input.value.trim();
  
  if (!text) return;

  input.value = '';
  if (!messageText) input.focus();

  const chat = chatSessions.find(c => c.id === currentChatId);
  if (!chat) return;

  chat.messages.push({ text, isUser: true });
  // Update title if it's the first message
  if (chat.messages.length === 1) {
      chat.title = text.slice(0, 30);
  }
  
  saveChatSessions();
  addMessageToUI(text, true);
  renderChatSessions();

  showTyping();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });

    const data = await res.json();
    removeTyping();
    chat.messages.push({ text: data.reply, isUser: false });
    addMessageToUI(data.reply, false);
    saveChatSessions();
  } catch (err) {
    console.error(err);
    removeTyping();
    addMessageToUI('Something went wrong connecting to the server.', false);
  }
}

/* ---------- UTILS ---------- */
function sendSuggestion(text) { sendMessage(text); }

function toggleHistoryPanel() {
  document.getElementById('history-panel').classList.toggle('open');
  document.getElementById('overlay').classList.toggle('active');
}

function toggleSidebar() {
  document.getElementById('history-panel').classList.toggle('collapsed');
}

function saveChatSessions() {
  localStorage.setItem('healthbot_chats', JSON.stringify(chatSessions));
}

function loadChatSessions() {
  const saved = localStorage.getItem('healthbot_chats');
  if (saved) chatSessions = JSON.parse(saved);
}

/* ---------- EVENTS ---------- */
const inputField = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

if (sendBtn) sendBtn.onclick = () => sendMessage();

if (inputField) {
    inputField.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage();
      }
    });
}

window.onload = initializeApp;
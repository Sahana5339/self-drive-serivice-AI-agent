import ApiService from "../services/apiService.js";

const AgentName = "agent";
let activeSessionId = "";

document.addEventListener("DOMContentLoaded", () => {
  initChat();
});

function initChat() {
  const newSessionButton = document.getElementById("new-session");
  newSessionButton.addEventListener("click", createSession);
  listSessions();
}

// DOM elements
const messagesEl = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const sessionsListWrapper = document.getElementById("sessions-list");

function listSessions() {
  ApiService.get(`/apps/${AgentName}/users/user/sessions`)
    .then((sessions) => {
      if (sessions.length) {
        activeSessionId = sessions[0].id;
        for (let i = 0; i < sessions.length; i++) {
          createSessionElement(sessions[i].id);
        }
      }
    })
    .catch((error) => console.error(error));
}

function createSessionElement(id) {
  const li = document.createElement("li");
  li.setAttribute("id", `id-${id}`);
  li.setAttribute("class", "session-item");
  const spanEl = document.createElement("span");
  spanEl.innerHTML = id;
  if (activeSessionId === id) {
    li.classList.add("active");
  }
  li.onclick = () => updateActiveSession(id);
  li.appendChild(spanEl);
  sessionsListWrapper.appendChild(li);
}

function createSession() {
  ApiService.post(`/apps/${AgentName}/users/user/sessions`)
    .then((session) => {
      activeSessionId = session.id;
      createSessionElement(session.id);
    })
    .catch((error) => console.error(error));
}

function updateActiveSession(id) {
  const existingSessions = sessionsListWrapper.querySelectorAll(".session-item");
  existingSessions.forEach(s => s.classList.remove("active"));
  
  const listEl = document.getElementById(`id-${id}`);
  activeSessionId = id;
  listEl.classList.add("active");
  messagesEl.innerHTML = "";
}

function appendMessage(text, who = "model") {
  const el = document.createElement("div");
  el.className = `message ${who}`;
  el.innerHTML = text;
  messagesEl.appendChild(el);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setSending(isSending) {
  sendBtn.disabled = isSending;
  input.disabled = isSending;
}

async function sendMessage(text) {
  if (!text) return;

  setSending(true);
  appendMessage(text, "user");

  const payload = {
    appName: AgentName,
    newMessage: { role: "user", parts: [{ text }] },
    sessionId: activeSessionId,
    userId: "user",
  };

  try {
    const response = await ApiService.post("/run_sse", payload);
    if (response && response.content && response.content.parts) {
      appendMessage(response.content.parts[0].text, "model");
    } else {
      appendMessage("No response received", "model");
    }
  } catch (err) {
    console.error("Chat error:", err);
    appendMessage("Sorry, there was an error.", "model");
  } finally {
    setSending(false);
  }
}

// Form submit
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  input.value = "";
  await sendMessage(text);
});
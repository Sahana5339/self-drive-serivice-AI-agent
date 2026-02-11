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
const fileInput = document.getElementById("file-input");
const uploadList = document.getElementById("upload-list");
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
  const deleteIcon = document.createElement("i");
  deleteIcon.setAttribute("class", "fa fa-trash delete-session");
  deleteIcon.onclick = (event) => deleteSession(event, id);
  const spanEl = document.createElement("span");
  spanEl.innerHTML = id;
  if (activeSessionId === id) {
    const existingSessions =
      sessionsListWrapper.querySelectorAll(".session-item");
    if (existingSessions.length) {
      for (let j = 0; j < existingSessions.length; j++) {
        existingSessions[j].classList.remove("active");
      }
    }
    li.classList.add("active");
    updateActiveSession(id);
  }
  li.onclick = () => updateActiveSession(id);
  li.appendChild(spanEl);
  li.appendChild(deleteIcon);
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

function deleteSession(event, id) {
  event.stopPropagation();
  ApiService.delete(`/apps/${AgentName}/users/user/sessions/${id}`)
    .then(() => {
      const session = document.getElementById(`id-${id}`);
      const wasActive = session.classList.contains("active");
      if (wasActive) {
        const firstSession = document.querySelector(".session-item");
        firstSession.classList.add("active");
        activeSession = firstSession.getAttribute("id");
      }
      session.parentNode.removeChild(session);
    })
    .catch((error) => console.error(error));
}

function updateActiveSession(id) {
  ApiService.get(`/apps/${AgentName}/users/user/sessions/${id}`)
    .then((sessionResponse) => {
      const existingSessions =
        sessionsListWrapper.querySelectorAll(".session-item");
      if (existingSessions.length) {
        for (let j = 0; j < existingSessions.length; j++) {
          existingSessions[j].classList.remove("active");
        }
      }
      const listEl = document.getElementById(`id-${id}`);
      activeSessionId = id;
      listEl.classList.add("active");
      messagesEl.innerHTML = "";
      renderEvents(sessionResponse.events);
    })
    .catch((error) => console.error(error));
}

function renderEvents(events) {
  for (let i = 0; i < events.length; i++) {
    if (events[i].content) {
      appendMessage(events[i].content, events[i].content.role);
    }
  }
}

// Helpers
function appendMessage(content, who = "model") {
  const el = document.createElement("div");
  if (content.parts) {
    for (let i = 0; i < content.parts.length; i++) {
      const part = content.parts[i];
      if (part.functionResponse) {
        el.className = `message model function`;
        el.innerHTML = `<i class="fa fa-check"></i> ${part.functionResponse.name}`;
      } else {
        el.className = `message ${who}`;
        if (part.text) {
          el.innerHTML = marked.parse(part.text);
        }
        if (part.functionCall) {
          el.classList.add("function");
          el.innerHTML = `<i class="fa fa-bolt"></i> ${part.functionCall.name}`;
        }
        if (part.inlineData) {
          const mediaEl = createMediaElement(part.inlineData);
          if (mediaEl) {
            el.appendChild(mediaEl);
          }
        }
      }
    }
  }
  messagesEl.appendChild(el);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return el;
}

function createMediaElement({ data, mimeType, displayName }) {
  const wrapper = document.createElement("div");
  wrapper.className = "message-media";
  const encrpytedData = data.replace(/_/g, "/").replace(/-/g, "+");
  if (mimeType.startsWith("image/")) {
    const img = document.createElement("img");
    img.src = `data:${mimeType};base64,${encrpytedData}`;
    img.alt = displayName;
    img.loading = "lazy";
    wrapper.appendChild(img);
  } else {
    // For non-image files, show a download link
    const link = document.createElement("a");
    link.href = `data:${mimeType};base64,${encrpytedData}`;
    link.download = displayName;
    link.innerHTML = `<i class="fa fa-download"></i> ${displayName}`;
    wrapper.appendChild(link);
  }

  return wrapper;
}

function setSending(isSending) {
  sendBtn.disabled = isSending;
  input.disabled = isSending;
}

// File handling
let currentFile = null;
const filePreview = document.createElement("div");
filePreview.className = "file-preview";
form.insertBefore(filePreview, form.firstChild);

async function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      // Extract the base64 data from the DataURL
      const base64Data = reader.result.split(",")[1];
      resolve({
        data: base64Data,
        displayName: file.name,
        mimeType: file.type,
      });
    };
    reader.onerror = (error) => reject(error);
  });
}

function showFilePreview(file) {
  filePreview.innerHTML = "";
  if (!file) return;

  const wrapper = document.createElement("div");
  wrapper.className = "preview-wrapper";

  if (file.type.startsWith("image/")) {
    const img = document.createElement("img");
    img.className = "message-media preview";
    const reader = new FileReader();
    reader.onload = (e) => (img.src = e.target.result);
    reader.readAsDataURL(file);
    wrapper.appendChild(img);
  } else {
    const fileInfo = document.createElement("div");
    fileInfo.className = "file-info";
    fileInfo.innerHTML = `<i class="fa fa-file"></i> ${file.name}`;
    wrapper.appendChild(fileInfo);
  }

  const removeBtn = document.createElement("button");
  removeBtn.className = "remove-preview";
  removeBtn.innerHTML = '<i class="fa fa-times"></i>';
  removeBtn.onclick = clearFilePreview;
  wrapper.appendChild(removeBtn);

  filePreview.appendChild(wrapper);
}

function clearFilePreview() {
  filePreview.innerHTML = "";
  currentFile = null;
  fileInput.value = "";
}

async function sendMessage(text, attachedFile = null) {
  if (!text && !attachedFile) return;

  // Show user's message
  setSending(true);
  const parts = [];

  if (text) {
    parts.push({ text });
  }

  if (attachedFile) {
    const base64Data = await fileToBase64(attachedFile);
    parts.push({ inlineData: base64Data });
  }

  appendMessage({ parts }, "user");
  clearFilePreview();

  const payload = {
    appName: AgentName,
    newMessage: { role: "user", parts },
    sessionId: activeSessionId,
    stateDelta: null,
    streaming: false,
    userId: "user",
  };

  try {
    const response = await ApiService.post("/run_sse", payload);
    if (response && response.content) {
      appendMessage(response.content, "model");
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }
  } catch (err) {
    console.error("Chat error:", err);
    appendMessage({parts: [{text: "Sorry, there was an error processing your message."}]}, "model");
  } finally {
    setSending(false);
  }
}

// File input handler
fileInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (file) {
    currentFile = file;
    showFilePreview(file);
  }
});

// Form submit
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  input.value = "";
  await sendMessage(text, currentFile);
});

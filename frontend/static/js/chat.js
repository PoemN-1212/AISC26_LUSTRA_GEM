/**
 * 💎 GEM PLATFORM (AISC 2026 - UIT)
 * CHAT CO-PILOT MODULE & DOMAIN-SPECIFIC MARKDOWN ENGINE
 */

// ===================================================================
// 1. CHAT INITIALIZATION & CONTROLLER
// ===================================================================

function initChat() {
  const container = document.getElementById("chat-messages");
  if (!container) return;
  container.innerHTML = "";

  appendGemMessage(
    "👋 Chào bạn! Mình là **Lustra** — Linh vật và Trợ lý AI của Nền tảng **GEM** (AISC 2026 - UIT).\n\n" +
    "Mình ở đây để đồng hành cùng bạn định hướng và khớp nối năng lực Đồ án CNTT với xu hướng tuyển dụng thực tế. Bạn đang có ý tưởng làm đề tài gì cho đồ án tốt nghiệp sắp tới? Hãy chia sẻ tự do nhé:\n" +
    "• **Bài toán muốn giải quyết** (ví dụ: OLAP Bank Transaction Fraud, Web E-Commerce, Hệ thống Bệnh viện,...)\n" +
    "• **Vị trí nghề nghiệp đang hướng tới** (Data Engineer, AI Engineer, Backend, DevOps,...)\n" +
    "• **Quỹ thời gian & công nghệ mong muốn** (3 tháng, 6 tháng, Python, Java,...)"
  );
}

function resetChatSession() {
  currentSessionId = null;
  currentBlueprint = null;
  currentProjectTopic = "";
  latestUserQuery = "";
  currentActiveGaps.clear();

  if (window.GEM_STATE) {
    window.GEM_STATE.currentSessionId = null;
    window.GEM_STATE.currentBlueprint = null;
    window.GEM_STATE.currentProjectTopic = "";
    window.GEM_STATE.latestUserQuery = "";
    window.GEM_STATE.currentActiveGaps.clear();
  }

  initChat();

  const tunerBar = document.getElementById("blueprint-tuner-bar");
  if (tunerBar) tunerBar.style.display = "none";

  const targetRoleBadge = document.getElementById("blueprint-target-role");
  if (targetRoleBadge) targetRoleBadge.textContent = "Chờ phân tích";

  const scoreBadge = document.getElementById("blueprint-readiness-badge");
  if (scoreBadge) scoreBadge.style.display = "none";

  const blueprintContent = document.getElementById("blueprint-content");
  if (blueprintContent) {
    blueprintContent.innerHTML = getEmptyStateHTML();
  }

  showToast("🔄 Đã làm mới phiên hội thoại", "info");
}

function getEmptyStateHTML() {
  return `
    <div class="empty-blueprint-state">
      <div class="mascot-empty-wrapper">
        <div class="mascot-aura-glow"></div>
        <img src="/static/assets/mascot.png" alt="Lustra Crystal Fox Mascot" class="mascot-empty-img" onerror="this.src='/static/assets/gem_logo.png'">
        <div class="mascot-chat-bubble">
          <span class="mascot-bubble-sparkle">✨</span>
          <span>Chào bạn! Mình là <b>Lustra</b>. Hãy chọn 1 đề tài mẫu bên dưới hoặc gõ ý tưởng vào khung chat để mình chẩn đoán độ vênh kỹ năng ngay nhé!</span>
        </div>
      </div>
      <h3 class="empty-title">Trung Tâm Định Hướng & Thẩm Định Năng Lực Đồ Án</h3>
      <p class="empty-desc">
        Hệ thống AI đối chiếu tự động với <b>700 Tin Tuyển Dụng IT TopCV</b> để lượng hóa Điểm Thực Chiến, đề xuất kiến trúc 3 lớp và lộ trình thu hẹp Skill Gap.
      </p>

      <!-- 1-CLICK DEMO SHOWCASE -->
      <div class="demo-showcase-box">
        <div class="demo-showcase-label">✨ Trải nghiệm nhanh các Đề tài Mẫu đo ni đóng giày (1-Click):</div>
        <div class="demo-showcase-buttons">
          <button type="button" class="demo-btn demo-btn-olap" onclick="loadDemoProject('olap')">
            <span class="demo-btn-icon">🏦</span>
            <div class="demo-btn-text">
              <b>OLAP Big Data & Fraud Detection</b>
              <span>Data Engineer · ClickHouse & dbt · 3 Tháng</span>
            </div>
            <span class="demo-arrow">➔</span>
          </button>
          <button type="button" class="demo-btn demo-btn-ecom" onclick="loadDemoProject('ecom')">
            <span class="demo-btn-icon">🛒</span>
            <div class="demo-btn-text">
              <b>Web E-Commerce Đa Kênh Tích Hợp</b>
              <span>Backend Developer · PostgreSQL & Redis · 3 Tháng</span>
            </div>
            <span class="demo-arrow">➔</span>
          </button>
          <button type="button" class="demo-btn demo-btn-ai" onclick="loadDemoProject('ai')">
            <span class="demo-btn-icon">🧠</span>
            <div class="demo-btn-text">
              <b>Hệ Thống Y Tế & Chẩn Đoán AI</b>
              <span>AI / Machine Learning Engineer · FastAPI & Model Serving</span>
            </div>
            <span class="demo-arrow">➔</span>
          </button>
        </div>
      </div>

      <div class="empty-features-grid">
        <div class="empty-feature-item">
          <span class="feature-icon">🎯</span>
          <b>Đo Điểm Thực Chiến</b>
          <span>Lượng hóa độ vênh năng lực theo công thức chuẩn</span>
        </div>
        <div class="empty-feature-item">
          <span class="feature-icon">⚡</span>
          <b>Mô phỏng Kỹ năng Động</b>
          <span>Bật/tắt công nghệ để xem điểm nhảy theo thời gian thực</span>
        </div>
        <div class="empty-feature-item">
          <span class="feature-icon">💼</span>
          <b>Khớp Tin Tuyển Dụng</b>
          <span>Tìm tin tuyển dụng TopCV thật sát nhất với đồ án</span>
        </div>
        <div class="empty-feature-item">
          <span class="feature-icon">📦</span>
          <b>Gói Khởi Động</b>
          <span>Xuất sẵn Dockerfile, docker-compose & README mẫu</span>
        </div>
      </div>
    </div>
  `;
}

function loadDemoProject(type) {
  resetChatSession();
  if (type === "olap") {
    currentProjectTopic = "Hệ thống OLAP Big Data & Phát hiện Gian lận Giao dịch Ngân hàng (Bank Fraud Detection)";
    sendQuickPrompt("tôi muốn làm một đồ án OLAP về bank transaction fraud ấy");
  } else if (type === "ecom") {
    currentProjectTopic = "Website Thương mại Điện tử Đa Kênh Tích Hợp (E-Commerce Platform)";
    sendQuickPrompt("Tôi muốn làm website thương mại điện tử cho cửa hàng nhỏ. Tôi chưa biết nên chọn công nghệ nào.");
  } else if (type === "ai") {
    currentProjectTopic = "Hệ thống Y tế Hỗ trợ Chẩn đoán Hình ảnh & Bệnh án (HealthTech AI)";
    sendQuickPrompt("Tôi muốn làm hệ thống y tế hỗ trợ chẩn đoán hình ảnh và phân tích bệnh án cho bệnh viện, hướng tới AI Engineer.");
  }
}

function sendQuickPrompt(promptText) {
  const input = document.getElementById("chat-input");
  if (!input) return;
  input.value = promptText;
  handleChatSubmit(new Event("submit"));
}

function replyNumberedQuestion(text) {
  const input = document.getElementById("chat-input");
  if (!input) return;
  input.focus();
  input.value = text.trim() + " ";
  input.scrollIntoView({ behavior: "smooth", block: "center" });
  showToast("✍️ Đã chọn câu hỏi, hãy nhập thêm thông tin và nhấn Gửi nhé!", "info");
}

// ===================================================================
// 2. CHAT SUBMISSION & STREAM HANDLING
// ===================================================================

async function handleChatSubmit(e) {
  if (e) e.preventDefault();
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  if (!input) return;

  const text = input.value.trim();
  if (!text) return;

  latestUserQuery = text;
  if (window.GEM_STATE) window.GEM_STATE.latestUserQuery = text;

  // Render User Message
  appendUserMessage(text);
  input.value = "";
  input.disabled = true;
  if (sendBtn) sendBtn.disabled = true;

  // Typing Indicator
  const typingId = appendTypingIndicator();

  // Trigger Blueprint Reloading Banner
  if (typeof setBlueprintReloadingState === "function") {
    setBlueprintReloadingState(true, text);
  }

  try {
    const response = await fetch("/api/consultation/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: currentSessionId,
        message: text,
      }),
    });

    removeTypingIndicator(typingId);

    if (!response.ok) {
      throw new Error(`Máy chủ trả về mã ${response.status}`);
    }

    const data = await response.json();
    currentSessionId = data.session_id;
    if (window.GEM_STATE) window.GEM_STATE.currentSessionId = data.session_id;

    // Render GEM Response with rich formatting
    appendGemMessage(data.reply);

    // Update Live Blueprint
    if (data.blueprint) {
      if (data.blueprint.domain) {
        currentProjectTopic = data.blueprint.domain;
      } else if (!currentProjectTopic) {
        currentProjectTopic = text;
      }
      if (window.GEM_STATE) window.GEM_STATE.currentProjectTopic = currentProjectTopic;

      data.blueprint.idea_text = data.blueprint.domain || currentProjectTopic;
      data.blueprint.user_inquiry = latestUserQuery;
      currentBlueprint = data.blueprint;
      if (window.GEM_STATE) window.GEM_STATE.currentBlueprint = data.blueprint;

      if (typeof renderBlueprint === "function") {
        renderBlueprint(data.blueprint);
      }
      if (typeof triggerBlueprintReloadEffect === "function") {
        triggerBlueprintReloadEffect();
      }
      showToast("✓ Đã cập nhật Báo cáo Định hướng & Thu hẹp Skill Gap!", "success");
    }
  } catch (err) {
    removeTypingIndicator(typingId);
    if (typeof setBlueprintReloadingState === "function") {
      setBlueprintReloadingState(false);
    }
    appendGemMessage("⚠️ Xin lỗi, đã có lỗi kết nối tới máy chủ GEM. Vui lòng kiểm tra lại dịch vụ Backend (port 8000).");
    showToast("Lỗi kết nối Backend", "error");
    console.error("Chat error:", err);
  } finally {
    if (typeof setBlueprintReloadingState === "function") {
      setBlueprintReloadingState(false);
    }
    input.disabled = false;
    if (sendBtn) sendBtn.disabled = false;
    input.focus();
  }
}

// ===================================================================
// 3. MESSAGE BUBBLE BUILDERS
// ===================================================================

function appendUserMessage(text) {
  const container = document.getElementById("chat-messages");
  if (!container) return;

  const div = document.createElement("div");
  div.className = "chat-bubble-container user";
  div.innerHTML = `
    <div class="avatar user" title="Sinh viên / Thí sinh UIT">SV</div>
    <div class="bubble-wrapper">
      <div class="bubble-content">
        <div class="bubble-body">
          <p class="user-bubble-text">${escapeHtml(text)}</p>
        </div>
      </div>
    </div>
  `;
  container.appendChild(div);
  scrollToBottom();
}

function appendGemMessage(markdownText) {
  const container = document.getElementById("chat-messages");
  if (!container) return;

  const div = document.createElement("div");
  div.className = "chat-bubble-container gem";
  div.innerHTML = `
    <div class="avatar gem" title="Lustra — Cố vấn AI GEM (AISC 2026)">
      <img src="/static/assets/mascot.png" class="avatar-logo-img avatar-mascot" alt="Lustra Crystal Fox" onerror="this.src='/static/assets/gem_logo.png'">
    </div>
    <div class="bubble-wrapper">
      <div class="bubble-content">
        <div class="bubble-body">
          ${formatMarkdown(markdownText)}
        </div>
        <div class="bubble-actions-toolbar">
          <div class="toolbar-left-actions">
            <button type="button" class="bubble-action-btn copy-action-btn" onclick="copyMessageText(this)" title="Sao chép toàn bộ phản hồi">
              <svg class="action-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
              <span class="btn-text">Sao chép</span>
            </button>
            <button type="button" class="bubble-action-btn tts-action-btn" onclick="speakMessageText(this)" title="Nghe đọc tư vấn bằng giọng nói AI">
              <svg class="action-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
              </svg>
              <span class="btn-text">Đọc AI</span>
            </button>
          </div>
          <div class="bubble-meta-tag">
            <span class="meta-dot"></span>
            <span>Lustra Cố Vấn AISC 2026</span>
          </div>
        </div>
      </div>
    </div>
  `;
  container.appendChild(div);
  scrollToBottom();
}

function appendTypingIndicator() {
  const id = "typing-" + Date.now();
  const container = document.getElementById("chat-messages");
  if (!container) return id;

  const div = document.createElement("div");
  div.id = id;
  div.className = "chat-bubble-container gem";
  div.innerHTML = `
    <div class="avatar gem" title="Lustra">
      <img src="/static/assets/mascot.png" class="avatar-logo-img avatar-mascot" alt="Lustra" onerror="this.src='/static/assets/gem_logo.png'">
    </div>
    <div class="bubble-content" style="color: var(--text-muted); font-style: italic;">
      <span>Lustra đang phân tích độ vênh kỹ năng và đối chiếu TopCV</span>
      <span class="typing-dots">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </span>
    </div>
  `;
  container.appendChild(div);
  scrollToBottom();
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function scrollToBottom() {
  const container = document.getElementById("chat-messages");
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

// ===================================================================
// 4. ACTION TOOLBAR HANDLERS (COPY, TTS, TRANSCRIPT)
// ===================================================================

function copyMessageText(btn) {
  const container = btn.closest(".bubble-content") || btn.closest(".chat-bubble-container");
  if (!container) return;
  const body = container.querySelector(".bubble-body") || container;
  const clone = body.cloneNode(true);
  const toolbar = clone.querySelector(".bubble-actions-toolbar");
  if (toolbar) toolbar.remove();
  const text = clone.innerText.trim();

  navigator.clipboard.writeText(text).then(() => {
    const origHtml = btn.innerHTML;
    btn.classList.add("copied");
    btn.innerHTML = `
      <svg class="action-icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="20 6 9 17 4 12"></polyline>
      </svg>
      <span class="btn-text" style="color: #10b981; font-weight: 700;">Đã chép</span>
    `;
    showToast("📋 Đã sao chép nội dung phản hồi", "success");
    setTimeout(() => {
      btn.classList.remove("copied");
      btn.innerHTML = origHtml;
    }, 2000);
  }).catch(() => {
    showToast("Không thể sao chép tự động", "warning");
  });
}

function speakMessageText(btn) {
  if (!('speechSynthesis' in window)) {
    showToast("Trình duyệt chưa hỗ trợ đọc giọng nói", "warning");
    return;
  }
  if (window.speechSynthesis.speaking) {
    window.speechSynthesis.cancel();
    btn.classList.remove("speaking");
    const label = btn.querySelector(".btn-text");
    if (label) label.textContent = "Đọc AI";
    showToast("⏹️ Đã dừng đọc", "info");
    return;
  }
  const container = btn.closest(".bubble-content") || btn.closest(".chat-bubble-container");
  if (!container) return;
  const body = container.querySelector(".bubble-body") || container;
  const rawText = body.innerText.replace(/[•#*`_~]/g, " ").replace(/\s+/g, " ").trim();
  if (!rawText) return;

  const utterance = new SpeechSynthesisUtterance(rawText);
  utterance.lang = "vi-VN";
  utterance.rate = 1.05;
  utterance.pitch = 1.0;

  btn.classList.add("speaking");
  const label = btn.querySelector(".btn-text");
  if (label) label.textContent = "Dừng đọc";

  utterance.onend = () => {
    btn.classList.remove("speaking");
    if (label) label.textContent = "Đọc AI";
  };
  utterance.onerror = () => {
    btn.classList.remove("speaking");
    if (label) label.textContent = "Đọc AI";
  };

  window.speechSynthesis.speak(utterance);
  showToast("🔊 GEM đang đọc phản hồi bằng giọng nói...", "info");
}

function exportChatTranscript() {
  const messages = document.querySelectorAll("#chat-messages .chat-bubble-container");
  if (messages.length <= 1) {
    showToast("⚠️ Chưa có nội dung hội thoại nào để lưu!", "info");
    return;
  }

  let markdown = `# 💎 BẢN GHI HỘI THOẠI CỐ VẤN ĐỒ ÁN CNTT — GEM PLATFORM (AISC 2026)\n`;
  markdown += `*Thời gian xuất:* ${new Date().toLocaleString("vi-VN")}\n`;
  markdown += `*Hệ thống:* Dual Engine Google Gemini Flash & Local Qwen 2.5 · TopCV Vietnam Intelligence\n\n---\n\n`;

  messages.forEach(msg => {
    const isUser = msg.classList.contains("user");
    const sender = isUser ? "🧑‍🎓 **Sinh Viên**" : "💎 **Cố Vấn GEM**";
    const bubble = msg.querySelector(".bubble-content");
    if (!bubble) return;
    const clone = bubble.cloneNode(true);
    const toolbar = clone.querySelector(".bubble-actions-toolbar");
    if (toolbar) toolbar.remove();
    markdown += `### ${sender}:\n${clone.innerText.trim()}\n\n`;
  });

  const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `GEM_Lich_Su_Tu_Van_${Date.now()}.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  showToast("💾 Đã lưu lịch sử tư vấn ra file Markdown", "success");
}

// ===================================================================
// 5. VOICE & FILE INPUT TOOLS
// ===================================================================

function toggleVoiceRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    showToast("⚠️ Trình duyệt chưa hỗ trợ Web Speech API. Vui lòng dùng Google Chrome hoặc Microsoft Edge.", "error");
    return;
  }

  const voiceBtn = document.getElementById("voice-input-btn");
  const voiceIcon = document.getElementById("voice-icon");
  const statusText = document.getElementById("voice-status-text");
  const chatInput = document.getElementById("chat-input");

  if (isVoiceListening) {
    if (voiceRecognition) voiceRecognition.stop();
    isVoiceListening = false;
    if (voiceBtn) voiceBtn.classList.remove("listening");
    if (voiceIcon) voiceIcon.textContent = "🎙️";
    if (statusText) statusText.style.display = "none";
    showToast("⏹️ Đã dừng ghi âm", "info");
    return;
  }

  try {
    voiceRecognition = new SpeechRecognition();
    voiceRecognition.lang = "vi-VN";
    voiceRecognition.continuous = false;
    voiceRecognition.interimResults = false;

    voiceRecognition.onstart = () => {
      isVoiceListening = true;
      if (voiceBtn) voiceBtn.classList.add("listening");
      if (voiceIcon) voiceIcon.textContent = "🛑";
      if (statusText) statusText.style.display = "inline";
      showToast("🎙️ Đang nghe... Hãy nói ý tưởng đề tài bằng Tiếng Việt", "info");
    };

    voiceRecognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (transcript && chatInput) {
        chatInput.value = (chatInput.value ? chatInput.value + " " : "") + transcript;
        chatInput.focus();
        showToast("✓ Đã nhận diện giọng nói", "success");
      }
    };

    voiceRecognition.onerror = (event) => {
      console.warn("Speech recognition error:", event.error);
      isVoiceListening = false;
      if (voiceBtn) voiceBtn.classList.remove("listening");
      if (voiceIcon) voiceIcon.textContent = "🎙️";
      if (statusText) statusText.style.display = "none";
      if (event.error !== "no-speech") {
        showToast(`⚠️ Lỗi giọng nói: ${event.error}`, "error");
      }
    };

    voiceRecognition.onend = () => {
      isVoiceListening = false;
      if (voiceBtn) voiceBtn.classList.remove("listening");
      if (voiceIcon) voiceIcon.textContent = "🎙️";
      if (statusText) statusText.style.display = "none";
    };

    voiceRecognition.start();
  } catch (err) {
    console.error("Voice recognition failed:", err);
    showToast("Không thể khởi động ghi âm: " + err.message, "error");
  }
}

function triggerFileInput() {
  const fileInput = document.getElementById("syllabus-file-input");
  if (fileInput) fileInput.click();
}

function handleFileUpload(event) {
  const file = event.target.files && event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    const content = e.target.result;
    const chatInput = document.getElementById("chat-input");
    if (!chatInput) return;
    const summary = content.substring(0, 1000);
    chatInput.value = `Tôi có tóm tắt đề cương đề tài (${file.name}):\n"${summary}${content.length > 1000 ? '...' : ''}"\nHãy phân tích và định hướng đồ án cho tôi.`;
    chatInput.focus();
    showToast(`📎 Đã đọc file "${file.name}" (${file.size} bytes)`, "success");
  };
  reader.onerror = () => {
    showToast("⚠️ Không thể đọc file văn bản này", "error");
  };
  reader.readAsText(file);
}

// ===================================================================
// 6. RICH DOMAIN-SPECIFIC MARKDOWN ENGINE (AISC 2026)
// ===================================================================

function formatMarkdown(text) {
  if (!text) return "";
  let raw = String(text).trim();

  // Normalize newlines
  raw = raw.replace(/\r\n/g, "\n").replace(/\r/g, "\n");

  // Code blocks: ```lang ... ```
  const codeBlocks = [];
  raw = raw.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (match, lang, code) => {
    const idx = codeBlocks.length;
    const langLabel = lang ? lang.toUpperCase() : "CODE";
    codeBlocks.push(`
      <div class="chat-code-card">
        <div class="code-card-header">
          <span class="code-lang-tag">${escapeHtml(langLabel)}</span>
          <button type="button" class="code-copy-btn" onclick="copySnippet(this)">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
            <span>Sao chép</span>
          </button>
        </div>
        <pre class="code-pre"><code>${escapeHtml(code.trim())}</code></pre>
      </div>
    `);
    return `__CODE_BLOCK_${idx}__`;
  });

  // Split into paragraphs / sections
  const blocks = raw.split(/\n{2,}/);
  const htmlBlocks = blocks.map(block => {
    block = block.trim();
    if (!block) return "";

    // Code block placeholder
    if (/^__CODE_BLOCK_\d+__$/.test(block)) {
      const idx = parseInt(block.replace("__CODE_BLOCK_", "").replace("__", ""), 10);
      return codeBlocks[idx] || "";
    }

    // Horizontal Divider: --- or ***
    if (/^(---|---|\*\*\*|___)$/.test(block)) {
      return `<div class="chat-section-divider"><span class="divider-line"></span><span class="divider-gem">💎</span><span class="divider-line"></span></div>`;
    }

    // Headings: ###, ##, #
    if (/^#{1,4}\s+(.+)$/m.test(block)) {
      const match = block.match(/^(#{1,4})\s+(.+)$/m);
      if (match) {
        const level = match[1].length;
        const headingContent = formatInline(match[2]);
        const restOfBlock = block.slice(match[0].length).trim();
        const restHtml = restOfBlock ? `<div class="heading-subcontent">${formatBlockContent(restOfBlock)}</div>` : "";

        let iconHtml = `<span class="heading-icon-badge default">💎 Chẩn đoán</span>`;
        if (headingContent.includes("1.") || headingContent.includes("Nền tảng") || headingContent.includes("Điểm mạnh") || headingContent.includes("Gap 1")) {
          iconHtml = `<span class="heading-icon-badge strength">🎯 Điểm mạnh sẵn có</span>`;
        } else if (headingContent.includes("2.") || headingContent.includes("Khoảng cách") || headingContent.includes("Actionable Gaps") || headingContent.includes("Gap 2")) {
          iconHtml = `<span class="heading-icon-badge gap">⚡ Gaps cần lấp đầy</span>`;
        } else if (headingContent.includes("3.") || headingContent.includes("Cảnh báo") || headingContent.includes("Over-Engineering") || headingContent.includes("Tránh sa lầy")) {
          iconHtml = `<span class="heading-icon-badge warning">⚠️ Tránh sa lầy</span>`;
        } else if (headingContent.includes("4.") || headingContent.includes("bước tiếp theo") || headingContent.includes("Lộ trình") || headingContent.includes("Hành động")) {
          iconHtml = `<span class="heading-icon-badge next">🚀 Bước tiếp theo</span>`;
        } else if (headingContent.includes("Câu hỏi") || headingContent.includes("💬") || headingContent.includes("Probing") || headingContent.includes("tương tác mở")) {
          iconHtml = `<span class="heading-icon-badge question">💬 Câu hỏi tương tác</span>`;
        }

        return `
          <div class="chat-heading-wrapper level-${level}">
            <div class="chat-heading-title">
              ${iconHtml}
              <h${level} class="chat-h${level}">${headingContent}</h${level}>
            </div>
            ${restHtml}
          </div>
        `;
      }
    }

    // Callout Note Card: *(Lưu ý: ...)* or *(Cảnh báo: ...)*
    if (/^\*\((?:Lưu ý|Chú ý|Mẹo|Gợi ý|Cảnh báo):\s*([\s\S]+?)\)\*$/.test(block)) {
      const match = block.match(/^\*\((?:Lưu ý|Chú ý|Mẹo|Gợi ý|Cảnh báo):\s*([\s\S]+?)\)\*$/);
      const content = formatInline(match[1]);
      return `
        <div class="chat-callout-card note">
          <div class="callout-icon">💡</div>
          <div class="callout-body">
            <span class="callout-tag">Lưu ý cố vấn</span>
            <p>${content}</p>
          </div>
        </div>
      `;
    }

    // Blockquote: > text
    if (/^>\s*([\s\S]+)$/.test(block)) {
      const bqText = block.replace(/^>\s*/gm, "");
      return `
        <div class="chat-callout-card question" style="border-left: 3px solid var(--accent-cyan); background: rgba(6, 182, 212, 0.06); padding: 0.85rem 1rem; border-radius: 8px; margin: 0.75rem 0;">
          <div style="font-weight: 600; color: var(--accent-cyan); margin-bottom: 0.35rem; font-size: 0.78rem;">💬 Gợi ý thảo luận từ GEM:</div>
          <div style="font-style: italic; color: var(--text-primary); font-size: 0.88rem; line-height: 1.6;">${formatBlockContent(bqText)}</div>
        </div>
      `;
    }

    // Numbered Questions group (Interactive Probing questions)
    // Only match when items end with '?' or look like actual questions
    if (/^1\.\s+[\s\S]+\?\s*\n2\.\s+[\s\S]+/i.test(block)) {
      const items = block.split(/\n(?=\d+\.\s+)/);
      const itemsHtml = items.map(item => {
        const m = item.match(/^(\d+)\.\s+([\s\S]+)$/);
        if (!m) return `<p class="chat-line">${formatInline(item)}</p>`;
        const num = m[1];
        const qText = formatInline(m[2]);
        const cleanPrompt = m[2].replace(/'/g, "\\'").replace(/\n/g, " ").trim();
        return `
          <div class="chat-probing-card" onclick="replyNumberedQuestion('Trả lời câu ${num}: ')" title="Nhấn để trả lời câu hỏi này">
            <div class="probing-number">${num}</div>
            <div class="probing-text">${qText}</div>
            <span class="probing-action-hint">✍️ Trả lời</span>
          </div>
        `;
      }).join("");
      return `<div class="chat-probing-group">${itemsHtml}</div>`;
    }

    return `<div class="chat-text-paragraph">${formatBlockContent(block)}</div>`;
  });

  return htmlBlocks.filter(b => b.trim().length > 0).join("");
}

function formatBlockContent(text) {
  const lines = text.split("\n");
  const result = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();
    if (!trimmed) continue;

    // Blockquote line: > "text"
    if (/^>\s*(.+)$/.test(trimmed)) {
      const bqMatch = trimmed.match(/^>\s*(.+)$/);
      result.push(`
        <div class="chat-callout-card question" style="border-left: 3px solid var(--accent-cyan); background: rgba(6, 182, 212, 0.06); padding: 0.75rem 1rem; border-radius: 8px; margin: 0.65rem 0;">
          <div style="font-weight: 700; color: var(--accent-cyan); margin-bottom: 0.25rem; font-size: 0.78rem;">💬 Gợi ý thảo luận từ GEM:</div>
          <div style="font-style: italic; color: var(--text-primary); font-size: 0.88rem; line-height: 1.6;">${formatInline(bqMatch[1])}</div>
        </div>
      `);
      continue;
    }

    // Key-value special artifacts / reasons / solutions (e.g. * Lý do:*, * Bằng chứng nộp:*, Artifact trên Git:*, Giải pháp:*, Tránh xa:*, Thay vào đó:*)
    const kvRegex = /^\s*[•*-]?\s*\*?(Lý do|Bằng chứng nộp|Artifact|Artifact trên Git|Giải pháp|Tránh xa|Thay vào đó|Tại sao)\*?:\*?\s*(.+)$/i;
    if (kvRegex.test(trimmed)) {
      const kvMatch = trimmed.match(kvRegex);
      const key = kvMatch[1].toLowerCase();
      let icon = "🔹";
      let tagClass = "sub-generic";
      let label = kvMatch[1] + ":";

      if (key.includes("lý do")) {
        icon = "🎯";
        tagClass = "sub-reason";
        label = "Lý do cốt lõi:";
      } else if (key.includes("bằng chứng") || key.includes("artifact")) {
        icon = "📦";
        tagClass = "sub-artifact";
        label = "Bằng chứng nộp Git (Artifacts):";
      } else if (key.includes("tránh xa")) {
        icon = "⚠️";
        tagClass = "sub-warning";
        label = "Cần tránh sa lầy:";
      } else if (key.includes("thay vào đó") || key.includes("giải pháp")) {
        icon = "💡";
        tagClass = "sub-solution";
        label = "Giải pháp kiến trúc đề xuất:";
      } else if (key.includes("tại sao")) {
        icon = "⚡";
        tagClass = "sub-why";
        label = "Giải thích:";
      }

      result.push(`
        <div class="chat-sub-bullet-card ${tagClass}">
          <span class="sub-bullet-icon">${icon}</span>
          <div class="sub-bullet-body"><strong>${label}</strong> ${formatInline(kvMatch[2])}</div>
        </div>
      `);
      continue;
    }

    // Nested sub-bullet with leading spaces: "  * Lý do: ..." or "  * Bằng chứng nộp: ..."
    if (/^\s{2,}\*\s+(.+)$/.test(line)) {
      const subMatch = line.match(/^\s{2,}\*\s+(.+)$/);
      let content = subMatch[1];
      let icon = "🔹";
      let tagClass = "sub-generic";

      if (/^\*?Lý do:\*?/i.test(content)) {
        icon = "🎯";
        tagClass = "sub-reason";
        content = content.replace(/^\*?Lý do:\*?\s*/i, "<strong>Lý do cốt lõi:</strong> ");
      } else if (/^\*?(?:Bằng chứng nộp|Artifact|Artifact trên Git):\*?/i.test(content)) {
        icon = "📦";
        tagClass = "sub-artifact";
        content = content.replace(/^\*?(?:Bằng chứng nộp|Artifact|Artifact trên Git):\*?\s*/i, "<strong>Bằng chứng cần nộp (Artifacts):</strong> ");
      } else if (/^\*?Tại sao\??\*?/i.test(content)) {
        icon = "⚡";
        tagClass = "sub-why";
        content = content.replace(/^\*?Tại sao\??\*?\s*/i, "<strong>Giải thích:</strong> ");
      } else if (/^\*?Tránh xa:\*?/i.test(content)) {
        icon = "⚠️";
        tagClass = "sub-warning";
        content = content.replace(/^\*?Tránh xa:\*?\s*/i, "<strong>Tránh sa lầy:</strong> ");
      }

      result.push(`
        <div class="chat-sub-bullet-card ${tagClass}">
          <span class="sub-bullet-icon">${icon}</span>
          <div class="sub-bullet-body">${formatInline(content)}</div>
        </div>
      `);
      continue;
    }

    // Main Bullet item: • or - or *
    if (/^[•*-]\s+(.+)$/.test(trimmed)) {
      const itemMatch = trimmed.match(/^[•*-]\s+(.+)$/);
      let itemContent = itemMatch[1];
      const isTechHeader = /^\*\*[^*]+(?:\d+(?:\.\d+)?%\s*JD)[^*]*\*\*/i.test(itemContent);

      result.push(`
        <div class="chat-main-bullet-item ${isTechHeader ? 'tech-spec-item' : ''}">
          <span class="bullet-dot"></span>
          <div class="bullet-content">${formatInline(itemContent)}</div>
        </div>
      `);
      continue;
    }

    // Numbered item: 1. ...
    if (/^\d+\.\s+(.+)$/.test(trimmed)) {
      const numMatch = trimmed.match(/^(\d+)\.\s+(.+)$/);
      const num = numMatch[1];
      const content = numMatch[2];
      
      // If content is a question ending with '?', provide reply button
      const isQuestion = content.trim().endsWith("?");
      result.push(`
        <div class="chat-numbered-item">
          <span class="chat-num-badge">${num}</span>
          <div class="chat-num-content">
            ${formatInline(content)}
            ${isQuestion ? `<button type="button" class="reply-question-btn" onclick="replyNumberedQuestion('Trả lời câu ${num}: ')">✍️ Trả lời</button>` : ""}
          </div>
        </div>
      `);
      continue;
    }

    // Regular text line
    if (trimmed.length > 0) {
      result.push(`<p class="chat-line">${formatInline(trimmed)}</p>`);
    }
  }

  return result.join("");
}

function formatInline(str) {
  if (!str) return "";
  let out = escapeHtml(str);

  // Bold: **text**
  out = out.replace(/\*\*(.*?)\*\*/g, "<strong class=\"chat-strong\">$1</strong>");

  // Italic: *text*
  out = out.replace(/(^|[^\*])\*([^\*]+)\*([^\*]|$)/g, "$1<em class=\"chat-em\">$2</em>$3");

  // Inline Code: `code`
  out = out.replace(/`([^`]+)`/g, "<code class=\"chat-inline-code\">$1</code>");

  // Market Demand JD tags: (30.43% JD), (17.39% JD)
  out = out.replace(/\(?(\d+(?:\.\d+)?%\s*JD)\)?/gi, "<span class=\"chat-jd-tag\"><span class=\"jd-pulse\"></span>$1</span>");

  // Score Badge: 89/100
  out = out.replace(/\b(89\/100|\d{1,3}\/100)\b/g, "<span class=\"chat-score-badge\">$1</span>");

  // Metric Green: +44% khoảng cách
  out = out.replace(/\b(\+\d+%\s*khoảng cách[^\s,.<>)]*)/gi, "<span class=\"chat-metric-green\">$1</span>");

  return out;
}

function copySnippet(btn) {
  const card = btn.closest(".chat-code-card");
  if (!card) return;
  const code = card.querySelector("code");
  if (!code) return;
  navigator.clipboard.writeText(code.innerText.trim()).then(() => {
    const orig = btn.innerHTML;
    btn.innerHTML = `<span>✓ Đã chép</span>`;
    showToast("📋 Đã sao chép đoạn mã", "success");
    setTimeout(() => { btn.innerHTML = orig; }, 2000);
  });
}

// ===================================================================
// 7. WINDOW GLOBAL ATTACHMENTS
// ===================================================================

window.initChat = initChat;
window.resetChatSession = resetChatSession;
window.loadDemoProject = loadDemoProject;
window.sendQuickPrompt = sendQuickPrompt;
window.replyNumberedQuestion = replyNumberedQuestion;
window.handleChatSubmit = handleChatSubmit;
window.appendUserMessage = appendUserMessage;
window.appendGemMessage = appendGemMessage;
window.appendTypingIndicator = appendTypingIndicator;
window.removeTypingIndicator = removeTypingIndicator;
window.scrollToBottom = scrollToBottom;
window.copyMessageText = copyMessageText;
window.speakMessageText = speakMessageText;
window.exportChatTranscript = exportChatTranscript;
window.toggleVoiceRecognition = toggleVoiceRecognition;
window.triggerFileInput = triggerFileInput;
window.handleFileUpload = handleFileUpload;
window.formatMarkdown = formatMarkdown;
window.formatBlockContent = formatBlockContent;
window.formatInline = formatInline;
window.copySnippet = copySnippet;
window.getEmptyStateHTML = getEmptyStateHTML;

window.GEM_CHAT = {
  initChat,
  resetChatSession,
  loadDemoProject,
  sendQuickPrompt,
  replyNumberedQuestion,
  handleChatSubmit,
  appendUserMessage,
  appendGemMessage,
  appendTypingIndicator,
  removeTypingIndicator,
  scrollToBottom,
  copyMessageText,
  speakMessageText,
  exportChatTranscript,
  toggleVoiceRecognition,
  triggerFileInput,
  handleFileUpload,
  formatMarkdown,
  formatBlockContent,
  formatInline,
  copySnippet,
};

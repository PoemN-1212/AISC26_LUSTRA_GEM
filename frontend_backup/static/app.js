/**
 * 💎 GEM (LUSTRA_GEM) - Modern Interactive Frontend Controller
 * AISC 2026 · Nền tảng AI Định hướng và Khớp nối Năng lực Đồ án CNTT với Xu hướng Tuyển dụng
 */

// STATE MANAGEMENT
let currentSessionId = null;
let currentBlueprint = null;
let currentActiveGaps = new Set();
let allRolesCache = [];
let currentExportTab = "readme";
let voiceRecognition = null;
let isVoiceListening = false;
let currentSelectedDomain = "Tất cả";
let roleProfilesCache = {};
let currentProjectTopic = "";
let latestUserQuery = "";

// DOM READY
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initChat();
  loadMarketRoles();
  initKeyboardShortcuts();
});

function initKeyboardShortcuts() {
  document.addEventListener("keydown", (e) => {
    // Ctrl + Enter to send chat message
    if (e.ctrlKey && e.key === "Enter") {
      const chatInput = document.getElementById("chat-input");
      if (chatInput && chatInput.value.trim()) {
        e.preventDefault();
        handleChatSubmit(new Event("submit"));
      }
    }
    // "/" key to focus chat input (when not typing elsewhere)
    if (e.key === "/" && document.activeElement.tagName !== "INPUT" && document.activeElement.tagName !== "TEXTAREA") {
      const chatInput = document.getElementById("chat-input");
      if (chatInput) {
        e.preventDefault();
        chatInput.focus();
      }
    }
    // Escape key to close modals
    if (e.key === "Escape") {
      closeExportModal();
      closeRoleCompareModal();
    }
  });
}

// ===================================================================
// 1. THEME SWITCHER (DARK / LIGHT MODE)
// ===================================================================
function initTheme() {
  const savedTheme = localStorage.getItem("gem_theme") || "dark";
  document.documentElement.setAttribute("data-theme", savedTheme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "dark";
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("gem_theme", next);
  showToast(next === "light" ? "☀️ Đã chuyển sang Chế độ Sáng" : "🌙 Đã chuyển sang Chế độ Tối", "info");
}

// ===================================================================
// 2. TAB SWITCHER
// ===================================================================
function switchTab(tabId) {
  document.querySelectorAll(".tab-pane").forEach(pane => {
    pane.classList.remove("active");
    pane.setAttribute("aria-hidden", "true");
  });
  document.querySelectorAll(".nav-tab-btn").forEach(btn => {
    btn.classList.remove("active");
    btn.setAttribute("aria-selected", "false");
  });

  const targetPane = document.getElementById(`tab-pane-${tabId}`);
  const targetBtn = document.getElementById(`tab-btn-${tabId}`);

  if (targetPane) {
    targetPane.classList.add("active");
    targetPane.setAttribute("aria-hidden", "false");
  }
  if (targetBtn) {
    targetBtn.classList.add("active");
    targetBtn.setAttribute("aria-selected", "true");
  }
}

// ===================================================================
// 3. CHAT CO-PILOT CONTROLLER
// ===================================================================
function initChat() {
  const container = document.getElementById("chat-messages");
  container.innerHTML = "";

  appendGemMessage(
    "👋 Chào bạn! Mình là **GEM** — Nền tảng AI định hướng và khớp nối năng lực Đồ án CNTT với xu hướng tuyển dụng (AISC 2026 - UIT).\n\n" +
    "Bạn đang có ý tưởng làm đề tài gì cho đồ án tốt nghiệp sắp tới? Hãy chia sẻ tự do:\n" +
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
  initChat();

  const tunerBar = document.getElementById("blueprint-tuner-bar");
  if (tunerBar) tunerBar.style.display = "none";

  const blueprintContent = document.getElementById("blueprint-content");
  blueprintContent.innerHTML = `
    <div class="empty-blueprint-state">
      <div class="empty-icon-wrapper">
        <span class="empty-icon">💡</span>
      </div>
      <h3 class="empty-title">Chưa có ý tưởng nào được phân tích</h3>
      <p class="empty-desc">
        Hãy nhập mô tả bài toán đồ án của bạn ở khung bên trái hoặc bấm vào một trong các <b>nút gợi ý nhanh</b>.
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

  document.getElementById("blueprint-target-role").textContent = "Chờ phân tích";
  const scoreBadge = document.getElementById("blueprint-readiness-badge");
  scoreBadge.style.display = "none";
  showToast("🔄 Đã làm mới phiên hội thoại", "info");
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
      if (transcript) {
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
    const copyBtn = clone.querySelector(".bubble-copy-btn");
    if (copyBtn) copyBtn.remove();
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

function replyNumberedQuestion(text) {
  const input = document.getElementById("chat-input");
  if (!input) return;
  input.focus();
  input.value = text.trim() + " ";
  input.scrollIntoView({ behavior: "smooth", block: "center" });
  showToast("✍️ Đã chọn câu hỏi, hãy nhập thêm thông tin và nhấn Gửi nhé!", "info");
}

function sendQuickPrompt(promptText) {
  const input = document.getElementById("chat-input");
  input.value = promptText;
  handleChatSubmit(new Event("submit"));
}

async function handleChatSubmit(e) {
  if (e) e.preventDefault();
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const text = input.value.trim();

  if (!text) return;

  // Ghi nhận câu hỏi/nội dung mới nhất của người dùng
  latestUserQuery = text;

  // Render User Message bên trái
  appendUserMessage(text);
  input.value = "";
  input.disabled = true;
  sendBtn.disabled = true;

  // Render Typing Indicator cho cột Chat bên trái
  const typingId = appendTypingIndicator();

  // BẬT TRẠNG THÁI RELOAD / LOADING CHO MÀN HÌNH BÁO CÁO BÊN PHẢI (BLUEPRINT PANEL)
  setBlueprintReloadingState(true, text);

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

    // Render GEM response bên trái
    appendGemMessage(data.reply);

    // Update Live Blueprint bên phải
    if (data.blueprint) {
      if (data.blueprint.domain) {
        currentProjectTopic = data.blueprint.domain;
      } else if (!currentProjectTopic) {
        currentProjectTopic = text;
      }
      data.blueprint.idea_text = data.blueprint.domain || currentProjectTopic;
      data.blueprint.user_inquiry = latestUserQuery;
      currentBlueprint = data.blueprint;

      // Render lại màn hình báo cáo bên phải với dữ liệu mới
      renderBlueprint(data.blueprint);
      
      // Hiệu ứng reload nhấp nháy highlight & toast thông báo
      triggerBlueprintReloadEffect();
      showToast("✓ Đã cập nhật Báo cáo Định hướng & Thu hẹp Skill Gap!", "success");
    }
  } catch (err) {
    removeTypingIndicator(typingId);
    setBlueprintReloadingState(false);
    appendGemMessage("⚠️ Xin lỗi, đã có lỗi kết nối tới máy chủ GEM. Vui lòng kiểm tra lại dịch vụ Backend (port 8000).");
    showToast("Lỗi kết nối Backend", "error");
    console.error("Chat error:", err);
  } finally {
    setBlueprintReloadingState(false);
    input.disabled = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

function setBlueprintReloadingState(isLoading, queryText) {
  const roleBadge = document.getElementById("blueprint-target-role");
  const blueprintContent = document.getElementById("blueprint-content");
  if (!blueprintContent) return;

  if (isLoading) {
    // 1. Cập nhật header badge bên phải
    if (roleBadge) {
      roleBadge.dataset.origText = roleBadge.textContent;
      roleBadge.innerHTML = `<span class="reloading-spin">🔄</span> Đang cập nhật...`;
      roleBadge.classList.add("role-badge-reloading");
    }

    // 2. Nếu đã có nội dung báo cáo bên phải (đang có .readiness-card)
    const inquiryBox = blueprintContent.querySelector(".readiness-inquiry-box");
    if (inquiryBox && queryText) {
      const inquiryText = inquiryBox.querySelector(".inquiry-text");
      if (inquiryText) {
        inquiryText.innerHTML = `"${escapeHtml(queryText)}" <span class="inquiry-updating-tag">⏳ Đang phân tích...</span>`;
      }
    }

    // Chèn banner Reloading ở đầu màn hình báo cáo bên phải
    let reloadBanner = document.getElementById("blueprint-reload-banner");
    if (!reloadBanner) {
      reloadBanner = document.createElement("div");
      reloadBanner.id = "blueprint-reload-banner";
      reloadBanner.className = "blueprint-reload-banner";
      reloadBanner.innerHTML = `
        <div class="reload-banner-inner">
          <div class="reload-banner-spinner"></div>
          <div class="reload-banner-text">
            <b>Đang tái phân tích độ vênh kỹ năng & cập nhật báo cáo cho câu hỏi mới...</b>
            <span>Hệ thống đang đối chiếu 700 JDs TopCV, tính toán lại điểm thực chiến & ma trận kỹ năng tương ứng.</span>
          </div>
        </div>
      `;
      blueprintContent.insertBefore(reloadBanner, blueprintContent.firstChild);
      blueprintContent.classList.add("blueprint-is-reloading");
      blueprintContent.scrollTop = 0;
    }

    // Nếu là empty state ban đầu (chưa có báo cáo nào)
    const emptyState = blueprintContent.querySelector(".empty-blueprint-state");
    if (emptyState) {
      emptyState.style.display = "none";
      let skeleton = document.getElementById("blueprint-skeleton-loading");
      if (!skeleton) {
        skeleton = document.createElement("div");
        skeleton.id = "blueprint-skeleton-loading";
        skeleton.className = "blueprint-skeleton-loading";
        skeleton.innerHTML = `
          <div class="skeleton-card-pulse">
            <div class="skeleton-shimmer-line skeleton-title"></div>
            <div class="skeleton-shimmer-line skeleton-desc"></div>
            <div class="skeleton-row">
              <div class="skeleton-circle"></div>
              <div class="skeleton-shimmer-line skeleton-col"></div>
            </div>
            <div class="skeleton-shimmer-line skeleton-desc" style="width: 80%; margin-top: 1rem;"></div>
          </div>
        `;
        blueprintContent.appendChild(skeleton);
      }
    }
  } else {
    // Tắt trạng thái loading
    const reloadBanner = document.getElementById("blueprint-reload-banner");
    if (reloadBanner) reloadBanner.remove();
    const skeleton = document.getElementById("blueprint-skeleton-loading");
    if (skeleton) skeleton.remove();
    blueprintContent.classList.remove("blueprint-is-reloading");
    if (roleBadge) {
      roleBadge.classList.remove("role-badge-reloading");
    }
    const emptyState = blueprintContent.querySelector(".empty-blueprint-state");
    if (emptyState && !currentBlueprint) {
      emptyState.style.display = "flex";
    }
  }
}

function triggerBlueprintReloadEffect() {
  const blueprintContent = document.getElementById("blueprint-content");
  if (!blueprintContent) return;
  blueprintContent.classList.remove("blueprint-updated-pulse");
  void blueprintContent.offsetWidth; // Trigger reflow
  blueprintContent.classList.add("blueprint-updated-pulse");
  setTimeout(() => {
    blueprintContent.classList.remove("blueprint-updated-pulse");
  }, 1600);
}

function appendUserMessage(text) {
  const container = document.getElementById("chat-messages");
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
  const div = document.createElement("div");
  div.className = "chat-bubble-container gem";
  div.innerHTML = `
    <div class="avatar gem" title="GEM AI Advisor (AISC 2026)">
      <img src="/static/assets/gem_logo.png" class="avatar-logo-img" alt="GEM">
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
            <span>GEM Cố Vấn AISC 2026</span>
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
  const div = document.createElement("div");
  div.id = id;
  div.className = "chat-bubble-container gem";
  div.innerHTML = `
    <div class="avatar gem"><img src="/static/assets/gem_logo.png" class="avatar-logo-img" alt="GEM"></div>
    <div class="bubble-content" style="color: var(--text-muted); font-style: italic;">
      <span>GEM đang phân tích độ vênh kỹ năng và đối chiếu TopCV</span>
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
  container.scrollTop = container.scrollHeight;
}

// ===================================================================
// 4. LIVE BLUEPRINT & SKILL GAP DIAGNOSIS RENDERER
// ===================================================================
function renderBlueprint(bp) {
  const container = document.getElementById("blueprint-content");
  const roleBadge = document.getElementById("blueprint-target-role");
  const scoreBadge = document.getElementById("blueprint-readiness-badge");

  if (roleBadge) {
    roleBadge.textContent = bp.target_role || "Định hướng";
  }

  // Hiển thị thanh Quick Tuner và đồng bộ giá trị đã chọn
  const tunerBar = document.getElementById("blueprint-tuner-bar");
  if (tunerBar) tunerBar.style.display = "flex";
  const tunerSelect = document.getElementById("tuner-role-select");
  if (tunerSelect && bp.target_role) {
    tunerSelect.value = bp.target_role;
  }

  const gap = bp.skill_gap_report || {};
  const metrics = bp.readiness_metrics || gap.metrics || {};
  const score = metrics.readiness_score || 80;

  if (scoreBadge) {
    scoreBadge.textContent = `🎯 ${score}/100 Điểm Thực Chiến`;
    scoreBadge.style.display = "inline-flex";
  }

  // Khởi tạo set các gap được chọn mặc định là tất cả
  currentActiveGaps.clear();
  if (gap.actionable_gaps) {
    gap.actionable_gaps.forEach((g, idx) => {
      currentActiveGaps.add(g.skill || `gap-${idx}`);
    });
  }

  let html = "";

  // 1. READINESS SCORE DASHBOARD (VỚI SVG GAUGE CIRCLE & RADAR CHART)
  if (metrics.readiness_score !== undefined) {
    const strokeDash = calculateGaugeOffset(score);
    const displayDomain = bp.domain || currentProjectTopic || "Đồ án Kỹ thuật & Công nghệ Thông tin";
    const displayInquiry = bp.user_inquiry || latestUserQuery || "";

    html += `
      <div class="readiness-card">
        <!-- TOP FULL-WIDTH CONTEXT: TOPIC & INQUIRY -->
        <div class="readiness-top-bar">
          <div class="readiness-project-badge" title="Miền đề tài: ${escapeHtml(displayDomain)}">
            <span class="project-badge-tag">💡 Đề tài</span>
            <span class="project-badge-name">${escapeHtml(displayDomain)}</span>
          </div>

          ${displayInquiry ? `
            <div class="readiness-inquiry-box" title="Nội dung/câu hỏi đang hỏi: ${escapeHtml(displayInquiry)}">
              <span class="inquiry-icon">💬</span>
              <div class="inquiry-body">
                <span class="inquiry-label">Nội dung đang hỏi:</span>
                <span class="inquiry-text">"${escapeHtml(displayInquiry)}"</span>
              </div>
            </div>
          ` : ""}
        </div>

        <div class="readiness-hero-row">
          <div class="readiness-info">
            <div class="readiness-title">
              <span>🎯 Điểm Khớp Nối Thực Chiến (Market Readiness)</span>
            </div>

            <div class="readiness-desc">
              Đo lường độ sẵn sàng thực tế khi đối chiếu với <b>${gap.sample_jd_count || 50}</b> tin tuyển dụng <b>${escapeHtml(bp.target_role || "IT")}</b> trên TopCV Việt Nam.
            </div>
          </div>

          <!-- GAUGE CIRCLE -->
          <div class="readiness-gauge-box" title="Điểm thực chiến đồ án">
            <svg class="readiness-gauge-svg" width="94" height="94" viewBox="0 0 100 100">
              <circle class="gauge-bg" cx="50" cy="50" r="45"></circle>
              <circle class="gauge-fill" id="gauge-fill-circle" cx="50" cy="50" r="45" style="stroke-dashoffset: ${strokeDash}; stroke: ${score >= 80 ? 'var(--accent-emerald)' : (score >= 60 ? 'var(--accent-cyan)' : 'var(--accent-amber)')};"></circle>
            </svg>
            <div class="gauge-center">
              <span class="gauge-score-value" id="gauge-score-num" style="color: ${score >= 80 ? 'var(--accent-emerald)' : (score >= 60 ? 'var(--accent-cyan)' : 'var(--accent-amber)')};">${score}</span>
              <span class="gauge-score-label">ĐIỂM</span>
            </div>
          </div>

          <!-- MULTI-DIMENSIONAL RADAR CHART -->
          <div class="readiness-radar-box" title="Radar phân bổ năng lực 5 chiều">
            <span class="radar-title">Radar Năng Lực Đa Chiều</span>
            <div id="radar-chart-container">
              ${generateRadarSvg(metrics.baseline_coverage || 45, metrics.potential_coverage || 85)}
            </div>
            <div class="radar-legend">
              <span class="radar-legend-item"><span class="radar-dot baseline"></span> Xuất phát: ${metrics.baseline_coverage || 45}%</span>
              <span class="radar-legend-item"><span class="radar-dot potential"></span> GEM: <span id="radar-legend-pot">${metrics.potential_coverage || 85}%</span></span>
            </div>
          </div>
        </div>

        <div class="metric-pill-grid">
          <div class="metric-pill">
            <div class="metric-pill-label">Phù hợp ngữ nghĩa</div>
            <div class="metric-pill-val" style="color: var(--accent-cyan);">${metrics.semantic_fit || 85}%</div>
          </div>
          <div class="metric-pill">
            <div class="metric-pill-label">Độ phủ ban đầu</div>
            <div class="metric-pill-val" style="color: var(--text-muted);">${metrics.baseline_coverage || 45}%</div>
          </div>
          <div class="metric-pill">
            <div class="metric-pill-label">Độ phủ sau can thiệp</div>
            <div class="metric-pill-val" id="val-potential-coverage" style="color: var(--accent-emerald);">${metrics.potential_coverage || 85}%</div>
          </div>
          <div class="metric-pill">
            <div class="metric-pill-label">Mức thu hẹp Gap</div>
            <div class="metric-pill-val metric-pill-delta" id="val-gap-delta">${metrics.gap_reduction_delta || "+40%"}</div>
          </div>
        </div>

        <div class="simulator-alert-banner" id="simulator-banner" style="display: none;">
          <span>⚡ Đang mô phỏng thay đổi công nghệ theo thời gian thực!</span>
          <button class="btn-copy-code" style="padding: 0.15rem 0.5rem;" onclick="resetSimulator()">Khôi phục gốc</button>
        </div>
      </div>
    `;
  }

  // 2. SKILL GAP MATRIX (3 NHÓM PHÂN ĐỊNH RẠCH RÒI)
  if (gap.covered_skills || gap.actionable_gaps || gap.deferred_or_overkill) {
    html += `
      <div class="layer-card">
        <span class="section-badge badge-layer1">Phần 1 · Đối chiếu Năng lực</span>
        <div class="layer-title">Ma trận 3 Trạng thái Skill Gap (${escapeHtml(bp.target_role || "IT")})</div>
        <div class="layer-desc">Phân định rõ kỹ năng tự nhiên đã bao phủ, kỹ năng cần bổ sung và kỹ năng nên tạm hoãn:</div>

        <div class="gap-matrix-container">
          <!-- NHÓM 1: ĐÃ BAO PHỦ TỰ NHIÊN -->
          ${gap.covered_skills && gap.covered_skills.length > 0 ? `
            <div class="matrix-group covered">
              <div class="matrix-group-title">
                <span class="matrix-tag-covered">🟢 Đã Bao Phủ trong Kế hoạch Đồ án</span>
                <span style="font-size: 0.7rem; color: var(--text-muted);">(Tự nhiên rèn luyện qua phạm vi đề tài)</span>
              </div>
              <div class="matrix-item-list">
                ${gap.covered_skills.map(s => `
                  <div class="matrix-item">
                    <div class="matrix-item-left">
                      <span class="matrix-item-name">${escapeHtml(s.skill)}</span>
                      <span class="matrix-item-reason">${escapeHtml(s.reason)}</span>
                    </div>
                    <span class="matrix-item-demand" style="color: var(--accent-emerald);">${s.demand_pct ? s.demand_pct + "% JD" : "Core"}</span>
                  </div>
                `).join("")}
              </div>
            </div>
          ` : ""}

          <!-- NHÓM 2: ACTIONABLE GAPS (CẦN BỔ SUNG KÈM BỘ MÔ PHỎNG TOGGLE) -->
          ${gap.actionable_gaps && gap.actionable_gaps.length > 0 ? `
            <div class="matrix-group actionable">
              <div class="matrix-group-title">
                <span class="matrix-tag-actionable">🟡 Cần Xem Xét Bổ Sung (Actionable Gaps)</span>
                <span style="font-size: 0.7rem; color: var(--text-muted);">(Bật/tắt công tắc bên dưới để mô phỏng điểm)</span>
              </div>
              <div class="matrix-item-list">
                ${gap.actionable_gaps.map((g, idx) => `
                  <div class="matrix-item">
                    <div class="matrix-item-left">
                      <div style="display: flex; align-items: center; gap: 0.45rem;">
                        <span class="matrix-item-name">${escapeHtml(g.skill)}</span>
                        <span style="font-size: 0.65rem; background: rgba(245, 158, 11, 0.2); color: var(--accent-amber); padding: 0.1rem 0.35rem; border-radius: 4px; font-weight: 700;">Actionable</span>
                      </div>
                      <span class="matrix-item-reason">${escapeHtml(g.why_needed)}</span>
                    </div>
                    <span class="matrix-item-demand" style="color: var(--accent-amber);">${g.demand_pct ? g.demand_pct + "% JD" : "+Booster"}</span>
                  </div>
                `).join("")}
              </div>
            </div>
          ` : ""}

          <!-- NHÓM 3: TẠM HOÃN / TRÁNH OVER-ENGINEERING -->
          ${gap.deferred_or_overkill && gap.deferred_or_overkill.length > 0 ? `
            <div class="matrix-group deferred">
              <div class="matrix-group-title">
                <span class="matrix-tag-deferred">⚪ Tạm Hoãn / Tránh Over-engineering</span>
                <span style="font-size: 0.7rem; color: var(--text-muted);">(Chưa cần cho MVP, tránh quá tải đồ án)</span>
              </div>
              <div class="matrix-item-list">
                ${gap.deferred_or_overkill.map(d => `
                  <div class="matrix-item">
                    <div class="matrix-item-left">
                      <span class="matrix-item-name" style="color: var(--text-muted);">${escapeHtml(d.skill)}</span>
                      <span class="matrix-item-reason">${escapeHtml(d.reason)}</span>
                    </div>
                    <span class="matrix-item-demand" style="color: var(--text-muted);">${escapeHtml(d.verdict || "Tạm hoãn")}</span>
                  </div>
                `).join("")}
              </div>
            </div>
          ` : ""}
        </div>
      </div>
    `;
  }

  // 3. ACTION & VERIFIABLE PROOF CARDS (CÓ SWITCH TOGGLE MÔ PHỎNG ĐIỂM)
  if (gap.actionable_gaps && gap.actionable_gaps.length > 0) {
    html += `
      <div class="layer-card">
        <span class="section-badge badge-layer2">Phần 2 · Kế hoạch Hành động & Mô phỏng</span>
        <div class="layer-title">Hành Động Can Thiệp & Bằng Chứng Nộp Git (Artifacts)</div>
        <div class="layer-desc">Thử bật/tắt từng kỹ năng dưới đây để thấy <b>Điểm Thực Chiến</b> thay đổi ngay lập tức:</div>

        <div class="action-cards-container">
          ${gap.actionable_gaps.map((g, idx) => {
            const isHigh = (g.priority || "").toLowerCase().includes("cao") || (g.priority || "").toLowerCase().includes("hàng đầu");
            return `
              <div class="action-card" id="action-card-${idx}">
                <div class="action-card-header">
                  <div class="action-card-title-group">
                    <span class="action-card-title">⚡ ${escapeHtml(g.skill)}</span>
                    <span class="priority-pill ${isHigh ? 'priority-high' : 'priority-medium'}">${escapeHtml(g.priority || "Khuyến nghị")}</span>
                    <span style="font-size: 0.72rem; color: var(--accent-cyan); font-weight: 700;">${g.demand_pct ? g.demand_pct + "% JD" : ""}</span>
                  </div>

                  <!-- SIMULATOR TOGGLE SWITCH -->
                  <label class="skill-toggle-control" title="Bật/tắt kỹ năng này để mô phỏng điểm số">
                    <input type="checkbox" class="toggle-switch-input" 
                      data-skill="${escapeHtml(g.skill)}" 
                      data-demand="${g.demand_pct || 25}" 
                      checked 
                      onchange="handleSkillToggle(this)">
                    <div class="toggle-switch-track">
                      <div class="toggle-switch-thumb"></div>
                    </div>
                    <span class="toggle-switch-label">Áp dụng</span>
                  </label>
                </div>

                <div class="action-field">
                  <b>🎯 Lý do kỹ thuật:</b> ${escapeHtml(g.why_needed)}
                </div>

                <div class="action-field">
                  <b>🛠️ Hành động triển khai:</b> ${escapeHtml(g.action_item)}
                </div>

                <div class="proof-artifact-box">
                  <span class="proof-artifact-icon">📦</span>
                  <div class="proof-artifact-text">
                    <b>Bằng chứng nộp Git:</b> ${escapeHtml(g.proof_deliverable)}
                  </div>
                </div>
              </div>
            `;
          }).join("")}
        </div>
      </div>
    `;
  }

  // 4. MODULE MỞ RỘNG HƯỚNG NGHIỆP (LỚP 3)
  if (bp.layer3_extension) {
    const l3 = bp.layer3_extension;
    html += `
      <div class="layer-card" style="border-left: 3px solid var(--accent-purple);">
        <span class="section-badge badge-layer3">Phần 3 · Mở rộng Hướng nghiệp (${escapeHtml(l3.target_role || bp.target_role)})</span>
        <div class="layer-title" style="color: var(--accent-purple);">🚀 ${escapeHtml(l3.proposed_module)}</div>
        <div class="layer-desc" style="margin-top: 0.35rem;">
          <b>Công nghệ đề xuất:</b> <span style="color: var(--accent-cyan); font-weight: 700;">${escapeHtml(l3.technologies)}</span>
        </div>
        <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.75rem; line-height: 1.55;">
          ${escapeHtml(l3.implementation_detail)}
        </p>
        <div style="font-size: 0.75rem; background: rgba(139, 92, 246, 0.08); border-left: 3px solid var(--accent-purple); padding: 0.55rem 0.85rem; border-radius: 4px;">
          <b>💎 Điểm cộng CV phỏng vấn:</b> ${escapeHtml(l3.cv_value)}
        </div>
      </div>
    `;
  }

  // 5. REAL TOPCV MATCHING JDS (TẬN DỤNG QDRANT VECTOR MATCH)
  const matchedJds = bp.matched_jds || [];
  if (matchedJds.length > 0) {
    html += `
      <div class="layer-card" style="border-left: 3px solid var(--accent-cyan);">
        <span class="section-badge" style="background: rgba(6, 182, 212, 0.15); color: var(--accent-cyan); border: 1px solid rgba(6, 182, 212, 0.3);">
          Phần 4 · Khớp Nối Thị Trường TopCV
        </span>
        <div class="layer-title">💼 Cơ Hội Việc Làm Thực Tế Khớp Nhất (${escapeHtml(bp.target_role)})</div>
        <div class="layer-desc">Các tin tuyển dụng thật từ kho dữ liệu TopCV mà đồ án này giúp sinh viên tự tin nộp CV:</div>

        <div class="matched-jds-list">
          ${matchedJds.map(jd => `
            <div class="jd-match-item">
              <div class="jd-match-header">
                <span class="jd-match-title">${escapeHtml(jd.title)}</span>
                <span class="jd-similarity-badge">${(jd.similarity_score ? (jd.similarity_score * 100).toFixed(0) : 88)}% Khớp</span>
              </div>
              <div class="jd-match-company">🏢 ${escapeHtml(jd.company || "Công ty Công nghệ")} · <i>${escapeHtml(jd.role || bp.target_role)}</i></div>
              <div class="jd-match-snippet">${escapeHtml(jd.snippet || "")}</div>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  }

  // 6. LỘ TRÌNH SPRINT THEO THỜI GIAN (ROADMAP)
  if (bp.roadmap && bp.roadmap.length > 0) {
    html += `
      <div class="layer-card">
        <div class="layer-title" style="margin-bottom: 0.75rem;">📅 Lộ trình Sprint Thu hẹp Khoảng cách (${bp.time_months || 3} Tháng)</div>
        <div class="roadmap-container">
          ${bp.roadmap.map(r => `
            <div class="roadmap-phase">
              <div class="phase-title">${escapeHtml(r.phase)}</div>
              ${r.milestones ? `
                <ul class="phase-milestones">
                  ${r.milestones.map(m => `<li>${escapeHtml(m)}</li>`).join("")}
                </ul>
              ` : `<div style="font-size: 0.75rem; color: var(--text-secondary);">${escapeHtml(r.focus || "")}</div>`}
            </div>
          `).join("")}
        </div>
      </div>
    `;
  }

  // 7. GHI CHÚ THAM KHẢO DỰ ÁN CŨ (GITHUB)
  if (bp.reference_projects) {
    const ref = bp.reference_projects;
    html += `
      <div class="layer-card">
        <div style="font-size: 0.82rem; font-weight: 700; color: var(--accent-cyan); margin-bottom: 0.35rem;">
          📚 Dự Án GitHub Thực Tế Tham Khảo
        </div>
        <p style="font-size: 0.76rem; color: var(--text-secondary); line-height: 1.5;">
          ${escapeHtml(ref.message)}
        </p>
        ${ref.projects && ref.projects.length > 0 ? `
          <div style="margin-top: 0.65rem; display: flex; flex-direction: column; gap: 0.45rem;">
            ${ref.projects.map(p => `
              <div style="font-size: 0.75rem; background: var(--bg-surface); padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--border-subtle);">
                🔗 <b>${escapeHtml(p.repo_name)}</b> (${escapeHtml(p.language || "Code")}) — Độ khớp ngữ nghĩa: <b>${(p.similarity_score * 100).toFixed(1)}%</b>
              </div>
            `).join("")}
          </div>
        ` : ""}
      </div>
    `;
  }

  container.innerHTML = html;
}

// ===================================================================
// 5. INTERACTIVE SKILL GAP SIMULATOR (TOGGLE & RECALCULATE)
// ===================================================================
function calculateGaugeOffset(score) {
  // Chu vi hình tròn r=45 là 2 * PI * 45 = 282.74 ~ 283
  const circumference = 283;
  const pct = Math.min(100, Math.max(0, score));
  return circumference - (circumference * pct) / 100;
}

function handleSkillToggle(checkbox) {
  const skill = checkbox.getAttribute("data-skill");
  if (checkbox.checked) {
    currentActiveGaps.add(skill);
  } else {
    currentActiveGaps.delete(skill);
  }

  recalculateSimulatedMetrics();
}

function recalculateSimulatedMetrics() {
  if (!currentBlueprint) return;

  const gap = currentBlueprint.skill_gap_report || {};
  const metrics = currentBlueprint.readiness_metrics || gap.metrics || {};
  const actionableGaps = gap.actionable_gaps || [];

  const baseline = metrics.baseline_coverage || 45;
  const originalPotential = metrics.potential_coverage || 85;
  const semantic = metrics.semantic_fit || 85;

  // Tỷ lệ các kỹ năng actionable đang được bật
  const totalActionable = actionableGaps.length || 1;
  const activeCount = currentActiveGaps.size;
  const activeRatio = activeCount / totalActionable;

  // Tính lại potential coverage & readiness score
  const newPotential = Math.round(baseline + activeRatio * (originalPotential - baseline));
  const newReadiness = Math.round(0.35 * semantic + 0.65 * newPotential);
  const newDelta = `+${newPotential - baseline}%`;

  // Cập nhật DOM
  const gaugeNum = document.getElementById("gauge-score-num");
  const gaugeFill = document.getElementById("gauge-fill-circle");
  const badgeScore = document.getElementById("blueprint-readiness-badge");
  const valPotential = document.getElementById("val-potential-coverage");
  const valDelta = document.getElementById("val-gap-delta");
  const banner = document.getElementById("simulator-banner");

  const scoreColor = newReadiness >= 80 ? 'var(--accent-emerald)' : (newReadiness >= 60 ? 'var(--accent-cyan)' : 'var(--accent-amber)');

  if (gaugeNum) {
    gaugeNum.textContent = newReadiness;
    gaugeNum.style.color = scoreColor;
  }
  if (gaugeFill) {
    gaugeFill.style.strokeDashoffset = calculateGaugeOffset(newReadiness);
    gaugeFill.style.stroke = scoreColor;
  }
  if (badgeScore) badgeScore.textContent = `🎯 ${newReadiness}/100 Điểm Thực Chiến`;
  if (valPotential) valPotential.textContent = `${newPotential}%`;
  if (valDelta) valDelta.textContent = newDelta;

  if (banner) {
    banner.style.display = (activeCount < totalActionable) ? "flex" : "none";
  }

  // Cập nhật Radar Chart đa chiều theo thời gian thực
  const potentialPoly = document.getElementById("radar-potential-poly");
  if (potentialPoly) {
    const cx = 200, cy = 132, maxR = 82;
    const axes = [
      { pFactor: 1.0 },
      { pFactor: 0.98 },
      { pFactor: 0.92 },
      { pFactor: 1.02 },
      { pFactor: 1.0 },
    ];
    const angles = [
      -Math.PI / 2,
      -Math.PI / 2 + (2 * Math.PI) / 5,
      -Math.PI / 2 + (4 * Math.PI) / 5,
      -Math.PI / 2 + (6 * Math.PI) / 5,
      -Math.PI / 2 + (8 * Math.PI) / 5,
    ];
    const newPts = axes.map((axis, i) => {
      const val = Math.min(100, Math.max(15, newPotential * axis.pFactor));
      const r = (val / 100) * maxR;
      const x = (cx + r * Math.cos(angles[i])).toFixed(1);
      const y = (cy + r * Math.sin(angles[i])).toFixed(1);
      return `${x},${y}`;
    }).join(" ");
    potentialPoly.setAttribute("points", newPts);
    potentialPoly.style.stroke = scoreColor;
  }
  const radarLegPot = document.getElementById("radar-legend-pot");
  if (radarLegPot) radarLegPot.textContent = `${newPotential}%`;

  showToast(`🎯 Điểm Thực Chiến mô phỏng: ${newReadiness} điểm (${activeCount}/${totalActionable} kỹ năng)`, "info");
}

function resetSimulator() {
  document.querySelectorAll(".toggle-switch-input").forEach(cb => {
    cb.checked = true;
    currentActiveGaps.add(cb.getAttribute("data-skill"));
  });
  recalculateSimulatedMetrics();
}

// ===================================================================
// 6. STARTER KIT EXPORT MODAL & TEMPLATE GENERATOR
// ===================================================================
function openExportModal() {
  const modal = document.getElementById("export-modal");
  modal.classList.add("active");
  updateExportContent();
}

function closeExportModal(e) {
  if (e && e.target !== e.currentTarget && !e.target.classList.contains("modal-close-btn") && !e.target.classList.contains("btn-modal-close")) {
    return;
  }
  const modal = document.getElementById("export-modal");
  modal.classList.remove("active");
}

function switchModalTab(tabKey) {
  currentExportTab = tabKey;
  document.querySelectorAll(".modal-tab-btn").forEach(btn => btn.classList.remove("active"));
  const btn = document.getElementById(`modal-tab-${tabKey}`);
  if (btn) btn.classList.add("active");
  updateExportContent();
}

function updateExportContent() {
  const bp = currentBlueprint || {};
  const role = bp.target_role || "Backend Developer";
  const idea = bp.idea_text || "Hệ thống CNTT";
  const domain = bp.domain || "Phần mềm & Dữ liệu";
  const filenameEl = document.getElementById("export-filename");
  const codeEl = document.getElementById("export-code-preview");

  let code = "";

  if (currentExportTab === "readme") {
    filenameEl.textContent = "README.md";
    code = `# 💎 Đề Tài: ${idea}
### Định hướng Vị trí: ${role} · Lĩnh vực: ${domain}
*Đồ án áp dụng Chuẩn Kiến trúc Năng lực & Thu hẹp Skill Gap của GEM (AISC 2026 - UIT)*

---

## 🎯 1. Mục tiêu Đề tài & Nghiệp vụ Cốt lõi
- Xây dựng hoàn chỉnh sản phẩm giải quyết bài toán ${domain}.
- Áp dụng các chuẩn công nghệ thực tế đòi hỏi từ thị trường tuyển dụng TopCV Việt Nam.

## 🏗️ 2. Kiến trúc Công nghệ 3 Lớp (GEM Blueprint)
- **Lớp 1 (Core Foundation):** Xây dựng MVP sản phẩm chạy được phục vụ bảo vệ đồ án.
- **Lớp 2 (Career Boosters):** Bổ sung Docker, Redis Caching, CI/CD và Unit Test tự động để nâng cao năng lực thực chiến.
- **Lớp 3 (Personal Extension):** Module chuyên sâu hướng nghiệp theo định hướng ${role}.

## 📦 3. Bằng chứng Bàn giao Kỹ thuật (Verifiable Evidence Artifacts)
- \`Dockerfile\`: Multi-stage build đóng gói ứng dụng.
- \`docker-compose.yml\`: Khởi chạy toàn bộ hệ thống cơ sở dữ liệu và máy chủ.
- \`tests/\`: Bộ kiểm thử tự động đảm bảo chất lượng source code.
- \`docs/api_spec.yaml\`: Tài liệu đặc tả OpenAPI/Swagger.

## 🚀 4. Hướng dẫn Khởi chạy Nhanh
\`\`\`bash
# 1. Khởi động các dịch vụ phụ trợ
docker compose up -d

# 2. Khởi chạy máy chủ ứng dụng
# (Xem hướng dẫn chi tiết trong tài liệu triển khai)
\`\`\`
`;
  } else if (currentExportTab === "docker") {
    filenameEl.textContent = "docker-compose.yml";
    code = `version: "3.8"

services:
  # Cơ sở dữ liệu chính
  postgres:
    image: postgres:15-alpine
    container_name: app_database
    restart: always
    environment:
      POSTGRES_USER: dev_user
      POSTGRES_PASSWORD: dev_password
      POSTGRES_DB: app_db
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  # Caching & Message Queue (Career Booster)
  redis:
    image: redis:7-alpine
    container_name: app_redis
    restart: always
    ports:
      - "6379:6379"

  # Ứng dụng chính (Application Server)
  # app:
  #   build: .
  #   container_name: app_backend
  #   ports:
  #     - "8000:8000"
  #   depends_on:
  #     - postgres
  #     - redis

volumes:
  pgdata:
`;
  } else if (currentExportTab === "report") {
    filenameEl.textContent = "Tom_tat_de_tai_GVHD.md";
    const gap = bp.skill_gap_report || {};
    const metrics = bp.readiness_metrics || gap.metrics || {};
    code = `# BẢN TÓM TẮT ĐỀ TÀI & LUẬN ĐIỂM KỸ THUẬT NỘP GIẢNG VIÊN HƯỚNG DẪN
**Đề tài:** ${idea}
**Sinh viên thực hiện:** Nhóm sinh viên CNTT
**Vị trí nghề nghiệp định hướng:** ${role}

---

### 1. Bối cảnh & Tính cấp thiết của Đề tài
Đề tài tập trung giải quyết bài toán thuộc miền ${domain}. Để đảm bảo đồ án vừa đạt yêu cầu học thuật trên trường, vừa bám sát nhu cầu thực tế của thị trường tuyển dụng lao động IT, nhóm đã sử dụng Nền tảng GEM (AISC 2026) để lượng hóa khoảng cách kỹ năng (Skill Gap).

### 2. Các Chỉ số Định lượng Khoa học (Đạt được qua GEM Engine):
- Điểm Khớp nối Thực chiến (Market Readiness): ${metrics.readiness_score || 80}/100 Điểm.
- Độ bao phủ kỹ năng tự nhiên ban đầu (Baseline Coverage): ${metrics.baseline_coverage || 45}%.
- Độ bao phủ tiềm năng sau khi hoàn thiện (Potential Coverage): ${metrics.potential_coverage || 85}%.
- Mức độ thu hẹp khoảng cách kỹ năng: ${metrics.gap_reduction_delta || "+40%"}.

### 3. Kế hoạch Hành động & Bằng chứng Năng lực nộp vào Git Repo:
${(gap.actionable_gaps || []).map(g => `- Công nghệ: ${g.skill}\n  + Lý do kỹ thuật: ${g.why_needed}\n  + Bằng chứng bàn giao: ${g.proof_deliverable}`).join("\n\n")}

Kính trình Giảng viên hướng dẫn xem xét và phê duyệt!
`;
  }

  codeEl.textContent = code;
}

function copyExportCode() {
  const codeEl = document.getElementById("export-code-preview");
  const copyBtnText = document.getElementById("copy-btn-text");

  navigator.clipboard.writeText(codeEl.textContent).then(() => {
    copyBtnText.textContent = "Đã chép! ✓";
    showToast("📋 Đã sao chép nội dung vào Clipboard", "success");
    setTimeout(() => {
      copyBtnText.textContent = "Sao chép";
    }, 2000);
  });
}

function downloadExportFile() {
  const filename = document.getElementById("export-filename").textContent;
  const content = document.getElementById("export-code-preview").textContent;

  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  showToast(`💾 Đã tải file ${filename} về máy`, "success");
}

// ===================================================================
// 7. TAB 2: MARKET INTELLIGENCE EXPLORER & COMPARISON
// ===================================================================
async function loadMarketRoles() {
  const sidebar = document.getElementById("roles-sidebar");
  try {
    const response = await fetch("/api/market/roles");
    if (!response.ok) return;
    const data = await response.json();

    allRolesCache = data.roles || [];
    if (allRolesCache.length === 0) return;

    // Populate Quick Tuner Dropdown in Blueprint Header
    populateTunerRoles(allRolesCache);

    // Initialize Domain Category Filters
    initDomainFilters();

    // Render roles list
    renderRolesList(allRolesCache);

    // Mặc định nạp vị trí đầu tiên
    if (allRolesCache[0]) {
      loadRoleProfile(allRolesCache[0].specific_role);
    }
  } catch (err) {
    console.error("Lỗi nạp roles:", err);
  }
}

function populateTunerRoles(roles) {
  const select = document.getElementById("tuner-role-select");
  if (!select) return;
  select.innerHTML = "";
  roles.forEach(r => {
    const opt = document.createElement("option");
    opt.value = r.specific_role;
    opt.textContent = `${r.specific_role}`;
    select.appendChild(opt);
  });
}

function handleTunerRoleChange(role) {
  if (!role) return;
  showToast(`🎯 Chuyển hướng mục tiêu nghề nghiệp: ${role}`, "info");
  sendQuickPrompt(`Tôi muốn định hướng nghề nghiệp của đồ án này chuyển sang vị trí ${role}`);
}

function handleTunerTimeChange(months) {
  document.querySelectorAll("#tuner-time-pills .time-pill").forEach(pill => {
    const pMonths = parseInt(pill.getAttribute("data-months"));
    if (pMonths === months) {
      pill.classList.add("active");
    } else {
      pill.classList.remove("active");
    }
  });
  showToast(`⏱️ Điều chỉnh thời gian đồ án sang: ${months} tháng`, "info");
  sendQuickPrompt(`Tôi muốn điều chỉnh thời gian thực hiện đồ án là ${months} tháng, hãy cập nhật lộ trình cho tôi`);
}

function initDomainFilters() {
  const container = document.getElementById("domain-filter-pills");
  if (!container || allRolesCache.length === 0) return;

  const domains = ["Tất cả"];
  allRolesCache.forEach(r => {
    if (r.domain && !domains.includes(r.domain)) {
      domains.push(r.domain);
    }
  });

  let html = "";
  domains.forEach(d => {
    const activeClass = d === currentSelectedDomain ? "active" : "";
    html += `<button type="button" class="domain-pill ${activeClass}" onclick="selectMarketDomain('${escapeHtml(d)}', this)">${escapeHtml(d)}</button>`;
  });
  container.innerHTML = html;
}

function selectMarketDomain(domainName, btnEl) {
  currentSelectedDomain = domainName;
  document.querySelectorAll(".domain-pill").forEach(p => p.classList.remove("active"));
  if (btnEl) btnEl.classList.add("active");

  const searchInput = document.getElementById("role-search-input");
  const query = searchInput ? searchInput.value.toLowerCase().trim() : "";

  let filtered = allRolesCache;
  if (domainName !== "Tất cả") {
    filtered = filtered.filter(r => r.domain === domainName);
  }
  if (query) {
    filtered = filtered.filter(r => r.specific_role.toLowerCase().includes(query));
  }
  renderRolesList(filtered);
}

function renderRolesList(roles) {
  const sidebar = document.getElementById("roles-sidebar");
  if (!sidebar) return;

  if (roles.length === 0) {
    sidebar.innerHTML = `<div style="font-size: 0.75rem; color: var(--text-muted); padding: 1rem; text-align: center;">Không tìm thấy vị trí phù hợp</div>`;
    return;
  }

  let html = "";
  roles.forEach((r, idx) => {
    const activeClass = idx === 0 ? "active" : "";
    html += `
      <button class="role-select-btn ${activeClass}" onclick="selectMarketRole('${escapeHtml(r.specific_role)}', this)">
        <span>${escapeHtml(r.specific_role)}</span>
        <span class="role-badge-count">${r.jd_count} JDs</span>
      </button>
    `;
  });
  sidebar.innerHTML = html;
}

function filterMarketRoles(query) {
  const q = (query || "").toLowerCase().trim();
  let filtered = allRolesCache;

  if (currentSelectedDomain && currentSelectedDomain !== "Tất cả") {
    filtered = filtered.filter(r => r.domain === currentSelectedDomain);
  }

  if (q) {
    filtered = filtered.filter(r => 
      r.specific_role.toLowerCase().includes(q) || (r.domain && r.domain.toLowerCase().includes(q))
    );
  }
  renderRolesList(filtered);
}

function selectMarketRole(roleName, btnEl) {
  document.querySelectorAll(".role-select-btn").forEach(b => b.classList.remove("active"));
  if (btnEl) btnEl.classList.add("active");
  loadRoleProfile(roleName);
}

async function loadRoleProfile(roleName) {
  const panel = document.getElementById("role-details-panel");
  panel.innerHTML = `<div style="color: var(--text-muted); padding: 3rem; text-align: center;">Đang phân tích hồ sơ kỹ năng ${escapeHtml(roleName)}...</div>`;

  try {
    const res = await fetch(`/api/market/role-profile/${encodeURIComponent(roleName)}`);
    if (!res.ok) throw new Error("API error");
    const data = await res.json();
    roleProfilesCache[roleName] = data;

    const core = data.core_skills || [];
    const boost = data.boost_skills || [];
    const totalJds = data.total_jds || 50;

    let html = `
      <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.85rem; flex-wrap: wrap; gap: 0.5rem;">
        <div>
          <h2 style="font-size: 1.3rem; font-weight: 800; color: var(--text-primary);">${escapeHtml(data.role_name)}</h2>
          <span style="font-size: 0.78rem; color: var(--text-muted);">Hệ quy chiếu từ <b>${totalJds}</b> tin tuyển dụng thực tế TopCV</span>
        </div>
        <button class="btn-starter-kit" onclick="sendQuickPrompt('Tôi muốn làm đồ án hướng tới vị trí ${escapeHtml(data.role_name)}')">
          🎯 Tư vấn đề tài cho vị trí này
        </button>
      </div>

      <!-- CORE SKILLS -->
      <div>
        <h3 style="font-size: 0.95rem; font-weight: 800; color: var(--accent-cyan); margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.4rem;">
          <span>🟢 Kỹ Năng Cốt Lõi (Core Must-Have Requirements)</span>
        </h3>
        <div style="display: flex; flex-direction: column; gap: 0.65rem;">
          ${core.map(s => `
            <div class="skill-bar-row">
              <div class="skill-bar-meta">
                <span style="color: var(--text-primary);">${escapeHtml(s.canonical_name)}</span>
                <span style="font-family: var(--font-mono); color: var(--accent-cyan);">${s.demand_pct}% JDs (${s.frequency})</span>
              </div>
              <div class="skill-bar-track">
                <div class="skill-bar-fill" style="width: ${Math.min(100, s.demand_pct * 1.3)}%;"></div>
              </div>
            </div>
          `).join("")}
        </div>
      </div>

      <!-- BOOST SKILLS -->
      <div style="margin-top: 1rem;">
        <h3 style="font-size: 0.95rem; font-weight: 800; color: var(--accent-purple); margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.4rem;">
          <span>🚀 Kỹ Năng Bứt Phá (Career Boosters / Differentiators)</span>
        </h3>
        <div style="display: flex; flex-direction: column; gap: 0.65rem;">
          ${boost.map(s => `
            <div class="skill-bar-row">
              <div class="skill-bar-meta">
                <span style="color: var(--text-primary);">${escapeHtml(s.canonical_name)}</span>
                <span style="font-family: var(--font-mono); color: var(--accent-purple);">${s.demand_pct}% JDs (${s.frequency})</span>
              </div>
              <div class="skill-bar-track">
                <div class="skill-bar-fill booster" style="width: ${Math.min(100, s.demand_pct * 1.5)}%;"></div>
              </div>
            </div>
          `).join("")}
        </div>
      </div>
    `;

    panel.innerHTML = html;
  } catch (err) {
    panel.innerHTML = `<div style="color: var(--accent-rose); padding: 2rem;">Lỗi tải dữ liệu vị trí: ${err.message}</div>`;
  }
}

// ===================================================================
// 8. ROLE COMPARISON MODAL CONTROLLER
// ===================================================================
function openRoleCompareModal() {
  const modal = document.getElementById("compare-modal");
  if (!modal) return;
  modal.classList.add("active");

  const selectA = document.getElementById("compare-role-a");
  const selectB = document.getElementById("compare-role-b");

  if (selectA && selectA.options.length === 0 && allRolesCache.length > 0) {
    allRolesCache.forEach(r => {
      const optA = document.createElement("option");
      optA.value = r.specific_role;
      optA.textContent = `${r.specific_role} (${r.jd_count} JDs)`;
      selectA.appendChild(optA);

      const optB = document.createElement("option");
      optB.value = r.specific_role;
      optB.textContent = `${r.specific_role} (${r.jd_count} JDs)`;
      selectB.appendChild(optB);
    });

    if (selectA.options.length > 1) {
      selectA.selectedIndex = 0;
      selectB.selectedIndex = Math.min(2, selectB.options.length - 1);
    }
  }

  runRoleComparison();
}

function closeRoleCompareModal(e) {
  if (e && e.target !== e.currentTarget && !e.target.classList.contains("modal-close-btn") && !e.target.classList.contains("btn-modal-close")) {
    return;
  }
  const modal = document.getElementById("compare-modal");
  if (modal) modal.classList.remove("active");
}

async function fetchRoleProfileData(roleName) {
  if (roleProfilesCache[roleName]) return roleProfilesCache[roleName];
  try {
    const res = await fetch(`/api/market/role-profile/${encodeURIComponent(roleName)}`);
    if (!res.ok) return null;
    const data = await res.json();
    roleProfilesCache[roleName] = data;
    return data;
  } catch (err) {
    console.error("Fetch profile error:", err);
    return null;
  }
}

async function runRoleComparison() {
  const selectA = document.getElementById("compare-role-a");
  const selectB = document.getElementById("compare-role-b");
  const resultsContainer = document.getElementById("compare-results-container");
  if (!selectA || !selectB || !resultsContainer) return;

  const roleA = selectA.value;
  const roleB = selectB.value;

  if (roleA === roleB) {
    resultsContainer.innerHTML = `<div style="text-align: center; color: var(--accent-amber); padding: 2rem;">Vui lòng chọn 2 vị trí khác nhau để so sánh đối chiếu!</div>`;
    return;
  }

  resultsContainer.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 2rem;">Đang đối chiếu dữ liệu tuyển dụng TopCV giữa <b>${escapeHtml(roleA)}</b> và <b>${escapeHtml(roleB)}</b>...</div>`;

  const [dataA, dataB] = await Promise.all([
    fetchRoleProfileData(roleA),
    fetchRoleProfileData(roleB)
  ]);

  if (!dataA || !dataB) {
    resultsContainer.innerHTML = `<div style="text-align: center; color: var(--accent-rose); padding: 2rem;">Lỗi tải dữ liệu so sánh</div>`;
    return;
  }

  const skillsA = (dataA.core_skills || []).concat(dataA.boost_skills || []);
  const skillsB = (dataB.core_skills || []).concat(dataB.boost_skills || []);

  const mapA = new Map(skillsA.map(s => [s.canonical_name.toLowerCase(), s]));
  const mapB = new Map(skillsB.map(s => [s.canonical_name.toLowerCase(), s]));

  const commonSkills = [];
  const onlyA = [];
  const onlyB = [];

  mapA.forEach((val, key) => {
    if (mapB.has(key)) {
      commonSkills.push({
        name: val.canonical_name,
        demandA: val.demand_pct,
        demandB: mapB.get(key).demand_pct,
      });
    } else {
      onlyA.push(val);
    }
  });

  mapB.forEach((val, key) => {
    if (!mapA.has(key)) {
      onlyB.push(val);
    }
  });

  commonSkills.sort((a, b) => (b.demandA + b.demandB) - (a.demandA + a.demandB));
  onlyA.sort((a, b) => b.demand_pct - a.demand_pct);
  onlyB.sort((a, b) => b.demand_pct - a.demand_pct);

  let html = `
    <div class="compare-grid-layout">
      <!-- CỘT 1: ĐẶC TRƯNG ROLE A -->
      <div class="compare-box" style="border-top: 3px solid var(--accent-cyan);">
        <div class="compare-box-title" style="color: var(--accent-cyan);">
          <span>🔵 Đặc trưng riêng: ${escapeHtml(roleA)}</span>
        </div>
        <div style="font-size: 0.72rem; color: var(--text-muted); margin-bottom: 0.65rem;">Kỹ năng chỉ đòi hỏi ở ${escapeHtml(roleA)}:</div>
        <div style="display: flex; flex-direction: column; gap: 0.45rem;">
          ${onlyA.slice(0, 7).map(s => `
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; background: var(--bg-surface); padding: 0.35rem 0.65rem; border-radius: 4px; border: 1px solid var(--border-subtle);">
              <span>${escapeHtml(s.canonical_name)}</span>
              <span style="color: var(--accent-cyan); font-family: var(--font-mono); font-weight: 700;">${s.demand_pct}%</span>
            </div>
          `).join("")}
          ${onlyA.length === 0 ? `<div style="font-size: 0.72rem; color: var(--text-muted);">Không có kỹ năng tách biệt</div>` : ""}
        </div>
      </div>

      <!-- CỘT 2: ĐIỂM GIAO THOA (COMMON CORE) -->
      <div class="compare-box" style="border-top: 3px solid var(--accent-emerald); background: rgba(16, 185, 129, 0.04);">
        <div class="compare-box-title" style="color: var(--accent-emerald);">
          <span>🟢 Điểm Giao Thoa Cốt Lõi (Common Core)</span>
        </div>
        <div style="font-size: 0.72rem; color: var(--text-muted); margin-bottom: 0.65rem;">Kỹ năng chung xuất hiện ở cả 2 vị trí:</div>
        <div style="display: flex; flex-direction: column; gap: 0.45rem;">
          ${commonSkills.slice(0, 7).map(s => `
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; background: var(--bg-surface); padding: 0.35rem 0.65rem; border-radius: 4px; border: 1px solid var(--border-subtle);">
              <span style="font-weight: 600;">${escapeHtml(s.name)}</span>
              <span style="color: var(--accent-emerald); font-family: var(--font-mono); font-size: 0.7rem;">${s.demandA}% / ${s.demandB}%</span>
            </div>
          `).join("")}
          ${commonSkills.length === 0 ? `<div style="font-size: 0.72rem; color: var(--text-muted);">Không có kỹ năng giao thoa</div>` : ""}
        </div>
      </div>

      <!-- CỘT 3: ĐẶC TRƯNG ROLE B -->
      <div class="compare-box" style="border-top: 3px solid var(--accent-purple);">
        <div class="compare-box-title" style="color: var(--accent-purple);">
          <span>🟣 Đặc trưng riêng: ${escapeHtml(roleB)}</span>
        </div>
        <div style="font-size: 0.72rem; color: var(--text-muted); margin-bottom: 0.65rem;">Kỹ năng chỉ đòi hỏi ở ${escapeHtml(roleB)}:</div>
        <div style="display: flex; flex-direction: column; gap: 0.45rem;">
          ${onlyB.slice(0, 7).map(s => `
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; background: var(--bg-surface); padding: 0.35rem 0.65rem; border-radius: 4px; border: 1px solid var(--border-subtle);">
              <span>${escapeHtml(s.canonical_name)}</span>
              <span style="color: var(--accent-purple); font-family: var(--font-mono); font-weight: 700;">${s.demand_pct}%</span>
            </div>
          `).join("")}
          ${onlyB.length === 0 ? `<div style="font-size: 0.72rem; color: var(--text-muted);">Không có kỹ năng tách biệt</div>` : ""}
        </div>
      </div>
    </div>
  `;

  resultsContainer.innerHTML = html;
}

// ===================================================================
// 9. MULTI-DIMENSIONAL RADAR SVG GENERATOR
// ===================================================================
function generateRadarSvg(baselinePct, potentialPct) {
  const cx = 200;
  const cy = 132;
  const maxR = 82;

  // 5 trục năng lực cốt lõi
  const axes = [
    { name: "Kiến trúc & Logic", bFactor: 0.95, pFactor: 1.0 },
    { name: "CSDL & Lưu trữ", bFactor: 1.05, pFactor: 0.98 },
    { name: "Kiểm thử & QA", bFactor: 0.70, pFactor: 0.92 },
    { name: "Docker & DevOps", bFactor: 0.75, pFactor: 1.02 },
    { name: "Chuẩn Bàn Giao", bFactor: 0.90, pFactor: 1.0 },
  ];

  // Tọa độ góc cho 5 trục (đỉnh 0 ở hướng 12 giờ)
  const angles = [
    -Math.PI / 2,
    -Math.PI / 2 + (2 * Math.PI) / 5,
    -Math.PI / 2 + (4 * Math.PI) / 5,
    -Math.PI / 2 + (6 * Math.PI) / 5,
    -Math.PI / 2 + (8 * Math.PI) / 5,
  ];

  // Tính tọa độ polygon
  function getPolygonPoints(score, factorKey) {
    return axes.map((axis, i) => {
      const val = Math.min(100, Math.max(15, score * axis[factorKey]));
      const r = (val / 100) * maxR;
      const x = (cx + r * Math.cos(angles[i])).toFixed(1);
      const y = (cy + r * Math.sin(angles[i])).toFixed(1);
      return `${x},${y}`;
    }).join(" ");
  }

  // Lưới đồng tâm ngũ giác (25%, 50%, 75%, 100%)
  const gridLevels = [0.25, 0.5, 0.75, 1.0];
  const gridPolygons = gridLevels.map(lvl => {
    const pts = angles.map(a => {
      const x = (cx + maxR * lvl * Math.cos(a)).toFixed(1);
      const y = (cy + maxR * lvl * Math.sin(a)).toFixed(1);
      return `${x},${y}`;
    }).join(" ");
    return `<polygon points="${pts}" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>`;
  }).join("");

  // Các đường trục tia
  const axisLines = angles.map(a => {
    const x = (cx + maxR * Math.cos(a)).toFixed(1);
    const y = (cy + maxR * Math.sin(a)).toFixed(1);
    return `<line x1="${cx}" y1="${cy}" x2="${x}" y2="${y}" stroke="rgba(255,255,255,0.12)" stroke-width="1"/>`;
  }).join("");

  // Nhãn chữ các trục có khoảng đệm biên rộng rãi (viewBox 400px)
  const labelOffsets = [
    { dx: 0, dy: -10, anchor: "middle" },
    { dx: 6, dy: 3, anchor: "start" },
    { dx: 6, dy: 12, anchor: "start" },
    { dx: -6, dy: 12, anchor: "end" },
    { dx: -6, dy: 3, anchor: "end" },
  ];

  const axisLabels = axes.map((axis, i) => {
    const x = cx + (maxR + 12) * Math.cos(angles[i]) + (labelOffsets[i].dx || 0);
    const y = cy + (maxR + 12) * Math.sin(angles[i]) + (labelOffsets[i].dy || 0);
    return `<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" text-anchor="${labelOffsets[i].anchor}" fill="var(--text-secondary)" font-size="9.5" font-weight="600">${axis.name}</text>`;
  }).join("");

  const baselinePoints = getPolygonPoints(baselinePct, "bFactor");
  const potentialPoints = getPolygonPoints(potentialPct, "pFactor");

  return `
    <svg class="radar-svg" viewBox="0 0 400 255" style="overflow: visible;">
      ${gridPolygons}
      ${axisLines}
      <!-- Polygon 1: Baseline Coverage -->
      <polygon id="radar-baseline-poly" points="${baselinePoints}" fill="rgba(148, 163, 184, 0.2)" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="3,3"/>
      <!-- Polygon 2: GEM Potential Coverage -->
      <polygon id="radar-potential-poly" points="${potentialPoints}" fill="rgba(6, 182, 212, 0.35)" stroke="var(--accent-emerald)" stroke-width="2"/>
      ${axisLabels}
    </svg>
  `;
}

// ===================================================================
// 10. PRINTABLE ACADEMIC ASSESSMENT REPORT
// ===================================================================
function printAssessmentReport() {
  if (!currentBlueprint) {
    showToast("⚠️ Vui lòng phân tích đề tài hoặc bấm xem đề tài mẫu trước khi in báo cáo!", "error");
    return;
  }

  const bp = currentBlueprint;
  const gap = bp.skill_gap_report || {};
  const metrics = bp.readiness_metrics || gap.metrics || {};
  const printContainer = document.getElementById("printable-report");
  if (!printContainer) return;

  const role = bp.target_role || "Backend Developer";
  const idea = bp.idea_text || "Đề tài Đồ án Tốt nghiệp CNTT";
  const domain = bp.domain || "Công nghệ Thông tin & Dữ liệu";

  let html = `
    <div style="border-bottom: 2px solid #000; padding-bottom: 12px; margin-bottom: 20px;">
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <div>
          <div style="font-size: 13pt; font-weight: bold; text-transform: uppercase;">TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN - ĐHQG-HCM</div>
          <div style="font-size: 10pt; font-weight: 600;">CUỘC THI AI SOLUTION CHALLENGE 2026 (AISC 2026)</div>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 14pt; font-weight: 800; color: #0284c7;">GEM PLATFORM</div>
          <div style="font-size: 9pt; font-style: italic;">Hệ Thống Thẩm Định Năng Lực Đồ Án CNTT</div>
        </div>
      </div>
      <h1 style="text-align: center; margin: 20px 0 6px 0; font-size: 16pt; text-transform: uppercase; letter-spacing: 0.5px;">
        BẢN BÁO CÁO THẨM ĐỊNH NĂNG LỰC ĐỒ ÁN & THU HẸP SKILL GAP
      </h1>
      <div style="text-align: center; font-size: 10pt; font-style: italic;">
        (Căn cứ hệ quy chiếu 700 Tin Tuyển Dụng IT Thực Tế TopCV Việt Nam · Chuẩn Kiểm Định AISC 2026)
      </div>
    </div>

    <!-- METADATA TABLE -->
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 10.5pt;">
      <tr>
        <td style="padding: 6px; border: 1px solid #ddd; width: 25%; font-weight: bold; background: #f9fafb;">Tên Đề Tài:</td>
        <td style="padding: 6px; border: 1px solid #ddd; font-weight: 600;">${escapeHtml(idea)}</td>
      </tr>
      <tr>
        <td style="padding: 6px; border: 1px solid #ddd; font-weight: bold; background: #f9fafb;">Miền Nghiệp Vụ:</td>
        <td style="padding: 6px; border: 1px solid #ddd;">${escapeHtml(domain)}</td>
      </tr>
      <tr>
        <td style="padding: 6px; border: 1px solid #ddd; font-weight: bold; background: #f9fafb;">Vị Trí Nghề Nghiệp Hướng Tới:</td>
        <td style="padding: 6px; border: 1px solid #ddd; font-weight: bold; color: #0284c7;">${escapeHtml(role)}</td>
      </tr>
      <tr>
        <td style="padding: 6px; border: 1px solid #ddd; font-weight: bold; background: #f9fafb;">Quỹ Thời Gian Thực Hiện:</td>
        <td style="padding: 6px; border: 1px solid #ddd;">${bp.time_months || 3} Tháng (Theo Lộ trình Sprint)</td>
      </tr>
      <tr>
        <td style="padding: 6px; border: 1px solid #ddd; font-weight: bold; background: #f9fafb;">Điểm Khớp Nối Thực Chiến:</td>
        <td style="padding: 6px; border: 1px solid #ddd; font-weight: 800; font-size: 12pt; color: #059669;">
          ${metrics.readiness_score || 80}/100 Điểm (Độ phủ tiềm năng: ${metrics.potential_coverage || 85}%, Mức thu hẹp gap: ${metrics.gap_reduction_delta || '+40%'})
        </td>
      </tr>
    </table>

    <!-- 1. COVERED SKILLS -->
    <h3 style="font-size: 12pt; margin: 16px 0 8px 0; border-bottom: 1px solid #ccc; padding-bottom: 4px;">
      1. Kỹ Năng Tự Nhiên Đã Bao Phủ (Covered Baseline)
    </h3>
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 16px; font-size: 10pt;">
      <thead>
        <tr style="background: #f3f4f6;">
          <th style="border: 1px solid #ccc; padding: 6px; text-align: left; width: 30%;">Kỹ Năng</th>
          <th style="border: 1px solid #ccc; padding: 6px; text-align: left;">Lý Do Kỹ Thuật Trong Thiết Kế Đồ Án</th>
          <th style="border: 1px solid #ccc; padding: 6px; text-align: center; width: 15%;">Nhu Cầu TopCV</th>
        </tr>
      </thead>
      <tbody>
        ${(gap.covered_skills || []).map(s => `
          <tr>
            <td style="border: 1px solid #ccc; padding: 6px; font-weight: bold;">${escapeHtml(s.skill)}</td>
            <td style="border: 1px solid #ccc; padding: 6px;">${escapeHtml(s.reason)}</td>
            <td style="border: 1px solid #ccc; padding: 6px; text-align: center; font-weight: bold;">${s.demand_pct ? s.demand_pct + "%" : "Core"}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>

    <!-- 2. ACTIONABLE GAPS & DELIVERABLES -->
    <h3 style="font-size: 12pt; margin: 16px 0 8px 0; border-bottom: 1px solid #ccc; padding-bottom: 4px;">
      2. Kế Hoạch Can Thiệp Bổ Sung & Bằng Chứng Nộp Git (Verifiable Evidence Artifacts)
    </h3>
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 16px; font-size: 10pt;">
      <thead>
        <tr style="background: #f3f4f6;">
          <th style="border: 1px solid #ccc; padding: 6px; text-align: left; width: 25%;">Kỹ Năng Cần Bổ Sung</th>
          <th style="border: 1px solid #ccc; padding: 6px; text-align: left;">Hành Động Triển Khai Trong Code</th>
          <th style="border: 1px solid #ccc; padding: 6px; text-align: left; width: 35%;">Bằng Chứng Bàn Giao Nộp Git (Artifact)</th>
        </tr>
      </thead>
      <tbody>
        ${(gap.actionable_gaps || []).map(g => `
          <tr>
            <td style="border: 1px solid #ccc; padding: 6px; font-weight: bold; color: #b45309;">${escapeHtml(g.skill)}</td>
            <td style="border: 1px solid #ccc; padding: 6px;">${escapeHtml(g.action_item)}</td>
            <td style="border: 1px solid #ccc; padding: 6px; font-weight: 600;">📦 ${escapeHtml(g.proof_deliverable)}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>

    <!-- 3. DEFERRED -->
    <h3 style="font-size: 12pt; margin: 16px 0 8px 0; border-bottom: 1px solid #ccc; padding-bottom: 4px;">
      3. Kỹ Năng Tạm Hoãn để Tránh Over-engineering
    </h3>
    <ul style="font-size: 10pt; line-height: 1.6; margin-bottom: 20px;">
      ${(gap.deferred_or_overkill || []).map(d => `
        <li><b>${escapeHtml(d.skill)}</b>: ${escapeHtml(d.reason)} <i>(Kết luận: ${escapeHtml(d.verdict || "Tạm hoãn")})</i></li>
      `).join("")}
    </ul>

    <!-- SIGNATURES -->
    <div style="margin-top: 40px; display: flex; justify-content: space-between; text-align: center; font-size: 10.5pt; page-break-inside: avoid;">
      <div style="width: 45%;">
        <div style="font-weight: bold;">ĐẠI DIỆN NHÓM SINH VIÊN</div>
        <div style="font-style: italic; font-size: 9pt; margin-bottom: 60px;">(Ký và ghi rõ họ tên)</div>
        <div style="font-weight: 600;">Nhóm Sinh viên Thực hiện</div>
      </div>
      <div style="width: 45%;">
        <div style="font-weight: bold;">GIẢNG VIÊN HƯỚNG DẪN DUYỆT</div>
        <div style="font-style: italic; font-size: 9pt; margin-bottom: 60px;">(Ký và cho ý kiến chuyên môn)</div>
        <div style="font-weight: 600;">Hội đồng / GVHD Đề tài</div>
      </div>
    </div>
  `;

  printContainer.innerHTML = html;
  window.print();
}

// ===================================================================
// 11. TOAST NOTIFICATIONS & UTILITIES
// ===================================================================
function showToast(message, type = "info", duration = 3000) {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = "toastOut 0.3s forwards";
    setTimeout(() => {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 300);
  }, duration);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatMarkdown(text) {
  if (!text) return "";
  let raw = text.trim();

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
        if (headingContent.includes("1.") || headingContent.includes("Nền tảng") || headingContent.includes("Điểm mạnh")) {
          iconHtml = `<span class="heading-icon-badge strength">🎯 Điểm mạnh sẵn có</span>`;
        } else if (headingContent.includes("2.") || headingContent.includes("Khoảng cách") || headingContent.includes("Actionable Gaps")) {
          iconHtml = `<span class="heading-icon-badge gap">⚡ Gaps cần lấp đầy</span>`;
        } else if (headingContent.includes("3.") || headingContent.includes("Cảnh báo") || headingContent.includes("Over-Engineering")) {
          iconHtml = `<span class="heading-icon-badge warning">⚠️ Tránh sa lầy</span>`;
        } else if (headingContent.includes("4.") || headingContent.includes("bước tiếp theo") || headingContent.includes("Lộ trình")) {
          iconHtml = `<span class="heading-icon-badge next">🚀 Bước tiếp theo</span>`;
        } else if (headingContent.includes("Câu hỏi") || headingContent.includes("💬") || headingContent.includes("Probing")) {
          iconHtml = `<span class="heading-icon-badge question">💬 Câu hỏi phản hồi</span>`;
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

    // Numbered Questions group (Interactive Probing)
    if (/^1\.\s+[\s\S]+\n2\.\s+[\s\S]+/.test(block)) {
      const items = block.split(/\n(?=\d+\.\s+)/);
      const itemsHtml = items.map(item => {
        const m = item.match(/^(\d+)\.\s+([\s\S]+)$/);
        if (!m) return `<p class="chat-line">${formatInline(item)}</p>`;
        const num = m[1];
        const qText = formatInline(m[2]);
        return `
          <div class="chat-probing-card" onclick="replyNumberedQuestion('Câu trả lời cho câu ${num}')" title="Nhấn để trả lời câu hỏi này">
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

    // Nested sub-bullet: * Lý do: ... or * Bằng chứng nộp: ...
    if (/^\s{2,}\*\s+(.+)$/.test(line)) {
      const subMatch = line.match(/^\s{2,}\*\s+(.+)$/);
      let content = subMatch[1];
      let icon = "🔹";
      let tagClass = "sub-generic";
      
      if (/^\*?Lý do:\*?/i.test(content)) {
        icon = "🎯";
        tagClass = "sub-reason";
        content = content.replace(/^\*?Lý do:\*?\s*/i, "<strong>Lý do cốt lõi:</strong> ");
      } else if (/^\*?Bằng chứng nộp:\*?/i.test(content)) {
        icon = "📦";
        tagClass = "sub-artifact";
        content = content.replace(/^\*?Bằng chứng nộp:\*?\s*/i, "<strong>Bằng chứng cần nộp (Artifacts):</strong> ");
      } else if (/^\*?Tại sao\??\*?/i.test(content)) {
        icon = "⚡";
        tagClass = "sub-why";
        content = content.replace(/^\*?Tại sao\??\*?\s*/i, "<strong>Giải thích:</strong> ");
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
      result.push(`
        <div class="chat-numbered-item" onclick="replyNumberedQuestion('Trả lời câu ${numMatch[1]}')">
          <span class="chat-num-badge">${numMatch[1]}</span>
          <div class="chat-num-content">${formatInline(numMatch[2])}</div>
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

  // Italic: *text* or _text_
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

/**
 * 💎 GEM PLATFORM (AISC 2026 - UIT)
 * UI CONTROLLER, THEME, TABS, TOASTS & UTILITIES
 */

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
// 2. TAB SWITCHER (SEGMENTED TOP NAVIGATION)
// ===================================================================

function switchTab(tabId) {
  // 1. Switch Tab Panes
  document.querySelectorAll(".tab-pane").forEach(pane => {
    pane.classList.remove("active");
    pane.setAttribute("aria-hidden", "true");
  });
  const targetPane = document.getElementById(`tab-pane-${tabId}`);
  if (targetPane) {
    targetPane.classList.add("active");
    targetPane.setAttribute("aria-hidden", "false");
  }

  // 2. Switch Nav Tab Buttons (Segmented Top Header)
  document.querySelectorAll(".nav-tab-btn").forEach(btn => {
    btn.classList.remove("active");
    btn.setAttribute("aria-selected", "false");
  });
  const targetBtn = document.getElementById(`tab-btn-${tabId}`);
  if (targetBtn) {
    targetBtn.classList.add("active");
    targetBtn.setAttribute("aria-selected", "true");
  }

  // 3. If switching to market, ensure roles are loaded
  if (tabId === "market" && typeof loadMarketRoles === "function") {
    loadMarketRoles();
  }
}

// ===================================================================
// 3. TOAST NOTIFICATIONS & UTILITIES
// ===================================================================

function showToast(message, type = "info", duration = 3000) {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;

  let icon = "💎";
  if (type === "success") icon = "✓";
  else if (type === "error") icon = "⚠️";
  else if (type === "warning") icon = "🔔";
  else if (type === "info") icon = "ℹ️";

  toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = "toastOut 0.3s ease-out forwards";
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

// ===================================================================
// 4. KEYBOARD SHORTCUTS & HEALTH STATUS
// ===================================================================

function initKeyboardShortcuts() {
  document.addEventListener("keydown", (e) => {
    // Ctrl + Enter to send chat message
    if (e.ctrlKey && e.key === "Enter") {
      const chatInput = document.getElementById("chat-input");
      if (chatInput && chatInput.value.trim()) {
        e.preventDefault();
        if (typeof handleChatSubmit === "function") {
          handleChatSubmit(new Event("submit"));
        }
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
      if (typeof closeExportModal === "function") closeExportModal();
      if (typeof closeRoleCompareModal === "function") closeRoleCompareModal();
    }
  });
}

async function updateHealthStatus() {
  const statusPill = document.getElementById("system-status-pill");
  const statusText = document.getElementById("system-status-text");
  if (!statusPill) return;

  try {
    const res = await fetch("/health");
    if (res.ok) {
      statusPill.classList.remove("status-offline");
      statusPill.classList.add("status-online");
      if (statusText) statusText.textContent = "FastAPI & Qdrant Live";
    } else {
      statusPill.classList.remove("status-online");
      statusPill.classList.add("status-offline");
      if (statusText) statusText.textContent = "Backend Disconnected";
    }
  } catch {
    statusPill.classList.remove("status-online");
    statusPill.classList.add("status-offline");
    if (statusText) statusText.textContent = "Backend Offline";
  }
}

// ===================================================================
// 5. GLOBAL ATTACHMENTS
// ===================================================================

window.initTheme = initTheme;
window.toggleTheme = toggleTheme;
window.switchTab = switchTab;
window.showToast = showToast;
window.escapeHtml = escapeHtml;
window.initKeyboardShortcuts = initKeyboardShortcuts;
window.updateHealthStatus = updateHealthStatus;

window.GEM_UI = {
  initTheme,
  toggleTheme,
  switchTab,
  showToast,
  escapeHtml,
  initKeyboardShortcuts,
  updateHealthStatus,
};

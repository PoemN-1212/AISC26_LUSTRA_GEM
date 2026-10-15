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

// DOM READY
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initChat();
  loadMarketRoles();
});

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
  currentActiveGaps.clear();
  initChat();

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

  // Render User Message
  appendUserMessage(text);
  input.value = "";
  input.disabled = true;
  sendBtn.disabled = true;

  // Render Typing Indicator
  const typingId = appendTypingIndicator();

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

    // Render GEM response
    appendGemMessage(data.reply);

    // Update Live Blueprint
    if (data.blueprint) {
      currentBlueprint = data.blueprint;
      renderBlueprint(data.blueprint);
    }
  } catch (err) {
    removeTypingIndicator(typingId);
    appendGemMessage("⚠️ Xin lỗi, đã có lỗi kết nối tới máy chủ GEM. Vui lòng kiểm tra lại dịch vụ Backend (port 8000).");
    showToast("Lỗi kết nối Backend", "error");
    console.error("Chat error:", err);
  } finally {
    input.disabled = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

function appendUserMessage(text) {
  const container = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = "chat-bubble-container user";
  div.innerHTML = `
    <div class="avatar user">SV</div>
    <div class="bubble-content">
      <p>${escapeHtml(text)}</p>
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
    <div class="avatar gem"><img src="/static/assets/gem_logo.png" class="avatar-logo-img" alt="GEM"></div>
    <div class="bubble-content">
      ${formatMarkdown(markdownText)}
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

  // 1. READINESS SCORE DASHBOARD (VỚI SVG GAUGE CIRCLE)
  if (metrics.readiness_score !== undefined) {
    const strokeDash = calculateGaugeOffset(score);
    html += `
      <div class="readiness-card">
        <div class="readiness-hero-row">
          <div class="readiness-info">
            <div class="readiness-title">
              <span>🎯 Điểm Khớp Nối Thực Chiến (Market Readiness)</span>
            </div>
            <div class="readiness-desc">
              Lượng hóa từ <b>${gap.sample_jd_count || 50}</b> tin tuyển dụng ${escapeHtml(bp.target_role || "IT")} thực tế trên TopCV Việt Nam.
            </div>
          </div>

          <div class="readiness-gauge-box" title="Điểm thực chiến đồ án">
            <svg class="readiness-gauge-svg" width="124" height="124" viewBox="0 0 100 100">
              <circle class="gauge-bg" cx="50" cy="50" r="45"></circle>
              <circle class="gauge-fill" id="gauge-fill-circle" cx="50" cy="50" r="45" style="stroke-dashoffset: ${strokeDash}; stroke: ${score >= 80 ? 'var(--accent-emerald)' : (score >= 60 ? 'var(--accent-cyan)' : 'var(--accent-amber)')};"></circle>
            </svg>
            <div class="gauge-center">
              <span class="gauge-score-value" id="gauge-score-num" style="color: ${score >= 80 ? 'var(--accent-emerald)' : (score >= 60 ? 'var(--accent-cyan)' : 'var(--accent-amber)')};">${score}</span>
              <span class="gauge-score-label">ĐIỂM</span>
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
// 7. TAB 2: MARKET INTELLIGENCE EXPLORER
// ===================================================================
async function loadMarketRoles() {
  const sidebar = document.getElementById("roles-sidebar");
  try {
    const response = await fetch("/api/market/roles");
    if (!response.ok) return;
    const data = await response.json();

    allRolesCache = data.roles || [];
    if (allRolesCache.length === 0) return;

    renderRolesList(allRolesCache);

    // Mặc định nạp vị trí đầu tiên
    if (allRolesCache[0]) {
      loadRoleProfile(allRolesCache[0].specific_role);
    }
  } catch (err) {
    console.error("Lỗi nạp roles:", err);
  }
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
  if (!q) {
    renderRolesList(allRolesCache);
    return;
  }

  const filtered = allRolesCache.filter(r => 
    r.specific_role.toLowerCase().includes(q) || (r.domain && r.domain.toLowerCase().includes(q))
  );
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
// 8. TOAST NOTIFICATIONS & UTILITIES
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
  let out = escapeHtml(text);

  // Bold
  out = out.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  // Code snippets
  out = out.replace(/`([^`]+)`/g, "<code style='background:rgba(255,255,255,0.08);padding:0.15rem 0.35rem;border-radius:3px;font-family:var(--font-mono);font-size:0.85em;'>$1</code>");

  // Bullet lists
  out = out.replace(/(?:^|\n)[•*-]\s+(.+)/g, "<br>• $1");

  // Paragraphs
  out = out.replace(/\n\n/g, "</p><p>");
  out = out.replace(/\n/g, "<br>");

  return `<p>${out}</p>`;
}

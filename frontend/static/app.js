/**
 * 💎 GEM (LUSTRA_GEM) - Modern Interactive Frontend Application
 * AISC 2026 · GEM - Nền tảng AI định hướng và khớp nối năng lực Đồ án CNTT với xu hướng tuyển dụng
 */

let currentSessionId = null;
let currentSelectedRole = "Backend Developer";

// Khởi chạy khi tài liệu đã sẵn sàng
document.addEventListener("DOMContentLoaded", () => {
  initChat();
  loadMarketRoles();
});

// Chuyển đổi qua lại giữa các Tabs
function switchTab(tabId) {
  document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));
  document.querySelectorAll(".nav-tab-btn").forEach(btn => btn.classList.remove("active"));

  const targetPane = document.getElementById(`tab-pane-${tabId}`);
  const targetBtn = document.getElementById(`tab-btn-${tabId}`);

  if (targetPane) targetPane.classList.add("active");
  if (targetBtn) targetBtn.classList.add("active");
}

// Khởi tạo cuộc trò chuyện ban đầu
function initChat() {
  const container = document.getElementById("chat-messages");
  container.innerHTML = "";

  appendGemMessage(
    "👋 Chào bạn! Mình là **GEM** — Nền tảng AI định hướng và khớp nối năng lực Đồ án CNTT với xu hướng tuyển dụng (AISC 2026).\n\n" +
    "Bạn đang có ý tưởng làm đề tài gì cho đồ án sắp tới? Bạn có thể chia sẻ tự do: **bài toán muốn giải quyết** (như OLAP phân tích gian lận, AI Healthcare, E-Commerce,...), **quỹ thời gian có sẵn** hoặc **vị trí nghề nghiệp đang hướng tới** (Data Engineer, AI Engineer, Backend,...)."
  );
}

function resetChatSession() {
  currentSessionId = null;
  initChat();
  document.getElementById("blueprint-content").innerHTML = `
    <div class="empty-blueprint-state">
      <span class="empty-icon">💡</span>
      <p><b>Chưa có ý tưởng nào được phân tích</b></p>
      <p>Hãy gõ một ý tưởng ở khung bên trái hoặc chọn nút gợi ý nhanh để GEM phân tích bài toán và đề xuất kiến trúc 3 lớp.</p>
    </div>
  `;
  document.getElementById("blueprint-target-role").textContent = "Chờ phân tích";
}

// Gửi tin nhắn nhanh từ Prompt Chips
function sendQuickPrompt(promptText) {
  const input = document.getElementById("chat-input");
  input.value = promptText;
  handleChatSubmit(new Event("submit"));
}

// Xử lý gửi tin nhắn từ người dùng
async function handleChatSubmit(e) {
  e.preventDefault();
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  const text = input.value.trim();

  if (!text) return;

  // 1. Render User Bubble
  appendUserMessage(text);
  input.value = "";
  input.disabled = true;
  sendBtn.disabled = true;

  // 2. Render Typing Indicator
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
      throw new Error(`Server returned ${response.status}`);
    }

    const data = await response.json();
    currentSessionId = data.session_id;

    // 3. Render GEM Reply
    appendGemMessage(data.reply);

    // 4. Update Live Blueprint Panel on the Right
    if (data.blueprint) {
      renderBlueprint(data.blueprint);
    }
  } catch (err) {
    removeTypingIndicator(typingId);
    appendGemMessage("⚠️ Xin lỗi, đã có lỗi kết nối tới máy chủ GEM. Vui lòng thử lại sau giây lát.");
    console.error("Chat error:", err);
  } finally {
    input.disabled = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

// Render Bong bóng User
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

// Render Bong bóng GEM
function appendGemMessage(markdownText) {
  const container = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = "chat-bubble-container gem";
  div.innerHTML = `
    <div class="avatar gem">💎</div>
    <div class="bubble-content">
      ${formatMarkdown(markdownText)}
    </div>
  `;
  container.appendChild(div);
  scrollToBottom();
}

// Typing Indicator
function appendTypingIndicator() {
  const id = "typing-" + Date.now();
  const container = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.id = id;
  div.className = "chat-bubble-container gem";
  div.innerHTML = `
    <div class="avatar gem">💎</div>
    <div class="bubble-content" style="color: var(--text-muted); font-style: italic;">
      <span>GEM đang suy luận và đối chiếu TopCV...</span>
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
// RENDER BLUEPRINT & ROADMAP (RIGHT COLUMN)
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

  if (scoreBadge) {
    if (metrics.readiness_score) {
      scoreBadge.textContent = `🎯 ${metrics.readiness_score}/100 Điểm Thực Chiến`;
      scoreBadge.style.display = "inline-flex";
    } else {
      scoreBadge.style.display = "none";
    }
  }

  let html = "";

  // =================================================================
  // 1. CHỈ SỐ THỰC CHIẾN & ĐỘ BAO PHỦ (READINESS DASHBOARD)
  // =================================================================
  if (metrics.readiness_score) {
    html += `
      <div class="readiness-card">
        <div class="readiness-header">
          <div class="readiness-title-group">
            <div class="readiness-title">
              <span>🎯 Điểm Khớp Nối Thực Chiến (Market Readiness)</span>
            </div>
            <div class="readiness-subtitle">
              Đối chiếu trực tiếp từ <b>${gap.sample_jd_count || 50}</b> tin tuyển dụng ${escapeHtml(bp.target_role || "IT")} thực tế trên TopCV
            </div>
          </div>
          <div class="readiness-score-badge">
            <span class="readiness-score-num">${metrics.readiness_score}</span>
            <span class="readiness-score-max">/100</span>
          </div>
        </div>

        <div class="metric-pill-grid">
          <div class="metric-pill">
            <div class="metric-pill-label">Phù hợp bài toán</div>
            <div class="metric-pill-val" style="color: var(--accent-cyan);">${metrics.semantic_fit || 85}%</div>
          </div>
          <div class="metric-pill">
            <div class="metric-pill-label">Độ phủ ban đầu</div>
            <div class="metric-pill-val" style="color: #94a3b8;">${metrics.baseline_coverage || 45}%</div>
          </div>
          <div class="metric-pill">
            <div class="metric-pill-label">Độ phủ sau can thiệp</div>
            <div class="metric-pill-val" style="color: var(--accent-emerald);">${metrics.potential_coverage || 85}%</div>
          </div>
          <div class="metric-pill">
            <div class="metric-pill-label">Mức thu hẹp Gap</div>
            <div class="metric-pill-val metric-pill-delta">${metrics.gap_reduction_delta || "+40%"}</div>
          </div>
        </div>
      </div>
    `;
  }

  // =================================================================
  // 2. BẢNG ĐỐI CHIẾU KỸ NĂNG (SKILL GAP MATRIX - 3 NHÓM)
  // =================================================================
  if (gap.covered_skills || gap.actionable_gaps || gap.deferred_or_overkill) {
    html += `
      <div class="layer-card">
        <span class="section-badge badge-layer1">Phần 1 · Đối chiếu Năng lực</span>
        <div class="layer-title">Ma trận Phân loại Skill Gap (${escapeHtml(bp.target_role || "IT")})</div>
        <div class="layer-desc">Phân định rõ kỹ năng tự nhiên đã bao phủ, kỹ năng cần bổ sung và kỹ năng nên tạm hoãn:</div>

        <div class="gap-matrix-container">
          <!-- NHÓM 1: ĐÃ BAO PHỦ TỰ NHIÊN -->
          ${gap.covered_skills && gap.covered_skills.length > 0 ? `
            <div class="matrix-group covered">
              <div class="matrix-group-title">
                <span class="matrix-tag-covered">🟢 Đã Bao Phủ trong Kế hoạch Đồ án</span>
                <span style="font-size: 0.7rem; color: var(--text-muted); font-weight: normal;">(Tự nhiên rèn luyện qua phạm vi bài toán)</span>
              </div>
              <div class="matrix-item-list">
                ${gap.covered_skills.map(s => `
                  <div class="matrix-item">
                    <div class="matrix-item-left">
                      <span class="matrix-item-name">${escapeHtml(s.skill)}</span>
                      <span class="matrix-item-reason">${escapeHtml(s.reason)}</span>
                    </div>
                    <span class="matrix-item-demand" style="color: var(--accent-emerald);">${s.demand_pct ? s.demand_pct + "% JD" : ""}</span>
                  </div>
                `).join("")}
              </div>
            </div>
          ` : ""}

          <!-- NHÓM 2: KHOẢNG CÁCH CẦN XEM XÉT BỔ SUNG -->
          ${gap.actionable_gaps && gap.actionable_gaps.length > 0 ? `
            <div class="matrix-group actionable">
              <div class="matrix-group-title">
                <span class="matrix-tag-actionable">🟡 Cần Xem Xét Bổ Sung (Actionable Gaps)</span>
                <span style="font-size: 0.7rem; color: var(--text-muted); font-weight: normal;">(Kỹ năng TopCV yêu cầu cao mà kế hoạch còn thiếu)</span>
              </div>
              <div class="matrix-item-list">
                ${gap.actionable_gaps.map(g => `
                  <div class="matrix-item">
                    <div class="matrix-item-left">
                      <span class="matrix-item-name">${escapeHtml(g.skill)}</span>
                      <span class="matrix-item-reason">${escapeHtml(g.why_needed)}</span>
                    </div>
                    <span class="matrix-item-demand" style="color: var(--accent-amber);">${g.demand_pct ? g.demand_pct + "% JD" : ""}</span>
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
                <span style="font-size: 0.7rem; color: var(--text-muted); font-weight: normal;">(Chưa cần thiết cho MVP, tránh quá tải kiến trúc)</span>
              </div>
              <div class="matrix-item-list">
                ${gap.deferred_or_overkill.map(d => `
                  <div class="matrix-item">
                    <div class="matrix-item-left">
                      <span class="matrix-item-name" style="color: #94a3b8;">${escapeHtml(d.skill)}</span>
                      <span class="matrix-item-reason">${escapeHtml(d.reason)}</span>
                    </div>
                    <span class="matrix-item-demand" style="color: #94a3b8;">${escapeHtml(d.verdict || "Tạm hoãn")}</span>
                  </div>
                `).join("")}
              </div>
            </div>
          ` : ""}
        </div>
      </div>
    `;
  }

  // =================================================================
  // 3. HÀNH ĐỘNG THU HẸP GAP & BẰNG CHỨNG NĂNG LỰC (ACTION & PROOF CARDS)
  // =================================================================
  if (gap.actionable_gaps && gap.actionable_gaps.length > 0) {
    html += `
      <div class="layer-card">
        <span class="section-badge badge-layer2">Phần 2 · Kế hoạch Hành động</span>
        <div class="layer-title">Hành Động Can Thiệp & Bằng Chứng Năng Lực Cần Tạo Ra</div>
        <div class="layer-desc">Mỗi công nghệ bổ sung bắt buộc phải gắn với một hành động kỹ thuật và sản phẩm bàn giao (Artifacts) vào Git Repo:</div>

        <div class="action-cards-container">
          ${gap.actionable_gaps.map(g => {
            const isHigh = (g.priority || "").toLowerCase().includes("cao") || (g.priority || "").toLowerCase().includes("hàng đầu");
            return `
              <div class="action-card">
                <div class="action-card-header">
                  <div class="action-card-title">⚡ ${escapeHtml(g.skill)}</div>
                  <div style="display: flex; gap: 0.4rem; align-items: center;">
                    <span class="priority-pill ${isHigh ? 'priority-high' : 'priority-medium'}">${escapeHtml(g.priority || "Khuyến nghị")}</span>
                    <span style="font-size: 0.72rem; color: var(--accent-cyan); font-weight: 700;">${g.demand_pct ? g.demand_pct + "% JD" : ""}</span>
                  </div>
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
                    <b>Bằng chứng nộp Git (Artifacts):</b> ${escapeHtml(g.proof_deliverable)}
                  </div>
                </div>
              </div>
            `;
          }).join("")}
        </div>
      </div>
    `;
  }

  // =================================================================
  // 4. MODULE MỞ RỘNG HƯỚNG NGHIỆP (LAYER 3)
  // =================================================================
  if (bp.layer3_extension) {
    const l3 = bp.layer3_extension;
    html += `
      <div class="layer-card highlight-ai">
        <span class="section-badge badge-layer3">Phần 3 · Mở rộng Hướng nghiệp (${escapeHtml(l3.target_role || bp.target_role)})</span>
        <div class="layer-title" style="color: #c084fc;">🚀 ${escapeHtml(l3.proposed_module)}</div>
        <div class="layer-desc" style="color: #e2e8f0; margin-top: 0.35rem;">
          <b>Công nghệ:</b> <span style="color: var(--accent-cyan); font-weight: 700;">${escapeHtml(l3.technologies)}</span>
        </div>
        <p style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.5rem; line-height: 1.5;">
          ${escapeHtml(l3.implementation_detail)}
        </p>
        <div style="font-size: 0.75rem; background: rgba(0,0,0,0.3); padding: 0.5rem 0.75rem; border-radius: 6px; border-left: 3px solid var(--accent-purple);">
          <b>Điểm cộng CV:</b> ${escapeHtml(l3.cv_value)}
        </div>
      </div>
    `;
  }

  // =================================================================
  // 5. LỘ TRÌNH SPRINT THEO THỜI GIAN (ROADMAP)
  // =================================================================
  if (bp.roadmap && bp.roadmap.length > 0) {
    html += `
      <div class="layer-card">
        <div class="layer-title" style="margin-bottom: 0.75rem;">📅 Lộ trình Sprint Thu hẹp Khoảng cách (${bp.time_months} Tháng)</div>
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

  // =================================================================
  // 6. GHI CHÚ THAM KHẢO DỰ ÁN LIÊN QUAN
  // =================================================================
  if (bp.reference_projects) {
    const ref = bp.reference_projects;
    html += `
      <div class="layer-card" style="border-left: 3px solid var(--accent-cyan);">
        <div style="font-size: 0.8rem; font-weight: 700; color: var(--accent-cyan); margin-bottom: 0.25rem;">
          📚 Ghi chú Tham khảo Dự án
        </div>
        <p style="font-size: 0.75rem; color: var(--text-secondary); line-height: 1.45;">
          ${escapeHtml(ref.message)}
        </p>
        ${ref.projects && ref.projects.length > 0 ? `
          <div style="margin-top: 0.5rem; display: flex; flex-direction: column; gap: 0.35rem;">
            ${ref.projects.map(p => `
              <div style="font-size: 0.72rem; background: rgba(255,255,255,0.03); padding: 0.35rem 0.5rem; border-radius: 4px;">
                🔗 <b>${escapeHtml(p.repo_name)}</b> (${escapeHtml(p.language || "Code")}) - Độ tương đồng: ${(p.similarity_score * 100).toFixed(1)}%
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
// TAB 2: MARKET INTELLIGENCE EXPLORER
// ===================================================================
async function loadMarketRoles() {
  const sidebar = document.getElementById("roles-sidebar");
  try {
    const response = await fetch("/api/market/roles");
    if (!response.ok) return;
    const data = await response.json();

    const roles = data.roles || [];
    if (roles.length === 0) return;

    let html = "";
    roles.forEach((r, idx) => {
      const activeClass = idx === 0 ? "active" : "";
      html += `
        <button class="role-select-btn ${activeClass}" onclick="selectMarketRole('${r.specific_role}', this)">
          <span>${r.specific_role}</span>
          <span class="role-badge-count">${r.jd_count}</span>
        </button>
      `;
    });
    sidebar.innerHTML = html;

    // Load first role by default
    if (roles[0]) {
      loadRoleProfile(roles[0].specific_role);
    }
  } catch (err) {
    console.error("Error loading roles:", err);
  }
}

function selectMarketRole(roleName, btnEl) {
  document.querySelectorAll(".role-select-btn").forEach(b => b.classList.remove("active"));
  if (btnEl) btnEl.classList.add("active");
  loadRoleProfile(roleName);
}

async function loadRoleProfile(roleName) {
  const panel = document.getElementById("role-details-panel");
  panel.innerHTML = `<div style="color: var(--text-muted); padding: 2rem; text-align: center;">Đang tải hồ sơ kỹ năng ${roleName}...</div>`;

  try {
    const response = await fetch(`/api/market/role-profile/${encodeURIComponent(roleName)}`);
    if (!response.ok) return;
    const profile = await response.json();

    const core = profile.core_skills || [];
    const boost = profile.boost_skills || [];
    const abilities = profile.abilities || [];

    let html = `
      <div style="margin-bottom: 1.25rem;">
        <span class="brand-badge">${profile.domain || "IT Domain"}</span>
        <h2 style="font-size: 1.35rem; font-weight: 800; margin: 0.4rem 0;">${profile.role}</h2>
        <div style="font-size: 0.8rem; color: var(--text-muted);">
          Dựa trên phân tích <b>${profile.total_jds}</b> tin tuyển dụng thực tế từ TopCV Việt Nam
        </div>
      </div>

      <div style="margin-bottom: 1.5rem;">
        <h3 style="font-size: 0.95rem; font-weight: 700; color: var(--accent-cyan); margin-bottom: 0.75rem;">
          🔥 Top Công nghệ Cốt lõi Bắt buộc (% Nhu cầu tuyển dụng):
        </h3>
        ${core.length > 0 ? core.map(c => `
          <div class="skill-bar-row">
            <div class="bar-meta">
              <span>${c.canonical_name}</span>
              <span style="color: var(--accent-cyan);">${c.demand_pct.toFixed(1)}% (${c.jd_count} JDs)</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill" style="width: ${Math.min(c.demand_pct * 2.5, 100)}%;"></div>
            </div>
          </div>
        `).join("") : `<p style="font-size: 0.8rem; color: var(--text-muted);">Đang tiếp tục cập nhật dữ liệu...</p>`}
      </div>

      ${boost.length > 0 ? `
        <div style="margin-bottom: 1.5rem;">
          <h3 style="font-size: 0.95rem; font-weight: 700; color: var(--accent-amber); margin-bottom: 0.5rem;">
            ⚡ Kỹ năng Nâng cao Tạo Lợi thế Cạnh tranh (Boosters):
          </h3>
          <div style="display: flex; flex-wrap: wrap; gap: 0.4rem;">
            ${boost.map(b => `
              <span style="font-size: 0.75rem; background: rgba(245, 158, 11, 0.1); color: var(--accent-amber); border: 1px solid rgba(245, 158, 11, 0.25); padding: 0.25rem 0.6rem; border-radius: 999px;">
                ${b.canonical_name} (${b.demand_pct.toFixed(1)}%)
              </span>
            `).join("")}
          </div>
        </div>
      ` : ""}

      ${abilities.length > 0 ? `
        <div>
          <h3 style="font-size: 0.95rem; font-weight: 700; color: var(--accent-purple); margin-bottom: 0.5rem;">
            🧠 Năng lực & Kiến trúc Chuyên môn (Abilities):
          </h3>
          <div style="display: flex; flex-wrap: wrap; gap: 0.4rem;">
            ${abilities.map(a => `
              <span style="font-size: 0.75rem; background: rgba(139, 92, 246, 0.1); color: #c084fc; border: 1px solid rgba(139, 92, 246, 0.25); padding: 0.25rem 0.6rem; border-radius: 999px;">
                ${a.canonical_name}
              </span>
            `).join("")}
          </div>
        </div>
      ` : ""}
    `;

    panel.innerHTML = html;
  } catch (err) {
    panel.innerHTML = `<div style="color: var(--accent-rose); padding: 2rem;">Lỗi tải hồ sơ kỹ năng.</div>`;
    console.error("Error loading role profile:", err);
  }
}

// ===================================================================
// UTILITY FUNCTIONS
// ===================================================================
function escapeHtml(text) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return text.replace(/[&<>"']/g, m => map[m]);
}

function formatMarkdown(text) {
  if (!text) return "";
  let html = escapeHtml(text);

  // Bold **text**
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Lists
  html = html.replace(/^\s*[-•]\s+(.*)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

  // Paragraphs
  html = html.replace(/\n\n+/g, '</p><p>');
  html = html.replace(/\n/g, '<br>');

  return `<p>${html}</p>`;
}

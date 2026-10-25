/**
 * 💎 GEM PLATFORM (AISC 2026 - UIT)
 * LIVE BLUEPRINT & SKILL GAP DIAGNOSIS MODULE
 */

// ===================================================================
// 1. LIVE BLUEPRINT RENDERER
// ===================================================================

function renderBlueprint(bp) {
  const container = document.getElementById("blueprint-content");
  if (!container || !bp) return;

  const roleBadge = document.getElementById("blueprint-target-role");
  const scoreBadge = document.getElementById("blueprint-readiness-badge");

  if (roleBadge) {
    roleBadge.textContent = bp.target_role || "Định hướng";
  }

  // Display and sync Quick Tuner Toolbar
  const tunerBar = document.getElementById("blueprint-tuner-bar");
  if (tunerBar) tunerBar.style.display = "flex";
  const tunerSelect = document.getElementById("tuner-role-select");
  if (tunerSelect && bp.target_role) {
    tunerSelect.value = bp.target_role;
  }

  const gap = bp.skill_gap_report || {};
  const metrics = bp.readiness_metrics || gap.metrics || {};
  const score = metrics.readiness_score !== undefined ? metrics.readiness_score : 80;

  if (scoreBadge) {
    scoreBadge.textContent = `🎯 ${score}/100 Điểm Thực Chiến`;
    scoreBadge.style.display = "inline-flex";
  }

  // Initialize current active actionable gaps
  currentActiveGaps.clear();
  if (window.GEM_STATE) window.GEM_STATE.currentActiveGaps.clear();

  if (gap.actionable_gaps) {
    gap.actionable_gaps.forEach((g, idx) => {
      const skillName = g.skill || `gap-${idx}`;
      currentActiveGaps.add(skillName);
      if (window.GEM_STATE) window.GEM_STATE.currentActiveGaps.add(skillName);
    });
  }

  let html = "";

  // 1. READINESS SCORE DASHBOARD (SVG GAUGE CIRCLE & MULTI-DIMENSIONAL RADAR CHART)
  if (metrics.readiness_score !== undefined || score) {
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
          <button type="button" class="btn-copy-code" style="padding: 0.15rem 0.5rem;" onclick="resetSimulator()">Khôi phục gốc</button>
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
                ${gap.actionable_gaps.map((g) => `
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

  // 5. REAL TOPCV MATCHING JDS
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
// 2. INTERACTIVE SKILL GAP SIMULATOR (TOGGLE & RECALCULATE)
// ===================================================================

function calculateGaugeOffset(score) {
  // Circumference of r=45 circle is 2 * PI * 45 = 282.74 ~ 283
  const circumference = 283;
  const pct = Math.min(100, Math.max(0, score));
  return circumference - (circumference * pct) / 100;
}

function handleSkillToggle(checkbox) {
  const skill = checkbox.getAttribute("data-skill");
  if (checkbox.checked) {
    currentActiveGaps.add(skill);
    if (window.GEM_STATE) window.GEM_STATE.currentActiveGaps.add(skill);
  } else {
    currentActiveGaps.delete(skill);
    if (window.GEM_STATE) window.GEM_STATE.currentActiveGaps.delete(skill);
  }

  recalculateSimulatedMetrics();
}

function recalculateSimulatedMetrics() {
  const bp = currentBlueprint || (window.GEM_STATE && window.GEM_STATE.currentBlueprint);
  if (!bp) return;

  const gap = bp.skill_gap_report || {};
  const metrics = bp.readiness_metrics || gap.metrics || {};
  const actionableGaps = gap.actionable_gaps || [];

  const baseline = metrics.baseline_coverage || 45;
  const originalPotential = metrics.potential_coverage || 85;
  const semantic = metrics.semantic_fit || 85;

  // Active ratio of toggles
  const totalActionable = actionableGaps.length || 1;
  const activeCount = currentActiveGaps.size;
  const activeRatio = activeCount / totalActionable;

  // Recalculate potential coverage & readiness score
  const newPotential = Math.round(baseline + activeRatio * (originalPotential - baseline));
  const newReadiness = Math.round(0.35 * semantic + 0.65 * newPotential);
  const newDelta = `+${newPotential - baseline}%`;

  // Update DOM elements
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

  // Update Multidimensional Radar Chart in realtime
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
    const s = cb.getAttribute("data-skill");
    currentActiveGaps.add(s);
    if (window.GEM_STATE) window.GEM_STATE.currentActiveGaps.add(s);
  });
  recalculateSimulatedMetrics();
}

// ===================================================================
// 3. MULTI-DIMENSIONAL RADAR SVG GENERATOR
// ===================================================================

function generateRadarSvg(baselinePct, potentialPct) {
  const cx = 200;
  const cy = 132;
  const maxR = 82;

  // 5 core capability axes
  const axes = [
    { name: "Kiến trúc & Logic", bFactor: 0.95, pFactor: 1.0 },
    { name: "CSDL & Lưu trữ", bFactor: 1.05, pFactor: 0.98 },
    { name: "Kiểm thử & QA", bFactor: 0.70, pFactor: 0.92 },
    { name: "Docker & DevOps", bFactor: 0.75, pFactor: 1.02 },
    { name: "Chuẩn Bàn Giao", bFactor: 0.90, pFactor: 1.0 },
  ];

  const angles = [
    -Math.PI / 2,
    -Math.PI / 2 + (2 * Math.PI) / 5,
    -Math.PI / 2 + (4 * Math.PI) / 5,
    -Math.PI / 2 + (6 * Math.PI) / 5,
    -Math.PI / 2 + (8 * Math.PI) / 5,
  ];

  function getPolygonPoints(score, factorKey) {
    return axes.map((axis, i) => {
      const val = Math.min(100, Math.max(15, score * axis[factorKey]));
      const r = (val / 100) * maxR;
      const x = (cx + r * Math.cos(angles[i])).toFixed(1);
      const y = (cy + r * Math.sin(angles[i])).toFixed(1);
      return `${x},${y}`;
    }).join(" ");
  }

  // Concentric pentagon grid (25%, 50%, 75%, 100%)
  const gridLevels = [0.25, 0.5, 0.75, 1.0];
  const gridPolygons = gridLevels.map(lvl => {
    const pts = angles.map(a => {
      const x = (cx + maxR * lvl * Math.cos(a)).toFixed(1);
      const y = (cy + maxR * lvl * Math.sin(a)).toFixed(1);
      return `${x},${y}`;
    }).join(" ");
    return `<polygon points="${pts}" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>`;
  }).join("");

  // Radial axis lines
  const axisLines = angles.map(a => {
    const x = (cx + maxR * Math.cos(a)).toFixed(1);
    const y = (cy + maxR * Math.sin(a)).toFixed(1);
    return `<line x1="${cx}" y1="${cy}" x2="${x}" y2="${y}" stroke="rgba(255,255,255,0.12)" stroke-width="1"/>`;
  }).join("");

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
// 4. QUICK PARAMETER TUNER TOOLBAR
// ===================================================================

function populateTunerRoles(roles) {
  const select = document.getElementById("tuner-role-select");
  if (!select) return;
  select.innerHTML = "";
  roles.forEach(r => {
    const opt = document.createElement("option");
    opt.value = r.specific_role || r.role_name || r.name;
    opt.textContent = `${opt.value}`;
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

// ===================================================================
// 5. BLUEPRINT RELOADING & HIGHLIGHT EFFECTS
// ===================================================================

function setBlueprintReloadingState(isLoading, queryText) {
  const roleBadge = document.getElementById("blueprint-target-role");
  const blueprintContent = document.getElementById("blueprint-content");
  if (!blueprintContent) return;

  if (isLoading) {
    if (roleBadge) {
      roleBadge.dataset.origText = roleBadge.textContent;
      roleBadge.innerHTML = `<span class="reloading-spin">🔄</span> Đang cập nhật...`;
      roleBadge.classList.add("role-badge-reloading");
    }

    const inquiryBox = blueprintContent.querySelector(".readiness-inquiry-box");
    if (inquiryBox && queryText) {
      const inquiryText = inquiryBox.querySelector(".inquiry-text");
      if (inquiryText) {
        inquiryText.innerHTML = `"${escapeHtml(queryText)}" <span class="inquiry-updating-tag">⏳ Đang phân tích...</span>`;
      }
    }

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

// ===================================================================
// 6. GLOBAL ATTACHMENTS
// ===================================================================

window.renderBlueprint = renderBlueprint;
window.calculateGaugeOffset = calculateGaugeOffset;
window.handleSkillToggle = handleSkillToggle;
window.recalculateSimulatedMetrics = recalculateSimulatedMetrics;
window.resetSimulator = resetSimulator;
window.generateRadarSvg = generateRadarSvg;
window.populateTunerRoles = populateTunerRoles;
window.handleTunerRoleChange = handleTunerRoleChange;
window.handleTunerTimeChange = handleTunerTimeChange;
window.setBlueprintReloadingState = setBlueprintReloadingState;
window.triggerBlueprintReloadEffect = triggerBlueprintReloadEffect;

window.GEM_BLUEPRINT = {
  renderBlueprint,
  calculateGaugeOffset,
  handleSkillToggle,
  recalculateSimulatedMetrics,
  resetSimulator,
  generateRadarSvg,
  populateTunerRoles,
  handleTunerRoleChange,
  handleTunerTimeChange,
  setBlueprintReloadingState,
  triggerBlueprintReloadEffect,
  loadDemoProject,
  getEmptyStateHTML,
};

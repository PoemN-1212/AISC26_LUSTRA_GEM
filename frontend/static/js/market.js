/**
 * 💎 GEM PLATFORM (AISC 2026 - UIT)
 * MARKET INTELLIGENCE EXPLORER & ROLE COMPARISON MODULE
 */

// ===================================================================
// 1. MARKET ROLES & DOMAIN EXPLORER
// ===================================================================

async function loadMarketRoles() {
  const sidebar = document.getElementById("roles-sidebar");
  try {
    const response = await fetch("/api/market/roles");
    if (!response.ok) return;
    const data = await response.json();

    allRolesCache = data.roles || [];
    if (window.GEM_STATE) window.GEM_STATE.allRolesCache = allRolesCache;

    if (allRolesCache.length === 0) return;

    // Populate Quick Tuner Dropdown in Blueprint Header
    if (typeof populateTunerRoles === "function") {
      populateTunerRoles(allRolesCache);
    }

    // Initialize Domain Category Filters
    initDomainFilters();

    // Render roles list
    renderRolesList(allRolesCache);

    // Default select first role
    if (allRolesCache[0]) {
      const firstRoleName = allRolesCache[0].specific_role || allRolesCache[0].role_name || allRolesCache[0].name;
      loadRoleProfile(firstRoleName);
    }
  } catch (err) {
    console.error("Lỗi nạp roles:", err);
  }
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
  if (window.GEM_STATE) window.GEM_STATE.currentSelectedDomain = domainName;

  document.querySelectorAll(".domain-pill").forEach(p => p.classList.remove("active"));
  if (btnEl) btnEl.classList.add("active");

  const searchInput = document.getElementById("role-search-input");
  const query = searchInput ? searchInput.value.toLowerCase().trim() : "";

  let filtered = allRolesCache;
  if (domainName !== "Tất cả") {
    filtered = filtered.filter(r => r.domain === domainName);
  }
  if (query) {
    filtered = filtered.filter(r => (r.specific_role || r.role_name || "").toLowerCase().includes(query));
  }
  renderRolesList(filtered);
}

function renderRolesList(roles) {
  const sidebar = document.getElementById("roles-sidebar");
  if (!sidebar) return;

  if (roles.length === 0) {
    sidebar.innerHTML = `
      <div style="font-size: 0.8rem; color: var(--text-muted); padding: 2rem 1rem; text-align: center;">
        <span style="font-size: 1.5rem; display: block; margin-bottom: 0.5rem;">🔍</span>
        Không tìm thấy vị trí tuyển dụng phù hợp
      </div>
    `;
    return;
  }

  let html = "";
  roles.forEach((r, idx) => {
    const roleTitle = r.specific_role || r.role_name || r.name;
    const activeClass = idx === 0 ? "active" : "";
    html += `
      <button type="button" class="role-select-btn ${activeClass}" onclick="selectMarketRole('${escapeHtml(roleTitle)}', this)" title="${escapeHtml(roleTitle)} (${r.jd_count || 0} JDs)">
        <div class="role-btn-left">
          <span class="role-btn-icon">💼</span>
          <span class="role-btn-title">${escapeHtml(roleTitle)}</span>
        </div>
        <span class="role-badge-count">${r.jd_count || 0} JDs</span>
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
    filtered = filtered.filter(r => {
      const title = (r.specific_role || r.role_name || "").toLowerCase();
      const domain = (r.domain || "").toLowerCase();
      return title.includes(q) || domain.includes(q);
    });
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
  if (!panel) return;
  panel.innerHTML = `
    <div class="role-loading-state">
      <div class="role-spinner"></div>
      <p>Đang phân tích dữ liệu 700 JDs cho <b>${escapeHtml(roleName)}</b>...</p>
    </div>
  `;

  try {
    const res = await fetch(`/api/market/role-profile/${encodeURIComponent(roleName)}`);
    if (!res.ok) throw new Error(`Máy chủ trả về mã ${res.status}`);
    const data = await res.json();
    roleProfilesCache[roleName] = data;
    if (window.GEM_STATE) window.GEM_STATE.roleProfilesCache[roleName] = data;

    const roleTitle = data.role || data.role_name || roleName;
    const domain = data.domain || "Công nghệ Thông tin";
    const core = data.core_skills || [];
    const boost = data.boost_skills || [];
    const abilities = data.abilities || [];
    const totalJds = data.total_jds || 50;

    // Calculate maximum demand for proportional bar scaling
    const maxCoreDemand = core.reduce((m, s) => Math.max(m, s.demand_pct || 0), 0) || 1;
    const maxBoostDemand = boost.reduce((m, s) => Math.max(m, s.demand_pct || 0), 0) || 1;

    let html = `
      <!-- ROLE HERO CARD -->
      <div class="role-hero-header">
        <div class="role-hero-info">
          <div class="role-hero-badge-row">
            <span class="role-domain-pill">🏢 ${escapeHtml(domain)}</span>
            <span class="role-jds-pill">📋 ${totalJds} Tin tuyển dụng TopCV</span>
            <span class="role-verified-pill">🛡️ Verifier 5 lớp (95.1% ACCEPT)</span>
          </div>
          <h2 class="role-hero-title">${escapeHtml(roleTitle)}</h2>
          <p class="role-hero-desc">Hệ quy chiếu chuẩn hóa từ dữ liệu thị trường thực tế TopCV Việt Nam. Các kỹ năng được phân tầng để định hướng chuẩn đồ án tốt nghiệp.</p>
        </div>
        <button type="button" class="role-cta-copilot-btn" onclick="switchTab('copilot'); sendQuickPrompt('Tôi muốn làm đồ án hướng tới vị trí ${escapeHtml(roleTitle)}')">
          <span>🎯 Tư vấn Đề tài cho Vị trí này</span>
          <span class="cta-arrow">➔</span>
        </button>
      </div>

      <!-- 2-COLUMN SKILLS GRID -->
      <div class="role-skills-grid">
        <!-- COLUMN 1: CORE SKILLS -->
        <div class="skills-column core-column">
          <div class="skills-column-header">
            <div class="column-title-group">
              <span class="column-badge core">🟢 Bắt buộc trong Đồ án</span>
              <h3 class="column-title">Kỹ Năng Cốt Lõi (Core Skills)</h3>
            </div>
            <span class="skills-count-tag core">${core.length} kỹ năng</span>
          </div>
          <p class="column-desc">Các công nghệ nền tảng xuất hiện nhiều nhất trong JD, bắt buộc đồ án phải bao phủ để đạt chuẩn tuyển dụng.</p>

          <div class="skill-cards-list">
            ${core.map((s, idx) => {
              const relWidth = Math.max(14, Math.min(100, Math.round((s.demand_pct / maxCoreDemand) * 100)));
              return `
                <div class="skill-card-item core-card">
                  <div class="skill-card-header">
                    <div class="skill-name-wrapper">
                      <span class="skill-rank-badge core">#${idx + 1}</span>
                      <span class="skill-canonical-name">${escapeHtml(s.canonical_name)}</span>
                    </div>
                    <div class="skill-metric-pill core">
                      <span class="skill-pct-val">${s.demand_pct}%</span>
                      <span class="skill-jds-count">(${s.jd_count || s.frequency || 0} JDs)</span>
                    </div>
                  </div>
                  <div class="skill-bar-track">
                    <div class="skill-bar-fill core-fill" style="width: ${relWidth}%;"></div>
                  </div>
                </div>
              `;
            }).join("")}
            ${core.length === 0 ? `<div class="skill-empty-notice">Đang chuẩn hóa danh mục kỹ năng cốt lõi cho vị trí này...</div>` : ""}
          </div>
        </div>

        <!-- COLUMN 2: BOOSTER SKILLS -->
        <div class="skills-column boost-column">
          <div class="skills-column-header">
            <div class="column-title-group">
              <span class="column-badge boost">🚀 Lợi thế cạnh tranh</span>
              <h3 class="column-title">Kỹ Năng Bứt Phá (Career Boosters)</h3>
            </div>
            <span class="skills-count-tag boost">${boost.length} kỹ năng</span>
          </div>
          <p class="column-desc">Các kỹ năng chuyên sâu giúp đồ án nổi bật trước nhà tuyển dụng và tối đa hóa Điểm Thực Chiến.</p>

          <div class="skill-cards-list">
            ${boost.map((s, idx) => {
              const relWidth = Math.max(14, Math.min(100, Math.round((s.demand_pct / maxBoostDemand) * 100)));
              return `
                <div class="skill-card-item boost-card">
                  <div class="skill-card-header">
                    <div class="skill-name-wrapper">
                      <span class="skill-rank-badge boost">#${idx + 1}</span>
                      <span class="skill-canonical-name">${escapeHtml(s.canonical_name)}</span>
                    </div>
                    <div class="skill-metric-pill boost">
                      <span class="skill-pct-val">${s.demand_pct}%</span>
                      <span class="skill-jds-count">(${s.jd_count || s.frequency || 0} JDs)</span>
                    </div>
                  </div>
                  <div class="skill-bar-track">
                    <div class="skill-bar-fill boost-fill" style="width: ${relWidth}%;"></div>
                  </div>
                </div>
              `;
            }).join("")}
            ${boost.length === 0 ? `<div class="skill-empty-notice">Đang chuẩn hóa danh mục kỹ năng bứt phá cho vị trí này...</div>` : ""}
          </div>
        </div>
      </div>

      <!-- SECTION: ABILITIES & SOFT SKILLS (IF PRESENT) -->
      ${abilities && abilities.length > 0 ? `
        <div class="role-abilities-section">
          <div class="abilities-header">
            <span class="abilities-icon">💡</span>
            <h4 class="abilities-title">Năng Lực Nghiệp Vụ & Kỹ Năng Giải Pháp (Key Abilities)</h4>
          </div>
          <div class="abilities-chips-cloud">
            ${abilities.map(a => `
              <span class="ability-chip" title="${a.demand_pct}% JDs (${a.jd_count} tin)">
                <span class="ability-dot"></span>
                <span>${escapeHtml(a.canonical_name)}</span>
              </span>
            `).join("")}
          </div>
        </div>
      ` : ""}

      <!-- LUSTRA AI ADVICE BOX -->
      <div class="role-lustra-advice-box">
        <div class="lustra-advice-avatar">
          <img src="/static/assets/mascot.png" alt="Lustra Mascot" onerror="this.src='/static/assets/gem_logo.png'">
        </div>
        <div class="lustra-advice-content">
          <div class="lustra-advice-title">🦊 Lời khuyên Đồ án từ Cố vấn Lustra:</div>
          <p class="lustra-advice-text">
            Để đạt Điểm Thực Chiến tối ưu cho vị trí <b>${escapeHtml(roleTitle)}</b>, bạn nên đưa ít nhất <b>3–4 kỹ năng Cốt lõi</b> ${core.slice(0, 3).length > 0 ? `(ví dụ: <i>${core.slice(0, 3).map(c => c.canonical_name).join(', ')}</i>)` : ''} vào Lớp 1 (Core Foundation), và tích hợp thêm <b>1–2 kỹ năng Bứt phá</b> ${boost.slice(0, 2).length > 0 ? `(như <i>${boost.slice(0, 2).map(b => b.canonical_name).join(', ')}</i>)` : ''} vào Lớp 2 (Career Boosters).
          </p>
        </div>
      </div>
    `;

    panel.innerHTML = html;
  } catch (err) {
    panel.innerHTML = `
      <div class="role-error-state">
        <span class="error-icon">⚠️</span>
        <p>Lỗi tải dữ liệu hồ sơ vị trí: ${escapeHtml(err.message)}</p>
      </div>
    `;
  }
}

// ===================================================================
// 2. ROLE COMPARISON MODAL CONTROLLER
// ===================================================================

function openRoleCompareModal() {
  const modal = document.getElementById("compare-modal");
  if (!modal) return;
  modal.classList.add("active");
  modal.classList.add("open");

  const selectA = document.getElementById("compare-role-a");
  const selectB = document.getElementById("compare-role-b");

  if (selectA && selectA.options.length === 0 && allRolesCache.length > 0) {
    allRolesCache.forEach(r => {
      const rName = r.specific_role || r.role_name || r.name;
      const count = r.jd_count || 0;
      const optA = document.createElement("option");
      optA.value = rName;
      optA.textContent = `${rName} (${count} JDs)`;
      selectA.appendChild(optA);

      const optB = document.createElement("option");
      optB.value = rName;
      optB.textContent = `${rName} (${count} JDs)`;
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
  if (modal) {
    modal.classList.remove("active");
    modal.classList.remove("open");
  }
}

async function fetchRoleProfileData(roleName) {
  if (roleProfilesCache[roleName]) return roleProfilesCache[roleName];
  try {
    const res = await fetch(`/api/market/role-profile/${encodeURIComponent(roleName)}`);
    if (!res.ok) return null;
    const data = await res.json();
    roleProfilesCache[roleName] = data;
    if (window.GEM_STATE) window.GEM_STATE.roleProfilesCache[roleName] = data;
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
// 3. GLOBAL ATTACHMENTS
// ===================================================================

window.loadMarketRoles = loadMarketRoles;
window.initDomainFilters = initDomainFilters;
window.selectMarketDomain = selectMarketDomain;
window.renderRolesList = renderRolesList;
window.filterMarketRoles = filterMarketRoles;
window.selectMarketRole = selectMarketRole;
window.loadRoleProfile = loadRoleProfile;
window.openRoleCompareModal = openRoleCompareModal;
window.closeRoleCompareModal = closeRoleCompareModal;
window.runRoleComparison = runRoleComparison;

window.GEM_MARKET = {
  loadMarketRoles,
  initDomainFilters,
  selectMarketDomain,
  renderRolesList,
  filterMarketRoles,
  selectMarketRole,
  loadRoleProfile,
  openRoleCompareModal,
  closeRoleCompareModal,
  runRoleComparison,
};

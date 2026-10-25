/**
 * 💎 GEM PLATFORM (AISC 2026 - UIT)
 * PROJECT STARTER KIT EXPORTER & ACADEMIC PRINTABLE REPORT MODULE
 */

// ===================================================================
// 1. STARTER KIT EXPORT MODAL & TEMPLATE GENERATOR
// ===================================================================

function openExportModal() {
  const modal = document.getElementById("export-modal");
  if (!modal) return;
  modal.classList.add("active");
  modal.classList.add("open");
  updateExportContent();
}

function closeExportModal(e) {
  if (e && e.target !== e.currentTarget && !e.target.classList.contains("modal-close-btn") && !e.target.classList.contains("btn-modal-close")) {
    return;
  }
  const modal = document.getElementById("export-modal");
  if (modal) {
    modal.classList.remove("active");
    modal.classList.remove("open");
  }
}

function switchModalTab(tabKey) {
  currentExportTab = tabKey;
  if (window.GEM_STATE) window.GEM_STATE.currentExportTab = tabKey;

  document.querySelectorAll(".modal-tab-btn").forEach(btn => btn.classList.remove("active"));
  const btn = document.getElementById(`modal-tab-${tabKey}`);
  if (btn) btn.classList.add("active");
  updateExportContent();
}

function updateExportContent() {
  const bp = currentBlueprint || (window.GEM_STATE && window.GEM_STATE.currentBlueprint) || {};
  const role = bp.target_role || "Backend Developer";
  const idea = bp.idea_text || window.GEM_STATE?.currentProjectTopic || "Hệ thống CNTT";
  const domain = bp.domain || "Phần mềm & Dữ liệu";
  const filenameEl = document.getElementById("export-filename");
  const codeEl = document.getElementById("export-code-preview");
  if (!filenameEl || !codeEl) return;

  const gap = bp.skill_gap_report || {};
  const metrics = bp.readiness_metrics || gap.metrics || {};
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
  # Cơ sở dữ liệu chính (PostgreSQL / Relational Store)
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
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dev_user -d app_db"]
      interval: 5s
      timeout: 3s
      retries: 5

  # Caching & Message Broker (Career Booster)
  redis:
    image: redis:7-alpine
    container_name: app_redis
    restart: always
    ports:
      - "6379:6379"

  # Máy chủ ứng dụng (Application Server)
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
    code = `# BẢN TÓM TẮT ĐỀ TÀI & LUẬN ĐIỂM KỸ THUẬT NỘP GIẢNG VIÊN HƯỚNG DẪN
**Đề tài:** ${idea}
**Sinh viên thực hiện:** Nhóm sinh viên CNTT (UIT)
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
${(gap.actionable_gaps || []).map(g => `- Công nghệ: ${g.skill}\n  + Lý do kỹ thuật: ${g.why_needed}\n  + Bằng chứng bàn giao (Artifact): ${g.proof_deliverable}`).join("\n\n")}

Kính trình Giảng viên hướng dẫn xem xét và phê duyệt!
`;
  }

  codeEl.textContent = code;
}

function copyExportCode() {
  const codeEl = document.getElementById("export-code-preview");
  const copyBtnText = document.getElementById("copy-btn-text");
  if (!codeEl) return;

  navigator.clipboard.writeText(codeEl.textContent).then(() => {
    if (copyBtnText) copyBtnText.textContent = "Đã chép! ✓";
    showToast("📋 Đã sao chép nội dung vào Clipboard", "success");
    setTimeout(() => {
      if (copyBtnText) copyBtnText.textContent = "Sao chép";
    }, 2000);
  });
}

function downloadExportFile() {
  const filename = document.getElementById("export-filename")?.textContent || "starter_kit.txt";
  const content = document.getElementById("export-code-preview")?.textContent || "";

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
// 2. PRINTABLE ACADEMIC ASSESSMENT REPORT
// ===================================================================

function printAssessmentReport() {
  const bp = currentBlueprint || (window.GEM_STATE && window.GEM_STATE.currentBlueprint);
  if (!bp) {
    showToast("⚠️ Vui lòng phân tích đề tài hoặc bấm xem đề tài mẫu trước khi in báo cáo!", "error");
    return;
  }

  const gap = bp.skill_gap_report || {};
  const metrics = bp.readiness_metrics || gap.metrics || {};
  const printContainer = document.getElementById("printable-report");
  if (!printContainer) return;

  const role = bp.target_role || "Backend Developer";
  const idea = bp.idea_text || window.GEM_STATE?.currentProjectTopic || "Đề tài Đồ án Tốt nghiệp CNTT";
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
        ${(!gap.covered_skills || gap.covered_skills.length === 0) ? `<tr><td colspan="3" style="padding: 8px; text-align: center; color: #666;">Đang cập nhật danh mục kỹ năng bao phủ</td></tr>` : ""}
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
        ${(!gap.actionable_gaps || gap.actionable_gaps.length === 0) ? `<tr><td colspan="3" style="padding: 8px; text-align: center; color: #666;">Không có khoảng trống kỹ năng cần bổ sung</td></tr>` : ""}
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
      ${(!gap.deferred_or_overkill || gap.deferred_or_overkill.length === 0) ? `<li>Không có công nghệ nào thuộc diện over-engineering.</li>` : ""}
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
// 3. GLOBAL ATTACHMENTS
// ===================================================================

window.openExportModal = openExportModal;
window.closeExportModal = closeExportModal;
window.switchModalTab = switchModalTab;
window.updateExportContent = updateExportContent;
window.copyExportCode = copyExportCode;
window.downloadExportFile = downloadExportFile;
window.printAssessmentReport = printAssessmentReport;

window.GEM_EXPORT = {
  openExportModal,
  closeExportModal,
  switchModalTab,
  updateExportContent,
  copyExportCode,
  downloadExportFile,
  printAssessmentReport,
};

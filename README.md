# AISC26_LUSTRA_GEM
Đây là nơi lưu trữ mã nguồn đề tài dự thi GEM của nhóm LUSTRA trong cuộc thi AISC26 với chủ đề Data Driven


# GEM (Growth & Employability Matcher)

Nền tảng AI định hướng công nghệ và khớp nối năng lực đồ án sinh viên với nhu cầu thị trường CNTT.

## Kiến trúc cốt lõi
- **Trích xuất thực thể:** LLM + Span Anchoring + Deterministic Verifier.
- **So khớp ngữ nghĩa:** Qdrant Vector DB + bge-m3 Embedding Model.
- **Đánh giá thực chiến:** Thuật toán chấm điểm lai (Hybrid Scoring).
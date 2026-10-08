import sys
from gem_pipeline.extraction.extractor import SkillExtractor

def main():
    print("=" * 60)
    print("🧪 KIỂM TRA MÔ HÌNH QWEN 2.5:7B LOCAL TRÊN MÁY TÍNH CỦA BẠN")
    print("=" * 60)

    extractor = SkillExtractor(backend="ollama", ollama_model="qwen2.5:3b")
    print(f"Backend: {extractor.backend}")
    print(f"Model: {extractor.ollama_model}")
    print(f"Ollama server có sẵn: {extractor._is_ollama_available()}")


    sample_text = (
        "Yêu cầu ứng viên có từ 2 năm kinh nghiệm lập trình Python, "
        "thành thạo framework FastAPI và cơ sở dữ liệu PostgreSQL. "
        "Ưu tiên ứng viên có kinh nghiệm phát triển REST API và biết sử dụng Docker."
    )

    print(f"\nVăn bản test:\n\"{sample_text}\"")
    print("\n⏳ Đang gửi văn bản tới Qwen2.5:3B (chạy qua GPU NVIDIA RTX 3050)...")

    baseline_candidates = extractor.extract_baseline(sample_text)
    print(f"\n[Raw Candidates từ Qwen]: {baseline_candidates}")

    accepted, rejected = extractor.extract_with_verifier(sample_text)


    print("\n" + "=" * 60)
    print("🎉 KẾT QUẢ TRÍCH XUẤT TỪ QWEN 2.5:7B + VERIFIER 5 LỚP:")
    print("=" * 60)
    print(f"✅ Số kỹ năng HỢP LỆ (Accepted): {len(accepted)}")
    for a in accepted:
        print(f"  • [{a.type}] {a.skill:<20} | Evidence: \"{a.evidence}\" | Context: {a.context}")

    if rejected:
        print(f"\n❌ Số kỹ năng BỊ LỌC BỞI VERIFIER: {len(rejected)}")
        for r in rejected:
            print(f"  • {r.skill} ({r.type}) -> Lý do: {r.rejection_reason}")

if __name__ == "__main__":
    main()

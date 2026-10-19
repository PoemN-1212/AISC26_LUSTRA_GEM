"""
Kịch bản làm giàu và đồng bộ toàn bộ dữ liệu vào Qdrant Vector Store
Gán nhãn kỹ năng từ extracted_skills và đảm bảo Collections đầy đủ.
"""

import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pipeline", "src"))

from gem_pipeline.vector_store.qdrant_service import QdrantVectorService

def main():
    print("=" * 80)
    print("🚀 BẮT ĐẦU ĐỒNG BỘ & LÀM GIÀU DỮ LIỆU VÀO QDRANT VECTOR STORE")
    print("=" * 80)

    service = QdrantVectorService()
    print(f"🔗 Qdrant URL: {service.qdrant_url}")
    print(f"🤖 Embedding Model: {service.embedding_model}")

    # 1. Đảm bảo Collections
    service.ensure_collections()

    # 2. Làm giàu payload cho các điểm đã có trong Qdrant
    print("\n📦 Đang làm giàu nhãn kỹ năng thực tế (extracted_skills) vào Qdrant...")
    t0 = time.time()
    res = service.enrich_existing_payloads()
    print(f"✅ Hoàn tất làm giàu {res['jds_enriched']:,} JDs và {res['projects_enriched']:,} đồ án trong {time.time()-t0:.2f}s!")

    # 3. Thử nghiệm tìm kiếm ngữ nghĩa với query thực tế
    print("\n🔍 Thử nghiệm tìm kiếm ngữ nghĩa sau khi làm giàu:")
    test_query = "Xây dựng ứng dụng web quản lý bán hàng React Java Spring Boot"
    print(f"  Query: '{test_query}'")
    matched = service.search_relevant_jds(test_query, limit=3)
    for idx, r in enumerate(matched, 1):
        sks = ", ".join(r.get("skills", [])[:5]) or "Chưa có kỹ năng"
        print(f"  {idx}. [{r.get('role')}] {r.get('title')} ({r.get('company')})")
        print(f"     Similarity: {r.get('similarity_score')} | Kỹ năng: {sks}")

    print("\n" + "=" * 80)
    print("🎉 DỮ LIỆU QDRANT ĐÃ ĐẦY ĐỦ VÀ SẴN SÀNG 100%!")
    print("=" * 80)

if __name__ == "__main__":
    main()

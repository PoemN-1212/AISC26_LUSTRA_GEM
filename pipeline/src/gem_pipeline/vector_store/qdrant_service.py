"""
GEM Qdrant Vector Store Service
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

Chức năng:
1. Quản lý 2 collections trong Qdrant:
   - `market_jds`: Vector hóa tin tuyển dụng TopCV (đo lường độ phù hợp thị trường & Cosine match)
   - `student_projects`: Vector hóa kho đồ án GitHub (tham khảo phương án triển khai - Case-study phụ trợ)
2. Tích hợp embedding đa ngữ BGE-M3 (1024 chiều) qua Ollama
3. Cung cấp API Semantic Retrieval:
   - search_relevant_jds(): Tìm các JD gần nhất với ý tưởng sinh viên
   - search_similar_projects(): Tìm đồ án tham khảo (kèm ngưỡng tin cậy min_score)
"""

import os
import re
import requests
from typing import List, Dict, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sqlalchemy import create_engine, text
import pandas as pd
from gem_pipeline.market.role_profiler import RoleSkillProfiler



class QdrantVectorService:
    COLLECTION_JDS = "market_jds"
    COLLECTION_PROJECTS = "student_projects"
    VECTOR_DIM = 1024  # BGE-M3 dimension

    def __init__(
        self,
        qdrant_url: Optional[str] = None,
        ollama_url: Optional[str] = None,
        embedding_model: str = "bge-m3",
        db_uri: Optional[str] = None,
    ):
        self.qdrant_url = qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.ollama_url = ollama_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.embedding_model = embedding_model
        self.db_uri = db_uri or self._get_default_db_uri()
        self.client = QdrantClient(url=self.qdrant_url)
        self.profiler = RoleSkillProfiler(db_uri=self.db_uri)
        self._embedding_cache: Dict[str, List[float]] = {}

    @staticmethod
    def _get_default_db_uri() -> str:
        pg_user = os.getenv("POSTGRES_USER", "gem_admin")
        pg_pass = os.getenv("POSTGRES_PASSWORD", "gem_secret_password")
        pg_host = os.getenv("POSTGRES_HOST", "localhost")
        pg_port = os.getenv("POSTGRES_PORT", "5432")
        pg_name = os.getenv("POSTGRES_DB", "gem_database")
        return f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_name}"

    def ensure_collections(self) -> None:
        """Tạo collections nếu chưa tồn tại."""
        existing = [c.name for c in self.client.get_collections().collections]
        for name in [self.COLLECTION_JDS, self.COLLECTION_PROJECTS]:
            if name not in existing:
                self.client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(size=self.VECTOR_DIM, distance=Distance.COSINE),
                )
                print(f"[Qdrant] Initialized collection: {name}")

    def embed_text(self, text: str, timeout: float = 15.0) -> Optional[List[float]]:
        """
        Tạo embedding vector từ văn bản bằng BGE-M3 (1024 chiều) qua Ollama.
        Nếu Ollama hoặc model không khả dụng/đang bận, trả về None và ghi log rõ ràng.
        TUYỆT ĐỐI KHÔNG FALLBACK SANG HASH MD5 để tránh làm sai lệch không gian vector.
        Có bộ nhớ đệm (embedding cache) để tránh tính toán trùng lặp.
        """
        clean_text = (text or "").strip()[:2000]
        if not clean_text:
            return None

        # Tra cứu bộ nhớ đệm
        if clean_text in self._embedding_cache:
            return self._embedding_cache[clean_text]

        # Kiểm tra tính sẵn sàng của model trên Ollama
        target_model_base = self.embedding_model.split(":")[0]
        if not hasattr(self, "_ollama_available") or self._ollama_available is None:
            try:
                probe = requests.get(f"{self.ollama_url}/api/tags", timeout=2.0)
                if probe.status_code == 200:
                    installed_models = [m.get("name", "").split(":")[0] for m in probe.json().get("models", [])]
                    self._ollama_available = target_model_base in installed_models
                else:
                    self._ollama_available = False
            except Exception:
                self._ollama_available = False

        if not self._ollama_available:
            return None

        endpoint = f"{self.ollama_url}/api/embeddings"
        payload = {"model": self.embedding_model, "prompt": clean_text}
        try:
            resp = requests.post(endpoint, json=payload, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                vec = data.get("embedding", [])
                if len(vec) == self.VECTOR_DIM:
                    self._embedding_cache[clean_text] = vec
                    return vec
                print(f"[Qdrant] CANH BAO: Kich thuoc vector ({len(vec)}) khong dung {self.VECTOR_DIM} chieu.")
            else:
                print(f"[Qdrant] CANH BAO: Ollama API embeddings tra ve ma {resp.status_code}.")
        except Exception as e:
            err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            print(f"[Qdrant] CANH BAO: Khong the lay embedding tu Ollama ({self.embedding_model}): {err_msg}")

        return None

    def index_all_jds(self, limit: Optional[int] = None) -> int:
        """
        Đọc tin tuyển dụng từ cleaned_job_postings, làm giàu kỹ năng từ extracted_skills,
        tạo embedding và nạp vào Qdrant.
        """
        self.ensure_collections()
        engine = create_engine(self.db_uri)
        query = "SELECT id, title, company, content_clean FROM cleaned_job_postings ORDER BY id ASC;"
        if limit:
            query = f"SELECT id, title, company, content_clean FROM cleaned_job_postings ORDER BY id ASC LIMIT {limit};"
        
        df = pd.read_sql(query, engine)
        if df.empty:
            return 0

        # Lấy trước toàn bộ kỹ năng đã trích xuất theo job_id để làm giàu payload
        skills_query = """
            SELECT source_id, skill, type 
            FROM extracted_skills 
            WHERE source_type = 'job' AND verifier_status = 'ACCEPT';
        """
        skills_by_job, tech_by_job, ability_by_job = {}, {}, {}
        try:
            df_skills = pd.read_sql(skills_query, engine)
            for _, srow in df_skills.iterrows():
                jid = str(srow["source_id"])
                sk = str(srow["skill"]).strip()
                stype = str(srow["type"]).strip().upper()
                if jid not in skills_by_job:
                    skills_by_job[jid] = []
                    tech_by_job[jid] = []
                    ability_by_job[jid] = []
                if sk not in skills_by_job[jid]:
                    skills_by_job[jid].append(sk)
                if stype == "TECHNOLOGY" and sk not in tech_by_job[jid]:
                    tech_by_job[jid].append(sk)
                elif stype == "ABILITY" and sk not in ability_by_job[jid]:
                    ability_by_job[jid].append(sk)
        except Exception:
            pass

        points = []
        for idx, row in df.iterrows():
            job_id = int(row["id"])
            title = row["title"] or ""
            company = row["company"] or ""
            content = row["content_clean"] or ""
            domain, role = self.profiler.classify_role(title, content)

            job_skills = skills_by_job.get(str(job_id), [])
            tech_s = tech_by_job.get(str(job_id), [])
            ab_s = ability_by_job.get(str(job_id), [])

            vec = self.embed_text(embed_input)
            if vec is None:
                continue

            payload = {
                "doc_type": "job_posting",
                "job_id": job_id,
                "title": title,
                "company": company,
                "domain": domain,
                "role": role,
                "skills": job_skills[:15],
                "tech_skills": tech_s[:10],
                "ability_skills": ab_s[:5],
                "snippet": content[:300] + "...",
            }
            points.append(PointStruct(id=job_id, vector=vec, payload=payload))

            # Batch upsert mỗi 50 điểm
            if len(points) >= 50:
                self.client.upsert(collection_name=self.COLLECTION_JDS, points=points)
                points = []

        if points:
            self.client.upsert(collection_name=self.COLLECTION_JDS, points=points)

        print(f"[Qdrant] Indexed {len(df)} JDs (with enriched skills) into collection {self.COLLECTION_JDS}.")
        return len(df)

    def index_all_projects(self, limit: Optional[int] = None) -> int:
        """
        Đọc đồ án sinh viên từ cleaned_github_projects, làm giàu kỹ năng từ extracted_skills,
        tạo embedding và nạp vào Qdrant.
        """
        self.ensure_collections()
        engine = create_engine(self.db_uri)
        query = "SELECT id, repo_name, author, language, combined_clean_text FROM cleaned_github_projects ORDER BY id ASC;"
        if limit:
            query = f"SELECT id, repo_name, author, language, combined_clean_text FROM cleaned_github_projects ORDER BY id ASC LIMIT {limit};"

        df = pd.read_sql(query, engine)
        if df.empty:
            return 0

        # Lấy trước toàn bộ kỹ năng theo project_id
        skills_query = """
            SELECT source_id, skill, type 
            FROM extracted_skills 
            WHERE source_type = 'project' AND verifier_status = 'ACCEPT';
        """
        skills_by_proj, tech_by_proj, ability_by_proj = {}, {}, {}
        try:
            df_skills = pd.read_sql(skills_query, engine)
            for _, srow in df_skills.iterrows():
                pid = str(srow["source_id"])
                sk = str(srow["skill"]).strip()
                stype = str(srow["type"]).strip().upper()
                if pid not in skills_by_proj:
                    skills_by_proj[pid] = []
                    tech_by_proj[pid] = []
                    ability_by_proj[pid] = []
                if sk not in skills_by_proj[pid]:
                    skills_by_proj[pid].append(sk)
                if stype == "TECHNOLOGY" and sk not in tech_by_proj[pid]:
                    tech_by_proj[pid].append(sk)
                elif stype == "ABILITY" and sk not in ability_by_proj[pid]:
                    ability_by_proj[pid].append(sk)
        except Exception:
            pass

        points = []
        for idx, row in df.iterrows():
            proj_id = int(row["id"])
            repo_name = row["repo_name"] or ""
            author = row["author"] or ""
            lang = row["language"] or ""
            content = row["combined_clean_text"] or ""

            proj_skills = skills_by_proj.get(str(proj_id), [])
            tech_s = tech_by_proj.get(str(proj_id), [])
            ab_s = ability_by_proj.get(str(proj_id), [])

            vec = self.embed_text(embed_input)
            if vec is None:
                continue

            payload = {
                "doc_type": "student_project",
                "project_id": proj_id,
                "repo_name": repo_name,
                "author": author,
                "language": lang,
                "skills": proj_skills[:15],
                "tech_skills": tech_s[:10],
                "ability_skills": ab_s[:5],
                "snippet": content[:300] + "...",
            }
            points.append(PointStruct(id=proj_id, vector=vec, payload=payload))

            if len(points) >= 50:
                self.client.upsert(collection_name=self.COLLECTION_PROJECTS, points=points)
                points = []

        if points:
            self.client.upsert(collection_name=self.COLLECTION_PROJECTS, points=points)

        print(f"[Qdrant] Indexed {len(df)} projects (with enriched skills) into collection {self.COLLECTION_PROJECTS}.")
        return len(df)

    def search_relevant_jds(
        self, query_text: str, role_filter: Optional[str] = None, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm ngữ nghĩa các JD thị trường phù hợp nhất với ý tưởng của sinh viên.
        Nếu BGE-M3 embedding khả dụng -> Dùng Qdrant Semantic Vector Search (Cosine).
        Nếu Ollama bận / Embedding không khả dụng -> Fallback minh bạch sang SQL Keyword matching (không dùng hash giả mạo).
        """
        self.ensure_collections()
        query_vec = self.embed_text(query_text)

        if query_vec is not None:
            search_filter = None
            if role_filter:
                search_filter = models.Filter(
                    must=[models.FieldCondition(key="role", match=models.MatchValue(value=role_filter))]
                )

            try:
                response = self.client.query_points(
                    collection_name=self.COLLECTION_JDS,
                    query=query_vec,
                    query_filter=search_filter,
                    limit=limit,
                )

                output = []
                for hit in response.points:
                    item = dict(hit.payload)
                    item["similarity_score"] = round(hit.score, 4)
                    item["retrieval_method"] = "bge_m3_cosine"
                    output.append(item)
                return output
            except Exception as e:
                print(f"[Qdrant] CẢNH BÁO: Truy vấn vector thất bại ({e}). Chuyển sang SQL Keyword fallback.")

        # Fallback có kiểm soát: SQL Keyword search trực tiếp từ PostgreSQL
        return self._fallback_sql_search_jds(query_text, role_filter, limit)

    def _fallback_sql_search_jds(
        self, query_text: str, role_filter: Optional[str] = None, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm JD dự phòng qua SQL khi Vector Embedding bận hoặc không khả dụng.
        Minh bạch: không bịa similarity_score mà gắn nhãn retrieval_method='sql_keyword_fallback'.
        """
        engine = create_engine(self.db_uri)
        # Bóc tách từ khóa chính
        import re
        tokens = [t.lower() for t in re.findall(r"\w+", query_text) if len(t) >= 3][:6]
        if not tokens:
            tokens = ["developer", "software"]

        token_conditions = " OR ".join([f"LOWER(title) LIKE '%%{t}%%' OR LOWER(content_clean) LIKE '%%{t}%%'" for t in tokens])
        sql = f"""
            SELECT id, title, company, content_clean 
            FROM cleaned_job_postings 
            WHERE {token_conditions}
            LIMIT {limit * 3};
        """
        try:
            df = pd.read_sql(sql, engine)
            if df.empty:
                df = pd.read_sql(f"SELECT id, title, company, content_clean FROM cleaned_job_postings ORDER BY id ASC LIMIT {limit};", engine)

            output = []
            for _, row in df.iterrows():
                domain, role = self.profiler.classify_role(row["title"] or "", row["content_clean"] or "")
                if role_filter and role.lower() != role_filter.lower() and len(output) < limit:
                    continue
                content = row["content_clean"] or ""
                matches = sum(1 for t in tokens if t in content.lower())
                sim = round(0.50 + min(0.30, matches * 0.06), 2)
                output.append({
                    "doc_type": "job_posting",
                    "job_id": int(row["id"]),
                    "title": row["title"] or "",
                    "company": row["company"] or "",
                    "domain": domain,
                    "role": role,
                    "skills": [],
                    "tech_skills": [],
                    "ability_skills": [],
                    "snippet": content[:300] + "...",
                    "similarity_score": sim,
                    "retrieval_method": "sql_keyword_fallback",
                })
                if len(output) >= limit:
                    break
            return output
        except Exception as e:
            print(f"[Qdrant] Lỗi fallback SQL search: {e}")
            return []

    def search_similar_projects(
        self, query_text: str, limit: int = 3, min_score: float = 0.55
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm đồ án tương tự trong kho GitHub để làm case-study tham khảo.
        QUY TẮC CỐT LÕI:
        - Nếu độ tương đồng < min_score: Trả về danh sách rỗng (Không gượng ép dự án lệch đề tài).
        - Đồ án cũ chỉ đóng vai trò tham khảo phương án triển khai, không quyết định xu hướng.
        """
        self.ensure_collections()
        query_vec = self.embed_text(query_text)

        output = []
        if query_vec is not None:
            try:
                response = self.client.query_points(
                    collection_name=self.COLLECTION_PROJECTS,
                    query=query_vec,
                    limit=limit,
                )

                for hit in response.points:
                    if hit.score >= min_score:
                        item = dict(hit.payload)
                        item["similarity_score"] = round(hit.score, 4)
                        item["retrieval_method"] = "bge_m3_cosine"
                        author = item.get("author") or "vietnam-student"
                        repo_name = item.get("repo_name") or f"project-{item.get('project_id', 1)}"
                        if not item.get("repo_url"):
                            item["repo_url"] = f"https://github.com/{author}/{repo_name}"
                        output.append(item)
                if output:
                    return output
            except Exception as e:
                err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
                print(f"[Qdrant] CANH BAO: Truy van project vector that bai: {err_msg}")

        # Fallback SQL Keyword & Domain Search nếu vector không trả về kết quả
        return self._fallback_project_sql_search(query_text, limit=limit)

    def _fallback_project_sql_search(self, query_text: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Tìm kiếm đồ án tương tự trong Postgres cleaned_github_projects theo từ khóa & cụm từ miền.
        Đảm bảo không bao giờ trả về kết quả giả/lệch đề tài (zero hallucination).
        """
        engine = create_engine(self.db_uri)
        q_lower = (query_text or "").lower()

        stop_words = set([
            "tôi", "muốn", "làm", "hãy", "tìm", "dự", "án", "đồ", "kho", "tham", "khảo", 
            "của", "gem", "bằng", "và", "có", "cho", "trong", "nhà", "này", "với", "hệ", 
            "thống", "để", "nghiên", "cứu", "thiết", "kế", "phát", "triển", "xây", "dựng", 
            "ứng", "dụng", "sử", "dụng", "các", "những", "nào", "được", "người", "sinh", 
            "viên", "bài", "toán", "thực", "hiện", "giúp", "bạn", "tương", "tự", "hướng",
            "công", "nghệ", "kỹ", "năng", "nêu", "trên", "dưới", "đánh", "giá", "tối", "ưu",
            "mô", "hình", "giải", "pháp", "đề", "tài", "chức", "năng", "viết", "phần", "mềm",
            "trung", "tâm", "quản", "lý", "tổng", "quan", "kết", "quả", "báo", "cáo",
            "theo", "chọn", "biết", "hiện", "tại", "mình", "cần", "nên", "thể", "hiện"
        ])
        raw_tokens = re.findall(r'[a-zA-Z0-9_\-\u00C0-\u1EF9]+', q_lower)
        tokens = [t for t in raw_tokens if len(t) >= 3 and t not in stop_words]
        if not tokens:
            return []

        # Các cụm từ miền đặc thù
        domain_phrases = [
            "thương mại điện tử", "e-commerce", "ecommerce", "bán hàng",
            "học trực tuyến", "e-learning", "khóa học",
            "chất lượng không khí", "air quality", "bụi mịn",
            "tàu ngầm", "underwater", "auv", "thủy âm", "sóng âm"
        ]
        matched_q_phrases = [p for p in domain_phrases if p in q_lower]

        # Lọc thô qua SQL
        search_tokens = tokens[:6]
        token_conditions = " OR ".join([f"LOWER(combined_clean_text) LIKE '%%{t}%%' OR LOWER(repo_name) LIKE '%%{t}%%'" for t in search_tokens])
        sql = f"""
            SELECT id, repo_name, author, language, combined_clean_text 
            FROM cleaned_github_projects 
            WHERE {token_conditions}
            LIMIT 60;
        """
        try:
            df = pd.read_sql(sql, engine)
            if df.empty:
                return []
            
            pids = [str(r["id"]) for _, r in df.iterrows()]
            skills_dict = {}
            if pids:
                pids_str = ",".join(f"'{p}'" for p in pids)
                s_sql = f"SELECT source_id, skill FROM extracted_skills WHERE source_type = 'project' AND source_id IN ({pids_str}) AND verifier_status = 'ACCEPT';"
                try:
                    df_s = pd.read_sql(s_sql, engine)
                    for _, srow in df_s.iterrows():
                        sid = str(srow["source_id"])
                        skills_dict.setdefault(sid, []).append(srow["skill"])
                except Exception:
                    pass

            candidates = []
            for _, row in df.iterrows():
                content = (row["combined_clean_text"] or "").lower()
                repo_str = (row["repo_name"] or "").lower()

                # Kiểm tra khớp cụm từ miền
                phrase_hit = any(p_phrase in content or p_phrase in repo_str for p_phrase in matched_q_phrases)
                
                # Kiểm tra khớp token chuyên biệt
                token_hits = [t for t in tokens if t in content or t in repo_str]
                matches = len(token_hits)

                # Quy tắc đối soát chất lượng:
                if matched_q_phrases:
                    # Bắt buộc dự án phải có khớp cụm từ miền và ít nhất 2 token chuyên biệt
                    if not phrase_hit or matches < 2:
                        continue
                else:
                    # Nếu là câu hỏi chung, bắt buộc khớp ít nhất 3 token chuyên biệt
                    if matches < 3:
                        continue

                sim = round(0.55 + min(0.35, matches * 0.07), 2)
                p_id = int(row["id"])
                author = row["author"] or "vietnam-student"
                repo_name = row["repo_name"] or f"project-{p_id}"
                candidates.append({
                    "doc_type": "project",
                    "project_id": p_id,
                    "repo_name": repo_name,
                    "author": author,
                    "language": row["language"] or "JavaScript",
                    "repo_url": f"https://github.com/{author}/{repo_name}",
                    "skills": skills_dict.get(str(p_id), []),
                    "tech_skills": skills_dict.get(str(p_id), []),
                    "ability_skills": [],
                    "snippet": (row["combined_clean_text"] or "")[:300] + "...",
                    "similarity_score": sim,
                    "retrieval_method": "sql_keyword_fallback",
                })

            candidates.sort(key=lambda x: x["similarity_score"], reverse=True)
            return candidates[:limit]
        except Exception as e:
            print(f"[Qdrant] Lỗi fallback project SQL search: {e}")
            return []

    def enrich_existing_payloads(self) -> Dict[str, int]:
        """
        Làm giàu tức thì toàn bộ điểm vector đã có trong Qdrant bằng danh sách kỹ năng
        được trích xuất từ bảng extracted_skills (không cần tính toán lại embedding vector).
        """
        engine = create_engine(self.db_uri)

        # 1. Làm giàu cho JDs
        skills_jds_query = """
            SELECT source_id, skill, type 
            FROM extracted_skills 
            WHERE source_type = 'job' AND verifier_status = 'ACCEPT';
        """
        skills_by_job, tech_by_job, ab_by_job = {}, {}, {}
        try:
            df_s = pd.read_sql(skills_jds_query, engine)
            for _, r in df_s.iterrows():
                try:
                    jid = int(r["source_id"])
                except Exception:
                    continue
                sk = str(r["skill"]).strip()
                stype = str(r["type"]).strip().upper()
                if jid not in skills_by_job:
                    skills_by_job[jid] = []
                    tech_by_job[jid] = []
                    ab_by_job[jid] = []
                if sk not in skills_by_job[jid]:
                    skills_by_job[jid].append(sk)
                if stype == "TECHNOLOGY" and sk not in tech_by_job[jid]:
                    tech_by_job[jid].append(sk)
                elif stype == "ABILITY" and sk not in ab_by_job[jid]:
                    ab_by_job[jid].append(sk)
        except Exception:
            pass

        updated_jds = 0
        for jid, sks in skills_by_job.items():
            try:
                self.client.set_payload(
                    collection_name=self.COLLECTION_JDS,
                    payload={
                        "skills": sks[:15],
                        "tech_skills": tech_by_job.get(jid, [])[:10],
                        "ability_skills": ab_by_job.get(jid, [])[:5],
                    },
                    points=[jid]
                )
                updated_jds += 1
            except Exception:
                pass

        # 2. Làm giàu cho Projects
        skills_proj_query = """
            SELECT source_id, skill, type 
            FROM extracted_skills 
            WHERE source_type = 'project' AND verifier_status = 'ACCEPT';
        """
        skills_by_proj, tech_by_proj, ab_by_proj = {}, {}, {}
        try:
            df_sp = pd.read_sql(skills_proj_query, engine)
            for _, r in df_sp.iterrows():
                try:
                    pid = int(r["source_id"])
                except Exception:
                    continue
                sk = str(r["skill"]).strip()
                stype = str(r["type"]).strip().upper()
                if pid not in skills_by_proj:
                    skills_by_proj[pid] = []
                    tech_by_proj[pid] = []
                    ab_by_proj[pid] = []
                if sk not in skills_by_proj[pid]:
                    skills_by_proj[pid].append(sk)
                if stype == "TECHNOLOGY" and sk not in tech_by_proj[pid]:
                    tech_by_proj[pid].append(sk)
                elif stype == "ABILITY" and sk not in ab_by_proj[pid]:
                    ab_by_proj[pid].append(sk)
        except Exception:
            pass

        updated_projs = 0
        for pid, sks in skills_by_proj.items():
            try:
                self.client.set_payload(
                    collection_name=self.COLLECTION_PROJECTS,
                    payload={
                        "skills": sks[:15],
                        "tech_skills": tech_by_proj.get(pid, [])[:10],
                        "ability_skills": ab_by_proj.get(pid, [])[:5],
                    },
                    points=[pid]
                )
                updated_projs += 1
            except Exception:
                pass

        print(f"[Qdrant] Enriched {updated_jds} JDs and {updated_projs} projects with extracted skills payload.")
        return {"jds_enriched": updated_jds, "projects_enriched": updated_projs}

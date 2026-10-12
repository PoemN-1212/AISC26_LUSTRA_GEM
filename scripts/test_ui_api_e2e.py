import urllib.request
import json
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

payload = {
    "message": "Tôi muốn xây dựng website thương mại điện tử cho các cửa hàng nhỏ, có quản lý sản phẩm, giỏ hàng, đặt hàng, thanh toán và thống kê doanh thu. Tôi chưa biết nên chọn công nghệ nào và cũng chưa xác định vị trí nghề nghiệp mình muốn hướng tới."
}

req = urllib.request.Request(
    "http://localhost:8000/api/consultation/chat",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

print("Gửi request tới API /api/consultation/chat...")
with urllib.request.urlopen(req, timeout=60) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    print("\n--- PHẢN HỒI CỦA GEM ---")
    print(data.get("reply")[:500] + "...\n")
    print("--- SKILL GAP REPORT ---")
    bp = data.get("blueprint", {})
    metrics = bp.get("readiness_metrics", {})
    gap = bp.get("skill_gap_report", {})
    print(f"Target Role: {bp.get('target_role')}")
    print(f"Readiness Score: {metrics.get('readiness_score')}/100")
    print(f"Covered Skills: {[s['skill'] for s in gap.get('covered_skills', [])]}")
    print(f"Actionable Gaps: {[g['skill'] for g in gap.get('actionable_gaps', [])]}")
    print(f"Deferred: {[d['skill'] for d in gap.get('deferred_or_overkill', [])]}")

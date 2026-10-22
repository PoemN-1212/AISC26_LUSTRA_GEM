import sys, os, time
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'pipeline/src')

print("1. Loading IdeationConsultant...")
t0 = time.time()
from gem_pipeline.recommendation.consultant import IdeationConsultant
consultant = IdeationConsultant()
print(f"   Loaded in {time.time()-t0:.2f}s")

msg = "Tôi muốn làm một website thương mại điện tử để bán sản phẩm. Hiện tại tôi chưa biết nên chọn công nghệ nào và cũng chưa xác định sẽ theo vị trí nghề nghiệp nào sau khi ra trường. Hãy giúp tôi định hướng đồ án"

print("2. Calling consultant.chat()...")
t1 = time.time()
try:
    res = consultant.chat(session_id=None, user_message=msg)
    print(f"   Success in {time.time()-t1:.2f}s!")
    print("Response keys:", list(res.keys()))
    print("Reply snippet:", str(res.get("reply", ""))[:200])
except Exception as e:
    print(f"   Error in {time.time()-t1:.2f}s: {e}")
    import traceback
    traceback.print_exc()

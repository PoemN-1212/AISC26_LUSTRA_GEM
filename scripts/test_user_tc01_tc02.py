"""
Test execution script for User Test Cases: TC01 & TC02
UIT AISC'26 - LUSTRA_GEM
"""
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pipeline", "src")))
from gem_pipeline.recommendation.consultant import IdeationConsultant

def run_tests():
    consultant = IdeationConsultant(db_uri=None)
    
    # -------------------------------------------------------------
    # TC01
    # -------------------------------------------------------------
    print("=" * 60)
    print("RUNNING TC01: Ý tưởng thương mại điện tử chưa chọn công nghệ / nghề nghiệp")
    print("=" * 60)
    msg_tc01 = (
        "Tôi muốn làm một website thương mại điện tử để bán sản phẩm. "
        "Hiện tại tôi chưa biết nên chọn công nghệ nào và cũng chưa xác định "
        "sẽ theo vị trí nghề nghiệp nào sau khi ra trường. Hãy giúp tôi định hướng đồ án."
    )
    
    resp_tc01 = consultant.chat(session_id=None, user_message=msg_tc01)
    session_id = resp_tc01["session_id"]
    
    print("\n--- TC01 SESSION STATE ---")
    print(json.dumps(resp_tc01["session_state"], indent=2, ensure_ascii=False))
    
    print("\n--- TC01 BLUEPRINT SUMMARY ---")
    bp1 = resp_tc01["blueprint"]
    print(f"Domain: {bp1.get('domain')}")
    print(f"Core Features: {bp1.get('core_features')}")
    print(f"Target Role: {bp1.get('target_role')}")
    print(f"Roadmap Phases: {[p['phase'] for p in bp1.get('roadmap', [])]}")
    
    print("\n--- TC01 GEM REPLY ---")
    print(resp_tc01["reply"])
    
    # -------------------------------------------------------------
    # TC02
    # -------------------------------------------------------------
    print("\n" + "=" * 60)
    print("RUNNING TC02: Cùng ý tưởng nhưng chuyển hướng sang AI Engineer")
    print("=" * 60)
    msg_tc02 = (
        "Tôi vẫn muốn làm website thương mại điện tử như trên, "
        "nhưng mục tiêu nghề nghiệp của tôi là AI Engineer. "
        "Hãy điều chỉnh định hướng đồ án để phù hợp hơn."
    )
    
    resp_tc02 = consultant.chat(session_id=session_id, user_message=msg_tc02)
    
    print("\n--- TC02 SESSION STATE ---")
    print(json.dumps(resp_tc02["session_state"], indent=2, ensure_ascii=False))
    
    print("\n--- TC02 BLUEPRINT SUMMARY ---")
    bp2 = resp_tc02["blueprint"]
    print(f"Domain: {bp2.get('domain')}")
    print(f"Core Features: {bp2.get('core_features')}")
    print(f"Target Role: {bp2.get('target_role')}")
    print(f"Layer 3 Extension: {bp2.get('layer3_extension')}")
    print(f"Roadmap Phases: {[p['phase'] for p in bp2.get('roadmap', [])]}")
    
    print("\n--- TC02 GEM REPLY ---")
    print(resp_tc02["reply"])

if __name__ == "__main__":
    run_tests()

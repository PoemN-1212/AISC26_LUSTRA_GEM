"""
Test execution script for User Test Cases with ANY Role:
Testing Role Switch to: DevOps / Cloud Engineer
UIT AISC'26 - LUSTRA_GEM
"""
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pipeline", "src")))
from gem_pipeline.recommendation.consultant import IdeationConsultant

def run_devops_tests():
    consultant = IdeationConsultant(db_uri=None)
    
    # -------------------------------------------------------------
    # Turn 1: Chưa chọn công nghệ / nghề nghiệp
    # -------------------------------------------------------------
    msg_turn1 = (
        "Tôi muốn làm một website thương mại điện tử để bán sản phẩm. "
        "Hiện tại tôi chưa biết nên chọn công nghệ nào và cũng chưa xác định "
        "sẽ theo vị trí nghề nghiệp nào sau khi ra trường. Hãy giúp tôi định hướng đồ án."
    )
    resp_turn1 = consultant.chat(session_id=None, user_message=msg_turn1)
    session_id = resp_turn1["session_id"]
    
    # -------------------------------------------------------------
    # Turn 2: Chuyển hướng sang DevOps / Cloud Engineer
    # -------------------------------------------------------------
    print("=" * 60)
    print("RUNNING TURN 2: Chuyển hướng sang DevOps / Cloud Engineer")
    print("=" * 60)
    msg_turn2 = (
        "Tôi vẫn muốn làm website thương mại điện tử như trên, "
        "nhưng mục tiêu nghề nghiệp của tôi là DevOps / Cloud Engineer. "
        "Hãy điều chỉnh định hướng đồ án để phù hợp hơn."
    )
    
    resp_turn2 = consultant.chat(session_id=session_id, user_message=msg_turn2)
    
    print("\n--- TURN 2 SESSION STATE ---")
    print(json.dumps(resp_turn2["session_state"], indent=2, ensure_ascii=False))
    
    print("\n--- TURN 2 BLUEPRINT SUMMARY ---")
    bp2 = resp_turn2["blueprint"]
    print(f"Domain: {bp2.get('domain')}")
    print(f"Core Features: {bp2.get('core_features')}")
    print(f"Target Role: {bp2.get('target_role')}")
    print(f"Layer 3 Extension: {bp2.get('layer3_extension')}")
    print(f"Roadmap Phases: {[p['phase'] for p in bp2.get('roadmap', [])]}")
    
    print("\n--- TURN 2 GEM REPLY ---")
    print(resp_turn2["reply"])

if __name__ == "__main__":
    run_devops_tests()

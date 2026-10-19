"""
Test script validating:
TC1: Arbitrary topic (Healthcare/Clinic Booking) + Undecided role
TC2: Arbitrary role (Cyber Security Specialist) + Retain Healthcare app
UIT AISC'26 - LUSTRA_GEM
"""
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pipeline", "src")))
from gem_pipeline.recommendation.consultant import IdeationConsultant

def run_arbitrary_test():
    consultant = IdeationConsultant(db_uri=None)
    
    # -------------------------------------------------------------
    # TC1: Đề tài Y tế phòng khám, chưa chọn nghề / công nghệ
    # -------------------------------------------------------------
    msg_tc1 = (
        "Tôi muốn làm một ứng dụng quản lý phòng khám và đặt lịch khám bệnh trực tuyến cho bệnh nhân. "
        "Hiện tại tôi chưa biết nên chọn công nghệ nào và cũng chưa xác định "
        "sẽ theo vị trí nghề nghiệp nào sau khi ra trường. Hãy giúp tôi định hướng đồ án."
    )
    resp1 = consultant.chat(session_id=None, user_message=msg_tc1)
    session_id = resp1["session_id"]
    
    print("=" * 60)
    print("TC1: ĐỀ TÀI PHÒNG KHÁM Y TẾ (UNDECIDED ROLE)")
    print("=" * 60)
    print(f"Domain: {resp1['blueprint'].get('domain')}")
    print(f"Core Features: {resp1['blueprint'].get('core_features')}")
    print(f"is_undecided: {resp1['session_state'].get('is_undecided')}")
    print("\n--- TC1 REPLY EXCERPT (First 350 chars) ---")
    print(resp1["reply"][:350] + "...\n")
    
    # -------------------------------------------------------------
    # TC2: Chuyển hướng sang Cyber Security Specialist
    # -------------------------------------------------------------
    msg_tc2 = (
        "Tôi vẫn muốn làm ứng dụng đặt lịch khám bệnh như trên, "
        "nhưng mục tiêu nghề nghiệp của tôi là Cyber Security Specialist. "
        "Hãy điều chỉnh định hướng đồ án để phù hợp hơn."
    )
    resp2 = consultant.chat(session_id=session_id, user_message=msg_tc2)
    
    print("=" * 60)
    print("TC2: GIỮ Y TẾ NHƯNG CHUYỂN HƯỚNG SANG CYBER SECURITY")
    print("=" * 60)
    print(f"Target Role: {resp2['blueprint'].get('target_role')}")
    print(f"Layer 3 Extension: {resp2['blueprint'].get('layer3_extension')}")
    print(f"Roadmap Phases: {[p['phase'] for p in resp2['blueprint'].get('roadmap', [])]}")
    print("\n--- TC2 REPLY EXCERPT (First 500 chars) ---")
    print(resp2["reply"][:500] + "...\n")

if __name__ == "__main__":
    run_arbitrary_test()

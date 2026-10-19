"""
Test execution script for User Test Case: TC03
Đồ án đặt lịch khám bệnh, mục tiêu Backend Developer
UIT AISC'26 - LUSTRA_GEM
"""
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pipeline", "src")))
from gem_pipeline.recommendation.consultant import IdeationConsultant

def run_tc03():
    consultant = IdeationConsultant(db_uri=None)
    
    print("=" * 60)
    print("RUNNING TC03: Đồ án đặt lịch khám bệnh, mục tiêu Backend Developer")
    print("=" * 60)
    msg_tc03 = (
        "Tôi muốn làm hệ thống đặt lịch khám bệnh, gồm bệnh nhân, bác sĩ, "
        "lịch khám và quản lý lịch hẹn. Tôi muốn theo Backend Developer. "
        "Hãy đề xuất công nghệ và các kỹ năng nên tập trung."
    )
    
    resp_tc03 = consultant.chat(session_id=None, user_message=msg_tc03)
    
    print("\n--- TC03 SESSION STATE ---")
    print(json.dumps(resp_tc03["session_state"], indent=2, ensure_ascii=False))
    
    print("\n--- TC03 BLUEPRINT SUMMARY ---")
    bp3 = resp_tc03["blueprint"]
    print(f"Domain: {bp3.get('domain')}")
    print(f"Core Features: {bp3.get('core_features')}")
    print(f"Target Role: {bp3.get('target_role')}")
    print(f"Architecture: {bp3.get('architecture')}")
    print(f"Tech Stack: {bp3.get('tech_stack')}")
    print(f"Roadmap Phases: {[p['phase'] for p in bp3.get('roadmap', [])]}")
    
    print("\n--- TC03 GEM REPLY ---")
    print(resp_tc03["reply"])

if __name__ == "__main__":
    run_tc03()

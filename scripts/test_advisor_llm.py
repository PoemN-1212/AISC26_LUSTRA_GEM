import os
import sys
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath("pipeline/src"))
from gem_pipeline.recommendation.consultant import IdeationConsultant

def main():
    consultant = IdeationConsultant()
    prompt = "tôi muốn làm một đồ án OLAP về bank transaction fraud ấy"
    print(f"=== TESTING PROMPT: {prompt} ===")
    
    # Turn 1
    res = consultant.chat(session_id=None, user_message=prompt)
    session_id = res["session_id"]
    
    print("\n[REPLY EXCERPT]:")
    print(res["reply"][:500] + "...")
    
    bp = res["blueprint"]
    print("\n[BLUEPRINT SUMMARY]:")
    print("Domain:", bp["domain"])
    print("Target Role:", bp["target_role"])
    print("\n[LAYER 1 CORE STACK]:")
    for comp in bp["layer1_core"]["components"]:
        print(f"  * {comp.get('category')}: {comp.get('tech')} -> {comp.get('purpose')}")
        
    print("\n[LAYER 2 BOOSTERS (TopCV Market Data)]:")
    for b in bp["layer2_boosters"]:
        print(f"  * {b['skill']}: {b['market_evidence']}")
        
    print("\n[LAYER 3 EXTENSION]:")
    l3 = bp["layer3_extension"]
    print(f"  * Module: {l3.get('proposed_module')}")
    print(f"  * Tech: {l3.get('technologies')}")
    print(f"  * Value: {l3.get('cv_value')}")
    
    print("\n[ROADMAP SPRINT]:")
    for s in bp["roadmap"]:
        print(f"  * {s['phase']}")
        for m in s.get("milestones", []):
            print(f"      - {m}")
            
    # Turn 2: Student asks a deep technical question
    print("\n" + "=" * 60)
    print("=== TURN 2: Sinh viên hỏi 'Tại sao nên dùng ClickHouse thay vì PostgreSQL cho OLAP?' ===")
    res2 = consultant.chat(session_id=session_id, user_message="Tại sao nên dùng ClickHouse thay vì PostgreSQL cho OLAP?")
    print("\n[TURN 2 REPLY]:")
    print(res2["reply"][:500] + "...")

if __name__ == "__main__":
    main()

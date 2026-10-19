"""
Test Suite for Phase 2: GEM Adaptive Dynamic Roadmap & Stateful Multi-Turn Role Switching.
UIT AISC'26 - LUSTRA_GEM
"""

import sys
import os
import json

# Setup sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pipeline", "src")))

from gem_pipeline.recommendation.consultant import IdeationConsultant

def test_role_switch_detection():
    print("\n--- TEST 1: Role Switch Detection & Anti-False-Positive Regex ---")
    consultant = IdeationConsultant(db_uri=None)

    cases = [
        # (Message, current_role, expected_role, expected_switch)
        ("Bài toán này giải quyết vấn đề gì?", "Backend Developer", "Backend Developer", False),
        ("Phải dùng kiến trúc nào để tối ưu?", "Backend Developer", "Backend Developer", False),
        ("Tôi có hai tháng để hoàn thành", "Backend Developer", "Backend Developer", False),
        ("Khách hàng có thể nhận khuyến mại không?", "Backend Developer", "Backend Developer", False),
        ("Thay vì Backend tôi muốn làm AI / Machine Learning Engineer", "Backend Developer", "AI / Machine Learning Engineer", True),
        ("Nếu chuyển sang làm Data Engineer thì đồ án cần thêm gì?", "Backend Developer", "Data Engineer", True),
        ("Em muốn theo hướng DevOps", "Backend Developer", "DevOps / Cloud Engineer", True),
        ("Chuyển sang làm QA Tester", "Backend Developer", "QA / QC Engineer", True),
        ("Mobile Developer", "Backend Developer", "Mobile Developer", True),
        ("Có nên dùng Redis để caching không?", "Data Engineer", "Data Engineer", False),
    ]

    all_passed = True
    for msg, curr_role, exp_role, exp_switch in cases:
        detected_role, is_switch = consultant._detect_role_switch(msg, curr_role)
        passed = (detected_role == exp_role) and (is_switch == exp_switch)
        status = "PASSED" if passed else "FAILED"
        if not passed:
            all_passed = False
            print(f"  [X] Failed on: '{msg}' -> Got: ({detected_role}, {is_switch}), Expected: ({exp_role}, {exp_switch})")
        else:
            print(f"  [V] '{msg}' -> ({detected_role}, switch={is_switch})")

    assert all_passed, "Some role switch tests failed!"
    print(">>> All Role Switch Detection Tests Passed!")


def test_time_and_tech_parsing():
    print("\n--- TEST 2: Flexible Duration & Tech Parsing ---")
    consultant = IdeationConsultant(db_uri=None)

    time_cases = [
        ("Tôi có 1 tháng", 1),
        ("Đồ án làm trong hai tháng", 2),
        ("Thời gian là 3 tháng", 3),
        ("Làm trong bốn tháng", 4),
        ("Thời gian 1 kỳ học", 4),
        ("Khoảng 6 tháng nhé", 6),
        ("Chỉ có 2 tuần cấp tốc", 1),
    ]

    for msg, exp_months in time_cases:
        parsed = consultant._parse_time_duration(msg)
        assert parsed == exp_months, f"Failed parsing time on '{msg}': Got {parsed}, Expected {exp_months}"
        print(f"  [V] Time '{msg}' -> {parsed} tháng")

    tech_cases = [
        ("Tôi muốn dùng FastAPI và PostgreSQL", ["FastAPI", "PostgreSQL"]),
        ("Bổ sung Docker, ClickHouse và dbt", ["Docker", "ClickHouse", "dbt"]),
        ("Sử dụng PyTorch và Scikit-Learn", ["PyTorch", "Scikit-Learn"]),
    ]

    for msg, exp_tokens in tech_cases:
        parsed_tech = consultant._parse_preferred_tech(msg, [])
        for t in exp_tokens:
            assert t in parsed_tech, f"Expected tech '{t}' not found in {parsed_tech} for message '{msg}'"
        print(f"  [V] Tech '{msg}' -> {parsed_tech}")

    print(">>> All Time and Tech Parsing Tests Passed!")


def test_adaptive_dynamic_roadmap():
    print("\n--- TEST 3: Adaptive Dynamic Roadmap for N Months & Archetypes ---")
    consultant = IdeationConsultant(db_uri=None)

    mock_analysis = {"domain": "Hệ thống Phân tích Dữ liệu Giao dịch Tài chính"}
    mock_gap_report = {
        "actionable_gaps": [
            {"skill": "ClickHouse", "proof_deliverable": "Script DDL bảng dạng cột và benchmark ghi 100k records/s"},
            {"skill": "dbt", "proof_deliverable": "Mô hình hóa dữ liệu Star Schema với dbt models"},
            {"skill": "Docker", "proof_deliverable": "docker-compose.yml kết nối đầy đủ pipeline"},
        ]
    }

    durations = [1, 2, 3, 4, 5, 6]
    for d in durations:
        roadmap = consultant._build_dynamic_roadmap(
            analysis=mock_analysis,
            time_months=d,
            target_role="Data Engineer",
            gap_report=mock_gap_report
        )
        expected_len = 2 if d <= 2 else d
        assert len(roadmap) == expected_len, f"Duration {d} months expected {expected_len} phases, got {len(roadmap)}"
        print(f"  [V] Duration {d} months -> Generated {len(roadmap)} phases:")
        for phase in roadmap:
            print(f"      - {phase['phase']} ({len(phase['milestones'])} milestones)")
            assert len(phase["milestones"]) >= 2, "Phase must have at least 2 milestones"

    # Test AI/ML Archetype
    roadmap_ai = consultant._build_dynamic_roadmap(
        analysis={"domain": "Trí tuệ nhân tạo Y tế"},
        time_months=3,
        target_role="AI / Machine Learning Engineer",
        gap_report=mock_gap_report
    )
    assert len(roadmap_ai) == 3
    ai_text = json.dumps(roadmap_ai, ensure_ascii=False)
    assert "Huấn Luyện Baseline" in ai_text or "Baseline" in ai_text
    print("  [V] AI/ML Archetype generated domain-specific milestones correctly.")

    print(">>> All Adaptive Roadmap Tests Passed!")


def test_stateful_multiturn_flow():
    print("\n--- TEST 4: Full Multi-Turn Stateful Flow in chat() ---")
    consultant = IdeationConsultant(db_uri=None)

    # Turn 1: Initial Idea
    turn1 = consultant.chat(
        session_id=None,
        user_message="Xây dựng nền tảng thương mại điện tử bán hàng trực tuyến với giỏ hàng và thanh toán"
    )
    session_id = turn1["session_id"]
    state1 = turn1["session_state"]
    print(f"  [Turn 1] Initial Role: {state1['target_role']} | Time: {state1['time_months']}m")
    assert state1["target_role"] in ["Backend Developer", "Fullstack Developer", "Full-stack Developer"]
    assert state1["time_months"] == 3
    assert len(turn1["blueprint"]["roadmap"]) == 3

    # Turn 2: Role Switch to Data Engineer
    turn2 = consultant.chat(
        session_id=session_id,
        user_message="Thay vì Backend, tôi muốn chuyển sang làm Data Engineer để phân tích dữ liệu mua sắm lớn"
    )
    state2 = turn2["session_state"]
    print(f"  [Turn 2] After Switch: Role: {state2['target_role']} | Switched: {state2['role_switched']} (from {state2['previous_role']})")
    assert state2["target_role"] == "Data Engineer"
    assert state2["role_switched"] == True
    assert state2["previous_role"] in ["Backend Developer", "Fullstack Developer", "Full-stack Developer"]
    # Check that blueprint updated to Data Engineer
    bp2 = turn2["blueprint"]
    assert bp2["target_role"] == "Data Engineer"
    print(f"  [Turn 2] Reply preview: {turn2['reply'][:120]}...")

    # Turn 3: Time duration change to 1 month
    turn3 = consultant.chat(
        session_id=session_id,
        user_message="Nếu tôi chỉ có 1 tháng cấp tốc thì lộ trình thế nào?"
    )
    state3 = turn3["session_state"]
    print(f"  [Turn 3] After Time Change: Time: {state3['time_months']}m | Role: {state3['target_role']}")
    assert state3["time_months"] == 1
    assert state3["target_role"] == "Data Engineer"
    assert len(turn3["blueprint"]["roadmap"]) == 2  # 1 month compressed into 2 sprints
    print(f"  [Turn 3] Compressed Roadmap: {turn3['blueprint']['roadmap'][0]['phase']} & {turn3['blueprint']['roadmap'][1]['phase']}")

    print(">>> All Multi-Turn Stateful Flow Tests Passed!")


if __name__ == "__main__":
    test_role_switch_detection()
    test_time_and_tech_parsing()
    test_adaptive_dynamic_roadmap()
    test_stateful_multiturn_flow()
    print("\n=======================================================")
    print("PHASE 2 VALIDATION COMPLETED 100% SUCCESSFULLY!")
    print("=======================================================")

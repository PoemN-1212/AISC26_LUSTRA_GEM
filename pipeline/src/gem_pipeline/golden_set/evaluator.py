"""
GEM Golden Set Evaluator (Bộ đánh giá hiệu năng trích xuất kỹ năng)
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

Thực hiện đo lường khoa học:
- Precision, Recall, F1-score (cả 2 chế độ: Strict Match và Relaxed Match)
- Phân tích riêng theo nhãn: TECHNOLOGY vs ABILITY
- Tỷ lệ ảo giác (Hallucination Rate)
- Tỷ lệ vi phạm từ cấm/chức danh (Negative Rule Violation Rate)
- So sánh định lượng: Baseline LLM vs. GEM Pipeline (LLM + Verifier)
"""

from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
import pandas as pd


@dataclass
class EvaluationMetrics:
    tp: int = 0
    fp: int = 0
    fn: int = 0
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0

    def compute(self):
        self.precision = self.tp / (self.tp + self.fp) if (self.tp + self.fp) > 0 else 0.0
        self.recall = self.tp / (self.tp + self.fn) if (self.tp + self.fn) > 0 else 0.0
        self.f1 = (2 * self.precision * self.recall) / (self.precision + self.recall) if (self.precision + self.recall) > 0 else 0.0


@dataclass
class ExperimentReport:
    name: str
    total_predictions: int
    total_ground_truth: int
    strict_metrics_overall: EvaluationMetrics
    relaxed_metrics_overall: EvaluationMetrics
    strict_metrics_technology: EvaluationMetrics
    strict_metrics_ability: EvaluationMetrics
    hallucination_count: int
    hallucination_rate: float
    negative_rule_violations: int
    violation_rate: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Tên thực nghiệm": self.name,
            "Tổng số dự đoán": self.total_predictions,
            "Tổng số Ground Truth": self.total_ground_truth,
            "Strict Precision": round(self.strict_metrics_overall.precision * 100, 2),
            "Strict Recall": round(self.strict_metrics_overall.recall * 100, 2),
            "Strict F1-Score": round(self.strict_metrics_overall.f1 * 100, 2),
            "Relaxed F1-Score": round(self.relaxed_metrics_overall.f1 * 100, 2),
            "F1 TECHNOLOGY": round(self.strict_metrics_technology.f1 * 100, 2),
            "F1 ABILITY": round(self.strict_metrics_ability.f1 * 100, 2),
            "Số lỗi ảo giác (Hallucinations)": self.hallucination_count,
            "Tỷ lệ ảo giác (%)": round(self.hallucination_rate, 2),
            "Số lỗi vi phạm chức danh/phúc lợi": self.negative_rule_violations,
            "Tỷ lệ vi phạm (%)": round(self.violation_rate, 2)
        }


class ExtractionEvaluator:
    """
    Module tính toán các chỉ số đánh giá chất lượng trích xuất dựa trên tập Golden Set.
    """

    @staticmethod
    def _is_relaxed_match(pred_skill: str, gt_skill: str) -> bool:
        """Kiểm tra khớp nới lỏng (Relaxed match) qua bao hàm xâu con."""
        p = pred_skill.lower().strip()
        g = gt_skill.lower().strip()
        return p == g or p in g or g in p

    def evaluate_predictions(
        self,
        experiment_name: str,
        predictions_by_doc: Dict[str, List[Dict[str, Any]]],
        ground_truth_by_doc: Dict[str, List[Dict[str, Any]]],
        hallucination_counts_by_doc: Dict[str, int] = None,
        violation_counts_by_doc: Dict[str, int] = None
    ) -> ExperimentReport:
        """
        Đánh giá toàn diện tập dự đoán so với tập chuẩn Ground Truth.
        """
        all_docs = set(predictions_by_doc.keys()).union(set(ground_truth_by_doc.keys()))

        total_preds = 0
        total_gt = 0

        # Metrics tổng thể
        strict_overall = EvaluationMetrics()
        relaxed_overall = EvaluationMetrics()

        # Metrics theo từng nhóm nhãn
        strict_tech = EvaluationMetrics()
        strict_ability = EvaluationMetrics()

        for doc_id in all_docs:
            preds = predictions_by_doc.get(doc_id, [])
            gts = ground_truth_by_doc.get(doc_id, [])

            total_preds += len(preds)
            total_gt += len(gts)

            # 1. Đánh giá STRICT MATCH
            pred_set = {(p.get("skill", "").strip().lower(), p.get("type", "TECHNOLOGY").upper()) for p in preds}
            gt_set = {(g.get("skill", "").strip().lower(), g.get("type", "TECHNOLOGY").upper()) for g in gts}

            tp_strict = len(pred_set.intersection(gt_set))
            fp_strict = len(pred_set - gt_set)
            fn_strict = len(gt_set - pred_set)

            strict_overall.tp += tp_strict
            strict_overall.fp += fp_strict
            strict_overall.fn += fn_strict

            # Phân tách theo nhãn TECHNOLOGY & ABILITY
            for p_skill, p_type in pred_set:
                matched = (p_skill, p_type) in gt_set
                if p_type == "TECHNOLOGY":
                    if matched:
                        strict_tech.tp += 1
                    else:
                        strict_tech.fp += 1
                elif p_type == "ABILITY":
                    if matched:
                        strict_ability.tp += 1
                    else:
                        strict_ability.fp += 1

            for g_skill, g_type in gt_set:
                if (g_skill, g_type) not in pred_set:
                    if g_type == "TECHNOLOGY":
                        strict_tech.fn += 1
                    elif g_type == "ABILITY":
                        strict_ability.fn += 1

            # 2. Đánh giá RELAXED MATCH
            matched_gt_indices = set()
            for p in preds:
                p_skill = p.get("skill", "")
                p_type = p.get("type", "TECHNOLOGY").upper()
                found = False
                for g_idx, g in enumerate(gts):
                    if g_idx in matched_gt_indices:
                        continue
                    if p_type == g.get("type", "").upper() and self._is_relaxed_match(p_skill, g.get("skill", "")):
                        matched_gt_indices.add(g_idx)
                        relaxed_overall.tp += 1
                        found = True
                        break
                if not found:
                    relaxed_overall.fp += 1

            relaxed_overall.fn += (len(gts) - len(matched_gt_indices))

        strict_overall.compute()
        relaxed_overall.compute()
        strict_tech.compute()
        strict_ability.compute()

        # Thống kê Hallucination & Negative Rules
        total_hallucinations = sum(hallucination_counts_by_doc.values()) if hallucination_counts_by_doc else 0
        hallucination_rate = (total_hallucinations / total_preds * 100) if total_preds > 0 else 0.0

        total_violations = sum(violation_counts_by_doc.values()) if violation_counts_by_doc else 0
        violation_rate = (total_violations / total_preds * 100) if total_preds > 0 else 0.0

        return ExperimentReport(
            name=experiment_name,
            total_predictions=total_preds,
            total_ground_truth=total_gt,
            strict_metrics_overall=strict_overall,
            relaxed_metrics_overall=relaxed_overall,
            strict_metrics_technology=strict_tech,
            strict_metrics_ability=strict_ability,
            hallucination_count=total_hallucinations,
            hallucination_rate=hallucination_rate,
            negative_rule_violations=total_violations,
            violation_rate=violation_rate
        )

    @staticmethod
    def compare_experiments(reports: List[ExperimentReport]) -> pd.DataFrame:
        """Tạo bảng đối sánh hiệu năng trực quan giữa các cấu hình."""
        rows = [r.to_dict() for r in reports]
        df = pd.DataFrame(rows)
        return df

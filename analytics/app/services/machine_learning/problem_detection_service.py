from __future__ import annotations

import pandas as pd

from app.models.ml_problem_type import MLProblemType


class ProblemDetectionService:
    """Determines the supervised ML problem type from the target series."""

    def detect(self, target: pd.Series) -> MLProblemType:
        if not pd.api.types.is_numeric_dtype(target):
            return MLProblemType.CLASSIFICATION

        if target.nunique() == 2:
            return MLProblemType.CLASSIFICATION

        return MLProblemType.REGRESSION

    def class_distribution(self, target: pd.Series) -> dict:
        class_counts = target.value_counts()
        total = len(target)
        distribution = {
            str(label): round(float(count / total), 4)
            for label, count in class_counts.items()
        }
        minority_ratio = float(class_counts.min() / total)
        return {
            "distribution": distribution,
            "imbalanceDetected": minority_ratio < 0.20,
        }

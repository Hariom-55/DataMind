from __future__ import annotations

import pandas as pd
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_score

from app.models.ml_problem_type import MLProblemType


class CrossValidationService:
    """Owns cross-validation strategy construction and scoring."""

    def build(self, y: pd.Series, problem_type: MLProblemType):
        if problem_type == MLProblemType.CLASSIFICATION:
            class_counts = y.value_counts()
            if class_counts.empty:
                return None
            min_class_count = int(class_counts.min())
            if min_class_count < 2:
                return None
            return StratifiedKFold(
                n_splits=min(5, min_class_count),
                shuffle=True,
                random_state=42,
            )

        if problem_type == MLProblemType.REGRESSION:
            if len(y) < 2:
                return None
            return KFold(
                n_splits=min(5, len(y)),
                shuffle=True,
                random_state=42,
            )

        raise ValueError(f"Unsupported problem Type: {problem_type}")

    def score(self, pipeline, X, y, problem_type: MLProblemType) -> dict | None:
        cv = self.build(y, problem_type)
        if cv is None:
            return None

        if problem_type == MLProblemType.CLASSIFICATION:
            scores = cross_val_score(pipeline, X, y, cv=cv, scoring="accuracy")
        else:
            scores = -cross_val_score(
                pipeline,
                X,
                y,
                cv=cv,
                scoring="neg_mean_absolute_error",
            )

        return {
            "meanScore": round(float(scores.mean()), 4),
            "standardDeviation": round(float(scores.std()), 4),
        }

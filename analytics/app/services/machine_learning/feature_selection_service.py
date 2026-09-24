from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.feature_selection import f_classif, f_regression, mutual_info_classif, mutual_info_regression

from app.models.ml_problem_type import MLProblemType


class FeatureSelectionService:
    """Performs deterministic, training-only feature selection and records its decision."""

    DEFAULT_CONFIGURATION = {
        "identifier": True,
        "constant": True,
        "redundancy": False,
        "correlationThreshold": 0.95,
    }

    def select(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        problem_type: MLProblemType,
        configuration: dict | None = None,
    ) -> tuple[pd.DataFrame, dict]:
        config = {**self.DEFAULT_CONFIGURATION, **(configuration or {})}
        selected = list(X.columns)
        removed: list[dict] = []

        def remove(column: str, reason: str):
            if column in selected:
                selected.remove(column)
                removed.append({"feature": column, "reason": reason})

        if config.get("identifier", True):
            for column in list(selected):
                series = X[column]
                unique_ratio = series.nunique(dropna=False) / max(len(series), 1)
                normalized = str(column).strip().lower().replace("_", "")
                is_identifier = unique_ratio >= 0.95 and (
                    normalized == "id"
                    or normalized.endswith("id")
                    or "identifier" in normalized
                )
                # Never remove the final usable feature: a dataset containing
                # only an identifier still needs a deterministic training path.
                if is_identifier and len(selected) > 1:
                    remove(column, "IDENTIFIER")

        if config.get("constant", True):
            for column in list(selected):
                if X[column].nunique(dropna=False) <= 1:
                    remove(column, "CONSTANT")

        threshold = float(config.get("correlationThreshold", 0.95))
        if config.get("redundancy", True) and len(selected) > 1:
            numeric = X[selected].select_dtypes(include=["number"])
            if numeric.shape[1] > 1:
                corr = numeric.corr().abs()
                upper = corr.where(
                    np.triu(np.ones(corr.shape), k=1).astype(bool)
                )
                columns = list(numeric.columns)
                for left_index in range(len(columns)):
                    left = columns[left_index]
                    for right_index in range(left_index + 1, len(columns)):
                        right = columns[right_index]
                        value = corr.loc[left, right]
                        if pd.notna(value) and value > threshold and right in selected:
                            remove(right, f"REDUNDANT_CORRELATION>{threshold}")

        if not selected:
            raise ValueError("Feature selection removed all feature columns")

        metadata = {
            "method": "DETERMINISTIC_FILTERS",
            "configuration": config,
            "selectedFeatures": selected,
            "removedFeatures": removed,
            "originalFeatureCount": int(X.shape[1]),
            "selectedFeatureCount": int(len(selected)),
        }

        return X[selected].copy(), metadata

    def rank_supervised_features(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        problem_type: MLProblemType,
        method: str,
        top_k: int,
    ) -> dict:
        """Optional ranking API for future/configured statistical or MI selection."""
        numeric = X.select_dtypes(include=["number"])
        if numeric.empty:
            return {"method": method, "selectedFeatures": list(X.columns), "scores": {}}

        if method == "STATISTICAL":
            scores, _ = (
                f_classif(numeric, y) if problem_type == MLProblemType.CLASSIFICATION
                else f_regression(numeric, y)
            )
        elif method == "MUTUAL_INFORMATION":
            scores = (
                mutual_info_classif(numeric, y, random_state=42)
                if problem_type == MLProblemType.CLASSIFICATION
                else mutual_info_regression(numeric, y, random_state=42)
            )
        else:
            raise ValueError(f"Unsupported feature selection method: {method}")

        ranked = sorted(
            zip(numeric.columns, scores),
            key=lambda item: float(item[1]) if pd.notna(item[1]) else 0.0,
            reverse=True,
        )
        selected = [name for name, _ in ranked[: max(1, min(top_k, len(ranked)))]]
        return {
            "method": method,
            "selectedFeatures": selected,
            "scores": {
                str(name): round(float(score), 6) if pd.notna(score) else 0.0
                for name, score in ranked
            },
        }

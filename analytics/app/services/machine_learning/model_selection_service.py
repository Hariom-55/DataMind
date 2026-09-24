from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import Pipeline

from app.models.ml_problem_type import MLProblemType
from app.services.machine_learning.cross_validation_service import CrossValidationService


class ModelSelectionService:
    """Owns candidate-model construction, comparison, and selection."""

    def __init__(self, cross_validation_service: CrossValidationService | None = None):
        self.cross_validation_service = cross_validation_service or CrossValidationService()

    def candidates(self, problem_type: MLProblemType) -> dict:
        if problem_type == MLProblemType.CLASSIFICATION:
            return {
                "LogisticRegression": LogisticRegression(max_iter=1000),
                "RandomForestClassifier": RandomForestClassifier(
                    n_estimators=100,
                    random_state=42,
                ),
            }

        if problem_type == MLProblemType.REGRESSION:
            return {
                "LinearRegression": LinearRegression(),
                "RandomForestRegressor": RandomForestRegressor(
                    n_estimators=100,
                    random_state=42,
                ),
            }

        raise ValueError(f"Unsupported problem Type: {problem_type}")

    def compare(self, X, y, preprocessor, problem_type: MLProblemType) -> dict:
        results = {}
        for model_name, model in self.candidates(problem_type).items():
            pipeline = Pipeline([
                ("preprocessor", preprocessor),
                ("model", model),
            ])
            score = self.cross_validation_service.score(
                pipeline, X, y, problem_type
            )
            if score is not None:
                results[model_name] = score
        return results

    def select_best(self, comparison_results: dict, problem_type: MLProblemType) -> str:
        if not comparison_results:
            raise ValueError("No model comparison results availabe")

        if problem_type == MLProblemType.CLASSIFICATION:
            return max(
                comparison_results,
                key=lambda model: comparison_results[model]["meanScore"],
            )

        return min(
            comparison_results,
            key=lambda model: comparison_results[model]["meanScore"],
        )

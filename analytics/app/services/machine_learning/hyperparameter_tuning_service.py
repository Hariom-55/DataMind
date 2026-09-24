from __future__ import annotations

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

from app.models.ml_problem_type import MLProblemType
from app.services.machine_learning.cross_validation_service import CrossValidationService


class HyperparameterTuningService:
    """Owns optional, explicitly requested Random Forest tuning."""

    PARAM_GRID = {
        "model__n_estimators": [50, 100],
        "model__max_depth": [None, 10],
        "model__min_samples_split": [2, 5],
    }

    def __init__(self, cross_validation_service: CrossValidationService | None = None):
        self.cross_validation_service = cross_validation_service or CrossValidationService()

    def tune(self, X_train, y_train, preprocessor, problem_type: MLProblemType):
        if problem_type == MLProblemType.CLASSIFICATION:
            model = RandomForestClassifier(random_state=42)
            scoring = "accuracy"
            model_name = "RandomForestClassifier"
        elif problem_type == MLProblemType.REGRESSION:
            model = RandomForestRegressor(random_state=42)
            scoring = "neg_mean_absolute_error"
            model_name = "RandomForestRegressor"
        else:
            raise ValueError("Unsupported problem type for Random Forest Tuning")

        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("model", model),
        ])
        cv = self.cross_validation_service.build(y_train, problem_type)
        if cv is None:
            raise ValueError("Not enough data for hyperparameter tuning")

        grid_search = GridSearchCV(
            estimator=pipeline,
            param_grid=self.PARAM_GRID,
            scoring=scoring,
            cv=cv,
            n_jobs=1,
            refit=True,
        )
        grid_search.fit(X_train, y_train)

        best_score = float(grid_search.best_score_)
        if problem_type == MLProblemType.REGRESSION:
            best_score = -best_score

        return {
            "model": model_name,
            "bestParameters": grid_search.best_params_,
            "bestScore": best_score,
            "bestEstimator": grid_search.best_estimator_,
        }

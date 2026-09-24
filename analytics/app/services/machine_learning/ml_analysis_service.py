from __future__ import annotations

import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    silhouette_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from app.core.analysis_service import AnalysisService
from app.loaders.dataset_loader import DatasetLoader
from app.models.ml_problem_type import MLProblemType
from app.services.machine_learning.cross_validation_service import CrossValidationService
from app.services.machine_learning.feature_selection_service import FeatureSelectionService
from app.services.machine_learning.hyperparameter_tuning_service import HyperparameterTuningService
from app.services.machine_learning.ml_artifact_store import MLArtifactStore
from app.services.machine_learning.model_evaluation_service import ModelEvaluationService
from app.services.machine_learning.model_selection_service import ModelSelectionService
from app.services.machine_learning.preprocessing_service import PreprocessingService
from app.services.machine_learning.problem_detection_service import ProblemDetectionService
from app.services.visualization.visualization_limits import MAX_VISUALIZATION_POINTS, evenly_spaced_sample


class MLAnalysisService(AnalysisService):
    """Application-level ML orchestration.

    Specialized concerns are delegated to dedicated services. The class keeps
    compatibility wrappers for the existing test and integration surface while
    remaining the single entry point for the analysis registry.
    """

    def __init__(
        self,
        dataset_loader: DatasetLoader,
        model_evaluation_service: ModelEvaluationService | None = None,
        artifact_store: MLArtifactStore | None = None,
    ):
        self.dataset_loader = dataset_loader
        self.problem_detection_service = ProblemDetectionService()
        self.cross_validation_service = CrossValidationService()
        self.preprocessing_service = PreprocessingService()
        self.model_selection_service = ModelSelectionService(self.cross_validation_service)
        self.tuning_service = HyperparameterTuningService(self.cross_validation_service)
        self.feature_selection_service = FeatureSelectionService()
        self.evaluation_service = model_evaluation_service or ModelEvaluationService()
        self.artifact_store = artifact_store or MLArtifactStore()

    # ------------------------------------------------------------------
    # Delegation boundaries kept stable for existing callers/tests.
    # ------------------------------------------------------------------
    def _detect_problem_type(self, target: pd.Series) -> MLProblemType:
        return self.problem_detection_service.detect(target)

    def _analyze_class_distribution(self, target: pd.Series) -> dict:
        return self.problem_detection_service.class_distribution(target)

    def _build_cv(self, y, problem_type):
        return self.cross_validation_service.build(y, problem_type)

    def _cross_validate_model(self, pipeline: Pipeline, X, y, problem_type) -> dict | None:
        return self.cross_validation_service.score(pipeline, X, y, problem_type)

    def _build_preprocessor(self, X: pd.DataFrame):
        return self.preprocessing_service.build(X)

    def _get_candidate_models(self, problem_type: MLProblemType) -> dict:
        return self.model_selection_service.candidates(problem_type)

    def _compare_models(self, X, y, preprocessor, problem_type) -> dict:
        return self.model_selection_service.compare(X, y, preprocessor, problem_type)

    def _select_best_model(self, comparison_results: dict, problem_type: MLProblemType) -> str:
        return self.model_selection_service.select_best(comparison_results, problem_type)

    def _tune_random_forest(self, X_train, y_train, preprocessor, problem_type):
        return self.tuning_service.tune(X_train, y_train, preprocessor, problem_type)

    # ------------------------------------------------------------------
    # Feature-importance projection remains here because it depends on the
    # fitted pipeline representation rather than model-selection policy.
    # ------------------------------------------------------------------
    def _get_transformed_feature_names(self, pipeline: Pipeline) -> list[str]:
        return pipeline.named_steps["preprocessor"].get_feature_names_out().tolist()

    def _get_feature_importance(self, pipeline: Pipeline) -> list[dict]:
        model = pipeline.named_steps["model"]
        feature_names = self._get_transformed_feature_names(pipeline)
        original_feature_names = self._get_original_feature_names(pipeline)

        if hasattr(model, "coef_"):
            coefficients = model.coef_
            importance_values = (
                abs(coefficients)
                if coefficients.ndim == 1
                else abs(coefficients).mean(axis=0)
            )
        elif hasattr(model, "feature_importances_"):
            importance_values = model.feature_importances_
        else:
            return []

        transformed_importance = [
            {
                "feature": feature_name,
                "importance": round(float(value), 4),
            }
            for feature_name, value in zip(feature_names, importance_values)
        ]
        return self._aggregate_feature_importance(
            transformed_importance,
            original_feature_names,
        )

    def _aggregate_feature_importance(
        self,
        feature_importance: list[dict],
        original_feature_names: list[str],
    ) -> list[dict]:
        aggregated = {}
        for item, original_feature in zip(feature_importance, original_feature_names):
            importance = item["importance"]
            aggregated[original_feature] = aggregated.get(original_feature, 0.0) + importance ** 2

        result = [
            {
                "feature": feature,
                "importance": round(value ** 0.5, 4),
            }
            for feature, value in aggregated.items()
        ]
        result.sort(key=lambda item: item["importance"], reverse=True)
        return result

    def _get_original_feature_names(self, pipeline: Pipeline) -> list[str]:
        preprocessor = pipeline.named_steps["preprocessor"]
        feature_names = []

        for transformer_name, transformer, columns in preprocessor.transformers_:
            if transformer == "drop":
                continue
            if transformer == "passthrough":
                feature_names.extend(columns)
                continue

            if transformer_name == "numeric":
                feature_names.extend(columns)
            elif transformer_name == "categorical":
                if len(columns) == 0:
                    continue
                encoder = transformer.named_steps["encoder"]
                for column, categories in zip(columns, encoder.categories_):
                    feature_names.extend([column] * len(categories))

        return feature_names

    # ------------------------------------------------------------------
    # Unsupervised workflow.
    # ------------------------------------------------------------------
    def _cluster_dataset(self, df: pd.DataFrame) -> dict:
        numeric = df.select_dtypes(include=["number"]).replace(
            [np.inf, -np.inf], np.nan
        )
        numeric = numeric.dropna(axis=1, how="all")
        if numeric.shape[1] == 0:
            raise ValueError("Clustering requires at least one numeric feature column")
        if len(numeric) < 2:
            raise ValueError("Clustering requires at least two dataset rows")

        imputed = SimpleImputer(strategy="median").fit_transform(numeric)
        scaled = StandardScaler().fit_transform(imputed)
        distinct_rows = np.unique(scaled, axis=0).shape[0]
        cluster_count = min(3, distinct_rows)
        model = KMeans(n_clusters=cluster_count, random_state=42, n_init=10)
        labels = model.fit_predict(scaled)
        actual_clusters = np.unique(labels)

        metrics = {"inertia": round(float(model.inertia_), 6)}
        if 1 < len(actual_clusters) < len(scaled):
            metrics["silhouetteScore"] = round(float(silhouette_score(scaled, labels)), 4)

        component_count = min(2, scaled.shape[1], scaled.shape[0])
        pca = PCA(n_components=component_count, random_state=42)
        coordinates = pca.fit_transform(scaled)
        pca_rows = []
        for row_index, point in enumerate(coordinates):
            row = {
                "row": int(row_index),
                "cluster": int(labels[row_index]),
                "PC1": round(float(point[0]), 6),
            }
            if component_count > 1:
                row["PC2"] = round(float(point[1]), 6)
            pca_rows.append(row)

        total_pca_points = len(pca_rows)
        pca_rows = evenly_spaced_sample(pca_rows, MAX_VISUALIZATION_POINTS)
        return {
            "targetColumn": None,
            "rowCount": int(len(df)),
            "columnCount": int(len(df.columns)),
            "featureCount": int(numeric.shape[1]),
            "featureColumns": list(numeric.columns),
            "excludedNonNumericColumns": [c for c in df.columns if c not in numeric.columns],
            "problemType": "CLUSTERING",
            "training": {
                "model": "KMeans",
                "metrics": metrics,
                "clusterCount": int(len(actual_clusters)),
                "clusterDistribution": {
                    str(int(label)): int(np.count_nonzero(labels == label))
                    for label in actual_clusters
                },
                "pca": {
                    "componentCount": int(component_count),
                    "explainedVarianceRatio": [
                        round(float(value), 6)
                        for value in np.nan_to_num(
                            pca.explained_variance_ratio_,
                            nan=0.0,
                            posinf=0.0,
                            neginf=0.0,
                        )
                    ],
                    "coordinates": pca_rows,
                    "totalPointCount": total_pca_points,
                    "coordinatesTruncated": total_pca_points > MAX_VISUALIZATION_POINTS,
                },
            },
        }

    # ------------------------------------------------------------------
    # Supervised training orchestration.
    # ------------------------------------------------------------------
    def _train_model(
        self,
        df: pd.DataFrame,
        target_column: str,
        problem_type: MLProblemType,
        enable_hyperparameter_tuning: bool = False,
        job_id=None,
        feature_selection_configuration: dict | None = None,
    ) -> dict:
        data = df.dropna(subset=[target_column])
        X = data.drop(columns=[target_column])
        y = data[target_column]

        if X.empty:
            raise ValueError("Dataset must have at least one feature column")
        if len(data) < 4:
            raise ValueError("Dataset must have at least 4 rows for training")
        if problem_type == MLProblemType.CLASSIFICATION and y.nunique() < 2:
            raise ValueError("classification target must cpnatin atleast two classes")

        test_size = max(0.2, 2 / len(X))
        if problem_type == MLProblemType.CLASSIFICATION:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

        selected_X_train, feature_selection = self.feature_selection_service.select(
            X_train,
            y_train,
            problem_type,
            feature_selection_configuration,
        )
        X_test = X_test[selected_X_train.columns].copy()

        preprocessor = self._build_preprocessor(selected_X_train)
        comparison_results = self._compare_models(
            selected_X_train,
            y_train,
            preprocessor,
            problem_type,
        )
        if not comparison_results:
            raise ValueError("Unable to compare models with available dataset")

        best_model_name = self._select_best_model(comparison_results, problem_type)
        candidate_models = self._get_candidate_models(problem_type)
        best_model = candidate_models[best_model_name]
        tuning_result = None

        if enable_hyperparameter_tuning and best_model_name in (
            "RandomForestClassifier",
            "RandomForestRegressor",
        ):
            tuning_result = self._tune_random_forest(
                selected_X_train,
                y_train,
                preprocessor,
                problem_type,
            )
            pipeline = tuning_result["bestEstimator"]
        else:
            pipeline = Pipeline([
                ("preprocessor", preprocessor),
                ("model", best_model),
            ])
            pipeline.fit(selected_X_train, y_train)

        predictions = pd.Series(pipeline.predict(X_test), index=y_test.index)
        y_score = None
        if problem_type == MLProblemType.CLASSIFICATION:
            if hasattr(pipeline, "predict_proba"):
                y_score = pipeline.predict_proba(X_test)
                if y_score.shape[1] == 2:
                    y_score = y_score[:, 1]
            elif hasattr(pipeline, "decision_function"):
                y_score = pipeline.decision_function(X_test)

        evaluation = self.evaluation_service.evaluate(
            y_test, predictions, problem_type.value, y_score
        )
        feature_importance = self._get_feature_importance(pipeline)
        tuning_response = None
        if tuning_result is not None:
            tuning_response = {
                "bestParameters": tuning_result["bestParameters"],
                "bestScore": round(float(tuning_result["bestScore"]), 4),
            }

        if problem_type == MLProblemType.CLASSIFICATION:
            metrics = {
                "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
                "precision": round(float(precision_score(y_test, predictions, average="weighted", zero_division=0)), 4),
                "recall": round(float(recall_score(y_test, predictions, average="weighted", zero_division=0)), 4),
                "f1_score": round(float(f1_score(y_test, predictions, average="weighted", zero_division=0)), 4),
            }
        else:
            mse = mean_squared_error(y_test, predictions)
            metrics = {
                "mean_squared_error": round(float(mse), 4),
                "mean_absolute_error": round(float(mean_absolute_error(y_test, predictions)), 4),
                "root_mean_squared_error": round(float(mse ** 0.5), 4),
                "r2Score": round(float(r2_score(y_test, predictions)), 4),
            }

        training_configuration = {
            "testSize": float(test_size),
            "enableHyperparameterTuning": bool(enable_hyperparameter_tuning),
            "targetColumn": target_column,
            "problemType": problem_type.value,
        }

        run_id = self.artifact_store.create_run(job_id)
        artifacts = self.artifact_store.save(
            run_id,
            pipeline,
            feature_selection,
            training_configuration,
            metrics,
        )

        return {
            "model": best_model_name,
            "modelComparison": comparison_results,
            "tuning": tuning_response,
            "metrics": metrics,
            "evaluation": evaluation,
            "featureImportance": feature_importance,
            "featureSelection": feature_selection,
            "artifacts": artifacts,
        }

    def analyze(
        self,
        dataset_path: str,
        file_type: str | None = None,
        target_column: str | None = None,
        enable_hyperparameter_tuning: bool = False,
        job_id=None,
        feature_selection_configuration: dict | None = None,
    ) -> dict:
        df = self.dataset_loader.load(dataset_path, file_type)
        if df.empty:
            raise ValueError("Dataset cannot be empty")

        if not target_column:
            return self._cluster_dataset(df)

        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in dataset.")

        target = df[target_column]
        if target.isnull().all():
            raise ValueError("Target column cannot be empty")
        target = target.dropna()
        if len(target) < 2:
            raise ValueError("Target column must have atleast two values")

        problem_type = self._detect_problem_type(target)
        class_distribution = None
        if problem_type == MLProblemType.CLASSIFICATION:
            class_distribution = self._analyze_class_distribution(target)

        training_results = self._train_model(
            df,
            target_column,
            problem_type,
            enable_hyperparameter_tuning,
            job_id,
            feature_selection_configuration,
        )
        return {
            "targetColumn": target_column,
            "rowCount": len(df),
            "columnCount": len(df.columns),
            "problemType": problem_type.value,
            "classDistribution": class_distribution,
            "training": training_results,
        }

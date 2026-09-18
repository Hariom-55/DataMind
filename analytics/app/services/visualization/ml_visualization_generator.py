from app.services.visualization.visualization_generator import VisualizationGenerator
from app.services.visualization.visualization_spec import VisualizationSpec
from app.services.visualization.visualization_types import VisualizationType


class MLVisualizationGenerator(VisualizationGenerator):

    def generate(self, analysis_results: dict) -> list[dict]:

        if not isinstance(analysis_results, dict):
            raise ValueError(
                "analysis_results must be a dictionary"
            )

        visualizations = []

        problem_type = analysis_results.get(
            "problemType"
        )

        if problem_type == "CLASSIFICATION":
            visualizations.extend(
                self._generate_class_distribution(
                    analysis_results
                )
            )

        training = analysis_results.get(
            "training",
            {}
        )

        if not isinstance(training, dict):
            return visualizations

        visualizations.extend(
            self._generate_model_comparison(
                training
            )
        )

        visualizations.extend(
            self._generate_metrics(
                training,
                problem_type
            )
        )

        visualizations.extend(
            self._generate_feature_importance(
                training
            )
        )

        return visualizations

    def _generate_class_distribution(
        self,
        analysis_results: dict
    ) -> list[dict]:

        class_distribution = analysis_results.get(
            "classDistribution"
        )

        if not isinstance(class_distribution, dict):
            return []

        distribution = class_distribution.get(
            "distribution",
            {}
        )

        if not distribution:
            return []

        data = [
            {
                "class": str(label),
                "proportion": float(proportion),
            }
            for label, proportion
            in distribution.items()
        ]

        spec = VisualizationSpec(
            type=VisualizationType.BAR,
            title="Class Distribution",
            description=(
                "Proportion of observations belonging "
                "to each target class."
            ),
            x="class",
            y="proportion",
            data=data,
            metadata={
                "source": "MACHINE_LEARNING",
                "metric": "classDistribution",
                "imbalanceDetected": class_distribution.get(
                    "imbalanceDetected",
                    False
                ),
            },
        )

        return [spec.to_dict()]

    def _generate_model_comparison(
        self,
        training: dict
    ) -> list[dict]:

        model_comparison = training.get(
            "modelComparison",
            {}
        )

        if not model_comparison:
            return []

        data = []

        for model, result in model_comparison.items():

            if not isinstance(result, dict):
                continue

            mean_score = result.get(
                "meanScore"
            )

            standard_deviation = result.get(
                "standardDeviation"
            )

            if mean_score is None:
                continue

            data.append(
                {
                    "model": model,
                    "meanScore": float(mean_score),
                    "standardDeviation": (
                        float(standard_deviation)
                        if standard_deviation is not None
                        else None
                    ),
                }
            )

        if not data:
            return []

        spec = VisualizationSpec(
            type=VisualizationType.BAR,
            title="Model Comparison",
            description=(
                "Cross-validation performance of "
                "candidate machine learning models."
            ),
            x="model",
            y="meanScore",
            data=data,
            metadata={
                "source": "MACHINE_LEARNING",
                "metric": "modelComparison",
            },
        )

        return [spec.to_dict()]

    def _generate_metrics(
        self,
        training: dict,
        problem_type: str | None
    ) -> list[dict]:

        metrics = training.get(
            "metrics",
            {}
        )

        if not metrics:
            return []

        if problem_type == "CLASSIFICATION":

            metric_names = (
                "accuracy",
                "precision",
                "recall",
                "f1_score",
            )

            title = "Classification Metrics"
            metric_key = "classificationMetrics"

        elif problem_type == "REGRESSION":

            metric_names = (
                "mean_squared_error",
                "mean_absolute_error",
                "root_mean_squared_error",
                "r2Score",
            )

            title = "Regression Metrics"
            metric_key = "regressionMetrics"

        else:
            return []

        data = [
            {
                "metric": metric,
                "value": float(metrics[metric]),
            }
            for metric in metric_names
            if metric in metrics
            and metrics[metric] is not None
        ]

        if not data:
            return []

        spec = VisualizationSpec(
            type=VisualizationType.BAR,
            title=title,
            description=(
                "Evaluation metrics for the selected "
                "machine learning model."
            ),
            x="metric",
            y="value",
            data=data,
            metadata={
                "source": "MACHINE_LEARNING",
                "metric": metric_key,
            },
        )

        return [spec.to_dict()]

    def _generate_feature_importance(
        self,
        training: dict
    ) -> list[dict]:

        feature_importance = training.get(
            "featureImportance",
            []
        )

        if not feature_importance:
            return []

        data = []

        for item in feature_importance:

            if not isinstance(item, dict):
                continue

            feature = item.get(
                "feature"
            )

            importance = item.get(
                "importance"
            )

            if feature is None or importance is None:
                continue

            data.append(
                {
                    "feature": str(feature),
                    "importance": float(importance),
                }
            )

        if not data:
            return []

        spec = VisualizationSpec(
            type=VisualizationType.BAR,
            title="Feature Importance",
            description=(
                "Relative importance of input features "
                "for the selected machine learning model."
            ),
            x="feature",
            y="importance",
            data=data,
            metadata={
                "source": "MACHINE_LEARNING",
                "metric": "featureImportance",
            },
        )

        return [spec.to_dict()]
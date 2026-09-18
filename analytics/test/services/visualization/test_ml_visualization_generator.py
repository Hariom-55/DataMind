from copy import deepcopy
from typing import Any

import pytest

from app.services.visualization.ml_visualization_generator import MLVisualizationGenerator
from app.services.visualization.visualization_types import VisualizationType


class TestMLVisualizationGenerator:

    def setup_method(self):
        self.generator = MLVisualizationGenerator()

    def test_should_generate_classification_visualizations(self):
        analysis_results = {
            "targetColumn": "churn",
            "problemType": "CLASSIFICATION",
            "classDistribution": {
                "distribution": {
                    "0": 0.75,
                    "1": 0.25,
                },
                "imbalanceDetected": False,
            },
            "training": {
                "model": "RandomForestClassifier",
                "modelComparison": {
                    "LogisticRegression": {
                        "meanScore": 0.82,
                        "standardDeviation": 0.03,
                    },
                    "RandomForestClassifier": {
                        "meanScore": 0.91,
                        "standardDeviation": 0.02,
                    },
                },
                "metrics": {
                    "accuracy": 0.91,
                    "precision": 0.90,
                    "recall": 0.89,
                    "f1_score": 0.895,
                },
                "featureImportance": [
                    {
                        "feature": "age",
                        "importance": 0.62,
                    },
                    {
                        "feature": "income",
                        "importance": 0.38,
                    },
                ],
            },
        }

        result = self.generator.generate(analysis_results)

        assert len(result) == 4

        types = [item["type"] for item in result]

        assert types == [
            VisualizationType.BAR.value,
            VisualizationType.BAR.value,
            VisualizationType.BAR.value,
            VisualizationType.BAR.value,
        ]

    def test_should_generate_class_distribution_visualization(self):
        analysis_results = {
            "problemType": "CLASSIFICATION",
            "classDistribution": {
                "distribution": {
                    "No": 0.70,
                    "Yes": 0.30,
                },
                "imbalanceDetected": False,
            },
            "training": {},
        }

        result = self.generator.generate(analysis_results)

        visualization = next(
            item
            for item in result
            if item["metadata"].get("metric") == "classDistribution"
        )

        assert visualization["type"] == VisualizationType.BAR.value
        assert visualization["title"] == "Class Distribution"
        assert visualization["x"] == "class"
        assert visualization["y"] == "proportion"

        assert visualization["data"] == [
            {"class": "No", "proportion": 0.70},
            {"class": "Yes", "proportion": 0.30},
        ]

    def test_should_generate_model_comparison_visualization(self):
        analysis_results = {
            "problemType": "CLASSIFICATION",
            "training": {
                "modelComparison": {
                    "LogisticRegression": {
                        "meanScore": 0.82,
                        "standardDeviation": 0.03,
                    },
                    "RandomForestClassifier": {
                        "meanScore": 0.91,
                        "standardDeviation": 0.02,
                    },
                }
            },
        }

        result = self.generator.generate(analysis_results)

        visualization = next(
            item
            for item in result
            if item["metadata"].get("metric") == "modelComparison"
        )

        assert visualization["type"] == VisualizationType.BAR.value
        assert visualization["title"] == "Model Comparison"
        assert visualization["x"] == "model"
        assert visualization["y"] == "meanScore"

        assert visualization["data"] == [
            {
                "model": "LogisticRegression",
                "meanScore": 0.82,
                "standardDeviation": 0.03,
            },
            {
                "model": "RandomForestClassifier",
                "meanScore": 0.91,
                "standardDeviation": 0.02,
            },
        ]

    def test_should_generate_classification_metrics_visualization(self):
        analysis_results = {
            "problemType": "CLASSIFICATION",
            "training": {
                "metrics": {
                    "accuracy": 0.91,
                    "precision": 0.90,
                    "recall": 0.89,
                    "f1_score": 0.895,
                }
            },
        }

        result = self.generator.generate(analysis_results)

        visualization = next(
            item
            for item in result
            if item["metadata"].get("metric") == "classificationMetrics"
        )

        assert visualization["type"] == VisualizationType.BAR.value
        assert visualization["title"] == "Classification Metrics"

        assert visualization["data"] == [
            {"metric": "accuracy", "value": 0.91},
            {"metric": "precision", "value": 0.90},
            {"metric": "recall", "value": 0.89},
            {"metric": "f1_score", "value": 0.895},
        ]

    def test_should_generate_regression_metrics_visualization(self):
        analysis_results = {
            "problemType": "REGRESSION",
            "training": {
                "metrics": {
                    "mean_squared_error": 12.5,
                    "mean_absolute_error": 2.8,
                    "root_mean_squared_error": 3.54,
                    "r2Score": 0.78,
                }
            },
        }

        result = self.generator.generate(analysis_results)

        visualization = next(
            item
            for item in result
            if item["metadata"].get("metric") == "regressionMetrics"
        )

        assert visualization["type"] == VisualizationType.BAR.value
        assert visualization["title"] == "Regression Metrics"

        assert visualization["data"] == [
            {"metric": "mean_squared_error", "value": 12.5},
            {"metric": "mean_absolute_error", "value": 2.8},
            {"metric": "root_mean_squared_error", "value": 3.54},
            {"metric": "r2Score", "value": 0.78},
        ]

    def test_should_generate_feature_importance_visualization(self):
        analysis_results = {
            "training": {
                "featureImportance": [
                    {
                        "feature": "age",
                        "importance": 0.62,
                    },
                    {
                        "feature": "income",
                        "importance": 0.38,
                    },
                ]
            }
        }

        result = self.generator.generate(analysis_results)

        visualization = next(
            item
            for item in result
            if item["metadata"].get("metric") == "featureImportance"
        )

        assert visualization["type"] == VisualizationType.BAR.value
        assert visualization["title"] == "Feature Importance"
        assert visualization["x"] == "feature"
        assert visualization["y"] == "importance"

        assert visualization["data"] == [
            {
                "feature": "age",
                "importance": 0.62,
            },
            {
                "feature": "income",
                "importance": 0.38,
            },
        ]

    def test_should_return_empty_for_missing_ml_results(self):
        result = self.generator.generate({})

        assert result == []

    def test_should_return_empty_for_empty_training_results(self):
        result = self.generator.generate(
            {
                "training": {}
            }
        )

        assert result == []

    def test_should_raise_error_for_invalid_input(self):
        invalid_input: Any = []

        with pytest.raises(
            ValueError,
            match="analysis_results must be a dictionary",
        ):
            self.generator.generate(invalid_input)

    def test_should_not_mutate_input(self):
        analysis_results = {
            "problemType": "CLASSIFICATION",
            "classDistribution": {
                "distribution": {
                    "0": 0.80,
                    "1": 0.20,
                },
                "imbalanceDetected": False,
            },
            "training": {
                "modelComparison": {
                    "LogisticRegression": {
                        "meanScore": 0.80,
                        "standardDeviation": 0.02,
                    }
                },
                "metrics": {
                    "accuracy": 0.80,
                    "precision": 0.79,
                    "recall": 0.78,
                    "f1_score": 0.785,
                },
                "featureImportance": [
                    {
                        "feature": "age",
                        "importance": 0.70,
                    }
                ],
            },
        }

        original = deepcopy(analysis_results)

        self.generator.generate(analysis_results)

        assert analysis_results == original
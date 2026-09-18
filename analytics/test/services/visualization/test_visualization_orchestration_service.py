from copy import deepcopy
from typing import Any
from unittest.mock import Mock

import pytest

from app.services.visualization.visualization_orchestration_service import (
    VisualizationOrchestrationService,
)


class TestVisualizationOrchestrationService:

    def setup_method(self):
        self.eda_generator = Mock()
        self.statistical_generator = Mock()
        self.ml_generator = Mock()
        self.distribution_generator = Mock()

        self.eda_generator.generate.return_value = []
        self.statistical_generator.generate.return_value = []
        self.distribution_generator.generate.return_value = []
        self.ml_generator.generate.return_value = []

        self.service = VisualizationOrchestrationService(
            eda_generator=self.eda_generator,
            statistical_generator=self.statistical_generator,
            distribution_generator =self.distribution_generator,
            ml_generator=self.ml_generator,
        )

    def test_should_generate_eda_visualizations(self):
        self.eda_generator.generate.return_value = [
            {
                "type": "BAR",
                "title": "Missing Values",
            }
        ]

        analysis_results = {
            "eda": {
                "missingValues": {
                    "age": 10,
                }
            }
        }

        result = self.service.generate(analysis_results)

        assert len(result["visualizations"]) == 1
        assert result["visualizations"][0]["title"] == "Missing Values"

        self.eda_generator.generate.assert_called_once_with(
            analysis_results["eda"]
        )

    def test_should_generate_statistical_visualizations(self):
        self.statistical_generator.generate.return_value = [
            {
                "type": "HEATMAP",
                "title": "Pearson Correlation Matrix",
            }
        ]

        analysis_results = {
            "statistical": {
                "correlations": {
                    "pearson": {
                        "age": {
                            "salary": 0.8,
                        }
                    }
                }
            }
        }

        result = self.service.generate(analysis_results)

        assert len(result["visualizations"]) == 1
        assert (
            result["visualizations"][0]["title"]
            == "Pearson Correlation Matrix"
        )

        self.statistical_generator.generate.assert_called_once_with(
            analysis_results["statistical"]
        )

    def test_should_generate_ml_visualizations(self):
        self.ml_generator.generate.return_value = [
            {
                "type": "BAR",
                "title": "Feature Importance",
            }
        ]

        analysis_results = {
            "machineLearning": {
                "problemType": "CLASSIFICATION",
                "training": {
                    "featureImportance": [
                        {
                            "feature": "age",
                            "importance": 0.8,
                        }
                    ]
                },
            }
        }

        result = self.service.generate(analysis_results)

        assert len(result["visualizations"]) == 1
        assert result["visualizations"][0]["title"] == "Feature Importance"

        self.ml_generator.generate.assert_called_once_with(
            analysis_results["machineLearning"]
        )

    def test_should_combine_all_visualizations(self):
        self.eda_generator.generate.return_value = [
            {
                "type": "BAR",
                "title": "Missing Values",
            }
        ]

        self.statistical_generator.generate.return_value = [
            {
                "type": "HEATMAP",
                "title": "Correlation Matrix",
            }
        ]

        self.distribution_generator.generate.return_value =[
            {
                "type": "TABLE",
                "title": "Distribution Analysis"
            }
        ]

        self.ml_generator.generate.return_value = [
            {
                "type": "BAR",
                "title": "Feature Importance",
            }
        ]

        analysis_results = {
            "eda": {"data": "eda"},
            "statistical": {"data": "statistics"},
            "machineLearning": {"data": "ml"},
        }

        result = self.service.generate(analysis_results)

        assert len(result["visualizations"]) == 4

        assert result["visualizations"][0]["title"] == "Missing Values"
        assert result["visualizations"][1]["title"] == "Correlation Matrix"
        assert result["visualizations"][2]["title"] == "Distribution Analysis"
        assert result["visualizations"][3]["title"] == "Feature Importance"

    def test_should_not_call_ml_generator_when_ml_results_are_missing(self):
        self.eda_generator.generate.return_value = []
        self.statistical_generator.generate.return_value = []

        analysis_results = {
            "eda": {},
            "statistical": {},
        }

        result = self.service.generate(analysis_results)

        assert result["visualizations"] == []

        self.ml_generator.generate.assert_not_called()

    def test_should_return_empty_visualizations_for_empty_input(self):
        self.eda_generator.generate.return_value = []
        self.statistical_generator.generate.return_value = []

        result = self.service.generate({})

        assert result == {
            "visualizations": []
        }

        self.eda_generator.generate.assert_not_called()
        self.statistical_generator.generate.assert_not_called()
        self.ml_generator.generate.assert_not_called()

    def test_should_raise_error_for_invalid_input(self):
        invalid_input: Any = []

        with pytest.raises(
            ValueError,
            match="analysis_results must be a dictionary",
        ):
            self.service.generate(invalid_input)

    def test_should_not_mutate_input(self):
        self.eda_generator.generate.return_value = [
            {
                "type": "BAR",
                "title": "Missing Values",
            }
        ]

        self.statistical_generator.generate.return_value = []

        analysis_results = {
            "eda": {
                "missingValues": {
                    "age": 10,
                }
            },
            "statistical": {
                "correlations": {}
            }
        }

        original = deepcopy(analysis_results)

        self.service.generate(analysis_results)

        assert analysis_results == original

    def test_should_propagate_eda_generator_failure(self):
        self.eda_generator.generate.side_effect = RuntimeError(
            "EDA visualization generation failed"
        )

        analysis_results = {
            "eda": {}
        }

        with pytest.raises(
            RuntimeError,
            match="EDA visualization generation failed",
        ):
            self.service.generate(analysis_results)

    def test_should_propagate_statistical_generator_failure(self):
        self.eda_generator.generate.return_value = []

        self.statistical_generator.generate.side_effect = RuntimeError(
            "Statistical visualization generation failed"
        )

        analysis_results = {
            "eda": {},
            "statistical": {},
        }

        with pytest.raises(
            RuntimeError,
            match="Statistical visualization generation failed",
        ):
            self.service.generate(analysis_results)

    def test_should_propagate_ml_generator_failure(self):
        self.eda_generator.generate.return_value = []
        self.statistical_generator.generate.return_value = []

        self.ml_generator.generate.side_effect = RuntimeError(
            "ML visualization generation failed"
        )

        analysis_results = {
            "eda": {},
            "statistical": {},
            "machineLearning": {},
        }

        with pytest.raises(
            RuntimeError,
            match="ML visualization generation failed",
        ):
            self.service.generate(analysis_results)

    def test_should_generate_distribution_visualizations(self):
        self.distribution_generator.generate.return_value = [
            {
                "type": "TABLE",
                "title": "Distribution Analysis",
            }
        ]

        analysis_results = {
            "statistical": {
                "distributions": {
                    "age": {
                        "sampleSize": 100,
                        "shape": "APPROXIMATELY_SYMMETRIC",
                    }
                }
            }
        }

        result = self.service.generate(analysis_results)

        assert len(result["visualizations"]) == 1
        assert (
            result["visualizations"][0]["title"]
            == "Distribution Analysis"
        )

        self.distribution_generator.generate.assert_called_once_with(
            analysis_results["statistical"]
        )
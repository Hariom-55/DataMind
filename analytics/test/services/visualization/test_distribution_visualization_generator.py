from copy import deepcopy

import pytest

from app.services.visualization.distribution_visualization_generator import DistributionVisualizationGenerator
from app.services.visualization.visualization_types import VisualizationType


class TestDistributionVisualizationGenerator:

    def setup_method(self):
        self.generator = DistributionVisualizationGenerator()

    def test_should_generate_distribution_table(self):
        analysis_results = {
            "distributions": {
                "age": {
                    "sampleSize": 100,
                    "isConstant": False,
                    "skewness": 0.21,
                    "kurtosis": 0.15,
                    "shape": "APPROXIMATELY_SYMMETRIC",
                    "tailBehavior": "NORMAL_LIKE_TAILS",
                    "normality": {
                        "available": True,
                        "test": "SHAPIRO_WILK",
                        "statistic": 0.98,
                        "pValue": 0.12,
                        "alpha": 0.05,
                        "significant": False,
                        "decision": "FAIL_TO_REJECT_NULL",
                    },
                }
            }
        }

        result = self.generator.generate(analysis_results)

        assert len(result) == 1

        visualization = result[0]

        assert visualization["type"] == VisualizationType.TABLE.value
        assert visualization["title"] == "Distribution Analysis"
        assert visualization["metadata"]["source"] == "STATISTICS"
        assert visualization["metadata"]["metric"] == "distribution"

    def test_should_include_distribution_statistics(self):
        analysis_results = {
            "distributions": {
                "salary": {
                    "sampleSize": 250,
                    "isConstant": False,
                    "skewness": 1.25,
                    "kurtosis": 2.10,
                    "shape": "RIGHT_SKEWED",
                    "tailBehavior": "HEAVY_TAILED",
                    "normality": {
                        "available": True,
                        "test": "SHAPIRO_WILK",
                        "statistic": 0.85,
                        "pValue": 0.001,
                        "alpha": 0.05,
                        "significant": True,
                        "decision": "REJECT_NULL",
                    },
                }
            }
        }

        result = self.generator.generate(analysis_results)

        data = result[0]["data"]

        assert len(data) == 1

        row = data[0]

        assert row["column"] == "salary"
        assert row["sampleSize"] == 250
        assert row["skewness"] == 1.25
        assert row["kurtosis"] == 2.10
        assert row["shape"] == "RIGHT_SKEWED"
        assert row["tailBehavior"] == "HEAVY_TAILED"

    def test_should_include_normality_results_when_available(self):
        analysis_results = {
            "distributions": {
                "height": {
                    "sampleSize": 100,
                    "isConstant": False,
                    "skewness": 0.1,
                    "kurtosis": 0.2,
                    "shape": "APPROXIMATELY_SYMMETRIC",
                    "tailBehavior": "NORMAL_LIKE_TAILS",
                    "normality": {
                        "available": True,
                        "test": "SHAPIRO_WILK",
                        "statistic": 0.99,
                        "pValue": 0.42,
                        "alpha": 0.05,
                        "significant": False,
                        "decision": "FAIL_TO_REJECT_NULL",
                    },
                }
            }
        }

        result = self.generator.generate(analysis_results)

        row = result[0]["data"][0]

        assert row["normalityAvailable"] is True
        assert row["normalityTest"] == "SHAPIRO_WILK"
        assert row["normalityStatistic"] == 0.99
        assert row["normalityPValue"] == 0.42
        assert row["normalityAlpha"] == 0.05
        assert row["normalitySignificant"] is False
        assert row["normalityDecision"] == "FAIL_TO_REJECT_NULL"

    def test_should_handle_unavailable_normality_results(self):
        analysis_results = {
            "distributions": {
                "constantColumn": {
                    "sampleSize": 50,
                    "isConstant": True,
                    "skewness": None,
                    "kurtosis": None,
                    "shape": "CONSTANT",
                    "tailBehavior": None,
                    "normality": {
                        "available": False,
                        "test": "SHAPIRO_WILK",
                        "reason": "CONSTANT_DATA",
                    },
                }
            }
        }

        result = self.generator.generate(analysis_results)

        row = result[0]["data"][0]

        assert row["column"] == "constantColumn"
        assert row["sampleSize"] == 50
        assert row["isConstant"] is True
        assert row["shape"] == "CONSTANT"
        assert row["normalityAvailable"] is False
        assert row["normalityTest"] == "SHAPIRO_WILK"
        assert row["normalityReason"] == "CONSTANT_DATA"

    def test_should_handle_missing_normality_information(self):
        analysis_results = {
            "distributions": {
                "age": {
                    "sampleSize": 10,
                    "isConstant": False,
                    "skewness": 0.2,
                    "kurtosis": 0.1,
                    "shape": "APPROXIMATELY_SYMMETRIC",
                    "tailBehavior": "NORMAL_LIKE_TAILS",
                }
            }
        }

        result = self.generator.generate(analysis_results)

        row = result[0]["data"][0]

        assert row["column"] == "age"
        assert row["normalityAvailable"] is False
        assert row["normalityTest"] is None
        assert row["normalityReason"] is None

    def test_should_handle_empty_distributions(self):
        analysis_results = {
            "distributions": {}
        }

        result = self.generator.generate(analysis_results)

        assert result == []

    def test_should_handle_missing_distributions_key(self):
        analysis_results = {}

        result = self.generator.generate(analysis_results)

        assert result == []

    def test_should_raise_error_for_invalid_input(self):
        invalid_input = []

        with pytest.raises(ValueError, match="analysis_results must be a dictionary"):
            self.generator.generate(invalid_input)

    def test_should_not_mutate_input(self):
        analysis_results = {
            "distributions": {
                "age": {
                    "sampleSize": 100,
                    "isConstant": False,
                    "skewness": 0.21,
                    "kurtosis": 0.15,
                    "shape": "APPROXIMATELY_SYMMETRIC",
                    "tailBehavior": "NORMAL_LIKE_TAILS",
                    "normality": {
                        "available": True,
                        "test": "SHAPIRO_WILK",
                        "statistic": 0.98,
                        "pValue": 0.12,
                        "alpha": 0.05,
                        "significant": False,
                        "decision": "FAIL_TO_REJECT_NULL",
                    },
                }
            }
        }

        original = deepcopy(analysis_results)

        self.generator.generate(analysis_results)

        assert analysis_results == original
import pytest
from typing import cast

from app.services.insight.insight_engine import (
    InsightEngine
)


class TestInsightEngine:

    def setup_method(self):

        self.engine = InsightEngine()

    def test_should_return_empty_result_for_empty_input(self):

        result = self.engine.generate({})

        assert result["summary"]["totalInsights"] == 0
        assert result["insights"] == []

    def test_should_reject_invalid_input(self):

        invalid_input = cast(dict, [])

        with pytest.raises(
            ValueError,
            match="analysis_results must be a dictionary"
        ):
            self.engine.generate(invalid_input)

    def test_should_generate_data_quality_insight(self):

        results = {
            "eda": {
                "missingPercentages": {
                    "income": 30.0
                }
            }
        }

        result = self.engine.generate(
            results
        )

        assert result["summary"]["totalInsights"] == 1

        insight = result["insights"][0]

        assert insight["category"] == "DATA_QUALITY"
        assert insight["severity"] == "HIGH"

    def test_should_generate_statistical_insight(self):

        results = {
            "statistical": {
                "distributions": {
                    "salary": {
                        "shape": "RIGHT_SKEWED",
                        "skewness": 2.0
                    }
                }
            }
        }

        result = self.engine.generate(
            results
        )

        assert result["summary"]["totalInsights"] == 1

        assert (
            result["insights"][0]["category"]
            == "STATISTICAL"
        )

    def test_should_generate_ml_insight(self):

        results = {
            "machineLearning": {
                "problemType": "CLASSIFICATION",
                "classDistribution": {
                    "distribution": {
                        "0": 0.90,
                        "1": 0.10
                    },
                    "imbalanceDetected": True
                }
            }
        }

        result = self.engine.generate(
            results
        )

        assert result["summary"]["totalInsights"] == 1

        assert (
            result["insights"][0]["category"]
            == "MACHINE_LEARNING"
        )

    def test_should_combine_multiple_generators(self):

        results = {
            "eda": {
                "missingPercentages": {
                    "income": 30.0
                }
            },

            "statistical": {
                "distributions": {
                    "salary": {
                        "shape": "RIGHT_SKEWED",
                        "skewness": 2.0
                    }
                }
            },

            "machineLearning": {
                "problemType": "CLASSIFICATION",
                "classDistribution": {
                    "distribution": {
                        "0": 0.90,
                        "1": 0.10
                    },
                    "imbalanceDetected": True
                }
            }
        }

        result = self.engine.generate(
            results
        )

        assert (
            result["summary"]["totalInsights"]
            == 3
        )

        categories = {
            insight["category"]
            for insight in result["insights"]
        }

        assert "DATA_QUALITY" in categories
        assert "STATISTICAL" in categories
        assert "MACHINE_LEARNING" in categories

    def test_should_assign_public_insight_ids(self):

        results = {
            "eda": {
                "missingPercentages": {
                    "income": 30.0
                }
            }
        }

        result = self.engine.generate(
            results
        )

        insight = result["insights"][0]

        assert "id" in insight

        assert insight["id"] == "INSIGHT-001"

        assert "key" not in insight

    def test_should_include_required_insight_fields(self):

        results = {
            "eda": {
                "missingPercentages": {
                    "income": 30.0
                }
            }
        }

        result = self.engine.generate(
            results
        )

        insight = result["insights"][0]

        required_fields = {
            "id",
            "category",
            "severity",
            "source",
            "title",
            "description",
            "evidence",
            "recommendation"
        }

        assert required_fields.issubset(
            insight.keys()
        )

    def test_should_sort_high_severity_before_info(self):

        results = {
            "eda": {
                "missingPercentages": {
                    "income": 30.0
                }
            },

            "statistical": {
                "distributions": {
                    "salary": {
                        "shape": "RIGHT_SKEWED",
                        "skewness": 2.0
                    }
                }
            }
        }

        result = self.engine.generate(
            results
        )

        assert (
            result["insights"][0]["severity"]
            == "HIGH"
        )

        assert (
            result["insights"][1]["severity"]
            == "INFO"
        )

    def test_should_generate_summary_counts(self):

        results = {
            "eda": {
                "missingPercentages": {
                    "income": 30.0,
                    "age": 10.0
                }
            },

            "statistical": {
                "distributions": {
                    "salary": {
                        "shape": "RIGHT_SKEWED",
                        "skewness": 2.0
                    }
                }
            }
        }

        result = self.engine.generate(
            results
        )

        summary = result["summary"]

        assert summary["totalInsights"] == 3
        assert summary["high"] == 1
        assert summary["medium"] == 1
        assert summary["info"] == 1

    def test_should_deduplicate_same_insight(self):

        class DuplicateGenerator:

            def generate(self, analysis_results):

                return [
                    {
                        "key": "duplicate",
                        "category": "TEST",
                        "severity": "INFO",
                        "source": "TEST",
                        "title": "Test",
                        "description": "Test",
                        "evidence": {},
                        "recommendation": "Test"
                    },

                    {
                        "key": "duplicate",
                        "category": "TEST",
                        "severity": "INFO",
                        "source": "TEST",
                        "title": "Test",
                        "description": "Test",
                        "evidence": {},
                        "recommendation": "Test"
                    }
                ]

        engine = InsightEngine(
            generators=[
                DuplicateGenerator()
            ]
        )

        result = engine.generate({})

        assert result["summary"]["totalInsights"] == 1
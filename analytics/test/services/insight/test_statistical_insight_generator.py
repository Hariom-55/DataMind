from app.services.insight.statistical_insight_generator import StatisticalInsightGenerator


class TestStatisticalInsightGenerator:

    def setup_method(self):

        self.generator = (
            StatisticalInsightGenerator()
        )

    def test_should_generate_right_skew_insight(self):

        results = {
            "statistical": {
                "distributions": {
                    "salary": {
                        "shape": "RIGHT_SKEWED",
                        "skewness": 1.8
                    }
                }
            }
        }

        insights = self.generator.generate(
            results
        )

        assert len(insights) == 1

        assert (
            insights[0]["category"]
            == "STATISTICAL"
        )

        assert insights[0]["source"] == "STATISTICS"

        assert (
            insights[0]["evidence"]["shape"]
            == "RIGHT_SKEWED"
        )

    def test_should_generate_heavy_tail_insight(self):

        results = {
            "statistical": {
                "distributions": {
                    "salary": {
                        "shape": "APPROXIMATELY_SYMMETRIC",
                        "tailBehavior": "HEAVY_TAILED",
                        "kurtosis": 1.5
                    }
                }
            }
        }

        insights = self.generator.generate(
            results
        )

        assert len(insights) == 1

        assert insights[0]["severity"] == "MEDIUM"

    def test_should_generate_non_normality_insight(self):

        results = {
            "statistical": {
                "distributions": {
                    "income": {
                        "normality": {
                            "available": True,
                            "test": "SHAPIRO_WILK",
                            "statistic": 0.70,
                            "pValue": 0.001,
                            "alpha": 0.05,
                            "significant": True,
                            "decision": "REJECT_NULL"
                        }
                    }
                }
            }
        }

        insights = self.generator.generate(
            results
        )

        assert len(insights) == 1

        assert (
            insights[0]["severity"]
            == "MEDIUM"
        )

        assert (
            insights[0]["evidence"]["decision"]
            == "REJECT_NULL"
        )

    def test_should_not_generate_non_normality_insight_when_not_rejected(
        self
    ):

        results = {
            "statistical": {
                "distributions": {
                    "income": {
                        "normality": {
                            "available": True,
                            "pValue": 0.40,
                            "alpha": 0.05,
                            "decision": "FAIL_TO_REJECT_NULL"
                        }
                    }
                }
            }
        }

        insights = self.generator.generate(
            results
        )

        assert insights == []

    def test_should_generate_strong_correlation_insight(self):

        results = {
            "statistical": {
                "correlationAnalysis": {
                    "pearson": {
                        "pairs": [],
                        "strongest": [
                            {
                                "column1": "age",
                                "column2": "salary",
                                "correlation": 0.82,
                                "strength": "VERY_STRONG",
                                "direction": "POSITIVE"
                            }
                        ]
                    }
                }
            }
        }

        insights = self.generator.generate(
            results
        )

        assert len(insights) == 1

        assert (
            insights[0]["evidence"]["correlation"]
            == 0.82
        )

    def test_should_ignore_weak_correlation(self):

        results = {
            "statistical": {
                "correlationAnalysis": {
                    "pearson": {
                        "pairs": [],
                        "strongest": [
                            {
                                "column1": "age",
                                "column2": "salary",
                                "correlation": 0.25
                            }
                        ]
                    }
                }
            }
        }

        insights = self.generator.generate(
            results
        )

        assert insights == []

    def test_should_generate_significant_hypothesis_insight(self):

        results = {
            "statistical": {
                "hypothesisTesting": [
                    {
                        "test": "ONE_SAMPLE_T_TEST",
                        "pValue": 0.01,
                        "alpha": 0.05,
                        "significant": True,
                        "decision": "REJECT_NULL"
                    }
                ]
            }
        }

        insights = self.generator.generate(
            results
        )

        assert len(insights) == 1

        assert (
            insights[0]["evidence"]["test"]
            == "ONE_SAMPLE_T_TEST"
        )

    def test_should_ignore_non_significant_hypothesis(self):

        results = {
            "statistical": {
                "hypothesisTesting": [
                    {
                        "test": "ONE_SAMPLE_T_TEST",
                        "pValue": 0.40,
                        "alpha": 0.05,
                        "significant": False,
                        "decision": "FAIL_TO_REJECT_NULL"
                    }
                ]
            }
        }

        insights = self.generator.generate(
            results
        )

        assert insights == []
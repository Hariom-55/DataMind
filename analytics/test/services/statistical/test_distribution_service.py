import pandas as pd
import pytest

from app.services.statistical.distribution_service import (
    DistributionAnalysisService
)


class TestDistributionAnalysisService:

    def setup_method(self):

        self.service = DistributionAnalysisService()

    def test_should_analyze_numeric_distribution(self):

        df = pd.DataFrame({
            "age": [
                20, 21, 22, 23, 24,
                25, 26, 27, 28, 29
            ]
        })

        result = self.service.analyze(df)

        assert "distributions" in result
        assert "age" in result["distributions"]

    def test_should_return_sample_size(self):

        df = pd.DataFrame({
            "age": [20, 21, 22, 23, 24]
        })

        result = self.service.analyze(df)

        distribution = result["distributions"]["age"]

        assert distribution["sampleSize"] == 5

    def test_should_ignore_non_numeric_columns(self):

        df = pd.DataFrame({
            "age": [20, 21, 22],
            "city": [
                "Pune",
                "Mumbai",
                "Nashik"
            ]
        })

        result = self.service.analyze(df)

        distributions = result["distributions"]

        assert "age" in distributions
        assert "city" not in distributions

    def test_should_handle_missing_values(self):

        df = pd.DataFrame({
            "age": [
                20,
                21,
                None,
                22,
                None,
                23
            ]
        })

        result = self.service.analyze(df)

        distribution = result["distributions"]["age"]

        assert distribution["sampleSize"] == 4

    def test_should_classify_symmetric_distribution(self):

        df = pd.DataFrame({
            "value": [
                1, 2, 3, 4, 5,
                6, 7, 8, 9
            ]
        })

        result = self.service.analyze(df)

        distribution = result["distributions"]["value"]

        assert distribution["shape"] == (
            "APPROXIMATELY_SYMMETRIC"
        )

    def test_should_classify_right_skewed_distribution(self):

        df = pd.DataFrame({
            "value": [
                1, 1, 1, 1, 2,
                2, 3, 5, 10, 30
            ]
        })

        result = self.service.analyze(df)

        distribution = result["distributions"]["value"]

        assert distribution["shape"] == "RIGHT_SKEWED"

    def test_should_classify_left_skewed_distribution(self):

        df = pd.DataFrame({
            "value": [
                1, 20, 30, 40, 40,
                40, 40, 40, 40, 40
            ]
        })

        result = self.service.analyze(df)

        distribution = result["distributions"]["value"]

        assert distribution["shape"] == "LEFT_SKEWED"

    def test_should_calculate_skewness(self):

        df = pd.DataFrame({
            "value": [
                10, 20, 30, 40, 50
            ]
        })

        result = self.service.analyze(df)

        distribution = result["distributions"]["value"]

        assert distribution["skewness"] == pytest.approx(0.0)

    def test_should_calculate_kurtosis(self):

        df = pd.DataFrame({
            "value": [
                10, 20, 30, 40, 50
            ]
        })

        result = self.service.analyze(df)

        distribution = result["distributions"]["value"]

        assert distribution["kurtosis"] == pytest.approx(
            -1.2
        )

    def test_should_detect_constant_column(self):

        df = pd.DataFrame({
            "value": [
                10,
                10,
                10,
                10,
                10
            ]
        })

        result = self.service.analyze(df)

        distribution = result["distributions"]["value"]

        assert distribution["isConstant"] is True

        assert distribution["shape"] == "CONSTANT"

        assert distribution["normality"]["available"] is False

        assert distribution["normality"]["reason"] == (
            "CONSTANT_DATA"
        )

    def test_should_handle_no_valid_numeric_observations(self):

        df = pd.DataFrame({
            "value": pd.Series(
                [float("nan"), float("nan"), float('nan')],
                dtype="float64"
            )
            
        })

        result = self.service.analyze(df)

        distribution = result["distributions"]["value"]

        assert distribution["sampleSize"] == 0

        assert distribution["normality"]["available"] is False

        assert distribution["normality"]["reason"] == (
            "NO_VALID_OBSERVATIONS"
        )

    def test_should_ignore_all_missing_non_numeric_column(self):

        df = pd.DataFrame({
            "value":[
                None,
                None,
                None
            ]
        })

        result = self.service.analyze(df)

        assert "value" not in result["distributions"]

        assert result["distributions"] == {}

    def test_should_handle_insufficient_observations(self):

        df = pd.DataFrame({
            "value": [
                10,
                20
            ]
        })

        result = self.service.analyze(df)

        distribution = result["distributions"]["value"]

        normality = distribution["normality"]

        assert normality["available"] is False

        assert normality["reason"] == (
            "INSUFFICIENT_OBSERVATIONS"
        )

    def test_should_run_shapiro_wilk_normality_test(self):

        df = pd.DataFrame({
            "value": [
                10, 11, 12, 13, 14,
                15, 16, 17, 18, 19,
                20, 21, 22, 23, 24
            ]
        })

        result = self.service.analyze(df)

        normality = (
            result["distributions"]["value"]["normality"]
        )

        assert normality["available"] is True

        assert normality["test"] == "SHAPIRO_WILK"

        assert "statistic" in normality
        assert "pValue" in normality
        assert "alpha" in normality
        assert "significant" in normality
        assert "decision" in normality

    def test_should_support_custom_alpha(self):

        df = pd.DataFrame({
            "value": [
                10, 11, 12, 13, 14,
                15, 16, 17, 18, 19
            ]
        })

        result = self.service.analyze(
            df,
            alpha=0.01
        )

        normality = (
            result["distributions"]["value"]["normality"]
        )

        assert normality["alpha"] == pytest.approx(
            0.01
        )

    def test_should_reject_invalid_alpha(self):

        df = pd.DataFrame({
            "value": [
                10, 20, 30
            ]
        })

        with pytest.raises(
            ValueError,
            match="alpha must be between 0 and 1"
        ):
            self.service.analyze(
                df,
                alpha=0
            )

    def test_should_handle_multiple_numeric_columns(self):

        df = pd.DataFrame({
            "age": [
                20, 21, 22, 23, 24,
                25, 26, 27, 28, 29
            ],
            "salary": [
                30000,
                32000,
                34000,
                36000,
                38000,
                40000,
                42000,
                44000,
                46000,
                48000
            ]
        })

        result = self.service.analyze(df)

        distributions = result["distributions"]

        assert "age" in distributions
        assert "salary" in distributions

    def test_should_classify_light_tailed_distribution(self):

        df = pd.DataFrame({
            "value": [
                1, 2, 3, 4, 5,
                6, 7, 8, 9
            ]
        })

        result = self.service.analyze(df)

        distribution = result["distributions"]["value"]

        assert distribution["tailBehavior"] in [
            "LIGHT_TAILED",
            "NORMAL_LIKE_TAILS",
            "HEAVY_TAILED"
        ]

    def test_should_return_normality_decision_consistently(self):

        df = pd.DataFrame({
            "value": [
                10, 11, 12, 13, 14,
                15, 16, 17, 18, 19,
                20, 21, 22, 23, 24
            ]
        })

        result = self.service.analyze(df)

        normality = (
            result["distributions"]["value"]["normality"]
        )

        if normality["pValue"] < normality["alpha"]:

            assert normality["decision"] == (
                "REJECT_NULL"
            )

            assert normality["significant"] is True

        else:

            assert normality["decision"] == (
                "FAIL_TO_REJECT_NULL"
            )

            assert normality["significant"] is False
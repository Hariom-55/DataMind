import pandas as pd
import pytest

from app.services.statistical_service import StatisticalAnalysisService


class TestStatisticalAnalysisService:

    def setup_method(self):
        self.service = StatisticalAnalysisService()

    def test_should_generate_descriptive_statistics(self, tmp_path):

        dataset = pd.DataFrame({
            "age": [20, 30, 40, 50, 60]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        statistics = result["descriptiveStatistics"]["age"]

        assert statistics["count"] == 5
        assert statistics["mean"] == pytest.approx(40.0)
        assert statistics["median"] == pytest.approx(40.0)
        assert statistics["min"] == pytest.approx(20.0)
        assert statistics["max"] == pytest.approx(60.0)

    def test_should_generate_quartile_statistics(self, tmp_path):

        dataset = pd.DataFrame({
            "age": [20, 30, 40, 50, 60]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        statistics = result["descriptiveStatistics"]["age"]

        assert statistics["25%"] == pytest.approx(30.0)
        assert statistics["50%"] == pytest.approx(40.0)
        assert statistics["75%"] == pytest.approx(50.0)

    def test_should_generate_variance_and_standard_deviation(
            self,
            tmp_path
    ):

        dataset = pd.DataFrame({
            "value": [10, 20, 30, 40, 50]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        statistics = result["descriptiveStatistics"]["value"]

        assert statistics["std"] == pytest.approx(
            15.811388300841896
        )

        assert statistics["variance"] == pytest.approx(250.0)

    def test_should_generate_skewness_and_kurtosis(
            self,
            tmp_path
    ):

        dataset = pd.DataFrame({
            "value": [10, 20, 30, 40, 50]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        statistics = result["descriptiveStatistics"]["value"]

        assert statistics["skewness"] == pytest.approx(0.0)
        assert statistics["kurtosis"] == pytest.approx(-1.2)

    def test_should_analyze_multiple_numeric_columns(self, tmp_path):

        dataset = pd.DataFrame({
            "age": [20, 30, 40, 50],
            "salary": [30000, 40000, 50000, 60000]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        statistics = result["descriptiveStatistics"]

        assert "age" in statistics
        assert "salary" in statistics

        assert statistics["age"]["mean"] == pytest.approx(35.0)
        assert statistics["salary"]["mean"] == pytest.approx(45000.0)

    def test_should_generate_pearson_correlation(
            self,
            tmp_path
    ):

        dataset = pd.DataFrame({
            "age": [20, 30, 40, 50, 60],
            "salary": [20000, 30000, 40000, 50000, 60000]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        pearson = result["correlations"]["pearson"]

        assert pearson["age"]["age"] == pytest.approx(1.0)
        assert pearson["salary"]["salary"] == pytest.approx(1.0)

        assert pearson["age"]["salary"] == pytest.approx(1.0)
        assert pearson["salary"]["age"] == pytest.approx(1.0)

    def test_should_generate_spearman_correlation(
            self,
            tmp_path
    ):

        dataset = pd.DataFrame({
            "age": [20, 30, 40, 50, 60],
            "salary": [20000, 30000, 40000, 50000, 60000]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        spearman = result["correlations"]["spearman"]

        assert spearman["age"]["age"] == pytest.approx(1.0)
        assert spearman["salary"]["salary"] == pytest.approx(1.0)

        assert spearman["age"]["salary"] == pytest.approx(1.0)
        assert spearman["salary"]["age"] == pytest.approx(1.0)

    def test_should_ignore_non_numeric_columns(
            self,
            tmp_path
    ):

        dataset = pd.DataFrame({
            "name": ["Hariom", "Rahul", "Aman"],
            "age": [22, 24, 21],
            "salary": [30000, 40000, 35000]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        statistics = result["descriptiveStatistics"]

        assert "age" in statistics
        assert "salary" in statistics
        assert "name" not in statistics

    def test_should_handle_missing_numeric_values(
            self,
            tmp_path
    ):

        dataset = pd.DataFrame({
            "age": [20, 30, None, 50, 60]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        statistics = result["descriptiveStatistics"]["age"]

        assert statistics["count"] == 4
        assert statistics["mean"] == pytest.approx(40.0)

    def test_should_return_empty_statistics_when_no_numeric_columns(
            self,
            tmp_path
    ):

        dataset = pd.DataFrame({
            "name": ["Hariom", "Rahul", "Aman"],
            "department": ["IT", "HR", "Finance"]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        assert result["descriptiveStatistics"] == {}
        assert result["correlations"]["pearson"] == {}
        assert result["correlations"]["spearman"] == {}

    def test_should_not_generate_correlations_for_single_numeric_column(
            self,
            tmp_path
    ):

        dataset = pd.DataFrame({
            "age": [20, 30, 40, 50, 60]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        assert "age" in result["descriptiveStatistics"]

        assert result["correlations"]["pearson"] == {}
        assert result["correlations"]["spearman"] == {}
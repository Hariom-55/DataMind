import pandas as pd
import pytest
from app.services.profiling.eda_service import EDAService
from app.loaders.dataset_loader import DatasetLoader
from app.services.profiling.data_quality_service import DataQualityService


class TestEDAService:

    def setup_method(self):
        dataset_loader = DatasetLoader()
        data_quality_service = DataQualityService()
        self.service = EDAService(
            dataset_loader,
            data_quality_service
        )

    def test_should_return_basic_dataset_overview(self, tmp_path):

        dataset = pd.DataFrame({
            "name": ["Hariom", "Rahul", "Aman"],
            "age": [22, 24, 21]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        assert result["overview"]["rowCount"] == 3
        assert result["overview"]["columnCount"] == 2
        assert result["columns"] == ["name", "age"]
        assert result["overview"]["numericColumnCount"] == 1
        assert result["overview"]["categoricalColumnCount"] == 1

    def test_should_return_correct_data_types(self, tmp_path):

        dataset = pd.DataFrame({
            "name": ["Hariom", "Rahul"],
            "age": [22, 24],
            "active": [True, False]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        assert result["dataTypes"]["name"] == "str"
        assert result["dataTypes"]["age"] == "int64"
        assert result["dataTypes"]["active"] == "bool"

    def test_should_calculate_missing_values(self, tmp_path):

        dataset = pd.DataFrame({
            "name": ["Hariom", None, "Aman", None],
            "age": [22, 24, None, 25]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        assert result["missingValues"]["name"] == 2
        assert result["missingValues"]["age"] == 1

    def test_should_calculate_missing_value_percentages(self, tmp_path):

        dataset = pd.DataFrame({
            "name": ["Hariom", None, "Aman", None],
            "age": [22, 24, None, 25]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        assert result["missingPercentages"]["name"] == pytest.approx(50.0)
        assert result["missingPercentages"]["age"] == pytest.approx(25.0)

    def test_should_calculate_unique_value_counts(self, tmp_path):

        dataset = pd.DataFrame({
            "department": [
                "IT",
                "HR",
                "IT",
                "Finance",
                None
            ],
            "age": [20, 21, 20, 22, 23]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        assert result["uniqueValueCounts"]["department"] == 3
        assert result["uniqueValueCounts"]["age"] == 4

    def test_should_count_duplicate_rows(self, tmp_path):

        dataset = pd.DataFrame({
            "name": ["Hariom", "Rahul", "Hariom"],
            "age": [22, 24, 22]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        assert result["duplicateRows"] == 1

    def test_should_generate_numeric_statistics(self, tmp_path):

        dataset = pd.DataFrame({
            "age": [20, 30, 40, 50, 60]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        statistics = result["numericStatistics"]["age"]

        assert statistics["count"] == pytest.approx(5.0)
        assert statistics["mean"] == pytest.approx(40.0)
        assert statistics["min"] == pytest.approx(20.0)
        assert statistics["max"] == pytest.approx(60.0)
        assert statistics["50%"] == pytest.approx(40.0)

    def test_should_flag_iqr_outliers_when_quartiles_are_equal(self, tmp_path):
        dataset = pd.DataFrame({"constant_with_spike": [5, 5, 5, 5, 100]})
        file_path = tmp_path / "zero_iqr_outlier.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        signal = result["outlierSignals"]["constant_with_spike"]
        assert signal["lowerBound"] == 5.0
        assert signal["upperBound"] == 5.0
        assert signal["outlierCount"] == 1

    def test_should_identify_singleton_rare_categories(self, tmp_path):
        dataset = pd.DataFrame({"category": ["common", "common", "other", "rare"]})
        file_path = tmp_path / "rare_categories.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        assert result["categoricalStatistics"]["category"]["rareValues"] == {
            "other": 1,
            "rare": 1,
        }

    def test_should_cap_histogram_bins_and_rare_value_previews(self, tmp_path):
        dataset = pd.DataFrame({
            "value": list(range(5000)),
            "category": [f"unique-{index}" for index in range(5000)],
        })
        file_path = tmp_path / "bounded_payload.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        bins = result["numericHistograms"]["value"]
        rare = result["categoricalStatistics"]["category"]
        assert len(bins) <= 100
        assert sum(item["count"] for item in bins) == 5000
        assert len(rare["rareValues"]) == 20
        assert rare["rareValueCount"] == 5000
        assert rare["rareValuesTruncated"] is True

    def test_should_report_constant_and_high_cardinality_columns(self, tmp_path):
        dataset = pd.DataFrame({
            "constant": ["same"] * 40,
            "identifier": [f"id-{index}" for index in range(40)],
            "value": list(range(40)),
        })
        file_path = tmp_path / "quality_signals.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        assert result["dataQuality"]["constantColumns"] == ["constant"]
        assert result["dataQuality"]["highCardinalityThreshold"] == 0.5
        assert result["dataQuality"]["highCardinalityColumns"] == [{
            "column": "identifier",
            "uniqueCount": 40,
            "cardinalityRatio": 1.0,
        }]

    def test_should_generate_categorical_statistics(self, tmp_path):

        dataset = pd.DataFrame({
            "department": [
                "IT",
                "IT",
                "IT",
                "HR",
                "HR",
                "Finance"
            ]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        statistics = result["categoricalStatistics"]["department"]

        assert statistics["uniqueCount"] == 3
        assert statistics["topValues"]["IT"] == 3
        assert statistics["topValues"]["HR"] == 2
        assert statistics["topValues"]["Finance"] == 1

    def test_should_handle_empty_dataset_with_headers(self, tmp_path):

        dataset = pd.DataFrame(
            columns=["name", "age"]
        )

        file_path = tmp_path / "empty.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        assert "dataQuality" in result
        assert result["dataQuality"]["score"] == 0.0

        assert result["overview"]["rowCount"] == 0
        assert result["overview"]["columnCount"] == 2
        assert result["columns"] == ["name", "age"]

        assert result["missingPercentages"]["name"] == 0.0
        assert result["missingPercentages"]["age"] == 0.0

        assert result["duplicateRows"] == 0

    def test_should_handle_mixed_dataset(self, tmp_path):

        dataset = pd.DataFrame({
            "id": [1, 2, 3, 4],
            "age": [21, 25, 30, 35],
            "salary": [30000.0, 45000.0, 55000.0, 70000.0],
            "department": ["IT", "HR", "IT", "Finance"],
            "active": [True, True, False, True]
        })

        file_path = tmp_path / "mixed.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        assert result["overview"]["rowCount"] == 4
        assert result["overview"]["columnCount"] == 5

        assert result["uniqueValueCounts"]["department"] == 3

        assert result["numericStatistics"]["age"]["mean"] == pytest.approx(27.75)

        assert result["categoricalStatistics"]["department"]["uniqueCount"] == 3

        assert result["duplicateRows"] == 0

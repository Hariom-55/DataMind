import pandas as pd

from app.services.data_quality_service import DataQualityService

class TestDataQualityService:

    def setup_method(self):
        self.service = DataQualityService()

    def test_should_calculate_quality_for_complete_dataset(self):

        df = pd.DataFrame({
            "name": ["Hariom", "Rahul", "Amit"],
            "age": [22, 23, 24],
        })

        result = self.service.analyze(df)

        assert result["score"] == 100.0
        assert result["completeness"] == 100.0
        assert result["missingCells"] == 0
        assert result["duplicateRows"] == 0
        assert result["duplicatePercentage"] == 0.0

    def test_should_detect_missing_values(self):

        df = pd.DataFrame({
            "name": ["Hariom", None, "Amit"],
            "age": [22, 23, None],
        })

        result = self.service.analyze(df)

        assert result["missingCells"] == 2
        assert result["completeness"] == 66.67

    def test_should_detect_duplicate_rows(self):

        df = pd.DataFrame({
            "name": ["Hariom", "Rahul", "Hariom"],
            "age": [22, 23, 22]
        })

        result = self.service.analyze(df)

        assert result["duplicateRows"] == 1
        assert result["duplicatePercentage"] == 33.33
        assert result["duplicateFreePercentage"] == 66.67

    def test_should_calculate_quality_with_missing_and_duplicates(self):

        df = pd.DataFrame({
            "name": ["Hariom", None, "Hariom"],
            "age": [22, 23, 22]
        })

        result = self.service.analyze(df)

        assert result["missingCells"] == 1
        assert result["duplicateRows"] == 1
        assert result["completeness"] == 83.33
        assert result["duplicatePercentage"] == 33.33

    def test_should_return_zero_quality_for_empty_dataset(self):

        df = pd.DataFrame(
            columns=["name", "age"]
        )

        result = self.service.analyze(df)

        assert result["score"] == 0.0
        assert result["completeness"] == 0.0
        assert result["missingCells"] == 0
        assert result["duplicateRows"] == 0
        assert result["duplicatePercentage"] == 0.0

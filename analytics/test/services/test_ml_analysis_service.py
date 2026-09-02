import pytest

from app.services.ml_analysis_service import MLAnalysisService
from app.loaders.dataset_loader import DatasetLoader


class TestMLAnalysisService:

    def setup_method(self):
        dataset_loader = DatasetLoader()
        self.service = MLAnalysisService(dataset_loader)  

    def test_should_require_target_column(self):

        with pytest.raises(
            ValueError,
            match="Target column is required"
        ):
            self.service.analyze(
                "path/to/dataset.csv"
            )

    def test_should_reject_empty_dataset(self, tmp_path):

        dataset_path = tmp_path / "empty_dataset.csv"

        dataset_path.write_text(
            "name,age\n"
        )

        with pytest.raises(
            ValueError,
            match="Dataset cannot be empty"
        ):
            self.service.analyze(
                str(dataset_path),
                "text/csv",
                "age"
            )

    def test_should_reject_missing_target_column(self, tmp_path):

        dataset_path = tmp_path / "customers.csv"

        dataset_path.write_text(
            "name,age\n"
            "Hariom,22\n"
            "Rahul,23\n"
        )

        with pytest.raises(
            ValueError,
            match="Target column 'salary' not found in dataset"
        ):
            self.service.analyze(
                str(dataset_path),
                "text/csv",
                "salary"
            )

    def test_should_reject_target_with_only_missing_values(self, tmp_path):

        dataset_path = tmp_path / "customers.csv"

        dataset_path.write_text(
            "name,salary\n"
            "Hariom,\n"
            "Rahul,\n"
        )

        with pytest.raises(
            ValueError,
            match="Target column cannot be empty"
        ):
            self.service.analyze(
                str(dataset_path),
                "text/csv",
                "salary"
            )

    def test_should_validate_target_column(self, tmp_path):

        dataset_path = tmp_path / "customers.csv"

        dataset_path.write_text(
            "name,age\n"
            "Hariom,22\n"
            "Rahul,23\n"
            "Ankit,24\n"
            "Ravi,25\n"
        )

    
        result =self.service.analyze(
            str(dataset_path),
            "text/csv",
            "age"
        )

        assert result["targetColumn"] == "age"
        assert result["rowCount"] == 4
        assert result["columnCount"] == 2

    def test_should_detect_classification_for_categorical_target(
        self,
        tmp_path
    ):

        dataset_path = tmp_path / "customers.csv"

        dataset_path.write_text(
            "age,segment\n"
            "22,A\n"
            "23,B\n"
            "24,A\n"
            "25,B\n"
        )

        result = self.service.analyze(
            str(dataset_path),
            "text/csv",
            "segment"
        )

        assert result['problemType'] == "CLASSIFICATION"

    def test_should_detect_classification_for_low_cardinality_numeric_target(
        self,
        tmp_path
    ):

        dataset_path = tmp_path / "customers.csv"

        dataset_path.write_text(
            "age,purchased\n"
            "22,0\n"
            "23,1\n"
            "24,0\n"
            "25,1\n"
        )

        result = self.service.analyze(
            str(dataset_path),
            "text/csv",
            "purchased"
        )

        assert result["problemType"] == "CLASSIFICATION"

    def test_should_detect_regression_for_high_cardinality_numeric_target(
        self,
        tmp_path
    ):

        dataset_path = tmp_path / "sales.csv"

        rows = ["id,sales"]

        for i in range(1, 31):
            rows.append(f"{i},{1000 + i * 100}")

        dataset_path.write_text(
            "\n".join(rows)
        )

        result = self.service.analyze(
            str(dataset_path),
            "text/csv",
            "sales"
        )

        assert result["problemType"] == "REGRESSION"

    def test_should_train_classification_model(self, tmp_path):

        dataset_path = tmp_path / "customers.csv"

        dataset_path.write_text(
            "age,income,purchased\n"
            "20,20000,0\n"
            "25,30000,0\n"
            "30,40000,1\n"
            "35,50000,1\n"
            "40,60000,1\n"
            "45,70000,1\n"
            "50,80000,1\n"
            "55,90000,1\n"
            "60,100000,1\n"
            "65,110000,1\n"
        )

        result = self.service.analyze(
            str(dataset_path),
            "text/csv",
            "purchased"
        )

        assert result["problemType"] == "CLASSIFICATION"
        assert result["training"]["model"] == "LogisticRegression"
        assert "accuracy" in result["training"]["metrics"]

    def test_should_train_regression_model(self, tmp_path):

        dataset_path = tmp_path / "sales.csv"

        dataset_path.write_text(
            "age,income,sales\n"
            "20,20000,30000\n"
            "25,30000,40000\n"
            "30,40000,50000\n"
            "35,50000,60000\n"
            "40,60000,70000\n"
            "45,70000,80000\n"
            "50,80000,90000\n"
            "55,90000,100000\n"
            "60,100000,110000\n"
            "65,110000,120000\n"
        )

        result = self.service.analyze(
            str(dataset_path),
            "text/csv",
            "sales"
        )

        assert result["problemType"] == "REGRESSION"
        assert result["training"]["model"] == "LinearRegression"
        assert "mean_absolute_error" in result["training"]["metrics"]
        assert "root_mean_squared_error" in result["training"]["metrics"]       
                

            
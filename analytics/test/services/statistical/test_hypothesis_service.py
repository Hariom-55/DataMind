import pandas as pd
import pytest
from app.services.statistical.hypothesis_service import HypothesisTestingService
from app.loaders.dataset_loader import DatasetLoader

class TestHypothesisTestingService:

    def setup_method(self):
        self.dataset_loader = DatasetLoader()
        self.service = HypothesisTestingService()

    def test_one_sample_t_test_returns_non_significant_result(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "one_sample_t_test.csv"

        dataset_path.write_text(
            """salary
                39000
                40000
                41000
                40000
                40000
            """
        )

        df = self.dataset_loader.load(str(dataset_path))

        result = self.service.perform_one_sample_t_test(
            df,
            "salary",
            40000
        )

        assert result["test"] == "ONE_SAMPLE_T_TEST"
        assert result["column"] == "salary"
        assert result["referenceValue"] == 40000
        assert result["sampleSize"] == 5

        assert result["testStatistic"] == 0.0
        assert result["pValue"] == 1.0

        assert result["alpha"] == 0.05
        assert result["significant"] is False

        assert result["decision"] == "FAIL_TO_REJECT_NULL"

    def test_one_sample_t_test_returns_significant_result(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "significant_t_test.csv"

        dataset_path.write_text(
            """salary
                50000
                51000
                52000
                53000
                54000
            """
        )

        df = self.dataset_loader.load(str(dataset_path))

        result = self.service.perform_one_sample_t_test(
            df,
            "salary",
            40000
        )

        assert result["test"] == "ONE_SAMPLE_T_TEST"
        assert result["sampleSize"] == 5

        assert result["testStatistic"] > 0
        assert result["pValue"] < 0.05

        assert result["alpha"] == 0.05
        assert result["significant"] is True

        assert result["decision"] == "REJECT_NULL"

    def test_one_sample_t_test_ignores_missing_values(
        self
    ):
        df = pd.DataFrame({
        "salary": [
            50000,
            51000,
            52000,
            None,
            54000
        ]
    })

        result = self.service.perform_one_sample_t_test(
            df,
            "salary",
            40000
        )

        assert result["sampleSize"] == 4
        assert result["pValue"] < 0.05

    def test_one_sample_t_test_rejects_missing_column(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "invalid_column.csv"

        dataset_path.write_text(
            """salary
                50000
                51000
                52000
            """
        )

        df = self.dataset_loader.load(str(dataset_path))

        with pytest.raises(ValueError, match="Column not found"):
            self.service.perform_one_sample_t_test(
                df,
                "age",
                40000
            )

    def test_one_sample_t_test_rejects_non_numeric_column(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "categorical_t_test.csv"

        dataset_path.write_text(
            """city
                Delhi
                Mumbai
                Pune
            """
        )

        df = self.dataset_loader.load(str(dataset_path))

        with pytest.raises(
            ValueError,
            match="must be numeric"
        ):
            self.service.perform_one_sample_t_test(
                df,
                "city",
                40000
            )

    def test_one_sample_t_test_rejects_insufficient_observations(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "insufficient_t_test.csv"

        dataset_path.write_text(
            """salary
                50000
            """
        )

        df = self.dataset_loader.load(str(dataset_path))

        with pytest.raises(
            ValueError,
            match="at least 2"
        ):
            self.service.perform_one_sample_t_test(
                df,
                "salary",
                40000
            )

    def test_one_sample_t_test_rejects_invalid_alpha(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "invalid_alpha.csv"

        dataset_path.write_text(
            """salary
                50000
                51000
                52000
            """
        )

        df = self.dataset_loader.load(str(dataset_path))

        with pytest.raises(
            ValueError,
            match="alpha"
        ):
            self.service.perform_one_sample_t_test(
                df,
                "salary",
                40000,
                alpha=1.5
            )

    def test_one_sample_t_test_supports_custom_alpha(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "custom_alpha.csv"

        dataset_path.write_text(
            """salary
                50000
                51000
                52000
                53000
                54000
            """
        )

        df = self.dataset_loader.load(str(dataset_path))

        result = self.service.perform_one_sample_t_test(
            df,
            "salary",
            40000,
            alpha=0.01
        )

        assert result["alpha"] == 0.01
        assert result["pValue"] < 0.01
        assert result["significant"] is True

    def test_independent_t_test_returns_significant_result(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "independent_t_test.csv"

        dataset_path.write_text(
            """salary,department
    50000,A
    51000,A
    52000,A
    70000,B
    71000,B
    72000,B
    """
        )

        df = self.dataset_loader.load(str(dataset_path))

        result = self.service.perform_independent_t_test(
            df,
            "salary",
            "department"
        )

        assert result["test"] == "INDEPENDENT_T_TEST"
        assert result["valueColumn"] == "salary"
        assert result["groupColumn"] == "department"

        assert result["groups"] == ["A", "B"]

        assert result["sampleSizes"]["A"] == 3
        assert result["sampleSizes"]["B"] == 3

        assert result["testStatistic"] < 0
        assert result["pValue"] < 0.05

        assert result["alpha"] == 0.05
        assert result["significant"] is True
        assert result["decision"] == "REJECT_NULL"

    def test_independent_t_test_returns_non_significant_result(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "independent_t_test_equal.csv"

        dataset_path.write_text(
            """salary,department
    50000,A
    51000,A
    52000,A
    50000,B
    51000,B
    52000,B
    """
        )

        df = self.dataset_loader.load(str(dataset_path))

        result = self.service.perform_independent_t_test(
            df,
            "salary",
            "department"
        )

        assert result["groups"] == ["A", "B"]

        assert result["sampleSizes"]["A"] == 3
        assert result["sampleSizes"]["B"] == 3

        assert result["pValue"] >= 0.05
        assert result["significant"] is False
        assert result["decision"] == "FAIL_TO_REJECT_NULL"

    def test_independent_t_test_ignores_missing_values(
        self
    ):
        df = pd.DataFrame({
            "salary": [
                50000,
                51000,
                None,
                70000,
                71000,
                72000
            ],
            "department": [
                "A",
                "A",
                "A",
                "B",
                "B",
                "B"
            ]
        })

        result = self.service.perform_independent_t_test(
            df,
            "salary",
            "department"
        )

        assert result["sampleSizes"]["A"] == 2
        assert result["sampleSizes"]["B"] == 3

        assert result["pValue"] < 0.05

   
    def test_independent_t_test_rejects_missing_group_column(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "invalid_group_column.csv"

        dataset_path.write_text(
            """salary,department
    50000,A
    51000,A
    70000,B
    71000,B
    """
        )

        df = self.dataset_loader.load(str(dataset_path))

        with pytest.raises(
            ValueError,
            match="Column not found"
        ):
            self.service.perform_independent_t_test(
                df,
                "salary",
                "team"
            )

    def test_independent_t_test_rejects_non_numeric_value_column(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "non_numeric_value.csv"

        dataset_path.write_text(
            """city,department
    Delhi,A
    Mumbai,A
    Pune,B
    Jaipur,B
    """
        )

        df = self.dataset_loader.load(str(dataset_path))

        with pytest.raises(
            ValueError,
            match="must be numeric"
        ):
            self.service.perform_independent_t_test(
                df,
                "city",
                "department"
            )

    def test_independent_t_test_rejects_more_than_two_groups(
        self
    ):
        df = pd.DataFrame({
            "salary": [
                50000,
                51000,
                60000,
                61000,
                70000,
                71000
            ],
            "department": [
                "A",
                "A",
                "B",
                "B",
                "C",
                "C"
            ]
        })

        with pytest.raises(
            ValueError,
            match="exactly two groups"
        ):
            self.service.perform_independent_t_test(
                df,
                "salary",
                "department"
            )

    def test_independent_t_test_rejects_single_group(
        self
    ):
        df = pd.DataFrame({
            "salary": [
                50000,
                51000,
                52000
            ],
            "department": [
                "A",
                "A",
                "A"
            ]
        })

        with pytest.raises(
            ValueError,
            match="exactly two groups"
        ):
            self.service.perform_independent_t_test(
                df,
                "salary",
                "department"
            )

    def test_independent_t_test_rejects_insufficient_group_observations(
        self
    ):
        df = pd.DataFrame({
            "salary": [
                50000,
                70000,
                71000
            ],
            "department": [
                "A",
                "B",
                "B"
            ]
        })

        with pytest.raises(
            ValueError,
            match="at least 2 observations"
        ):
            self.service.perform_independent_t_test(
                df,
                "salary",
                "department"
            )

    def test_independent_t_test_rejects_invalid_alpha(
        self
    ):
        df = pd.DataFrame({
            "salary": [
                50000,
                51000,
                70000,
                71000
            ],
            "department": [
                "A",
                "A",
                "B",
                "B"
            ]
        })

        with pytest.raises(
            ValueError,
            match="alpha"
        ):
            self.service.perform_independent_t_test(
                df,
                "salary",
                "department",
                alpha=1.5
            )

    def test_paired_t_test_returns_significant_result(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "paired_t_test.csv"

        dataset_path.write_text(
            """before,after
    60,72
    55,66
    70,81
    65,77
    80,91
    """
        )

        df = self.dataset_loader.load(str(dataset_path))

        result = self.service.perform_paired_t_test(
            df,
            "before",
            "after"
        )

        assert result["test"] == "PAIRED_T_TEST"
        assert result["column1"] == "before"
        assert result["column2"] == "after"

        assert result["sampleSize"] == 5

        assert result["testStatistic"] < 0
        assert result["pValue"] < 0.05

        assert result["alpha"] == 0.05
        assert result["significant"] is True
        assert result["decision"] == "REJECT_NULL"

    def test_paired_t_test_ignores_missing_pairs(
        self
    ):
        df = pd.DataFrame({
            "before": [
                60,
                65,
                None,
                75,
                80
            ],
            "after": [
                72,
                77,
                80,
                None,
                91
            ]
        })

        result = self.service.perform_paired_t_test(
            df,
            "before",
            "after"
        )

        assert result["sampleSize"] == 3

    def test_paired_t_test_rejects_missing_first_column(
        self
    ):
        df = pd.DataFrame({
            "before": [60, 65, 70],
            "after": [70, 75, 80]
        })

        with pytest.raises(
            ValueError,
            match="Column not found"
        ):
            self.service.perform_paired_t_test(
                df,
                "missing",
                "after"
            )

    def test_paired_t_test_rejects_missing_second_column(
        self
    ):
        df = pd.DataFrame({
            "before": [60, 65, 70],
            "after": [70, 75, 80]
        })

        with pytest.raises(
            ValueError,
            match="Column not found"
        ):
            self.service.perform_paired_t_test(
                df,
                "before",
                "missing"
            )

    def test_paired_t_test_rejects_non_numeric_first_column(
        self
    ):
        df = pd.DataFrame({
            "before": [
                "low",
                "medium",
                "high"
            ],
            "after": [
                70,
                75,
                80
            ]
        })

        with pytest.raises(
            ValueError,
            match="must be numeric"
        ):
            self.service.perform_paired_t_test(
                df,
                "before",
                "after"
            )

    def test_paired_t_test_rejects_non_numeric_second_column(
        self
    ):
        df = pd.DataFrame({
            "before": [
                60,
                65,
                70
            ],
            "after": [
                "low",
                "medium",
                "high"
            ]
        })

        with pytest.raises(
            ValueError,
            match="must be numeric"
        ):
            self.service.perform_paired_t_test(
                df,
                "before",
                "after"
            )

    def test_paired_t_test_rejects_insufficient_pairs(
        self
    ):
        df = pd.DataFrame({
            "before": [60],
            "after": [70]
        })

        with pytest.raises(
            ValueError,
            match="at least 2 paired observations"
        ):
            self.service.perform_paired_t_test(
                df,
                "before",
                "after"
            )

    def test_paired_t_test_rejects_invalid_alpha(
        self
    ):
        df = pd.DataFrame({
            "before": [60, 65, 70],
            "after": [70, 75, 80]
        })

        with pytest.raises(
            ValueError,
            match="alpha"
        ):
            self.service.perform_paired_t_test(
                df,
                "before",
                "after",
                alpha=1.5
            )

    def test_paired_t_test_supports_custom_alpha(
        self
    ):
        df = pd.DataFrame({
            "before": [
                60,
                65,
                70,
                75,
                80
            ],
            "after": [
                72,
                77,
                81,
                87,
                91
            ]
        })

        result = self.service.perform_paired_t_test(
            df,
            "before",
            "after",
            alpha=0.01
        )

        assert result["alpha"] == 0.01
        assert result["pValue"] < 0.01
        assert result["significant"] is True

    def test_paired_t_test_returns_hypothesis_interpretation(
        self
    ):
        df = pd.DataFrame({
            "before": [60, 65, 70, 75, 80],
            "after": [72, 77, 81, 87, 91]
        })

        result = self.service.perform_paired_t_test(
            df,
            "before",
            "after"
        )

        assert result["nullHypothesis"] == (
            "The mean difference between the paired measurements is zero"
        )

        assert result["alternativeHypothesis"] == (
            "The mean difference between the paired measurements is not zero"
        )

        assert (
            "sufficient evidence"
            in result["interpretation"]
        )

    def test_chi_square_test_returns_significant_result(
        self
    ):
        df = pd.DataFrame({
            "gender": [
                "M", "M", "M", "M",
                "F", "F", "F", "F"
            ],
            "purchased": [
                "Yes", "Yes", "Yes", "Yes",
                "No", "No", "No", "No"
            ]
        })

        result = self.service.perform_chi_square_test(
            df,
            "gender",
            "purchased"
        )

        assert result["test"] == "CHI_SQUARE_INDEPENDENCE"
        assert result["column1"] == "gender"
        assert result["column2"] == "purchased"

        assert result["sampleSize"] == 8
        assert result["degreesOfFreedom"] == 1

        assert result["testStatistic"] > 0
        assert result["pValue"] < 0.05

        assert result["alpha"] == 0.05
        assert result["significant"] is True
        assert result["decision"] == "REJECT_NULL"

    def test_chi_square_test_returns_non_significant_result(
        self
    ):
        df = pd.DataFrame({
            "gender": [
                "M", "M", "M", "M",
                "F", "F", "F", "F"
            ],
            "purchased": [
                "Yes", "Yes",
                "No", "No",
                "Yes", "Yes",
                "No", "No"
            ]
        })

        result = self.service.perform_chi_square_test(
            df,
            "gender",
            "purchased"
        )

        assert result["test"] == "CHI_SQUARE_INDEPENDENCE"
        assert result["sampleSize"] == 8

        assert result["pValue"] >= 0.05
        assert result["significant"] is False
        assert result["decision"] == "FAIL_TO_REJECT_NULL"

    def test_chi_square_test_ignores_missing_pairs(
        self
    ):
        df = pd.DataFrame({
            "gender": [
                "M",
                "M",
                None,
                "F",
                "F"
            ],
            "purchased": [
                "Yes",
                "No",
                "Yes",
                "Yes",
                None
            ]
        })

        result = self.service.perform_chi_square_test(
            df,
            "gender",
            "purchased"
        )

        assert result["sampleSize"] == 3

    def test_chi_square_test_rejects_missing_first_column(
        self
    ):
        df = pd.DataFrame({
            "gender": ["M", "F"],
            "purchased": ["Yes", "No"]
        })

        with pytest.raises(
            ValueError,
            match="Column not found"
        ):
            self.service.perform_chi_square_test(
                df,
                "age",
                "purchased"
            )

    def test_chi_square_test_rejects_missing_second_column(
        self
    ):
        df = pd.DataFrame({
            "gender": ["M", "F"],
            "purchased": ["Yes", "No"]
        })

        with pytest.raises(
            ValueError,
            match="Column not found"
        ):
            self.service.perform_chi_square_test(
                df,
                "gender",
                "purchase"
            )

    def test_chi_square_test_rejects_insufficient_observations(
        self
    ):
        df = pd.DataFrame({
            "gender": ["M"],
            "purchased": ["Yes"]
        })

        with pytest.raises(
            ValueError,
            match="at least 2 observations"
        ):
            self.service.perform_chi_square_test(
                df,
                "gender",
                "purchased"
            )

    def test_chi_square_test_rejects_single_category_column(
        self
    ):
        df = pd.DataFrame({
            "gender": [
                "M",
                "M",
                "M",
                "M"
            ],
            "purchased": [
                "Yes",
                "No",
                "Yes",
                "No"
            ]
        })

        with pytest.raises(
            ValueError,
            match="at least two categories"
        ):
            self.service.perform_chi_square_test(
                df,
                "gender",
                "purchased"
            )

    def test_chi_square_test_rejects_invalid_alpha(
        self
    ):
        df = pd.DataFrame({
            "gender": [
                "M", "M",
                "F", "F"
            ],
            "purchased": [
                "Yes", "No",
                "Yes", "No"
            ]
        })

        with pytest.raises(
            ValueError,
            match="alpha"
        ):
            self.service.perform_chi_square_test(
                df,
                "gender",
                "purchased",
                alpha=1.5
            )

    def test_chi_square_test_supports_custom_alpha(
        self
    ):
        df = pd.DataFrame({
            "gender": [
                "M", "M", "M", "M",
                "F", "F", "F", "F"
            ],
            "purchased": [
                "Yes", "Yes", "Yes", "Yes",
                "No", "No", "No", "No"
            ]
        })

        result = self.service.perform_chi_square_test(
            df,
            "gender",
            "purchased",
            alpha=0.01
        )

        assert result["alpha"] == 0.01
        assert result["pValue"] > 0.01
        assert result["significant"] is False
        assert result["decision"] == "FAIL_TO_REJECT_NULL"

    def test_chi_square_test_returns_hypothesis_interpretation(
        self
    ):
        df = pd.DataFrame({
            "gender": [
                "M", "M", "M", "M",
                "F", "F", "F", "F"
            ],
            "purchased": [
                "Yes", "Yes", "Yes", "Yes",
                "No", "No", "No", "No"
            ]
        })

        result = self.service.perform_chi_square_test(
            df,
            "gender",
            "purchased"
        )

        assert result["nullHypothesis"] == (
            "The two categorical variables are independent"
        )

        assert result["alternativeHypothesis"] == (
            "The two categorical variables are associated"
        )

        assert (
            "sufficient evidence"
            in result["interpretation"]
        )
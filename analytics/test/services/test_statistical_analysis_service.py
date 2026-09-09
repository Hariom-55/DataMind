import pandas as pd
import pytest
from app.services.statistical_service import StatisticalAnalysisService
from app.loaders.dataset_loader import DatasetLoader

class TestStatisticalAnalysisService:

    def setup_method(self):
        self.dataset_loader = DatasetLoader()
        self.service = StatisticalAnalysisService(self.dataset_loader)

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

    def test_should_generate_missing_value_statistics(
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
        assert statistics["missingCount"] == 1
        assert statistics["missingPercentage"] == pytest.approx(20.0)

    def test_should_generate_range(
            self,
            tmp_path
    ):

        dataset = pd.DataFrame({
            "age": [20, 30, 40, 50, 60]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        statistics = result["descriptiveStatistics"]["age"]

        assert statistics["range"] == pytest.approx(40.0)

    def test_should_generate_iqr(
            self,
            tmp_path
    ):

        dataset = pd.DataFrame({
            "age": [20, 30, 40, 50, 60]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        statistics = result["descriptiveStatistics"]["age"]

        assert statistics["IQR"] == pytest.approx(20.0)

    def test_should_generate_mode(
            self,
            tmp_path
    ):

        dataset = pd.DataFrame({
            "age": [20, 30, 30, 40, 50]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        statistics = result["descriptiveStatistics"]["age"]

        assert statistics["mode"] == pytest.approx(30.0)

    def test_should_handle_constant_numeric_column(
            self,
            tmp_path
    ):

        dataset = pd.DataFrame({
            "age": [30, 30, 30, 30, 30]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        result = self.service.analyze(str(file_path))

        statistics = result["descriptiveStatistics"]["age"]

        assert statistics["count"] == 5
        assert statistics["mean"] == pytest.approx(30.0)
        assert statistics["median"] == pytest.approx(30.0)
        assert statistics["mode"] == pytest.approx(30.0)
        assert statistics["range"] == pytest.approx(0.0)
        assert statistics["IQR"] == pytest.approx(0.0)

    def test_correlation_analysis_identifies_strong_positive_relationship(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "correlation.csv"

        dataset_path.write_text(
            """age,salary
                20,20000
                30,30000
                40,40000
                50,50000
                60,60000
            """
        )

        result = self.service.analyze(str(dataset_path))

        strongest = result["correlationAnalysis"]["pearson"]["strongest"]

        assert len(strongest) == 1

        pair = strongest[0]

        assert pair["column1"] == "age"
        assert pair["column2"] == "salary"
        assert pair["correlation"] == 1.0
        assert pair["strength"] == "VERY_STRONG"
        assert pair["direction"] == "POSITIVE"

    def test_correlation_analysis_identifies_strong_negative_relationship(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "negative_correlation.csv"

        dataset_path.write_text(
            """age,performance
                20,100
                30,80
                40,60
                50,40
                60,20
            """
        )

        result = self.service.analyze(str(dataset_path))

        strongest = result["correlationAnalysis"]["pearson"]["strongest"]

        assert len(strongest) == 1

        pair = strongest[0]

        assert pair["column1"] == "age"
        assert pair["column2"] == "performance"
        assert pair["correlation"] == -1.0
        assert pair["strength"] == "VERY_STRONG"
        assert pair["direction"] == "NEGATIVE"   

    def test_correlation_analysis_does_not_return_duplicate_pairs(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "duplicate_pairs.csv"

        dataset_path.write_text(
            """age,salary,experience
                20,20000,1
                30,30000,2
                40,40000,3
                50,50000,4
                60,60000,5
            """
        )

        result = self.service.analyze(str(dataset_path))

        pairs = result["correlationAnalysis"]["pearson"]["pairs"]

        assert len(pairs) == 3

    def test_correlation_analysis_sorts_strongest_relationships_by_absolute_correlation(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "sorted_correlations.csv"

        dataset_path.write_text(
            """a,b,c
                1,1,5
                2,2,4
                3,4,3
                4,8,2
                5,16,1
            """
        )

        result = self.service.analyze(str(dataset_path))

        strongest = result["correlationAnalysis"]["pearson"]["strongest"]

        correlations = [
            abs(pair["correlation"])
            for pair in strongest
        ]

        assert correlations == sorted(
            correlations,
            reverse=True
        )

    def test_correlation_analysis_is_empty_without_numeric_columns(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "categorical.csv"

        dataset_path.write_text(
            """name,city
                Hariom,Delhi
                Rahul,Mumbai
                Aman,Pune
            """
        )

        result = self.service.analyze(str(dataset_path))

        correlation_analysis = result["correlationAnalysis"]

        assert correlation_analysis["pearson"]["pairs"] == []
        assert correlation_analysis["pearson"]["strongest"] == []

        assert correlation_analysis["spearman"]["pairs"] == []
        assert correlation_analysis["spearman"]["strongest"] == []

    def test_correlation_analysis_handles_constant_column(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "constant_correlation.csv"

        dataset_path.write_text(
            """age,constant
                20,1
                30,1
                40,1
                50,1
                60,1
            """
        )

        result = self.service.analyze(str(dataset_path))

        pairs = result["correlationAnalysis"]["pearson"]["pairs"]

        assert pairs == []

    def test_correlation_analysis_handles_zero_correlation(
        self,
        tmp_path
    ):
        dataset_path = tmp_path / "zero_correlation.csv"

        dataset_path.write_text(
            """x,y
               1,1
               2,-2
               3,0
               4,2
               5,-1
            """
        )

        result = self.service.analyze(str(dataset_path))

        pairs = result["correlationAnalysis"]["pearson"]["pairs"]

        assert len(pairs) == 1

        pair = pairs[0]

        assert pair["correlation"] == 0.0
        assert pair["direction"] == "NONE"
        assert pair["strength"] == "VERY_WEAK"

    def test_correlation_strength_classification(self):
        assert (
            self.service._correlation_strength(0.10)
            == "VERY_WEAK"
        )

        assert (
            self.service._correlation_strength(0.20)
            == "WEAK"
        )

        assert (
            self.service._correlation_strength(0.40)
            == "MODERATE"
        )

        assert (
            self.service._correlation_strength(0.60)
            == "STRONG"
        )

        assert (
            self.service._correlation_strength(0.80)
            == "VERY_STRONG"
        )

    def test_correlation_strength_uses_absolute_value(self):
        assert (
            self.service._correlation_strength(-0.85)
            == "VERY_STRONG"
        )

        assert (
            self.service._correlation_strength(-0.55)
            == "MODERATE"
        )

    def test_correlation_direction_classification(self):
        assert (
            self.service._correlation_direction(0.75)
            == "POSITIVE"
        )

        assert (
            self.service._correlation_direction(-0.75)
            == "NEGATIVE"
        )

        assert (
            self.service._correlation_direction(0.0)
            == "NONE"
        )

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
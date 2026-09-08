import pandas as pd
import pytest

from app.services.data_cleaning_engine import (
    DataCleaningEngine
)


class TestDataCleaningEngine:

    def setup_method(self):

        self.engine = DataCleaningEngine()

    def test_should_remove_duplicate_rows(self):

        df = pd.DataFrame({
            "name": [
                "Hariom",
                "Rahul",
                "Hariom"
            ],
            "age": [
                22,
                23,
                22
            ]
        })

        result = self.engine.apply_operation(
            df,
            "REMOVE_DUPLICATES"
        )

        assert len(result) == 2
        assert result.iloc[0]["name"] == "Hariom"
        assert result.iloc[1]["name"] == "Rahul"

    def test_should_replace_invalid_values(self):

        df = pd.DataFrame({
            "age": [
                22,
                float("inf"),
                float("-inf"),
                25
            ]
        })

        result = self.engine.apply_operation(
            df,
            "REPLACE_INVALID_VALUES",
            "age"
        )

        assert pd.isna(result.loc[1, "age"])
        assert pd.isna(result.loc[2, "age"])
        assert result.loc[0, "age"] == 22
        assert result.loc[3, "age"] == 25

    def test_should_apply_median_imputation(self):

        df = pd.DataFrame({
            "age": [
                20,
                22,
                None,
                24,
                26
            ]
        })

        result = self.engine.apply_operation(
            df,
            "IMPUTE_MISSING_VALUES",
            "age"
        )

        assert result["age"].isna().sum() == 0
        assert result.loc[2, "age"] == 23

    def test_should_normalize_categories(self):

        df = pd.DataFrame({
            "city": [
                " Delhi ",
                "DELHI",
                "Mumbai "
            ]
        })

        result = self.engine.apply_operation(
            df,
            "NORMALIZE_CATEGORIES",
            "city"
        )

        assert result["city"].tolist() == [
            "delhi",
            "delhi",
            "mumbai"
        ]

    def test_should_remove_feature(self):

        df = pd.DataFrame({
            "age": [20, 21, 22],
            "constant": ["A", "A", "A"]
        })

        result = self.engine.apply_operation(
            df,
            "REMOVE_FEATURE",
            "constant"
        )

        assert "constant" not in result.columns
        assert "age" in result.columns

    def test_should_reject_review_outliers_operation(self):

        df = pd.DataFrame({
            "age": [20, 21, 100]
        })

        with pytest.raises(
                ValueError,
                match="requires explicit review"
        ):
            self.engine.apply_operation(
                df,
                "REVIEW_OUTLIERS",
                "age"
            )

    def test_should_reject_unknown_column(self):

        df = pd.DataFrame({
            "age": [20, 21, 22]
        })

        with pytest.raises(
                ValueError,
                match="Column 'salary' not found"
        ):
            self.engine.apply_operation(
                df,
                "REMOVE_FEATURE",
                "salary"
            )

    def test_should_reject_unsupported_operation(self):

        df = pd.DataFrame({
            "age": [20, 21, 22]
        })

        with pytest.raises(
                ValueError,
                match="Unsupported cleaning operation"
        ):
            self.engine.apply_operation(
                df,
                "UNKNOWN_OPERATION",
                "age"
            )

    def test_should_not_modify_original_dataframe(self):

        df = pd.DataFrame({
            "city": [
                " Delhi ",
                "DELHI"
            ]
        })

        original = df.copy()

        result = self.engine.apply_operation(
            df,
            "NORMALIZE_CATEGORIES",
            "city"
        )

        assert df.equals(original)

        assert result["city"].tolist() == [
            "delhi",
            "delhi"
        ]

    def test_should_apply_mode_imputation_for_categorical_column(self):

        df = pd.DataFrame({
            "city": [
                "Delhi",
                "Mumbai",
                "Delhi",
                None,
                "Delhi"
            ]
        })

        result = self.engine.apply_operation(
            df,
            "IMPUTE_MISSING_VALUES",
            "city"
        )

        assert result["city"].isna().sum() == 0
        assert result.loc[3, "city"] == "Delhi"

    def test_should_reject_missing_column_for_imputation(self):

        df = pd.DataFrame({
            "age": [
                20,
                None,
                25
            ]
        })

        with pytest.raises(
                ValueError,
                match="Column 'salary' not found"
        ):
            self.engine.apply_operation(
                df,
                "IMPUTE_MISSING_VALUES",
                "salary"
            )


import pandas as pd
import pytest

from app.services.data_cleaning_services import DataCleaningService


from app.services.data_cleaning_workflow_service import  DataCleaningWorkflowService



class TestDataCleaningWorkflowService:

    def setup_method(self):

        self.cleaning_service = (
            DataCleaningService()
        )

        self.workflow_service = (
            DataCleaningWorkflowService(
                self.cleaning_service
            )
        )

    def test_should_return_no_issues_for_clean_dataset(self):

        df = pd.DataFrame({
            "age": [
                20,
                21,
                22,
                23,
                24
            ],
            "city": [
                "Delhi",
                "Mumbai",
                "Kolkata",
                "Chennai",
                "Pune"
            ]
        })

        result = (
            self.workflow_service
            .assess_dataset(df)
        )

        assert result["totalRows"] == 5
        assert result["totalColumns"] == 2
        assert result["issueCount"] == 0
        assert result["issues"] == []
        assert result["recommendations"] == []

    def test_should_return_issues_and_recommendations(self):

        df = pd.DataFrame({
            "age": [
                20,
                None,
                22,
                23,
                24
            ]
        })

        result = (
            self.workflow_service
            .assess_dataset(df)
        )

        assert result["issueCount"] > 0
        assert len(result["issues"]) > 0
        assert len(result["recommendations"]) > 0

    def test_should_generate_recommendation_for_each_issue(self):

        df = pd.DataFrame({
            "age": [
                20,
                None,
                22,
                23,
                24
            ],
            "country": [
                "India",
                "india",
                "India",
                "India",
                "India"
            ]
        })

        result = (
            self.workflow_service
            .assess_dataset(df)
        )

        issue_types = {
            issue["issueType"]
            for issue in result["issues"]
        }

        recommendation_types = {
            recommendation["issueType"]
            for recommendation
            in result["recommendations"]
        }

        assert issue_types == recommendation_types

    def test_should_not_modify_dataframe(self):

        df = pd.DataFrame({
            "age": [
                20,
                None,
                22
            ]
        })

        original = df.copy()

        self.workflow_service.assess_dataset(df)

        assert df.equals(original)

    def test_should_handle_multiple_issue_types(self):

        df = pd.DataFrame({
            "age": [
                20,
                None,
                22,
                float("inf"),
                100
            ],
            "country": [
                "India",
                "india",
                "India",
                "India",
                "India"
            ],
            "constant": [
                "A",
                "A",
                "A",
                "A",
                "A"
            ]
        })

        result = (
            self.workflow_service
            .assess_dataset(df)
        )

        issue_types = {
            issue["issueType"]
            for issue in result["issues"]
        }

        assert "MISSING_VALUES" in issue_types
        assert "INVALID_VALUES" in issue_types
        assert "CATEGORICAL_INCONSISTENCY" in issue_types
        assert "CONSTANT_FEATURE" in issue_types

        assert (
            len(result["recommendations"])
            == result["issueCount"]
        )

    def test_should_apply_selected_cleaning_operation(self):

        df = pd.DataFrame({
            "age": [
                20,
                None,
                24
            ]
        })

        operations = [
            {
                "operation": "IMPUTE_MISSING_VALUES",
                "column": "age"
            }
        ]

        result = (
            self.workflow_service
            .clean_dataset(
                df,
                operations
            )
        )

        assert result["operationsApplied"] == 1
        assert result["cleanedRows"] == 3
        assert result["cleanedColumns"] == 1

        assert (
            result["data"]["age"]
            .isna()
            .sum()
            == 0
        )

        assert len(result["changes"]) == 1
        assert result["changes"][0]["rowsAffected"] == 1

    def test_should_apply_multiple_cleaning_operations(self):

        df = pd.DataFrame({
            "age": [
                20,
                None,
                24,
                24
            ],
            "city": [
                " Delhi ",
                "DELHI",
                "Mumbai",
                "Mumbai"
            ]
        })

        operations = [
            {
                "operation": "REMOVE_DUPLICATES",
                "column": None
            },
            {
                "operation": "IMPUTE_MISSING_VALUES",
                "column": "age"
            },
            {
                "operation": "NORMALIZE_CATEGORIES",
                "column": "city"
            }
        ]

        result = (
            self.workflow_service
            .clean_dataset(
                df,
                operations
            )
        )

        assert result["operationsApplied"] == 3
        assert len(result["changes"]) == 3

        assert (
            result["data"]["age"]
            .isna()
            .sum()
            == 0
        )

        assert result["data"]["city"].tolist() == [
            "delhi",
            "delhi",
            "mumbai"
        ]

    def test_should_not_modify_original_dataframe_when_cleaning(self):

        df = pd.DataFrame({
            "age": [
                20,
                None,
                24
            ]
        })

        original = df.copy()

        operations = [
            {
                "operation": "IMPUTE_MISSING_VALUES",
                "column": "age"
            }
        ]

        self.workflow_service.clean_dataset(
            df,
            operations
        )

        assert df.equals(original)

    def test_should_reject_review_only_operation(self):

        df = pd.DataFrame({
            "age": [
                20,
                21,
                100
            ]
        })

        operations = [
            {
                "operation": "REVIEW_OUTLIERS",
                "column": "age"
            }
        ]

        with pytest.raises(
                ValueError,
                match="requires explicit review"
        ):
            self.workflow_service.clean_dataset(
                df,
                operations
            )

    def test_should_return_original_data_when_no_operations_selected(self):

        df = pd.DataFrame({
            "age": [
                20,
                None,
                24
            ]
        })

        result = (
            self.workflow_service
            .clean_dataset(
                df,
                []
            )
        )

        assert result["operationsApplied"] == 0
        assert result["changes"] == []
        assert result["data"].equals(df)


    def test_should_build_cleaned_dataset_result(self):

        df = pd.DataFrame({
            "name": ["Hariom", "Hariom", "Alice"],
            "age": [22, 22, 25]
        })

        operations = [
            {
                "operation": "REMOVE_DUPLICATES"
            }
        ]

        result = self.workflow_service.clean_dataset_result(
            df,
            operations
        )

        assert result.extension == "csv"

        assert result.original_rows == 3
        assert result.cleaned_rows == 2

        assert result.original_columns == 2
        assert result.cleaned_columns == 2

        assert result.operations_applied == 1

        assert isinstance(result.content, bytes)

        assert len(result.content_hash) == 64

    def test_should_preserve_extension(self):

        df = pd.DataFrame({
            "name": ["Hariom"]
        })

        result = self.workflow_service.clean_dataset_result(
            df,
            [],
            ".csv"
        )

        assert result.extension == "csv"

    def test_should_not_modify_original_dataframe(self):

        df = pd.DataFrame({
            "name": [" Hariom ", "Alice"],
            "age": [22, 25]
        })

        original_df = df.copy(deep=True)

        operations = [
            {
                "operation": "NORMALIZE_CATEGORIES",
                "column": "name"
            }
        ]

        self.workflow_service.clean_dataset_result(
            df,
            operations
        )

        pd.testing.assert_frame_equal(
            df,
            original_df
        )
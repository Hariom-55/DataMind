import pandas as pd

from app.services.data_cleaning_services import DataCleaningService


class TestDataCleaningService:

    def setup_method(self):

        self.service = DataCleaningService()


    def test_should_detect_missing_values(self):

        df = pd.DataFrame({
            "name": [
                "Hariom",
                "Rahul",
                "Ankit",
                "Ravi"
            ],
            "age": [
                22,
                None,
                24,
                None
            ]
        })

        result = self.service._detect_missing_values(
            df
        )

        assert len(result) == 1

        issue = result[0]

        assert issue["issueType"] == "MISSING_VALUES"
        assert issue["column"] == "age"
        assert issue["affectedRows"] == 2
        assert issue["affectedPercentage"] == 50.0
        assert issue["severity"] == "HIGH"


    def test_should_not_report_columns_without_missing_values(self):

        df = pd.DataFrame({
            "name": [
                "Hariom",
                "Rahul",
                "Ankit"
            ],
            "age": [
                22,
                23,
                24
            ]
        })

        result = self.service._detect_missing_values(
            df
        )

        assert result == []


    def test_should_detect_low_missing_percentage(self):

        df = pd.DataFrame({
            "age": [
                22,
                None,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31
            ]
        })

        result = self.service._detect_missing_values(
            df
        )

        assert len(result) == 1

        issue = result[0]

        assert issue["affectedRows"] == 1
        assert issue["affectedPercentage"] == 10.0
        assert issue["severity"] == "LOW"


    def test_should_return_no_issues_for_empty_dataframe(self):

        df = pd.DataFrame()

        result = self.service._detect_missing_values(
            df
        )

        assert result == []

    def test_should_detect_duplicate_rows(self):

        df = pd.DataFrame({
            "name": [
                "Hariom",
                "Rahul",
                "Hariom",
                "Ankit",
                "Rahul"
            ],
            "age": [
                22,
                23,
                22,
                24,
                23
            ]
        })

        result = self.service._detect_duplicate_rows(
            df
        )

        assert len(result) == 1

        issue = result[0]

        assert issue["issueType"] == "DUPLICATE_ROWS"
        assert issue["column"] is None
        assert issue["affectedRows"] == 2
        assert issue["affectedPercentage"] == 40.0
        assert issue["severity"] == "HIGH"

    def test_should_not_report_duplicate_rows_when_none_exist(self):

        df = pd.DataFrame({
            "name": [
                "Hariom",
                "Rahul",
                "Ankit"
            ],
            "age": [
                22,
                23,
                24
            ]
        })

        result = self.service._detect_duplicate_rows(
            df
        )

        assert result == []

    def test_should_return_no_duplicate_issues_for_empty_dataframe(self):

        df = pd.DataFrame()

        result = self.service._detect_duplicate_rows(
            df
        )

        assert result == []


    def test_should_detect_low_duplicate_percentage(self):

        df = pd.DataFrame({
            "id": [
                1, 2, 3, 4, 5,
                6, 7, 8, 9, 9
            ],
            "value": [
                "A", "B", "C", "D", "E",
                "F", "G", "H", "I", "I"
            ]
        })

        result = self.service._detect_duplicate_rows(
            df
        )

        assert len(result) == 1

        issue = result[0]

        assert issue["affectedRows"] == 1
        assert issue["affectedPercentage"] == 10.0
        assert issue["severity"] == "MEDIUM"

    def test_should_detect_infinite_numeric_values(self):

        df = pd.DataFrame({
            "age": [
                22,
                23,
                float("inf"),
                25,
                float("-inf")
            ]
        })

        result = self.service._detect_invalid_values(
            df
        )

        assert len(result) == 1

        issue = result[0]

        assert issue["issueType"] == "INVALID_VALUES"
        assert issue["column"] == "age"
        assert issue["affectedRows"] == 2
        assert issue["affectedPercentage"] == 40.0
        assert issue["severity"] == "HIGH"

    def test_should_ignore_non_numeric_columns(self):

        df = pd.DataFrame({
            "name": [
                "Hariom",
                "Rahul",
                "Ankit"
            ]
        })

        result = self.service._detect_invalid_values(
            df
        )

        assert result == []

    def test_should_not_report_valid_numeric_values(self):

        df = pd.DataFrame({
            "age": [
                22,
                23,
                24,
                25
            ]
        })

        result = self.service._detect_invalid_values(
            df
        )

        assert result == []

    def test_should_return_no_invalid_value_issues_for_empty_dataframe(self):

        df = pd.DataFrame()

        result = self.service._detect_invalid_values(
            df
        )

        assert result == []

    def test_should_detect_mixed_data_types(self):

        df = pd.DataFrame({
            "age": [
                22,
                "23",
                24,
                "25",
                26
            ]
        })

        result = self.service._detect_type_problems(df)

        assert len(result) == 1

        issue = result[0]

        assert issue["issueType"] == "TYPE_PROBLEM"
        assert issue["column"] == "age"
        assert issue["affectedRows"] == 2
        assert issue["affectedPercentage"] == 40.0
        assert issue["severity"] == "HIGH"

    def test_should_not_report_consistent_string_column(self):

        df = pd.DataFrame({
            "name": [
                "Hariom",
                "Rahul",
                "Ankit"
            ]
        })

        result = self.service._detect_type_problems(df)

        assert result == []

    def test_should_not_report_consistent_numeric_column(self):

        df = pd.DataFrame({
            "age": [
                22,
                23,
                24,
                25
            ]
        })

        result = self.service._detect_type_problems(df)

        assert result == []

    def test_should_detect_outliers_using_iqr(self):

        df = pd.DataFrame({
            "age": [
                20,
                21,
                22,
                23,
                24,
                100
            ]
        })

        result = self.service._detect_outliers(df)

        assert len(result) == 1

        issue = result[0]

        assert issue["issueType"] == "OUTLIERS"
        assert issue["column"] == "age"
        assert issue["affectedRows"] == 1
        assert issue["affectedPercentage"] == 16.67
        assert issue["severity"] == "MEDIUM"

    def test_should_not_report_normal_numeric_values_as_outliers(self):

        df = pd.DataFrame({
            "age": [
                20,
                21,
                22,
                23,
                24
            ]
        })

        result = self.service._detect_outliers(df)

        assert result == []

    def test_should_ignore_non_numeric_columns_for_outliers(self):

        df = pd.DataFrame({
            "name": [
                "Hariom",
                "Rahul",
                "Ankit",
                "Aman"
            ]
        })

        result = self.service._detect_outliers(df)

        assert result == []

    def test_should_detect_categorical_inconsistencies(self):

        df = pd.DataFrame({
            "city": [
                "Delhi",
                "delhi",
                "DELHI",
                "Mumbai",
                "Mumbai"
            ]
        })

        result = self.service._detect_categorical_inconsistencies(df)

        assert len(result) == 1

        issue = result[0]

        assert issue["issueType"] == "CATEGORICAL_INCONSISTENCY"
        assert issue["column"] == "city"
        assert issue["affectedRows"] == 3
        assert issue["affectedPercentage"] == 60.0
        assert issue["severity"] == "HIGH"

    def test_should_not_report_consistent_categorical_values(self):

        df = pd.DataFrame({
            "city": [
                "Delhi",
                "Mumbai",
                "Kolkata",
                "Chennai"
            ]
        })

        result = self.service._detect_categorical_inconsistencies(df)

        assert result == []

    def test_should_ignore_numeric_columns_for_categorical_inconsistencies(self):

        df = pd.DataFrame({
            "age": [
                20,
                21,
                22,
                23
            ]
        })

        result = self.service._detect_categorical_inconsistencies(df)

        assert result == []

    def test_should_detect_constant_feature(self):

        df = pd.DataFrame({
            "country": [
                "India",
                "India",
                "India",
                "India"
            ]
        })

        result = self.service._detect_constant_features(df)

        assert len(result) == 1

        issue = result[0]

        assert issue["issueType"] == "CONSTANT_FEATURE"
        assert issue["column"] == "country"
        assert issue["affectedRows"] == 4
        assert issue["affectedPercentage"] == 100.0
        assert issue["severity"] == "MEDIUM"

    def test_should_not_report_non_constant_feature(self):

        df = pd.DataFrame({
            "age": [
                20,
                21,
                22,
                23
            ]
        })

        result = self.service._detect_constant_features(df)

        assert result == []

    def test_should_detect_constant_feature_with_missing_values(self):

        df = pd.DataFrame({
            "country": [
                "India",
                "India",
                None,
                "India"
            ]
        })

        result = self.service._detect_constant_features(df)

        assert len(result) == 1

        issue = result[0]

        assert issue["column"] == "country"
        assert issue["affectedRows"] == 4
        assert issue["affectedPercentage"] == 100.0

    def test_should_detect_multiple_constant_features(self):

        df = pd.DataFrame({
            "country": [
                "India",
                "India",
                "India"
            ],
            "gender": [
                "Male",
                "Male",
                "Male"
            ],
            "age": [
                20,
                21,
                22
            ]
        })

        result = self.service._detect_constant_features(df)

        assert len(result) == 2

        columns = {
            issue["column"]
            for issue in result
        }

        assert columns == {
            "country",
            "gender"
        }


    def test_should_detect_near_constant_feature(self):

        df = pd.DataFrame({
            "country": (
                ["India"] * 19
                + ["USA"]
            )
        })

        result = self.service._detect_near_constant_features(df)

        assert len(result) == 1

        issue = result[0]

        assert issue["issueType"] == "NEAR_CONSTANT_FEATURE"
        assert issue["column"] == "country"
        assert issue["affectedRows"] == 19
        assert issue["affectedPercentage"] == 95.0
        assert issue["severity"] == "MEDIUM"

    
    def test_should_not_report_normal_feature_as_near_constant(self):

        df = pd.DataFrame({
            "city": [
                "Delhi",
                "Mumbai",
                "Kolkata",
                "Chennai",
                "Pune"
            ]
        })

        result = self.service._detect_near_constant_features(df)

        assert result == []

    def test_should_not_report_constant_feature_as_near_constant(self):

        df = pd.DataFrame({
            "country": [
                "India",
                "India",
                "India",
                "India"
            ]
        })

        result = self.service._detect_near_constant_features(df)

        assert result == []

    def test_should_detect_numeric_near_constant_feature(self):

        df = pd.DataFrame({
            "status": [
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                0
            ]
        })

        result = self.service._detect_near_constant_features(df)

        assert len(result) == 1

        issue = result[0]

        assert issue["column"] == "status"
        assert issue["affectedRows"] == 19
        assert issue["affectedPercentage"] == 95.0


    def test_should_detect_high_cardinality_categorical(self):

        df = pd.DataFrame({
            "customer_id": [
                f"C{i}"
                for i in range(60)
            ]
        })

        result = self.service._detect_high_cardinality_categoricals(df)

        assert len(result) == 1

        issue = result[0]

        assert issue["issueType"] == "HIGH_CARDINALITY"
        assert issue["column"] == "customer_id"
        assert issue["affectedRows"] == 60
        assert issue["affectedPercentage"] == 100.0
        assert issue["severity"] == "HIGH"

    def test_should_detect_high_cardinality_based_on_unique_percentage(self):

        df = pd.DataFrame({
            "code": [
                f"C{i}"
                for i in range(60)
            ] + [
                "A",
                "A",
                "A",
                "A",
                "A",
                "A",
                "A",
                "A",
                "A",
                "A"
            ]
        })

        result = self.service._detect_high_cardinality_categoricals(df)

        assert len(result) == 1

        issue = result[0]

        assert issue["column"] == "code"
        assert issue["affectedRows"] == 61
        assert issue["affectedPercentage"] == 87.14
        assert issue["severity"] == "HIGH"

    def test_should_assess_complete_dataset_quality(self):

        df = pd.DataFrame({
            "age": [
                20,
                21,
                None,
                23,
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

        result = self.service.assess_quality(df)

        assert result["totalRows"] == 5
        assert result["totalColumns"] == 3

        assert result["issueCount"] > 0

        assert isinstance(
            result["issues"],
            list
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

        result = self.service.assess_quality(df)

        assert result["totalRows"] == 5
        assert result["totalColumns"] == 2
        assert result["issueCount"] == 0
        assert result["issues"] == []

    def test_should_combine_multiple_issue_types(self):

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

        result = self.service.assess_quality(df)

        issue_types = {
            issue["issueType"]
            for issue in result["issues"]
        }

        assert "MISSING_VALUES" in issue_types
        assert "INVALID_VALUES" in issue_types
        assert "CATEGORICAL_INCONSISTENCY" in issue_types
        assert "CONSTANT_FEATURE" in issue_types


    def test_should_ignore_infinite_values_when_detecting_outliers(self):

        df = pd.DataFrame({
            "age": [
                20,
                21,
                22,
                23,
                float("inf")
            ]
        })

        result = self.service._detect_outliers(df)

        assert result == []

            
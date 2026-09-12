import pytest

from app.services.cleaning.cleaning_recommendation_service import (
    DataCleaningRecommendationService
)


class TestDataCleaningRecommendationService:

        def setup_method(self):

            self.service = (
                DataCleaningRecommendationService()
            )

        def test_should_generate_missing_value_recommendation(self):

            issues = [
                {
                    "issueType": "MISSING_VALUES",
                    "column": "age",
                    "severity": "MEDIUM"
                }
            ]

            result = self.service.generate_recommendations(
                issues
            )

            assert len(result) == 1

            recommendation = result[0]

            assert recommendation["issueType"] == "MISSING_VALUES"
            assert recommendation["column"] == "age"
            assert recommendation["severity"] == "MEDIUM"
            assert recommendation["operation"] == "IMPUTE_MISSING_VALUES"
            assert "impute" in recommendation["recommendation"].lower()

        def test_should_generate_duplicate_row_recommendation(self):

            issues = [
                {
                    "issueType": "DUPLICATE_ROWS",
                    "column": None,
                    "severity": "HIGH"
                }
            ]

            result = self.service.generate_recommendations(
                issues
            )

            assert len(result) == 1

            recommendation = result[0]

            assert recommendation["issueType"] == "DUPLICATE_ROWS"
            assert recommendation["column"] is None
            assert recommendation["operation"] == "REMOVE_DUPLICATES"
            assert "duplicate" in recommendation["recommendation"].lower()

        def test_should_generate_invalid_value_recommendation(self):

            issues = [
                {
                    "issueType": "INVALID_VALUES",
                    "column": "salary",
                    "severity": "LOW"
                }
            ]

            result = self.service.generate_recommendations(
                issues
            )

            assert len(result) == 1

            recommendation = result[0]

            assert recommendation["issueType"] == "INVALID_VALUES"
            assert recommendation["column"] == "salary"
            assert recommendation["operation"] == "REPLACE_INVALID_VALUES"
            assert "invalid" in recommendation["recommendation"].lower()

        def test_should_generate_type_problem_recommendation(self):

            issues = [
                {
                    "issueType": "TYPE_PROBLEM",
                    "column": "age",
                    "severity": "MEDIUM"
                }
            ]

            result = self.service.generate_recommendations(
                issues
            )

            assert len(result) == 1

            recommendation = result[0]

            assert recommendation["issueType"] == "TYPE_PROBLEM"
            assert recommendation["column"] == "age"
            assert recommendation["operation"] == "CONVERT_DATA_TYPE"
            assert "data type" in recommendation["recommendation"]

        def test_should_generate_outlier_recommendation(self):

            issues = [
                {
                    "issueType": "OUTLIERS",
                    "column": "income",
                    "severity": "LOW"
                }
            ]

            result = self.service.generate_recommendations(
                issues
            )

            assert len(result) == 1

            recommendation = result[0]

            assert recommendation["issueType"] == "OUTLIERS"
            assert recommendation["column"] == "income"
            assert recommendation["operation"] == "REVIEW_OUTLIERS"
            assert "outlier" in recommendation["recommendation"].lower()

        def test_should_generate_categorical_recommendation(self):

            issues = [
                {
                    "issueType": "CATEGORICAL_INCONSISTENCY",
                    "column": "city",
                    "severity": "MEDIUM"
                }
            ]

            result = self.service.generate_recommendations(
                issues
            )

            assert len(result) == 1

            recommendation = result[0]

            assert (
                recommendation["issueType"]
                == "CATEGORICAL_INCONSISTENCY"
            )

            assert recommendation["column"] == "city"
            assert recommendation["operation"] == "NORMALIZE_CATEGORIES"

            assert (
                "standardize"
                in recommendation["recommendation"].lower()
            )

        def test_should_generate_constant_feature_recommendation(self):

            issues = [
                {
                    "issueType": "CONSTANT_FEATURE",
                    "column": "country",
                    "severity": "MEDIUM"
                }
            ]

            result = self.service.generate_recommendations(
                issues
            )

            assert len(result) == 1

            recommendation = result[0]

            assert (
                recommendation["issueType"]
                == "CONSTANT_FEATURE"
            )

            assert recommendation["column"] == "country"
            assert recommendation["operation"] == "REMOVE_FEATURE"

            assert (
                "removing"
                in recommendation["recommendation"].lower()
            )

        def test_should_generate_near_constant_recommendation(self):

            issues = [
                {
                    "issueType": "NEAR_CONSTANT_FEATURE",
                    "column": "status",
                    "severity": "MEDIUM"
                }
            ]

            result = self.service.generate_recommendations(
                issues
            )

            assert len(result) == 1

            recommendation = result[0]

            assert (
                recommendation["issueType"]
                == "NEAR_CONSTANT_FEATURE"
            )

            assert recommendation["column"] == "status"

            assert recommendation["operation"] == "REVIEW_FEATURE"

            assert (
                "removing"
                in recommendation["recommendation"].lower()
            )

        def test_should_generate_high_cardinality_recommendation(self):

            issues = [
                {
                    "issueType": "HIGH_CARDINALITY",
                    "column": "customer_id",
                    "severity": "HIGH"
                }
            ]

            result = self.service.generate_recommendations(
                issues
            )

            assert len(result) == 1

            recommendation = result[0]

            assert (
                recommendation["issueType"]
                == "HIGH_CARDINALITY"
            )

            assert recommendation["column"] == "customer_id"
            assert recommendation["operation"] == "REVIEW_CARDINALITY"

            assert (
                "encoding"
                in recommendation["recommendation"].lower()
            )

        def test_should_generate_multiple_recommendations(self):

            issues = [
                {
                    "issueType": "MISSING_VALUES",
                    "column": "age",
                    "severity": "MEDIUM"
                },
                {
                    "issueType": "OUTLIERS",
                    "column": "income",
                    "severity": "LOW"
                },
                {
                    "issueType": "CONSTANT_FEATURE",
                    "column": "country",
                    "severity": "MEDIUM"
                }
            ]

            result = self.service.generate_recommendations(
                issues
            )

            assert len(result) == 3

            issue_types = {
                item["issueType"]
                for item in result
            }

            assert issue_types == {
                "MISSING_VALUES",
                "OUTLIERS",
                "CONSTANT_FEATURE"
            }

        def test_should_return_review_issue_for_unknown_issue_type(self):

            issues = [
                {
                    "issueType": "UNKNOWN_ISSUE",
                    "column": "test",
                    "severity": "LOW"
                }
            ]

            result = self.service.generate_recommendations(
                issues
            )

            assert len(result) == 1

            recommendation = result[0]

            assert recommendation["operation"] == "REVIEW_ISSUE"
class DataCleaningRecommendationService:

    def generate_recommendations(
            self,
            issues: list
    ) -> list:

        recommendations = []

        for issue in issues:

            issue_type = issue.get("issueType")

            recommendation = self._build_recommendation(
                issue_type
            )

            operation = self._get_operation(issue_type)

            recommendations.append({
                "issueType": issue_type,
                "column": issue.get("column"),
                "severity": issue.get("severity"),
                "operation": operation,
                "recommendation": recommendation
            })

        return recommendations

    def _build_recommendation(
            self,
            issue_type: str
    ) -> str:

        recommendations = {

            "MISSING_VALUES": (
                "Impute missing values using the median "
                "for numeric columns or the mode for "
                "categorical columns"
            ),

            "DUPLICATE_ROWS": (
                "Review duplicate rows and remove them "
                "if they do not represent legitimate "
                "repeated observations"
            ),

            "INVALID_VALUES": (
                "Review invalid values and replace them "
                "with an appropriate value or treat them "
                "as missing values"
            ),

            "TYPE_PROBLEM": (
                "Review the column data type and convert "
                "values to the appropriate data type"
            ),

            "OUTLIERS": (
                "Review outliers and determine whether "
                "they represent valid observations before "
                "removing or transforming them"
            ),

            "CATEGORICAL_INCONSISTENCY": (
                "Standardize inconsistent categorical values "
                "using a consistent representation"
            ),

            "CONSTANT_FEATURE": (
                "Review the feature and consider removing it "
                "because it provides no meaningful variation"
            ),

            "NEAR_CONSTANT_FEATURE": (
                "Review the feature and consider removing it "
                "if the limited variation does not provide "
                "meaningful analytical or predictive value"
            ),

            "HIGH_CARDINALITY": (
                "Review the feature and consider reducing, "
                "grouping, or encoding categories appropriately"
            )
        }

        return recommendations.get(
            issue_type,
            "Review the detected data-quality issue "
            "and determine an appropriate cleaning strategy"
        )

    def _get_operation(
            self,
            issue_type: str
    ) -> str:

        operations = {

            "MISSING_VALUES":
                "IMPUTE_MISSING_VALUES",

            "DUPLICATE_ROWS":
                "REMOVE_DUPLICATES",

            "INVALID_VALUES":
                "REPLACE_INVALID_VALUES",

            "TYPE_PROBLEM":
                "CONVERT_DATA_TYPE",

            "OUTLIERS":
                "REVIEW_OUTLIERS",

            "CATEGORICAL_INCONSISTENCY":
                "NORMALIZE_CATEGORIES",

            "CONSTANT_FEATURE":
                "REMOVE_FEATURE",

            "NEAR_CONSTANT_FEATURE":
                "REVIEW_FEATURE",

            "HIGH_CARDINALITY":
                "REVIEW_CARDINALITY"
        }

        return operations.get(
            issue_type,
            "REVIEW_ISSUE"
        )
import pandas as pd


class DataCleaningChangeTracker:

    def track(
            self,
            before: pd.DataFrame,
            after: pd.DataFrame,
            operation: str,
            column: str | None = None
    ) -> dict:

        rows_before = len(before)
        rows_after = len(after)

        columns_before = len(before.columns)
        columns_after = len(after.columns)

        if operation == "REMOVE_DUPLICATES":

            rows_affected = (
                rows_before - rows_after
            )

            return {
                "operation": operation,
                "column": None,
                "rowsAffected": rows_affected,
                "details": (
                    f"{rows_affected} duplicate rows removed"
                )
            }

        if operation == "REMOVE_FEATURE":

            return {
                "operation": operation,
                "column": column,
                "rowsAffected": rows_before,
                "details": (
                    f"Feature '{column}' removed"
                )
            }

        if operation == "IMPUTE_MISSING_VALUES":

            if column is None:
                raise ValueError(
                    "Column is required for "
                    "missing-value tracking"
                )

            missing_before = int(
                before[column].isna().sum()
            )

            missing_after = int(
                after[column].isna().sum()
            )

            rows_affected = (
                missing_before - missing_after
            )

            return {
                "operation": operation,
                "column": column,
                "rowsAffected": rows_affected,
                "details": (
                    f"{rows_affected} missing values "
                    "imputed"
                )
            }

        if operation == "REPLACE_INVALID_VALUES":

            if column is None:
                raise ValueError(
                    "Column is required for "
                    "invalid-value tracking"
                )

            invalid_before = int(
                before[column]
                .isin([
                    float("inf"),
                    float("-inf")
                ])
                .sum()
            )

            invalid_after = int(
                after[column]
                .isin([
                    float("inf"),
                    float("-inf")
                ])
                .sum()
            )

            rows_affected = (
                invalid_before - invalid_after
            )

            return {
                "operation": operation,
                "column": column,
                "rowsAffected": rows_affected,
                "details": (
                    f"{rows_affected} invalid values "
                    f"replaced"
                )
            }

        if operation == "NORMALIZE_CATEGORIES":

            if column is None:
                raise ValueError(
                    "Column is required for "
                    "category normalization tracking"
                )

            before_values = (
                before[column]
                .astype("string")
            )

            after_values = (
                after[column]
                .astype("string")
            )

            changed = (
                before_values
                != after_values
            )

            rows_affected = int(
                changed.fillna(False).sum()
            )

            return {
                "operation": operation,
                "column": column,
                "rowsAffected": rows_affected,
                "details": (
                    f"{rows_affected} categorical "
                    f"values normalized"
                )
            }

        return {
            "operation": operation,
            "column": column,
            "rowsAffected": 0,
            "details": (
                "No direct change tracking "
                "available for this operation"
            )
        }
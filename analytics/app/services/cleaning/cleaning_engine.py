import pandas as pd 

class DataCleaningEngine:

    def apply_operation(
            self,
            df:pd.DataFrame,
            operation: str,
            column: str | None = None,
            parameters: dict | None = None
    )-> pd.DataFrame:

        cleaned_df = df.copy()
        parameters = parameters or {}

        if operation == "REMOVE_DUPLICATES":
            return self._remove_duplicates(
                cleaned_df
            )

        if operation == "REPLACE_INVALID_VALUES":
            return self._replace_invalid_values(
                cleaned_df,
                column
            )

        if operation == "IMPUTE_MISSING_VALUES":
            return self._impute_missing_values(
                cleaned_df,
                column,
                parameters
            )

        if operation == "NORMALIZE_CATEGORIES":
            return self._normalize_categories(
                cleaned_df,
                column,
                parameters
            )

        if operation == "REMOVE_FEATURE":
            return self._remove_feature(
                cleaned_df,
                column
            )

        if operation in (
            "REVIEW_OUTLIERS",
            "REVIEW_FEATURE",
            "REVIEW_CARDINALITY"
        ):
            raise ValueError(
                f"Operation '{operation}' "
                "requires explicit review and "
                "cannot be applied automatically"
            )

        raise ValueError(
            f"Unsupported cleaning operation: "
            f"{operation}"
        )

    def _remove_duplicates(
            self,
            df:pd.DataFrame
    )-> pd.DataFrame:

        return df.drop_duplicates(
            ignore_index=True
        )

    def _replace_invalid_values(
            self,
            df: pd.DataFrame,
            column: str | None
    )-> pd.DataFrame:

        if column is None:
            numeric_columns = df.select_dtypes(include="number").columns

            for current_column in numeric_columns:

                df[current_column] = (
                    df[current_column]
                    .replace([float("inf"), float("-inf")],pd.NA)
                )

            return df

        if column not in df.columns:
            raise ValueError(
                f"Column '{column}' not found"
            )

        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError(
                f"Column '{column}' must be numeric"
            )

        df[column] = (
            df[column].replace(
                [float("inf"), float("-inf")],
                pd.NA
            )
        )

        return df

    def _impute_missing_values(
            self,
            df: pd.DataFrame,
            column: str | None,
            parameters: dict
    ) -> pd.DataFrame:

        if column is None:
            raise ValueError(
                "Column is required for "
                "missing-value imputation"
            )

        if column not in df.columns:
            raise ValueError(
                f"Column '{column}' not found"
            )

        strategy = parameters.get("strategy", "AUTO")
        is_numeric = pd.api.types.is_numeric_dtype(df[column])
        if strategy == "AUTO":
            strategy = "MEDIAN" if is_numeric else "MODE"

        if strategy == "CONSTANT":
            value = parameters["value"]
            if is_numeric:
                try:
                    value = float(value)
                except (TypeError, ValueError) as error:
                    raise ValueError("CONSTANT imputation requires a numeric value for this column") from error
        elif strategy == "MEDIAN":
            if not is_numeric:
                raise ValueError("MEDIAN imputation requires a numeric column")
            value = df[column].median()
        elif strategy == "MEAN":
            if not is_numeric:
                raise ValueError("MEAN imputation requires a numeric column")
            value = df[column].mean()
        elif strategy == "MODE":
            mode = df[column].mode()

            if mode.empty:
                raise ValueError(
                    f"Cannot determine an imputation "
                    f"value for column '{column}'"
                )

            value = mode.iloc[0]
        else:
            raise ValueError(f"Unsupported imputation strategy: {strategy}")

        df[column] = df[column].fillna(value)

        return df

    def _normalize_categories(
            self,
            df: pd.DataFrame,
            column: str | None,
            parameters: dict
    ) -> pd.DataFrame:

        if column is None:
            raise ValueError(
                "Column is required for "
                "category normalization"
            )

        if column not in df.columns:
            raise ValueError(
                f"Column '{column}' not found"
            )

        if not (
            pd.api.types.is_object_dtype(
                df[column]
            )
            or pd.api.types.is_string_dtype(
                df[column]
            )
        ):
            raise ValueError(
                f"Column '{column}' must be "
                "categorical or string"
            )

        values = df[column].astype("string")
        if parameters.get("trim", True):
            values = values.str.strip()
        if parameters.get("lowercase", True):
            values = values.str.lower()
        df[column] = values

        return df

    def _remove_feature(
            self,
            df: pd.DataFrame,
            column: str | None
    ) -> pd.DataFrame:

        if column is None:
            raise ValueError(
                "Column is required for "
                "feature removal"
            )

        if column not in df.columns:
            raise ValueError(
                f"Column '{column}' not found"
            )

        return df.drop(
            columns=[column]
        )

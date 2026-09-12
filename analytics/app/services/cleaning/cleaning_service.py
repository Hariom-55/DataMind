import pandas as pd 

class DataCleaningService:

    def _detect_missing_values(
            self, 
         df: pd.DataFrame
        )-> list:

        issues = []

        total_rows = len(df)

        if total_rows == 0:
            return issues

        for column in df.columns :
            missing_count = int(
                df[column].isna().sum()
            )

            if missing_count == 0:
                continue

            missing_percentage = (missing_count / total_rows) * 100

            if missing_percentage >= 50:
                severity = "HIGH"
            elif missing_percentage >=20 :
                severity = "MEDIUM"
            else:
                severity = "LOW"

            issues.append({
                "issueType": "MISSING_VALUES",
                "column": column,
                "severity": severity,
                "affectedRows": missing_count,
                "affectedPercentage": round(
                    float(missing_percentage), 2
                ),
                "description": (
                    "Column contains missing Values"
                ),

                "recommendation":(
                    "Review Missing values and "
                    "apply an appropriate imputation "
                    "or removal strategy"
                )
            })

        return issues

    def _detect_duplicate_rows(
            self,
            df: pd.DataFrame
    )-> list:

        total_rows = len(df)

        if total_rows == 0:
            return []

        duplicate_count = int(
            df.duplicated().sum()
        )

        if duplicate_count == 0:
            return []

        duplicate_percentage = (duplicate_count /total_rows) * 100

        if duplicate_percentage >= 20 :
            severity = "HIGH"

        elif duplicate_percentage >= 5 :
            severity = "MEDIUM"

        else:
            severity = "LOW"

        return [
            {
                "issueType":"DUPLICATE_ROWS",
                "column":None,
                "severity": severity,
                "affectedRows": duplicate_count,
                "affectedPercentage": round(
                    float(duplicate_percentage), 2
                ),
                "description": (
                    "Dataset contains duplicate rows"
                ),
                "recommendation": (
                    "Review duplicate rows and remove "
                    "then if they do not represent "
                    "legitimate repeated observations"
                )
            }
        ]

    def _detect_invalid_values(
            self,
            df: pd.DataFrame
    ) -> list:

        issues = []

        total_rows = len(df)

        if total_rows == 0:
            return issues

        for column in df.columns:

            if not pd.api.types.is_numeric_dtype(
                    df[column]
            ):
                continue

            invalid_count = int(
                df[column].isin([
                    float("inf"),
                    float("-inf")
                ]).sum()
            )

            if invalid_count == 0:
                continue

            invalid_percentage = (
                invalid_count / total_rows
            ) * 100

            if invalid_percentage >= 20:
                severity = "HIGH"

            elif invalid_percentage >= 5:
                severity = "MEDIUM"

            else:
                severity = "LOW"

            issues.append({
                "issueType": "INVALID_VALUES",
                "column": column,
                "severity": severity,
                "affectedRows": invalid_count,
                "affectedPercentage": round(
                    float(invalid_percentage),
                    2
                ),
                "description": (
                    "Column contains infinite numeric values"
                ),
                "recommendation": (
                    "Review infinite values and replace "
                    "them with an appropriate value or "
                    "treat them as missing values"
                )
            })

        return issues

    def _detect_type_problems(
            self,
            df: pd.DataFrame
    ) -> list:

        issues = []

        total_rows = len(df)

        if total_rows == 0:
            return issues

        for column in df.columns:

            series = df[column]

            # Only object/string columns need
            # generic mixed-type inspection.
            if not (
                pd.api.types.is_object_dtype(series)
                or pd.api.types.is_string_dtype(series)
            ):
                continue

            non_null_values = series.dropna()

            if len(non_null_values) == 0:
                continue

            type_counts = (
                non_null_values
                .map(type)
                .value_counts()
            )

            if len(type_counts) <= 1:
                continue

            affected_rows = int(
                sum(
                    non_null_values.map(type)
                    != non_null_values.map(type).mode()[0]
                )
            )

            affected_percentage = (
                affected_rows / total_rows
            ) * 100

            if affected_percentage >= 20:
                severity = "HIGH"
            elif affected_percentage >= 5:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            issues.append({
                "issueType": "TYPE_PROBLEM",
                "column": column,
                "severity": severity,
                "affectedRows": affected_rows,
                "affectedPercentage": round(
                    float(affected_percentage),
                    2
                ),
                "description": (
                    "Column contains values with "
                    "inconsistent data types"
                ),
                "recommendation": (
                    "Review the column and convert "
                    "values to a consistent data type"
                )
            })

        return issues

    def _detect_outliers(
            self,
            df: pd.DataFrame
    ) -> list:

        issues = []

        total_rows = len(df)

        if total_rows == 0:
            return issues

        for column in df.columns:

            if not pd.api.types.is_numeric_dtype(
                    df[column]
            ):
                continue

            series = df[column].dropna()

            series = series[
                ~series.isin([
                    float("inf"),
                    float("-inf")
                ])
            ]

            if len(series) < 4:
                continue

            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)

            iqr = q3 - q1

            if iqr == 0:
                continue

            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)

            outlier_mask = (
                (series < lower_bound)
                | (series > upper_bound)
            )

            outlier_count = int(
                outlier_mask.sum()
            )

            if outlier_count == 0:
                continue

            outlier_percentage = (
                outlier_count / total_rows
            ) * 100

            if outlier_percentage >= 20:
                severity = "HIGH"
            elif outlier_percentage >= 5:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            issues.append({
                "issueType": "OUTLIERS",
                "column": column,
                "severity": severity,
                "affectedRows": outlier_count,
                "affectedPercentage": round(
                    float(outlier_percentage),
                    2
                ),
                "description": (
                    "Column contains statistical "
                    "outliers based on the IQR method"
                ),
                "recommendation": (
                    "Review detected outliers and "
                    "determine whether they represent "
                    "valid observations, data errors, "
                    "or values requiring transformation"
                )
            })

        return issues

    def _detect_categorical_inconsistencies(
            self,
            df: pd.DataFrame
    ) -> list:

        issues = []

        total_rows = len(df)

        if total_rows == 0:
            return issues

        for column in df.columns:

            series = df[column]

            if not (
                pd.api.types.is_object_dtype(series)
                or pd.api.types.is_string_dtype(series)
            ):
                continue

            values = series.dropna()

            if values.empty:
                continue

            normalized_values = (
                values
                .astype(str)
                .str.strip()
                .str.lower()
            )

            original_unique = values.nunique()

            normalized_unique = normalized_values.nunique()

            if normalized_unique >= original_unique:
                continue

            affected_rows = int(
                values.groupby(
                    normalized_values
                ).transform("nunique").gt(1).sum()
            )

            if affected_rows == 0:
                continue

            affected_percentage = (
                affected_rows / total_rows
            ) * 100

            if affected_percentage >= 20:
                severity = "HIGH"
            elif affected_percentage >= 5:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            issues.append({
                "issueType": "CATEGORICAL_INCONSISTENCY",
                "column": column,
                "severity": severity,
                "affectedRows": affected_rows,
                "affectedPercentage": round(
                    float(affected_percentage),
                    2
                ),
                "description": (
                    "Categorical column contains values "
                    "that differ only by casing or "
                    "surrounding whitespace"
                ),
                "recommendation": (
                    "Normalize categorical values by "
                    "trimming whitespace and applying "
                    "consistent casing where appropriate"
                )
            })

        return issues


    def _detect_constant_features(
            self,
            df: pd.DataFrame
    ) -> list:

        issues = []

        total_rows = len(df)

        if total_rows == 0:
            return issues

        for column in df.columns:

            series = df[column].dropna()

            if series.empty:
                continue

            unique_count = series.nunique(
                dropna=True
            )

            if unique_count != 1:
                continue

            issues.append({
                "issueType": "CONSTANT_FEATURE",
                "column": column,
                "severity": "MEDIUM",
                "affectedRows": total_rows,
                "affectedPercentage": 100.0,
                "description": (
                    "Column contains only one unique "
                    "value and provides no variation"
                ),
                "recommendation": (
                    "Consider removing the column "
                    "if it does not provide meaningful "
                    "business or analytical information"
                )
            })

        return issues

    def _detect_near_constant_features(
            self,
            df: pd.DataFrame
    ) -> list:

        issues = []

        total_rows = len(df)

        if total_rows == 0:
            return issues

        for column in df.columns:

            series = df[column].dropna()

            if series.empty:
                continue

            unique_count = series.nunique(
                dropna=True
            )

           
            if unique_count <= 1:
                continue

            value_counts = series.value_counts()

            dominant_count = int(
                value_counts.iloc[0]
            )

            dominant_percentage = (
                dominant_count / len(series)
            ) * 100

            # Near-constant threshold
            if dominant_percentage < 95:
                continue

            affected_percentage = (
                dominant_count / total_rows
            ) * 100

            if affected_percentage >= 99:
                severity = "HIGH"
            elif affected_percentage >= 95:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            issues.append({
                "issueType": "NEAR_CONSTANT_FEATURE",
                "column": column,
                "severity": severity,
                "affectedRows": dominant_count,
                "affectedPercentage": round(
                    float(affected_percentage),
                    2
                ),
                "description": (
                    "Column is dominated by a single "
                    "value and contains very little "
                    "variation"
                ),
                "recommendation": (
                    "Review the feature and consider "
                    "removing it if the limited variation "
                    "does not provide meaningful "
                    "analytical or predictive value"
                )
            })

        return issues

    def _detect_high_cardinality_categoricals(
            self,
            df: pd.DataFrame
    ) -> list:

        issues = []

        total_rows = len(df)

        if total_rows == 0:
            return issues

        for column in df.columns:

            series = df[column].dropna()

            if series.empty:
                continue

            if not (
                pd.api.types.is_object_dtype(series)
                or pd.api.types.is_string_dtype(series)
                or isinstance(series.dtype, pd.CategoricalDtype)
            ):
                continue

            unique_count = series.nunique()

            unique_percentage = (
                unique_count / len(series)
            ) * 100

            if not (
                unique_count > 50
                or (
                    unique_count >= 10
                    and unique_percentage >= 50
                )
            ):
                continue

            affected_rows = unique_count

            affected_percentage = (
                unique_percentage
            )

            if unique_percentage >= 80:
                severity = "HIGH"
            elif unique_percentage >= 50:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            issues.append({
                "issueType": "HIGH_CARDINALITY",
                "column": column,
                "severity": severity,
                "affectedRows": affected_rows,
                "affectedPercentage": round(
                    float(affected_percentage),
                    2
                ),
                "description": (
                    "Categorical column contains a "
                    "large number of unique values "
                    "relative to the dataset"
                ),
                "recommendation": (
                    "Review whether the column represents "
                    "an identifier or high-cardinality "
                    "feature and consider grouping, "
                    "encoding, or excluding it from "
                    "one-hot encoding"
                )
            })

        return issues

    def assess_quality(
            self,
            df: pd.DataFrame
    ) -> dict:

        issues = []

        issues.extend(
            self._detect_missing_values(df)
        )

        issues.extend(
            self._detect_duplicate_rows(df)
        )

        issues.extend(
            self._detect_invalid_values(df)
        )

        issues.extend(
            self._detect_type_problems(df)
        )

        issues.extend(
            self._detect_outliers(df)
        )

        issues.extend(
            self._detect_categorical_inconsistencies(df)
        )

        issues.extend(
            self._detect_constant_features(df)
        )

        issues.extend(
            self._detect_near_constant_features(df)
        )

        issues.extend(
            self._detect_high_cardinality_categoricals(df)
        )

        return {
            "totalRows": len(df),
            "totalColumns": len(df.columns),
            "issueCount": len(issues),
            "issues": issues
        }
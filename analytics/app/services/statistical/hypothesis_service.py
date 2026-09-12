import pandas as pd
from scipy.stats import ttest_1samp, ttest_ind, ttest_rel, chi2_contingency

from app.services.common.stat_utils import safe_float


class HypothesisTestingService:

    def perform_one_sample_t_test(
        self,
        df: pd.DataFrame,
        column: str,
        reference_value: float,
        alpha: float = 0.05
    ) -> dict:

        
        if not 0 < alpha < 1:
            raise ValueError("alpha must be between 0 and 1")

        
        if column not in df.columns:
            raise ValueError(f"Column not found: {column}")

       
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError(f"Column '{column}' must be numeric")

        
        values = df[column].dropna()

       
        if len(values) < 2:
            raise ValueError(
                "One-sample t-test requires at least 2 observations"
            )

        
        test_result = ttest_1samp(
            values,
            reference_value
        )

        test_statistic = safe_float(
            test_result.statistic
        )

        p_value = safe_float(
            test_result.pvalue
        )

        if p_value is None:
            raise ValueError(
                "One-Sample t-test produced an undefined p-value"
            )

     
        significant = p_value < alpha

        decision = (
            "REJECT_NULL"
            if significant
            else "FAIL_TO_REJECT_NULL"
        )

        
        return {
            "test": "ONE_SAMPLE_T_TEST",
            "column": column,
            "referenceValue": safe_float(
                reference_value
            ),
            "sampleSize": int(len(values)),
            "testStatistic": test_statistic,
            "pValue": p_value,
            "alpha": safe_float(alpha),
            "significant": significant,
            "decision": decision,
            "nullHypothesis": (
                f"The population mean equals {reference_value}"
            ),
            "alternativeHypothesis": (
                f"The population mean is different from {reference_value}"
            ),
            "interpretation": (
                "There is sufficient evidence to reject the null hypothesis."
                if significant
                else
                "There is insufficient evidence to reject the null hypothesis."
            )
        }

    def perform_independent_t_test(
        self,
        df: pd.DataFrame,
        value_column: str,
        group_column: str,
        alpha: float = 0.05
    ) -> dict:

        # 1. Validate alpha
        if not 0 < alpha < 1:
            raise ValueError("alpha must be between 0 and 1")

        # 2. Validate value column
        if value_column not in df.columns:
            raise ValueError(
                f"Column not found: {value_column}"
            )

        # 3. Validate group column
        if group_column not in df.columns:
            raise ValueError(
                f"Column not found: {group_column}"
            )

        # 4. Validate value column is numeric
        if not pd.api.types.is_numeric_dtype(df[value_column]):
            raise ValueError(
                f"Column '{value_column}' must be numeric"
            )

        test_data = df[
            [value_column, group_column]
        ].dropna()


        groups = test_data[group_column].unique()

        if len(groups) != 2:
            raise ValueError(
                "Independent t-test requires exactly two groups"
            )

        group1 = groups[0]
        group2 = groups[1]

        # 7. Extract observations for each group

        value_series = test_data[value_column]
        group1_values = value_series[
            test_data[group_column] == group1
        ]
        
        group2_values = value_series[
            test_data[group_column] == group2
        ]

        # 8. Validate sample sizes
        if len(group1_values) < 2 or len(group2_values) < 2:
            raise ValueError(
                "Each group requires at least 2 observations"
            )

        # 9. Validate variance
        if (
            group1_values.nunique() == 1
            and group2_values.nunique() == 1
        ):
            raise ValueError(
                "Independent t-test produced an undefined p-value"
            )

        # 10. Perform Welch's independent t-test
        test_result = ttest_ind(
            group1_values,
            group2_values,
            equal_var=False
        )

        test_statistic = safe_float(
            test_result.statistic
        )

        p_value = safe_float(
            test_result.pvalue
        )

        # 11. Validate statistical result
        if p_value is None:
            raise ValueError(
                "Independent t-test produced an undefined p-value"
            )

        # 12. Statistical decision
        significant = p_value < alpha

        decision = (
            "REJECT_NULL"
            if significant
            else "FAIL_TO_REJECT_NULL"
        )

        # 13. Return structured result
        return {
            "test": "INDEPENDENT_T_TEST",
            "valueColumn": value_column,
            "groupColumn": group_column,
            "groups": [
                group1,
                group2
            ],
            "sampleSizes": {
                str(group1): int(len(group1_values)),
                str(group2): int(len(group2_values))
            },
            "testStatistic": test_statistic,
            "pValue": p_value,
            "alpha": safe_float(alpha),
            "significant": significant,
            "decision": decision,
            "nullHypothesis": (
                "The means of the two groups are equal"
            ),
            "alternativeHypothesis": (
                "The means of the two groups are different"
            ),
            "interpretation": (
                "There is sufficient evidence to reject "
                "the null hypothesis."
                if significant
                else
                "There is insufficient evidence to reject "
                "the null hypothesis."
            )
        } 

    def perform_paired_t_test(
        self,
        df: pd.DataFrame,
        column1: str,
        column2: str,
        alpha: float = 0.05
    ) -> dict:

        # 1. Validate alpha
        if not 0 < alpha < 1:
            raise ValueError("alpha must be between 0 and 1")

        # 2. Validate columns
        if column1 not in df.columns:
            raise ValueError(
                f"Column not found: {column1}"
            )

        if column2 not in df.columns:
            raise ValueError(
                f"Column not found: {column2}"
            )

        # 3. Validate numeric columns
        if not pd.api.types.is_numeric_dtype(df[column1]):
            raise ValueError(
                f"Column '{column1}' must be numeric"
            )

        if not pd.api.types.is_numeric_dtype(df[column2]):
            raise ValueError(
                f"Column '{column2}' must be numeric"
            )

        # 4. Keep complete pairs only
        paired_data = df[
            [column1, column2]
        ].dropna()

        # 5. Validate number of paired observations
        if len(paired_data) < 2:
            raise ValueError(
                "Paired t-test requires at least 2 paired observations"
            )

        # 6. Calculate paired differences
        differences = (
            paired_data[column2]
            - paired_data[column1]
        )

        # 7. Validate variance of differences
        if differences.nunique() == 1:
            if differences.iloc[0] == 0:
                raise ValueError(
                    "Paired t-test produced an undefined p-value"
                )

        # 8. Perform paired t-test
        test_result = ttest_rel(
            paired_data[column1],
            paired_data[column2]
        )

        test_statistic = safe_float(
            test_result.statistic
        )

        p_value = safe_float(
            test_result.pvalue
        )

        # 9. Validate statistical result
        if p_value is None:
            raise ValueError(
                "Paired t-test produced an undefined p-value"
            )

        # 10. Statistical decision
        significant = p_value < alpha

        decision = (
            "REJECT_NULL"
            if significant
            else "FAIL_TO_REJECT_NULL"
        )

        # 11. Return structured result
        return {
            "test": "PAIRED_T_TEST",
            "column1": column1,
            "column2": column2,
            "sampleSize": int(len(paired_data)),
            "testStatistic": test_statistic,
            "pValue": p_value,
            "alpha": safe_float(alpha),
            "significant": significant,
            "decision": decision,
            "nullHypothesis": (
                "The mean difference between the paired "
                "measurements is zero"
            ),
            "alternativeHypothesis": (
                "The mean difference between the paired "
                "measurements is not zero"
            ),
            "interpretation": (
                "There is sufficient evidence to reject "
                "the null hypothesis."
                if significant
                else
                "There is insufficient evidence to reject "
                "the null hypothesis."
            )
        }   

    def perform_chi_square_test(
        self,
        df: pd.DataFrame,
        column1: str,
        column2: str,
        alpha: float = 0.05
    ) -> dict:
        if not 0 < alpha < 1:
            raise ValueError("alpha must be between 0 and 1")

        if column1 not in df.columns:
            raise ValueError(f"Column not found: {column1}")

        if column2 not in df.columns:
            raise ValueError(f"Column not found: {column2}")

        test_data = df[[column1, column2]].dropna()

        if len(test_data) < 2:
            raise ValueError(
                "Chi-square test requires at least 2 observations"
            )

        if test_data[column1].nunique() < 2:
            raise ValueError(
                "Chi-square test requires at least two categories"
            )

        if test_data[column2].nunique() < 2:
            raise ValueError(
                "Chi-square test requires at least two categories"
            )

        contingency_table = pd.crosstab(
            test_data[column1],
            test_data[column2]
        )

        test_statistic, p_value, degrees_of_freedom, _ = chi2_contingency(
            contingency_table
        )

        test_statistic = safe_float(test_statistic)
        p_value = safe_float(p_value)

        if p_value is None:
            raise ValueError(
                "Chi-square test produced an undefined p-value"
            )

        significant = p_value < alpha

        decision = (
            "REJECT_NULL"
            if significant
            else "FAIL_TO_REJECT_NULL"
        )

        return {
            "test": "CHI_SQUARE_INDEPENDENCE",
            "column1": column1,
            "column2": column2,
            "sampleSize": int(len(test_data)),
            "degreesOfFreedom": int(degrees_of_freedom),
            "testStatistic": test_statistic,
            "pValue": p_value,
            "alpha": safe_float(alpha),
            "significant": significant,
            "decision": decision,
            "nullHypothesis": (
                "The two categorical variables are independent"
            ),
            "alternativeHypothesis": (
                "The two categorical variables are associated"
            ),
            "interpretation": (
                "There is sufficient evidence to reject "
                "the null hypothesis."
                if significant
                else
                "There is insufficient evidence to reject "
                "the null hypothesis."
            )
        }


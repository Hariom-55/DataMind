import pandas as pd 
from scipy.stats import ttest_1samp, ttest_ind, ttest_rel, chi2_contingency

from app.loaders.dataset_loader import DatasetLoader
from app.services.analysis_service import AnalysisService
class StatisticalAnalysisService(AnalysisService):

    def __init__(self, dataset_loader: DatasetLoader):
        self.dataset_loader = dataset_loader
        
    def analyze(self, dataset_path: str, file_type: str | None = None, target_column: str | None = None) -> dict :
        #1.Load Dataset
        df = self.dataset_loader.load(dataset_path, file_type=file_type)

        #2.Select numerical columns
        numeric_df = df.select_dtypes(include="number")

        descriptive_statistics = {}

        if not numeric_df.empty:
            for column in numeric_df.columns:

                series = numeric_df[column]

                q1 = series.quantile(0.25)
                q2 = series.quantile(0.50)
                q3 = series.quantile(0.75)

                mode = series.mode()

                descriptive_statistics[column] = {
                    "count": int(series.count()),

                    "missingCount": int(series.isna().sum()),

                    "missingPercentage": self._safe_float(
                        series.isna().mean() * 100
                    ),

                    "mean": self._safe_float(series.mean()),

                    "median": self._safe_float(q2),

                    "mode": (
                        self._safe_float(mode.iloc[0])
                        if not mode.empty
                        else None
                    ),

                    "std": self._safe_float(series.std()),

                    "variance": self._safe_float(series.var()),

                    "min": self._safe_float(series.min()),

                    "max": self._safe_float(series.max()),

                    "range": self._safe_float(
                        series.max() - series.min()
                    ),

                    "25%": self._safe_float(q1),

                    "50%": self._safe_float(q2),

                    "75%": self._safe_float(q3),

                    "IQR": self._safe_float(
                        q3 - q1
                    ),

                    "skewness": self._safe_float(series.skew()),

                    "kurtosis": self._safe_float(series.kurtosis())
                }


        #3. Correlation matrices 
        pearson_correlation = {}
        spearman_correlation = {}

        if len(numeric_df.columns) >= 2:

            pearson_correlation = self._correlation_to_dict(
                numeric_df.corr(method="pearson")
            )

            spearman_correlation = self._correlation_to_dict(
                numeric_df.corr(method="spearman")
            )

        correlation_analysis = {
            "pearson" : self._analyze_correlations(pearson_correlation),
            "spearman" : self._analyze_correlations(spearman_correlation)
        }

        return {
            "descriptiveStatistics": descriptive_statistics,
            "correlations": {
                "pearson" : pearson_correlation,
                "spearman" : spearman_correlation
            },
            "correlationAnalysis": correlation_analysis
        }

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

        test_statistic = self._safe_float(
            test_result.statistic
        )

        p_value = self._safe_float(
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
            "referenceValue": self._safe_float(
                reference_value
            ),
            "sampleSize": int(len(values)),
            "testStatistic": test_statistic,
            "pValue": p_value,
            "alpha": self._safe_float(alpha),
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

        test_statistic = self._safe_float(
            test_result.statistic
        )

        p_value = self._safe_float(
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
            "alpha": self._safe_float(alpha),
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

        test_statistic = self._safe_float(
            test_result.statistic
        )

        p_value = self._safe_float(
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
            "alpha": self._safe_float(alpha),
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

        test_statistic = self._safe_float(test_statistic)
        p_value = self._safe_float(p_value)

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
            "alpha": self._safe_float(alpha),
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

    @staticmethod 
    def _safe_float(value):

        if pd.isna(value):
            return None

        return float(value)

    @staticmethod
    def _correlation_to_dict(correlation_df):

        result = {}

        for column in correlation_df.columns:

            result[column] = {
                other_column: (
                    None
                    if pd.isna(value)
                    else float(value)
                )
                for other_column, value in
                correlation_df[column].items()
            }

        return result

    @staticmethod
    def _analyze_correlations(correlation_dict):

        if not correlation_dict:
            return {
                "pairs" : [],
                "strongest": []
            }
        
        pairs = []

        columns = list(correlation_dict.keys())

        for i in range(len(columns)):
            column1 = columns[i]

            for j in range(i + 1, len(columns)):
                column2 = columns[j]

                correlation = correlation_dict[column1][column2]

                if correlation is None:
                    continue

                pairs.append({
                    "column1": column1,
                    "column2": column2,
                    "correlation": correlation,
                    "strength": StatisticalAnalysisService._correlation_strength(
                        correlation
                    ),
                    "direction": StatisticalAnalysisService._correlation_direction(
                        correlation
                    )
                    })

        strongest = sorted(
            pairs,
            key=lambda pair: abs(pair["correlation"]),
            reverse=True
        )

        return {
            "pairs": pairs,
            "strongest": strongest
        }


    @staticmethod
    def _correlation_strength(correlation):
        absolute_correlation = abs(correlation)

        if absolute_correlation < 0.20:
            return "VERY_WEAK"

        if absolute_correlation < 0.40:
            return "WEAK"

        if absolute_correlation < 0.60:
            return "MODERATE"

        if absolute_correlation < 0.80:
            return "STRONG"

        return "VERY_STRONG"


    @staticmethod
    def _correlation_direction(correlation):
        if correlation > 0:
            return "POSITIVE"

        if correlation < 0:
            return "NEGATIVE"

        return "NONE"
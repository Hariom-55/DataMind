import pandas as pd
from scipy.stats import shapiro

from app.services.common.stat_utils import safe_float


class DistributionAnalysisService:

    SYMMETRY_THRESHOLD = 0.5
    KURTOSIS_THRESHOLD = 0.5

    MIN_NORMALITY_SAMPLE_SIZE = 3
    MAX_SHAPIRO_SAMPLE_SIZE = 5000

    DEFAULT_ALPHA = 0.05

    def __init__(self):
        pass

    def analyze(
        self,
        numeric_df: pd.DataFrame,
        alpha: float = DEFAULT_ALPHA
    ) -> dict:

        self._validate_alpha(alpha)

        distributions = {}

        if numeric_df.empty:
            return {
                "distributions": distributions
            }

        for column in numeric_df.columns:

            if not pd.api.types.is_numeric_dtype(
                numeric_df[column]
            ):
                continue

            distributions[column] = (
                self._analyze_column(
                    numeric_df[column],
                    alpha
                )
            )

        return {
            "distributions": distributions
        }

    def _analyze_column(
        self,
        series: pd.Series,
        alpha: float
    ) -> dict:

        values = series.dropna()

        sample_size = len(values)

        result = {
            "sampleSize": int(sample_size),
            "isConstant": False,
            "skewness": None,
            "kurtosis": None,
            "shape": None,
            "tailBehavior": None,
            "normality": None
        }

        if sample_size == 0:
            result["normality"] = {
                "available": False,
                "test": "SHAPIRO_WILK",
                "reason": "NO_VALID_OBSERVATIONS"
            }

            return result

        if values.nunique() == 1:

            result["isConstant"] = True
            result["shape"] = "CONSTANT"

            result["normality"] = {
                "available": False,
                "test": "SHAPIRO_WILK",
                "reason": "CONSTANT_DATA"
            }

            return result

        skewness = safe_float(
            values.skew()
        )

        kurtosis = safe_float(
            values.kurtosis()
        )

        result["skewness"] = skewness
        result["kurtosis"] = kurtosis

        result["shape"] = self._classify_shape(
            skewness
        )

        result["tailBehavior"] = self._classify_tail_behavior(
            kurtosis
        )

        result["normality"] = self._normality_analysis(
            values,
            alpha
        )

        return result

    @classmethod
    def _classify_shape(
        cls,
        skewness: float | None
    ) -> str | None:

        if skewness is None:
            return None

        if abs(skewness) <= cls.SYMMETRY_THRESHOLD:
            return "APPROXIMATELY_SYMMETRIC"

        if skewness > cls.SYMMETRY_THRESHOLD:
            return "RIGHT_SKEWED"

        return "LEFT_SKEWED"

    @classmethod
    def _classify_tail_behavior(
        cls,
        kurtosis: float | None
    ) -> str | None:

        if kurtosis is None:
            return None

        if kurtosis < -cls.KURTOSIS_THRESHOLD:
            return "LIGHT_TAILED"

        if kurtosis > cls.KURTOSIS_THRESHOLD:
            return "HEAVY_TAILED"

        return "NORMAL_LIKE_TAILS"

    def _normality_analysis(
        self,
        values: pd.Series,
        alpha: float
    ) -> dict:

        sample_size = len(values)

        if sample_size < self.MIN_NORMALITY_SAMPLE_SIZE:

            return {
                "available": False,
                "test": "SHAPIRO_WILK",
                "reason": "INSUFFICIENT_OBSERVATIONS"
            }

        if sample_size > self.MAX_SHAPIRO_SAMPLE_SIZE:

            return {
                "available": False,
                "test": "SHAPIRO_WILK",
                "reason": "SAMPLE_SIZE_EXCEEDS_SHAPIRO_LIMIT"
            }

        test_result = shapiro(values)

        statistic = safe_float(
            test_result.statistic
        )

        p_value = safe_float(
            test_result.pvalue
        )

        if p_value is None:

            return {
                "available": False,
                "test": "SHAPIRO_WILK",
                "reason": "UNDEFINED_P_VALUE"
            }

        significant = p_value < alpha

        decision = (
            "REJECT_NULL"
            if significant
            else
            "FAIL_TO_REJECT_NULL"
        )

        return {
            "available": True,
            "test": "SHAPIRO_WILK",
            "statistic": statistic,
            "pValue": p_value,
            "alpha": safe_float(alpha),
            "significant": significant,
            "decision": decision
        }

    @staticmethod
    def _validate_alpha(alpha: float) -> None:

        if not 0 < alpha < 1:
            raise ValueError(
                "alpha must be between 0 and 1"
            )
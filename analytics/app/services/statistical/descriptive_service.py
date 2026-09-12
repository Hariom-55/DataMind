import pandas as pd

from app.services.common.stat_utils import safe_float


class DescriptiveStatisticsService:

    def calculate(self, numeric_df: pd.DataFrame) -> dict:

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

                    "missingPercentage": safe_float(
                        series.isna().mean() * 100
                    ),

                    "mean": safe_float(series.mean()),

                    "median": safe_float(q2),

                    "mode": (
                        safe_float(mode.iloc[0])
                        if not mode.empty
                        else None
                    ),

                    "std": safe_float(series.std()),

                    "variance": safe_float(series.var()),

                    "min": safe_float(series.min()),

                    "max": safe_float(series.max()),

                    "range": safe_float(
                        series.max() - series.min()
                    ),

                    "25%": safe_float(q1),

                    "50%": safe_float(q2),

                    "75%": safe_float(q3),

                    "IQR": safe_float(
                        q3 - q1
                    ),

                    "skewness": safe_float(series.skew()),

                    "kurtosis": safe_float(series.kurtosis())
                }

        return descriptive_statistics

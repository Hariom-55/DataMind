import pandas as pd 
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
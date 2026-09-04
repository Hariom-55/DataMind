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

                descriptive_statistics[column] = {
                    "count": int(series.count()),
                    "mean": self._safe_float(series.mean()),
                    "median":self._safe_float(series.median()),
                    "std": self._safe_float(series.std()),
                    "variance": self._safe_float(series.var()),
                    "min": self._safe_float(series.min()),
                    "max": self._safe_float(series.max()),
                    "25%": self._safe_float(series.quantile(0.25)),
                    "50%": self._safe_float(series.quantile(0.50)),
                    "75%": self._safe_float(series.quantile(0.75)),
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

        return {
            "descriptiveStatistics": descriptive_statistics,
            "correlations": {
                "pearson" : pearson_correlation,
                "spearman" : spearman_correlation
            }
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
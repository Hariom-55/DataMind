import pandas as pd
import numpy as np

from app.loaders.dataset_loader import DatasetLoader
from app.core.analysis_service import AnalysisService
from app.services.profiling.data_quality_service import DataQualityService


class EDAService(AnalysisService):
    CONTRACT_VERSION = "v1"

    def __init__(
        self,
        dataset_loader: DatasetLoader,
        data_quality_service: DataQualityService,
    ):
        self.dataset_loader = dataset_loader
        self.data_quality_service = data_quality_service

    def analyze(
        self,
        dataset_path: str,
        file_type: str | None = None,
        target_column: str | None = None,
    ) -> dict:
        df = self.dataset_loader.load(dataset_path, file_type=file_type)

        row_count = int(df.shape[0])
        column_count = int(df.shape[1])
        numeric_df = df.select_dtypes(include="number")
        categorical_df = df.select_dtypes(include=["object", "category", "bool"])

        columns = list(df.columns)
        data_types = {
            column: (
                "str" if pd.api.types.is_object_dtype(dtype) else str(dtype)
            )
            for column, dtype in df.dtypes.items()
        }

        missing_values = {
            column: int(count)
            for column, count in df.isnull().sum().items()
        }
        missing_percentages = {
            column: float(round((count / row_count) * 100, 2))
            if row_count > 0 else 0.0
            for column, count in df.isnull().sum().items()
        }
        unique_value_counts = {
            column: int(df[column].nunique(dropna=True))
            for column in df.columns
        }
        duplicate_rows = int(df.duplicated().sum())
        data_quality = self.data_quality_service.analyze(df, duplicate_rows)
        data_quality["constantColumns"] = [
            column
            for column in df.columns
            if df[column].nunique(dropna=True) == 1
        ]
        cardinality_threshold = 0.5
        data_quality["highCardinalityThreshold"] = cardinality_threshold
        data_quality["highCardinalityColumns"] = [
            {
                "column": column,
                "uniqueCount": unique_value_counts[column],
                "cardinalityRatio": round(unique_value_counts[column] / row_count, 4),
            }
            for column in categorical_df.columns
            if row_count
            and unique_value_counts[column] >= 20
            and unique_value_counts[column] / row_count >= cardinality_threshold
        ]

        numeric_statistics = {}
        if not numeric_df.empty:
            statistics = numeric_df.describe()
            numeric_statistics = {
                column: {
                    metric: float(value)
                    for metric, value in statistics[column].items()
                    if pd.notna(value)
                }
                for column in numeric_df.columns
            }

        categorical_statistics = {}
        for column in categorical_df.columns:
            all_value_counts = df[column].value_counts(dropna=False)
            value_counts = all_value_counts.head(10)
            top_values = {
                str(value): int(count)
                for value, count in value_counts.items()
            }
            categorical_statistics[column] = {
                "uniqueCount": int(df[column].nunique(dropna=True)),
                "topValues": top_values,
                "rareValues": {
                    str(value): int(count)
                    for value, count in all_value_counts.items()
                    if count == 1 and pd.notna(value)
                },
                "missingCount": int(df[column].isna().sum()),
                "cardinalityRatio": (
                    float(round(df[column].nunique(dropna=True) / row_count, 4))
                    if row_count else 0.0
                ),
            }

        outlier_signals = self._outlier_signals(numeric_df)
        numeric_histograms = self._numeric_histograms(numeric_df)
        correlation = self._correlation(numeric_df)

        schema = [
            {
                "name": column,
                "dtype": data_types[column],
                "role": (
                    "numeric"
                    if column in numeric_df.columns
                    else "categorical"
                    if column in categorical_df.columns
                    else "other"
                ),
                "missingCount": missing_values[column],
                "missingPercentage": missing_percentages[column],
                "uniqueCount": unique_value_counts[column],
            }
            for column in columns
        ]

        overview = {
            "rowCount": row_count,
            "columnCount": column_count,
            "numericColumnCount": int(numeric_df.shape[1]),
            "categoricalColumnCount": int(categorical_df.shape[1]),
        }

        return {
            "contractVersion": self.CONTRACT_VERSION,
            "overview": overview,
            "columns": columns,
            "schema": schema,
            "dataTypes": data_types,
            "missingValues": missing_values,
            "missingPercentages": missing_percentages,
            "uniqueValueCounts": unique_value_counts,
            "duplicateRows": duplicate_rows,
            "numericStatistics": numeric_statistics,
            "categoricalStatistics": categorical_statistics,
            "outlierSignals": outlier_signals,
            "numericHistograms": numeric_histograms,
            "correlation": correlation,
            "dataQuality": data_quality,
        }

    @staticmethod
    def _numeric_histograms(numeric_df: pd.DataFrame) -> dict:
        result = {}
        for column in numeric_df.columns:
            series = pd.to_numeric(numeric_df[column], errors="coerce").dropna()
            if len(series) < 2 or float(series.min()) == float(series.max()):
                continue

            counts, edges = np.histogram(series.to_numpy(), bins="auto")
            bins = []
            for index, count in enumerate(counts):
                bins.append({
                    "bin": index + 1,
                    "lower": float(round(edges[index], 6)),
                    "upper": float(round(edges[index + 1], 6)),
                    "count": int(count),
                })
            result[column] = bins
        return result

    @staticmethod
    def _outlier_signals(numeric_df: pd.DataFrame) -> dict:
        result = {}
        for column in numeric_df.columns:
            series = pd.to_numeric(numeric_df[column], errors="coerce").dropna()
            if series.empty:
                continue

            q1 = float(series.quantile(0.25))
            q3 = float(series.quantile(0.75))
            iqr = q3 - q1

            if iqr == 0:
                lower = q1
                upper = q3
            else:
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
            count = int(((series < lower) | (series > upper)).sum())

            result[column] = {
                "method": "IQR",
                "lowerBound": lower,
                "upperBound": upper,
                "outlierCount": count,
                "outlierPercentage": float(round((count / len(series)) * 100, 2)),
            }
        return result

    @staticmethod
    def _correlation(numeric_df: pd.DataFrame) -> dict:
        if numeric_df.shape[1] < 2:
            return {
                "available": False,
                "method": "pearson",
                "matrix": {},
            }

        matrix = numeric_df.corr(method="pearson").replace(
            [np.inf, -np.inf], np.nan
        ).round(6).fillna(0.0)

        return {
            "available": True,
            "method": "pearson",
            "columns": list(matrix.columns),
            "matrix": matrix.to_dict(),
        }

import math

import pandas as pd

from app.services.visualization.visualization_generator import VisualizationGenerator
from app.services.visualization.visualization_spec import VisualizationSpec
from app.services.visualization.visualization_types import VisualizationType


class EDAVisualizationGenerator(VisualizationGenerator):

    def generate(self, analysis_results: dict) -> list[dict]:
        if not isinstance(analysis_results, dict):
            raise ValueError("analysis_results must be a dictionary")

        visualizations = []
        visualizations.extend(self._generate_missing_values_visualization(analysis_results))
        visualizations.extend(self._generate_numeric_visualizations(analysis_results))
        visualizations.extend(self._generate_categorical_visualizations(analysis_results))
        visualizations.extend(self._generate_correlation_visualization(analysis_results))
        return visualizations

    def _generate_missing_values_visualization(self, analysis_results: dict) -> list[dict]:
        missing_values = analysis_results.get("missingValues", {})
        missing_percentages = analysis_results.get("missingPercentages", {})
        if not missing_values:
            return []

        data = [
            {
                "column": column,
                "missingCount": int(count),
                "missingPercentage": float(missing_percentages.get(column, 0.0)),
            }
            for column, count in missing_values.items()
        ]

        if not data:
            return []

        return [VisualizationSpec(
            type=VisualizationType.BAR,
            title="Missing Values by Column",
            description="Number and percentage of missing values for each column.",
            x="column",
            y="missingCount",
            data=data,
            metadata={"source": "EDA", "metric": "missingValues"},
        ).to_dict()]

    def _generate_numeric_visualizations(self, analysis_results: dict) -> list[dict]:
        numeric_statistics = analysis_results.get("numericStatistics", {})
        visualizations = []

        for column, stats in numeric_statistics.items():
            minimum = stats.get("min")
            maximum = stats.get("max")

            histogram_data = analysis_results.get("numericHistograms", {}).get(column, [])
            histogram_x = "bin"
            histogram_y = "count"

            if not histogram_data:
                # Backward-compatible contract: a statistics-only caller
                # receives the original metadata specification. A full EDA
                # result includes numericHistograms and renders real bins.
                histogram_x = column
                histogram_y = None
                histogram_data = []

            visualizations.append(
                VisualizationSpec(
                    type=VisualizationType.HISTOGRAM,
                    title=f"{column.title()} Distribution",
                    description=f"Distribution of values in {column}.",
                    x=histogram_x,
                    y=histogram_y,
                    data=histogram_data,
                    metadata={
                        "source": "EDA",
                        "column": column,
                        "statistics": stats,
                    },
                ).to_dict()
            )

            outlier = analysis_results.get("outlierSignals", {}).get(column)
            if outlier:
                visualizations.append(
                    VisualizationSpec(
                        type=VisualizationType.BOX_PLOT,
                        title=f"{column.title()} Outlier Profile",
                        description=f"IQR-based outlier boundaries for {column}.",
                        data=[{
                            "column": column,
                            "min": minimum,
                            "q1": stats.get("25%"),
                            "median": stats.get("50%"),
                            "q3": stats.get("75%"),
                            "max": maximum,
                            "lowerBound": outlier.get("lowerBound"),
                            "upperBound": outlier.get("upperBound"),
                        }],
                        metadata={
                            "source": "EDA",
                            "metric": "outlierSignals",
                        },
                    ).to_dict()
                )

        return visualizations

    def _generate_categorical_visualizations(self, analysis_results: dict) -> list[dict]:
        categorical_statistics = analysis_results.get("categoricalStatistics", {})
        visualizations = []

        for column, statistics in categorical_statistics.items():
            top_values = statistics.get("topValues", {})
            if not top_values:
                continue

            data = [
                {"value": str(value), "count": int(count)}
                for value, count in top_values.items()
            ]

            visualizations.append(
                VisualizationSpec(
                    type=VisualizationType.BAR,
                    title=f"Top Values for {column.title()}",
                    description=f"Most frequent values in {column}.",
                    x="value",
                    y="count",
                    data=data,
                    metadata={
                        "source": "EDA",
                        "column": column,
                        "uniqueCount": statistics.get("uniqueCount", 0),
                    },
                ).to_dict()
            )

        return visualizations

    def _generate_correlation_visualization(self, analysis_results: dict) -> list[dict]:
        correlation = analysis_results.get("correlation", {})
        if not correlation.get("available"):
            return []

        matrix = correlation.get("matrix", {})
        columns = correlation.get("columns", [])
        data = []
        for row in columns:
            values = matrix.get(row, {})
            row_data = {"row": row}
            for column in columns:
                row_data[column] = values.get(column)
            data.append(row_data)

        return [VisualizationSpec(
            type=VisualizationType.HEATMAP,
            title="EDA Correlation Overview",
            description="Pearson correlation matrix for numerical variables.",
            data=data,
            metadata={"source": "EDA", "metric": "correlation", "columns": columns},
        ).to_dict()]

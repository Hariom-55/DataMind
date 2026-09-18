from app.services.visualization.visualization_generator import VisualizationGenerator
from app.services.visualization.visualization_spec import VisualizationSpec
from app.services.visualization.visualization_types import VisualizationType



class EDAVisualizationGenerator(VisualizationGenerator):

    def generate(
        self,
        analysis_results: dict
    ) -> list[dict]:

        if not isinstance(analysis_results, dict):
            raise ValueError(
                "analysis_results must be a dictionary"
            )

        visualizations: list[dict] = []

        visualizations.extend(
            self._generate_missing_values_visualization(
                analysis_results
            )
        )

        visualizations.extend(
            self._generate_numeric_visualizations(
                analysis_results
            )
        )

        visualizations.extend(
            self._generate_categorical_visualizations(
                analysis_results
            )
        )

        return visualizations

    def _generate_missing_values_visualization(
        self,
        analysis_results: dict
    ) -> list[dict]:

        missing_values = analysis_results.get(
            "missingValues",
            {}
        )

        missing_percentages = analysis_results.get(
            "missingPercentages",
            {}
        )

        if not missing_values:
            return []

        data = [
            {
                "column": column,
                "missingCount": int(count),
                "missingPercentage": float(
                    missing_percentages.get(column, 0.0)
                ),
            }
            for column, count in missing_values.items()
        ]

        spec = VisualizationSpec(
            type=VisualizationType.BAR,
            title="Missing Values by Column",
            description="Number and percentage of missing values for each column.",
            x="column",
            y="missingCount",
            data=data,
            metadata={
                "source": "EDA",
                "metric": "missingValues",
            },
        )

        return [spec.to_dict()]

    def _generate_numeric_visualizations(
        self,
        analysis_results: dict
    ) -> list[dict]:

        numeric_statistics = analysis_results.get(
            "numericStatistics",
            {}
        )

        visualizations = []

        for column in numeric_statistics:

            spec = VisualizationSpec(
                type=VisualizationType.HISTOGRAM,
                title=f"{column.title()} Distribution",
                description=f"Distribution of values in {column}.",
                x=column,
                data=[],
                metadata={
                    "source": "EDA",
                    "column": column,
                    "statistics": numeric_statistics[column],
                },
            )

            visualizations.append(
                spec.to_dict()
            )

        return visualizations

    def _generate_categorical_visualizations(
        self,
        analysis_results: dict
    ) -> list[dict]:

        categorical_statistics = analysis_results.get(
            "categoricalStatistics",
            {}
        )

        visualizations = []

        for column, statistics in categorical_statistics.items():

            top_values = statistics.get(
                "topValues",
                {}
            )

            if not top_values:
                continue

            data = [
                {
                    "value": str(value),
                    "count": int(count),
                }
                for value, count in top_values.items()
            ]

            spec = VisualizationSpec(
                type=VisualizationType.BAR,
                title=f"Top Values for {column.title()}",
                description=(
                    f"Most frequent values in {column}."
                ),
                x="value",
                y="count",
                data=data,
                metadata={
                    "source": "EDA",
                    "column": column,
                    "uniqueCount": statistics.get(
                        "uniqueCount",
                        0
                    ),
                },
            )

            visualizations.append(
                spec.to_dict()
            )

        return visualizations
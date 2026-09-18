from app.services.visualization.visualization_generator import VisualizationGenerator
from app.services.visualization.visualization_spec import VisualizationSpec
from app.services.visualization.visualization_types import VisualizationType


class StatisticalVisualizationGenerator(VisualizationGenerator):

    def generate(
        self,
        analysis_results: dict
    ) -> list[dict]:

        if not isinstance(analysis_results, dict):
            raise ValueError(
                "analysis_results must be a dictionary"
            )

        visualizations: list[dict] = []

        correlations = analysis_results.get(
            "correlations",
            {}
        )

        visualizations.extend(
            self._generate_correlation_heatmaps(
                correlations
            )
        )

        return visualizations

    def _generate_correlation_heatmaps(
        self,
        correlations: dict
    ) -> list[dict]:

        visualizations = []

        if not isinstance(correlations, dict):
            return visualizations

        for metric in ("pearson", "spearman"):

            matrix = correlations.get(
                metric,
                {}
            )

            if not matrix:
                continue

            columns = list(matrix.keys())

            data = []

            for row in columns:

                row_data = {
                    "row": row
                }

                values = matrix.get(row, {})

                for column in columns:
                    row_data[column] = values.get(
                        column,
                        None
                    )

                data.append(row_data)

            title = (
                "Pearson Correlation Matrix"
                if metric == "pearson"
                else "Spearman Correlation Matrix"
            )

            spec = VisualizationSpec(
                type=VisualizationType.HEATMAP,
                title=title,
                description=(
                    f"{metric.capitalize()} correlation "
                    "between numerical variables."
                ),
                data=data,
                metadata={
                    "source": "STATISTICS",
                    "metric": metric,
                    "columns": columns,
                },
            )

            visualizations.append(
                spec.to_dict()
            )

        return visualizations
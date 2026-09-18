from app.services.visualization.visualization_generator import VisualizationGenerator
from app.services.visualization.visualization_spec import VisualizationSpec
from app.services.visualization.visualization_types import VisualizationType


class DistributionVisualizationGenerator(VisualizationGenerator):

    def generate(self, analysis_results: dict) -> list[dict]:

        if not isinstance(analysis_results, dict):
            raise ValueError(
                "analysis_results must be a dictionary"
            )

        distributions = analysis_results.get(
            "distributions",
            {}
        )

        if not distributions:
            return []

        data = []

        for column, statistics in distributions.items():

            if not isinstance(statistics, dict):
                continue

            row = {
                "column": column,
                "sampleSize": statistics.get(
                    "sampleSize"
                ),
                "isConstant": statistics.get(
                    "isConstant",
                    False
                ),
                "skewness": statistics.get(
                    "skewness"
                ),
                "kurtosis": statistics.get(
                    "kurtosis"
                ),
                "shape": statistics.get(
                    "shape"
                ),
                "tailBehavior": statistics.get(
                    "tailBehavior"
                ),
            }

            self._add_normality_information(
                row,
                statistics.get("normality")
            )

            data.append(row)

        if not data:
            return []

        spec = VisualizationSpec(
            type=VisualizationType.TABLE,
            title="Distribution Analysis",
            description=(
                "Distribution characteristics and "
                "normality results for numerical variables."
            ),
            data=data,
            metadata={
                "source": "STATISTICS",
                "metric": "distribution",
            },
        )

        return [spec.to_dict()]

    @staticmethod
    def _add_normality_information(
        row: dict,
        normality: dict | None
    ) -> None:

        if not isinstance(normality, dict):

            row["normalityAvailable"] = False
            row["normalityTest"] = None
            row["normalityReason"] = None

            return

        available = normality.get(
            "available",
            False
        )

        row["normalityAvailable"] = bool(
            available
        )

        row["normalityTest"] = normality.get(
            "test"
        )

        if available:

            row["normalityStatistic"] = normality.get(
                "statistic"
            )

            row["normalityPValue"] = normality.get(
                "pValue"
            )

            row["normalityAlpha"] = normality.get(
                "alpha"
            )

            row["normalitySignificant"] = normality.get(
                "significant"
            )

            row["normalityDecision"] = normality.get(
                "decision"
            )

            row["normalityReason"] = None

        else:

            row["normalityStatistic"] = None
            row["normalityPValue"] = None
            row["normalityAlpha"] = None
            row["normalitySignificant"] = None
            row["normalityDecision"] = None

            row["normalityReason"] = normality.get(
                "reason"
            )
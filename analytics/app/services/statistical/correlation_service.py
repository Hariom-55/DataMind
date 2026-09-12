import pandas as pd


class CorrelationService:

    def calculate(self, numeric_df: pd.DataFrame) -> dict:

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
            "pearson": self._analyze_correlations(pearson_correlation),
            "spearman": self._analyze_correlations(spearman_correlation)
        }

        return {
            "pearson": pearson_correlation,
            "spearman": spearman_correlation,
            "correlationAnalysis": correlation_analysis
        }

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
                "pairs": [],
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
                    "strength": CorrelationService._correlation_strength(
                        correlation
                    ),
                    "direction": CorrelationService._correlation_direction(
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

from app.services.insight.insight_generator import (
    InsightGenerator
)


class DataQualityInsightGenerator(InsightGenerator):

    HIGH_MISSING_THRESHOLD = 20.0
    MEDIUM_MISSING_THRESHOLD = 5.0

    HIGH_DUPLICATE_THRESHOLD = 20.0
    MEDIUM_DUPLICATE_THRESHOLD = 5.0

    LOW_QUALITY_SCORE_THRESHOLD = 70.0
    MEDIUM_QUALITY_SCORE_THRESHOLD = 90.0

    def generate(
        self,
        analysis_results: dict
    ) -> list[dict]:

        eda_result = analysis_results.get("eda")

        if not eda_result:
            return []

        insights = []

        insights.extend(
            self._generate_quality_score_insight(
                eda_result
            )
        )

        insights.extend(
            self._generate_missing_value_insights(
                eda_result
            )
        )

        insights.extend(
            self._generate_duplicate_insights(
                eda_result
            )
        )

        return insights

    def _generate_quality_score_insight(
        self,
        eda_result: dict
    ) -> list[dict]:

        data_quality = eda_result.get(
            "dataQuality",
            {}
        )

        score = data_quality.get("score")

        if score is None:
            return []

        if score < self.LOW_QUALITY_SCORE_THRESHOLD:

            return [
                self._build_insight(
                    key="quality-score",
                    severity="HIGH",
                    title="Low data quality score",
                    description=(
                        f"The dataset has a data quality "
                        f"score of {score}."
                    ),
                    evidence={
                        "score": score
                    },
                    recommendation=(
                        "Review missing values, duplicates, "
                        "and other detected data-quality issues "
                        "before downstream analysis."
                    )
                )
            ]

        if score < self.MEDIUM_QUALITY_SCORE_THRESHOLD:

            return [
                self._build_insight(
                    key="quality-score",
                    severity="MEDIUM",
                    title="Data quality requires review",
                    description=(
                        f"The dataset has a data quality "
                        f"score of {score}."
                    ),
                    evidence={
                        "score": score
                    },
                    recommendation=(
                        "Review the dataset quality report "
                        "before relying on downstream results."
                    )
                )
            ]

        return []

    def _generate_missing_value_insights(
        self,
        eda_result: dict
    ) -> list[dict]:

        missing_percentages = eda_result.get(
            "missingPercentages",
            {}
        )

        insights = []

        for column, percentage in (
            missing_percentages.items()
        ):

            if percentage >= self.HIGH_MISSING_THRESHOLD:

                severity = "HIGH"

            elif percentage >= self.MEDIUM_MISSING_THRESHOLD:

                severity = "MEDIUM"

            else:

                continue

            insights.append(
                self._build_insight(
                    key=f"missing-{column}",
                    severity=severity,
                    title=(
                        f"Missing values detected in {column}"
                    ),
                    description=(
                        f"Column '{column}' contains "
                        f"{percentage}% missing values."
                    ),
                    evidence={
                        "column": column,
                        "missingPercentage": percentage
                    },
                    recommendation=(
                        "Review the missing-value pattern "
                        "and select an appropriate handling "
                        "strategy."
                    )
                )
            )

        return insights

    def _generate_duplicate_insights(
        self,
        eda_result: dict
    ) -> list[dict]:

        data_quality = eda_result.get(
            "dataQuality",
            {}
        )

        duplicate_rows = data_quality.get(
            "duplicateRows"
        )

        duplicate_percentage = data_quality.get(
            "duplicatePercentage"
        )

        if duplicate_rows is None:
            return []

        if duplicate_percentage is None:
            return []

        if duplicate_percentage >= (
            self.HIGH_DUPLICATE_THRESHOLD
        ):

            severity = "HIGH"

        elif duplicate_percentage >= (
            self.MEDIUM_DUPLICATE_THRESHOLD
        ):

            severity = "MEDIUM"

        else:

            return []

        return [
            self._build_insight(
                key="duplicate-rows",
                severity=severity,
                title="Duplicate rows detected",
                description=(
                    f"The dataset contains "
                    f"{duplicate_rows} duplicate rows "
                    f"({duplicate_percentage}%)."
                ),
                evidence={
                    "duplicateRows": duplicate_rows,
                    "duplicatePercentage": (
                        duplicate_percentage
                    )
                },
                recommendation=(
                    "Review duplicate rows and determine "
                    "whether they represent legitimate "
                    "observations before removing them."
                )
            )
        ]

    @staticmethod
    def _build_insight(
        key: str,
        severity: str,
        title: str,
        description: str,
        evidence: dict,
        recommendation: str
    ) -> dict:

        return {
            "key": key,
            "category": "DATA_QUALITY",
            "severity": severity,
            "source": "EDA",
            "title": title,
            "description": description,
            "evidence": evidence,
            "recommendation": recommendation
        }
from app.services.insight.data_quality_insight_generator import DataQualityInsightGenerator
from app.services.insight.statistical_insight_generator import StatisticalInsightGenerator
from app.services.insight.ml_insight_generator import MLInsightGenerator


class InsightEngine:

    SEVERITY_ORDER = {
        "HIGH": 0,
        "MEDIUM": 1,
        "LOW": 2,
        "INFO": 3
    }

    def __init__(
        self,
        generators=None
    ):

        self.generators = generators or [
            DataQualityInsightGenerator(),
            StatisticalInsightGenerator(),
            MLInsightGenerator()
        ]

    def generate(
        self,
        analysis_results: dict
    ) -> dict:

        if analysis_results is None:
            analysis_results = {}

        if not isinstance(
            analysis_results,
            dict
        ):
            raise ValueError(
                "analysis_results must be a dictionary"
            )

        insights = []

        for generator in self.generators:

            generated = generator.generate(
                analysis_results
            )

            if generated:
                insights.extend(
                    generated
                )

        insights = self._deduplicate(
            insights
        )

        insights.sort(
            key=lambda insight: (
                self.SEVERITY_ORDER.get(
                    insight["severity"],
                    99
                ),
                insight["category"],
                insight["key"]
            )
        )

        self._assign_ids(
            insights
        )

        return {
            "summary": self._build_summary(
                insights
            ),
            "insights": insights
        }

    @staticmethod
    def _deduplicate(
        insights: list[dict]
    ) -> list[dict]:

        seen = set()
        unique = []

        for insight in insights:

            key = (
                insight.get("category"),
                insight.get("source"),
                insight.get("key")
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(insight)

        return unique

    @staticmethod
    def _assign_ids(
        insights: list[dict]
    ) -> None:

        for index, insight in enumerate(
            insights,
            start=1
        ):

            insight["id"] = (
                f"INSIGHT-{index:03d}"
            )

            insight.pop(
                "key",
                None
            )

    @staticmethod
    def _build_summary(
        insights: list[dict]
    ) -> dict:

        summary = {
            "totalInsights": len(insights),
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0
        }

        for insight in insights:

            severity = (
                insight.get("severity", "")
                .lower()
            )

            if severity in summary:
                summary[severity] += 1

        return summary
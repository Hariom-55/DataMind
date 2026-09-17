from app.services.insight.data_quality_insight_generator import DataQualityInsightGenerator


class TestDataQualityInsightGenerator:

    def setup_method(self):

        self.generator = (
            DataQualityInsightGenerator()
        )

    def test_should_generate_high_missing_value_insight(self):

        results = {
            "eda": {
                "missingPercentages": {
                    "income": 25.0
                }
            }
        }

        insights = self.generator.generate(
            results
        )

        assert len(insights) == 1

        insight = insights[0]

        assert insight["category"] == "DATA_QUALITY"
        assert insight["severity"] == "HIGH"
        assert insight["source"] == "EDA"

        assert insight["evidence"]["column"] == "income"
        assert (
            insight["evidence"]["missingPercentage"]
            == 25.0
        )

    def test_should_generate_medium_missing_value_insight(self):

        results = {
            "eda": {
                "missingPercentages": {
                    "income": 10.0
                }
            }
        }

        insights = self.generator.generate(
            results
        )

        assert len(insights) == 1
        assert insights[0]["severity"] == "MEDIUM"

    def test_should_not_generate_insight_for_low_missing_values(self):

        results = {
            "eda": {
                "missingPercentages": {
                    "income": 2.0
                }
            }
        }

        insights = self.generator.generate(
            results
        )

        assert insights == []

    def test_should_generate_duplicate_row_insight(self):

        results = {
            "eda": {
                "dataQuality": {
                    "duplicateRows": 30,
                    "duplicatePercentage": 25.0
                }
            }
        }

        insights = self.generator.generate(
            results
        )

        assert len(insights) == 1

        assert insights[0]["severity"] == "HIGH"

        assert (
            insights[0]["evidence"]["duplicateRows"]
            == 30
        )

    def test_should_generate_low_quality_score_insight(self):

        results = {
            "eda": {
                "dataQuality": {
                    "score": 65.0
                }
            }
        }

        insights = self.generator.generate(
            results
        )

        assert len(insights) == 1
        assert insights[0]["severity"] == "HIGH"

    def test_should_return_no_insights_without_eda(self):

        insights = self.generator.generate({})

        assert insights == []
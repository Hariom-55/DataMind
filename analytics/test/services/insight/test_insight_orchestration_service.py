from unittest.mock import Mock

from app.services.insight.insight_engine import InsightEngine


from app.services.insight.insight_orchestration_service import InsightOrchestrationService



class TestInsightOrchestrationService:

    def setup_method(self):

        self.eda_service = Mock()

        self.statistical_service = Mock()

        self.ml_service = Mock()

        self.insight_engine = Mock(
            spec=InsightEngine
        )

        self.service = InsightOrchestrationService(
            eda_service=self.eda_service,
            statistical_service=self.statistical_service,
            ml_service=self.ml_service,
            insight_engine=self.insight_engine
        )

        self.eda_result = {
            "overview": {
                "rowCount": 100,
                "columnCount": 5
            },
            "missingPercentages": {},
            "dataQuality": {}
        }

        self.statistical_result = {
            "descriptiveStatistics": {},
            "correlations": {
                "pearson": {},
                "spearman": {}
            },
            "correlationAnalysis": {},
            "distributions": {}
        }

        self.ml_result = {
            "targetColumn": "target",
            "problemType": "CLASSIFICATION",
            "classDistribution": {
                "distribution": {
                    "0": 0.8,
                    "1": 0.2
                },
                "imbalanceDetected": False
            },
            "training": {
                "model": "LogisticRegression",
                "metrics": {
                    "accuracy": 0.85,
                    "precision": 0.84,
                    "recall": 0.83,
                    "f1_score": 0.835
                }
            }
        }

        self.insight_result = {
            "summary": {
                "totalInsights": 1,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 1
            },
            "insights": [
                {
                    "id": "INSIGHT-001",
                    "category": "STATISTICAL",
                    "severity": "INFO",
                    "source": "STATISTICS",
                    "title": "Example insight",
                    "description": "Example description",
                    "evidence": {},
                    "recommendation": "Example recommendation"
                }
            ]
        }

        self.eda_service.analyze.return_value = (
            self.eda_result
        )

        self.statistical_service.analyze.return_value = (
            self.statistical_result
        )

        self.ml_service.analyze.return_value = (
            self.ml_result
        )

        self.insight_engine.generate.return_value = (
            self.insight_result
        )

    def test_should_run_eda_and_statistics_without_target(
        self
    ):

        result = self.service.analyze(
            "dataset.csv"
        )

        self.eda_service.analyze.assert_called_once_with(
            "dataset.csv",
            None,
            None
        )

        self.statistical_service.analyze.assert_called_once_with(
            "dataset.csv",
            None,
            None
        )

        self.ml_service.analyze.assert_not_called()

        self.insight_engine.generate.assert_called_once()

        assert result["insights"] == (
            self.insight_result
        )

    def test_should_run_ml_when_target_is_provided(
        self
    ):

        result = self.service.analyze(
            "dataset.csv",
            "text/csv",
            "target"
        )

        self.eda_service.analyze.assert_called_once_with(
            "dataset.csv",
            "text/csv",
            "target"
        )

        self.statistical_service.analyze.assert_called_once_with(
            "dataset.csv",
            "text/csv",
            "target"
        )

        self.ml_service.analyze.assert_called_once_with(
            "dataset.csv",
            "text/csv",
            "target"
        )

        self.insight_engine.generate.assert_called_once()

        assert result["insights"] == (
            self.insight_result
        )

    def test_should_pass_combined_results_to_insight_engine(
        self
    ):

        self.service.analyze(
            "dataset.csv",
            "text/csv",
            "target"
        )

        call_args = (
            self.insight_engine.generate.call_args
        )

        combined_results = call_args.args[0]

        assert combined_results["eda"] == (
            self.eda_result
        )

        assert combined_results["statistical"] == (
            self.statistical_result
        )

        assert combined_results["machineLearning"] == (
            self.ml_result
        )

    def test_should_not_include_ml_when_target_is_missing(
        self
    ):

        self.service.analyze(
            "dataset.csv"
        )

        combined_results = (
            self.insight_engine
            .generate
            .call_args
            .args[0]
        )

        assert "eda" in combined_results

        assert "statistical" in combined_results

        assert "machineLearning" not in (
            combined_results
        )

    def test_should_return_analysis_and_insights(
        self
    ):

        result = self.service.analyze(
            "dataset.csv",
            target_column="target"
        )

        assert "analysis" in result

        assert "insights" in result

        assert result["analysis"]["eda"] == (
            self.eda_result
        )

        assert result["analysis"]["statistical"] == (
            self.statistical_result
        )

        assert result["analysis"]["machineLearning"] == (
            self.ml_result
        )

        assert result["insights"] == (
            self.insight_result
        )

    def test_should_propagate_eda_failure(
        self
    ):

        self.eda_service.analyze.side_effect = (
            ValueError("EDA failed")
        )

        try:

            self.service.analyze(
                "dataset.csv"
            )

            assert False, (
                "Expected ValueError"
            )

        except ValueError as exception:

            assert str(exception) == "EDA failed"

        self.statistical_service.analyze.assert_not_called()

        self.insight_engine.generate.assert_not_called()

    def test_should_propagate_statistical_failure(
        self
    ):

        self.statistical_service.analyze.side_effect = (
            ValueError("Statistical analysis failed")
        )

        try:

            self.service.analyze(
                "dataset.csv"
            )

            assert False, (
                "Expected ValueError"
            )

        except ValueError as exception:

            assert str(exception) == (
                "Statistical analysis failed"
            )

        self.ml_service.analyze.assert_not_called()

        self.insight_engine.generate.assert_not_called()

    def test_should_propagate_ml_failure(
        self
    ):

        self.ml_service.analyze.side_effect = (
            ValueError("ML analysis failed")
        )

        try:

            self.service.analyze(
                "dataset.csv",
                target_column="target"
            )

            assert False, (
                "Expected ValueError"
            )

        except ValueError as exception:

            assert str(exception) == (
                "ML analysis failed"
            )

        self.insight_engine.generate.assert_not_called()
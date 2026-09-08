import pandas as pd

from app.services.model_evaluation_service import ModelEvaluationService
from app.models.ml_problem_type import MLProblemType


class TestModelEvaluationService:
    def setup_method(self):
        self.service = ModelEvaluationService()

    def test_evaluate_classification_returns_confusion_matrix_and_report(self):



        y_true = pd.Series([0, 0, 1, 1])
        y_pred = pd.Series([0, 1, 1, 1])

        result = self.service.evaluate_classification(
            y_true,
            y_pred
        )

        assert "confusionMatrix" in result
        assert "classificationReport" in result

        assert result["confusionMatrix"] == [
            [1, 1],
            [0, 2]
        ]

        assert "0" in result["classificationReport"]
        assert "1" in result["classificationReport"]
        assert "accuracy" in result["classificationReport"]


    def test_evaluate_classification_calculates_binary_roc_auc_and_precision_recall(self):

        y_true = pd.Series([0, 0, 1, 1])
        y_pred = pd.Series([0, 0, 1, 1])

        y_score = pd.Series([
            0.10,
            0.20,
            0.80,
            0.90
        ])

        result = self.service.evaluate_classification(
            y_true,
            y_pred,
            y_score
        )

        assert "rocAuc" in result
        assert result["rocAuc"] == 1.0

        assert "precisionRecall" in result

        precision_recall = result["precisionRecall"]

        assert "precision" in precision_recall
        assert "recall" in precision_recall
        assert "thresholds" in precision_recall

        assert len(precision_recall["precision"]) > 0
        assert len(precision_recall["recall"]) > 0
        assert len(precision_recall["thresholds"]) > 0


    def test_evaluate_classification_without_scores_does_not_calculate_roc_auc(self):

        y_true = pd.Series([0, 0, 1, 1])
        y_pred = pd.Series([0, 1, 1, 1])

        result = self.service.evaluate_classification(
            y_true,
            y_pred
        )

        assert "rocAuc" not in result
        assert "precisionRecall" not in result

    def test_evaluate_classification_calculates_multiclass_roc_auc(self):


        y_true = pd.Series([
            0, 0,
            1, 1,
            2, 2
        ])

        y_pred = pd.Series([
            0, 1,
            1, 1,
            2, 2
        ])

        y_score = [
            [0.90, 0.05, 0.05],
            [0.10, 0.80, 0.10],
            [0.05, 0.90, 0.05],
            [0.05, 0.85, 0.10],
            [0.05, 0.10, 0.85],
            [0.05, 0.05, 0.90]
        ]

        result = self.service.evaluate_classification(
            y_true,
            y_pred,
            y_score
        )

        assert "confusionMatrix" in result
        assert "classificationReport" in result
        assert "rocAuc" in result

        assert result["rocAuc"] >= 0.0
        assert result["rocAuc"] <= 1.0

        assert "precisionRecall" not in result

    def test_evaluate_regression_returns_standard_metrics(self):

        y_true = pd.Series([10, 20, 30, 40])
        y_pred = pd.Series([12, 18, 33, 37])

        result = self.service.evaluate_regression(
            y_true,
            y_pred
        )

        assert "meanSquaredError" in result
        assert "meanAbsoluteError" in result
        assert "rootMeanSquaredError" in result
        assert "r2Score" in result


    def test_evaluate_regression_returns_residual_analysis(self):
        y_true = pd.Series([10, 20, 30, 40])
        y_pred = pd.Series([12, 18, 33, 37])

        result = self.service.evaluate_regression(
            y_true,
            y_pred
        )

        residuals = y_true - y_pred

        residual_analysis = result["residualAnalysis"]

        assert residual_analysis["meanResidual"] == float(
            residuals.mean()
        )

        assert residual_analysis["medianResidual"] == float(
            residuals.median()
        )

        assert residual_analysis["minResidual"] == float(
            residuals.min()
        )

        assert residual_analysis["maxResidual"] == float(
            residuals.max()
        )


    def test_evaluate_regression_returns_error_distribution(self):

        y_true = pd.Series([10, 20, 30, 40])
        y_pred = pd.Series([12, 18, 33, 37])

        result = self.service.evaluate_regression(
            y_true,
            y_pred
        )

        errors = y_true - y_pred
        absolute_errors = errors.abs()

        error_distribution = result["errorDistribution"]

        assert error_distribution["meanAbsoluteError"] == float(
            absolute_errors.mean()
        )

        assert error_distribution["medianAbsoluteError"] == float(
            absolute_errors.median()
        )

        assert error_distribution["maxAbsoluteError"] == float(
            absolute_errors.max()
        )

    def test_evaluate_regression_returns_zero_errors_for_perfect_predictions(self):
        y_true = pd.Series([10, 20, 30, 40])
        y_pred = pd.Series([10, 20, 30, 40])

        result = self.service.evaluate_regression(
            y_true,
            y_pred
        )

        assert result["meanSquaredError"] == 0.0
        assert result["meanAbsoluteError"] == 0.0
        assert result["rootMeanSquaredError"] == 0.0
        assert result["residualAnalysis"]["meanResidual"] == 0.0
        assert result["errorDistribution"]["maxAbsoluteError"] == 0.0

    def test_evaluate_dispatches_to_classification(self):

        y_true = pd.Series([0, 0, 1, 1])
        y_pred = pd.Series([0, 0, 1, 1])

        result = self.service.evaluate(
            y_true=y_true,
            y_pred=y_pred,
            problem_type=MLProblemType.CLASSIFICATION
        )

        assert "confusionMatrix" in result
        assert "classificationReport" in result


    def test_evaluate_dispatches_to_regression(self):

        y_true = pd.Series([10, 20, 30])
        y_pred = pd.Series([11, 19, 31])

        result = self.service.evaluate(
            y_true=y_true,
            y_pred=y_pred,
            problem_type=MLProblemType.REGRESSION
        )

        assert "meanSquaredError" in result
        assert "meanAbsoluteError" in result
        assert "residualAnalysis" in result
        assert "errorDistribution" in result


    def test_evaluate_rejects_unsupported_problem_type(self):

        y_true = pd.Series([1, 2])
        y_pred = pd.Series([1, 2])

        try:

            self.service.evaluate(
                y_true=y_true,
                y_pred=y_pred,
                problem_type="unsupported"
            )

            assert False, "Expected ValueError"

        except ValueError as exception:

            assert "Unsupported problem type" in str(exception)
import pandas as pd
from app.models.ml_problem_type import MLProblemType
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    roc_auc_score,
    precision_recall_curve,
    mean_squared_error,
    mean_absolute_error,
    r2_score
)


class ModelEvaluationService:

    def evaluate_classification(
            self,
            y_true: pd.Series,
            y_pred: pd.Series,
            y_score=None,
            classes=None
    ) -> dict:

        if classes is not None:

            labels = list(classes)

        else:
            labels = list(
                pd.concat(
                    [
                        pd.Series(y_true),
                        pd.Series(y_pred)
                    ]
                ).unique()
            )

        confusion = confusion_matrix(
            y_true,
            y_pred,
            labels=labels
        )

        report = classification_report(
            y_true,
            y_pred,
            labels=labels,
            output_dict=True,
            zero_division=0
        )

        evaluation = {
            "confusionMatrix": confusion.tolist(),
            "classificationReport": report
        }

        if y_score is not None:

            unique_classes = y_true.nunique()

            if unique_classes == 2:

                roc_y_true = y_true

                if classes is not None:

                    class_list = list(classes)

                    if len(class_list) == 2:

                        class_mapping = {
                            class_list[0]: 0,
                            class_list[1]: 1
                        }

                        roc_y_true = y_true.map(
                            class_mapping
                        )

                else:
                    if not set(
                        y_true.unique()
                    ).issubset({0, 1}):

                        unique_values = list(
                            y_true.unique()
                        )

                        class_mapping = {
                            unique_values[0]: 0,
                            unique_values[1]: 1
                        }

                        roc_y_true = y_true.map(
                            class_mapping
                        )

                roc_auc = roc_auc_score(
                    roc_y_true,
                    y_score
                )

                precision, recall, thresholds = (
                    precision_recall_curve(
                        roc_y_true,
                        y_score
                    )
                )

                evaluation["rocAuc"] = float(
                    roc_auc
                )

                evaluation["precisionRecall"] = {
                    "precision": precision.tolist(),
                    "recall": recall.tolist(),
                    "thresholds": thresholds.tolist()
                }

            elif unique_classes > 2:

                roc_auc = roc_auc_score(
                    y_true,
                    y_score,
                    multi_class="ovr",
                    average="weighted"
                )

                evaluation["rocAuc"] = float(
                    roc_auc
                )

        return evaluation

    def evaluate_regression(
            self,
            y_true: pd.Series,
            y_pred: pd.Series
    ) -> dict:

        errors = y_true - y_pred

        mse = mean_squared_error(
            y_true,
            y_pred
        )

        mae = mean_absolute_error(
            y_true,
            y_pred
        )

        rmse = mse ** 0.5

        r2 = r2_score(
            y_true,
            y_pred
        )

        return {
            "meanSquaredError": float(mse),

            "meanAbsoluteError": float(mae),

            "rootMeanSquaredError": float(rmse),

            "r2Score": float(r2),

            "residualAnalysis": {
                "meanResidual": float(
                    errors.mean()
                ),

                "medianResidual": float(
                    errors.median()
                ),

                "minResidual": float(
                    errors.min()
                ),

                "maxResidual": float(
                    errors.max()
                )
            },

            "errorDistribution": {
                "meanAbsoluteError": float(
                    errors.abs().mean()
                ),

                "medianAbsoluteError": float(
                    errors.abs().median()
                ),

                "maxAbsoluteError": float(
                    errors.abs().max()
                )
            }
        }

    def evaluate(
            self,
            y_true: pd.Series,
            y_pred: pd.Series,
            problem_type: str,
            y_score=None,
            classes=None
    ) -> dict:

        if problem_type == MLProblemType.CLASSIFICATION:

            return self.evaluate_classification(
                y_true=y_true,
                y_pred=y_pred,
                y_score=y_score,
                classes=classes
            )

        if problem_type == MLProblemType.REGRESSION:

            return self.evaluate_regression(
                y_true=y_true,
                y_pred=y_pred
            )

        raise ValueError(
            f"Unsupported problem type: {problem_type}"
        )
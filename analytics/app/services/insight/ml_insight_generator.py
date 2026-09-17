from app.services.insight.insight_generator import InsightGenerator


class MLInsightGenerator(InsightGenerator):

    LOW_CLASSIFICATION_F1_THRESHOLD = 0.60
    LOW_REGRESSION_R2_THRESHOLD = 0.30

    def generate(
        self,
        analysis_results: dict
    ) -> list[dict]:

        ml_result = analysis_results.get(
            "machineLearning"
        )

        if not ml_result:
            return []

        insights = []

        insights.extend(
            self._generate_class_imbalance_insight(
                ml_result
            )
        )

        insights.extend(
            self._generate_model_insights(
                ml_result
            )
        )

        insights.extend(
            self._generate_feature_importance_insight(
                ml_result
            )
        )

        return insights

    def _generate_class_imbalance_insight(
        self,
        ml_result: dict
    ) -> list[dict]:

        class_distribution = ml_result.get(
            "classDistribution"
        )

        if not class_distribution:
            return []

        if not class_distribution.get(
            "imbalanceDetected"
        ):
            return []

        return [
            self._build_insight(
                key="class-imbalance",
                severity="MEDIUM",
                title="Class imbalance detected",
                description=(
                    "The target variable contains a minority "
                    "class below the configured imbalance threshold."
                ),
                evidence={
                    "distribution": (
                        class_distribution.get(
                            "distribution"
                        )
                    ),
                    "imbalanceDetected": True
                },
                recommendation=(
                    "Review class distribution and consider "
                    "appropriate resampling, class weighting, "
                    "or evaluation strategies."
                )
            )
        ]

    def _generate_model_insights(
        self,
        ml_result: dict
    ) -> list[dict]:

        training = ml_result.get(
            "training",
            {}
        )

        if not training:
            return []

        model = training.get(
            "model"
        )

        problem_type = ml_result.get(
            "problemType"
        )

        metrics = training.get(
            "metrics",
            {}
        )

        insights = []

        if model:

            insights.append(
                self._build_insight(
                    key="selected-model",
                    severity="INFO",
                    title="Model selected",
                    description=(
                        f"{model} was selected for the "
                        f"{problem_type.lower() if problem_type else 'configured'} "
                        "problem."
                    ),
                    evidence={
                        "model": model,
                        "problemType": problem_type,
                        "modelComparison": (
                            training.get(
                                "modelComparison"
                            )
                        )
                    },
                    recommendation=(
                        "Review cross-validation results and "
                        "final evaluation metrics together when "
                        "assessing model behavior."
                    )
                )
            )

        if problem_type == "CLASSIFICATION":

            f1_score = metrics.get(
                "f1_score"
            )

            if (
                f1_score is not None
                and f1_score
                < self.LOW_CLASSIFICATION_F1_THRESHOLD
            ):

                insights.append(
                    self._build_insight(
                        key="low-f1-score",
                        severity="MEDIUM",
                        title="Low observed F1 score",
                        description=(
                            f"The observed weighted F1 score "
                            f"is {f1_score}."
                        ),
                        evidence={
                            "f1Score": f1_score
                        },
                        recommendation=(
                            "Review class-level performance, "
                            "class imbalance, and model errors "
                            "before drawing conclusions."
                        )
                    )
                )

        elif problem_type == "REGRESSION":

            r2_score = metrics.get(
                "r2Score"
            )

            if (
                r2_score is not None
                and r2_score
                < self.LOW_REGRESSION_R2_THRESHOLD
            ):

                insights.append(
                    self._build_insight(
                        key="low-r2-score",
                        severity="MEDIUM",
                        title="Low observed R² score",
                        description=(
                            f"The observed R² score is "
                            f"{r2_score}."
                        ),
                        evidence={
                            "r2Score": r2_score
                        },
                        recommendation=(
                            "Review residuals, feature quality, "
                            "data coverage, and model assumptions."
                        )
                    )
                )

        return insights

    def _generate_feature_importance_insight(
        self,
        ml_result: dict
    ) -> list[dict]:

        training = ml_result.get(
            "training",
            {}
        )

        feature_importance = training.get(
            "featureImportance",
            []
        )

        if not feature_importance:
            return []

        top_feature = feature_importance[0]

        return [
            self._build_insight(
                key="top-feature-importance",
                severity="INFO",
                title=(
                    f"{top_feature.get('feature')} "
                    "has the highest reported importance"
                ),
                description=(
                    f"The feature '{top_feature.get('feature')}' "
                    "has the highest reported feature importance "
                    "among the returned features."
                ),
                evidence={
                    "feature": top_feature.get(
                        "feature"
                    ),
                    "importance": top_feature.get(
                        "importance"
                    )
                },
                recommendation=(
                    "Investigate the feature's relationship "
                    "with the target and verify that its "
                    "importance is consistent with domain knowledge."
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
            "category": "MACHINE_LEARNING",
            "severity": severity,
            "source": "MACHINE_LEARNING",
            "title": title,
            "description": description,
            "evidence": evidence,
            "recommendation": recommendation
        }
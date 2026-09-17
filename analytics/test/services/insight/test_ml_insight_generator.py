from app.services.insight.ml_insight_generator import MLInsightGenerator


class TestMLInsightGenerator:

    def setup_method(self):

        self.generator = (
            MLInsightGenerator()
        )

    def test_should_generate_class_imbalance_insight(self):

        results = {
            "machineLearning": {
                "problemType": "CLASSIFICATION",
                "classDistribution": {
                    "distribution": {
                        "0": 0.90,
                        "1": 0.10
                    },
                    "imbalanceDetected": True
                }
            }
        }

        insights = self.generator.generate(
            results
        )

        assert len(insights) == 1

        assert (
            insights[0]["category"]
            == "MACHINE_LEARNING"
        )

        assert insights[0]["severity"] == "MEDIUM"

    def test_should_not_generate_imbalance_insight_when_balanced(
        self
    ):

        results = {
            "machineLearning": {
                "problemType": "CLASSIFICATION",
                "classDistribution": {
                    "distribution": {
                        "0": 0.50,
                        "1": 0.50
                    },
                    "imbalanceDetected": False
                }
            }
        }

        insights = self.generator.generate(
            results
        )

        assert insights == []

    def test_should_generate_selected_model_insight(self):

        results = {
            "machineLearning": {
                "problemType": "CLASSIFICATION",
                "training": {
                    "model": "RandomForestClassifier",
                    "modelComparison": {}
                }
            }
        }

        insights = self.generator.generate(
            results
        )

        assert len(insights) == 1

        assert (
            insights[0]["evidence"]["model"]
            == "RandomForestClassifier"
        )

    def test_should_generate_low_f1_insight(self):

        results = {
            "machineLearning": {
                "problemType": "CLASSIFICATION",
                "training": {
                    "model": "LogisticRegression",
                    "metrics": {
                        "f1_score": 0.42
                    }
                }
            }
        }

        insights = self.generator.generate(
            results
        )

        low_f1_insight = next(
            (
                insight
                for insight in insights
                if insight["key"] == "low-f1-score"
            ), 
            None
        )

        assert low_f1_insight is not None

        assert low_f1_insight["severity"] == "MEDIUM"

        assert low_f1_insight["evidence"]["f1Score"] == 0.42


    def test_should_generate_low_r2_insight(self):

        results = {
            "machineLearning": {
                "problemType": "REGRESSION",
                "training": {
                    "model": "LinearRegression",
                    "metrics": {
                        "r2Score": 0.15
                    }
                }
            }
        }

        insights = self.generator.generate(
            results
        )


        low_r2_insight = next(
            (
                insight
                for insight in insights
                if insight["key"] == "low-r2-score"
            ),
            None
        )

        assert low_r2_insight is not None 

        assert low_r2_insight["severity"] == "MEDIUM"

        assert low_r2_insight["evidence"]["r2Score"] == 0.15

    

    def test_should_generate_feature_importance_insight(self):

        results = {
            "machineLearning": {
                "problemType": "REGRESSION",
                "training": {
                    "featureImportance": [
                        {
                            "feature": "income",
                            "importance": 0.72
                        },
                        {
                            "feature": "age",
                            "importance": 0.28
                        }
                    ]
                }
            }
        }

        insights = self.generator.generate(
            results
        )

        assert len(insights) == 1

        assert (
            insights[0]["evidence"]["feature"]
            == "income"
        )
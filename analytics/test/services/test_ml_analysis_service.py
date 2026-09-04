import pytest
import pandas as pd
from app.services.ml_analysis_service import MLAnalysisService
from app.loaders.dataset_loader import DatasetLoader
from app.models.ml_problem_type import MLProblemType

class TestMLAnalysisService:

    def setup_method(self):
        dataset_loader = DatasetLoader()
        self.service = MLAnalysisService(dataset_loader)  

    def test_should_require_target_column(self):

        with pytest.raises(
            ValueError,
            match="Target column is required"
        ):
            self.service.analyze(
                "path/to/dataset.csv"
            )

    def test_should_reject_empty_dataset(self, tmp_path):

        dataset_path = tmp_path / "empty_dataset.csv"

        dataset_path.write_text(
            "name,age\n"
        )

        with pytest.raises(
            ValueError,
            match="Dataset cannot be empty"
        ):
            self.service.analyze(
                str(dataset_path),
                "text/csv",
                "age"
            )

    def test_should_reject_missing_target_column(self, tmp_path):

        dataset_path = tmp_path / "customers.csv"

        dataset_path.write_text(
            "name,age\n"
            "Hariom,22\n"
            "Rahul,23\n"
        )

        with pytest.raises(
            ValueError,
            match="Target column 'salary' not found in dataset"
        ):
            self.service.analyze(
                str(dataset_path),
                "text/csv",
                "salary"
            )

    def test_should_reject_target_with_only_missing_values(self, tmp_path):

        dataset_path = tmp_path / "customers.csv"

        dataset_path.write_text(
            "name,salary\n"
            "Hariom,\n"
            "Rahul,\n"
        )

        with pytest.raises(
            ValueError,
            match="Target column cannot be empty"
        ):
            self.service.analyze(
                str(dataset_path),
                "text/csv",
                "salary"
            )

    def test_should_validate_target_column(self, tmp_path):

        dataset_path = tmp_path / "customers.csv"

        dataset_path.write_text(
            "name,age\n"
            "Hariom,22\n"
            "Rahul,23\n"
            "Ankit,24\n"
            "Ravi,25\n"
        )

    
        result =self.service.analyze(
            str(dataset_path),
            "text/csv",
            "age"
        )

        assert result["targetColumn"] == "age"
        assert result["rowCount"] == 4
        assert result["columnCount"] == 2

    def test_should_detect_classification_for_categorical_target(
        self,
        tmp_path
    ):

        dataset_path = tmp_path / "customers.csv"

        dataset_path.write_text(
            "age,segment\n"
            "22,A\n"
            "23,B\n"
            "24,A\n"
            "25,B\n"
            "22,A\n"
            "23,A\n"
            "29,A\n"
            "28,B\n"
            "30,A\n"
            "31,B\n"
            
        )

        result = self.service.analyze(
            str(dataset_path),
            "text/csv",
            "segment"
        )

        assert result['problemType'] == "CLASSIFICATION"
        

    def test_should_detect_classification_for_low_cardinality_numeric_target(
        self,
        tmp_path
    ):

        dataset_path = tmp_path / "customers.csv"

        dataset_path.write_text(
            "age,purchased\n"
            "22,0\n"
            "23,1\n"
            "24,0\n"
            "25,1\n"
            "22,0\n"
            "23,1\n"
            "29,0\n"
            "28,0\n"
            "30,1\n"
            "31,1\n"
        )

        result = self.service.analyze(
            str(dataset_path),
            "text/csv",
            "purchased"
        )

        assert result["problemType"] == "CLASSIFICATION"

    def test_should_detect_regression_for_high_cardinality_numeric_target(
        self,
        tmp_path
    ):

        dataset_path = tmp_path / "sales.csv"

        rows = ["id,sales"]

        for i in range(1, 31):
            rows.append(f"{i},{1000 + i * 100}")

        dataset_path.write_text(
            "\n".join(rows)
        )

        result = self.service.analyze(
            str(dataset_path),
            "text/csv",
            "sales"
        )

        assert result["problemType"] == "REGRESSION"

    def test_should_train_classification_model(self, tmp_path):

        dataset_path = tmp_path / "customers.csv"

        dataset_path.write_text(
            "age,income,purchased\n"
            "20,20000,0\n"
            "25,30000,0\n"
            "30,40000,1\n"
            "35,50000,1\n"
            "40,60000,1\n"
            "45,70000,1\n"
            "50,80000,1\n"
            "55,90000,1\n"
            "60,100000,1\n"
            "65,110000,1\n"
        )

        result = self.service.analyze(
            str(dataset_path),
            "text/csv",
            "purchased"
        )

        assert result["problemType"] == "CLASSIFICATION"

        training = result["training"]

        comparison = training["modelComparison"]

        expected_model = max(
            comparison,
            key=lambda model:comparison[model]["meanScore"]
        )

        assert training["model"] == expected_model

        metrics = training["metrics"]
        feature_importance = training["featureImportance"]

        #feature importance
        assert len(feature_importance) > 0


        feature_names = [
            item["feature"]
            for item in feature_importance
        ]

        assert "age" in feature_names
        assert "income" in feature_names

        for item in feature_importance:
            assert "feature" in item
            assert "importance" in item
            assert item["importance"] >= 0

        importance_values = [
            item["importance"]
            for item in feature_importance
        ]

        assert importance_values == sorted(importance_values, reverse = True)

        #checking tranmsformed features names are not being eposed

        assert all(
            not feature.startswith("numeric__")
            for feature in feature_names
        )

        #Classificaton metrics
        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics

        assert 0<= metrics["accuracy"] <= 1
        assert 0<= metrics["precision"] <= 1
        assert 0<= metrics["recall"] <= 1
        assert 0<= metrics["f1_score"] <= 1

        
       

    def test_should_train_regression_model(self, tmp_path):

        dataset_path = tmp_path / "sales.csv"

        dataset_path.write_text(
            "age,income,sales\n"
            "20,20000,30000\n"
            "25,30000,40000\n"
            "30,40000,50000\n"
            "35,50000,60000\n"
            "40,60000,70000\n"
            "45,70000,80000\n"
            "50,80000,90000\n"
            "55,90000,100000\n"
            "60,100000,110000\n"
            "65,110000,120000\n"
        )

        result = self.service.analyze(
            str(dataset_path),
            "text/csv",
            "sales"
        )

        assert result["problemType"] == "REGRESSION"

        training = result["training"]

        comparison = training["modelComparison"]

        expected_model = min(
            comparison,
            key=lambda model: comparison[model]["meanScore"]
        )

        assert training["model"] == expected_model

        metrics = training["metrics"]
        feature_importance = training["featureImportance"]

        #Feature importance
        assert len(feature_importance) > 0

        feature_names = [
            item["feature"]
            for item in feature_importance
        ]

        assert "age" in feature_names
        assert "income" in feature_names
        
        for item in feature_importance:
            assert "feature" in item
            assert "importance" in item
            assert item["importance"] >= 0
        
        importance_values = [
            item["importance"]
            for item in feature_importance
        ]
        
        assert importance_values == sorted(importance_values, reverse = True)

        assert all(
            not feature.startswith("numeric__")
            for feature in feature_names
        )

        assert "mean_squared_error" in metrics
        assert "mean_absolute_error" in metrics
        assert "root_mean_squared_error" in metrics
        assert "r2Score" in metrics
    

        assert metrics["mean_squared_error"] >= 0
        assert metrics["mean_absolute_error"] >= 0
        assert metrics["root_mean_squared_error"] >= 0
        assert isinstance(metrics["r2Score"], float)

        

    def test_should_detected_balanced_class_distribution(self):

        target = pd.Series([
            "A","A","A","A","A",
            "B","B","B","B","B"
        ])

        result = self.service._analyze_class_distribution(target)

        assert result["imbalanceDetected"] is False
        assert result["distribution"]["A"] == 0.5
        assert result["distribution"]["B"] == 0.5      

    def test_should_detect_imbalanced_class_distribution(self):

        target = pd.Series([
            "A","A","A","A","A",
            "A","A","A","A",
            "B"
        ])
        
        result = self.service._analyze_class_distribution(target)

        assert result["imbalanceDetected"] is True
        assert result["distribution"]["A"] == 0.9 
        assert result["distribution"]["B"] == 0.1 

    def test_should_detect_multiclass_distribution(self):

        target = pd.Series([
            "A","A","A","A","A",
            "B","B","B",
            "C","C"
        ])

        result = self.service._analyze_class_distribution(target)

        assert result["imbalanceDetected"] is False

    def test_random_forest_feature_importance(
            self
    ):
        from sklearn.compose import ColumnTransformer
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.impute import SimpleImputer
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import OneHotEncoder 
        from app.services.ml_analysis_service import MLAnalysisService

        X = pd.DataFrame({
            "age": [20, 25, 30, 35, 40, 45, 50, 55],
            "income": [20000, 25000, 30000, 35000, 40000, 45000, 50000, 55000],
            "city": [
                "Delhi",
                "Mumbai",
                "Delhi",
                "Mumbai",
                "Delhi",
                "Mumbai",
                "Delhi",
                "Mumbai"
            ]
        })

        y = pd.Series([
            "No",
            "No",
            "No",
            "yes",
            "yes",
            "yes",
            "yes",
            "yes",
        ])

        numeric_features = ["age", "income"]
        categorical_features = ["city"]

        numeric_pipeline = Pipeline([
            (
                "imputer",
                SimpleImputer(strategy="median")
            )
        ])

        categorical_pipeline = Pipeline([
            (
                "imputer",
                SimpleImputer(strategy="most_frequent")
            ),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore")
            )
        ])

        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "numeric",
                    numeric_pipeline,
                    numeric_features
                ),
                (
                    "categorical",
                    categorical_pipeline,
                    categorical_features
                )
            ]
        )

        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )

        pipeline = Pipeline([
            (
                "preprocessor",
                preprocessor
            ),
            (
                "model",
                model
            )
        ])

        pipeline.fit(X, y)


        feature_importance = self.service._get_feature_importance(pipeline)

        assert feature_importance

        assert all(
            "feature" in item
            for item in feature_importance
        )

        assert all(
            "importance" in item
            for item in feature_importance
        )

        feature_names = {
            item["feature"]
            for item in feature_importance
        }

        assert "age" in feature_names
        assert "income" in feature_names
        assert "city" in feature_names

        assert all(
            not item["feature"].startswith("numeric__")
            for item in feature_importance
        )

        assert all(
            not item["feature"].startswith("categorical__")
            for item in feature_importance
        )


        assert all(
            item["importance"] >= 0
            for item in feature_importance
        )

    def test_compare_classification_models(self):

        X = pd.DataFrame({
            "age": [20, 21, 25, 30, 35, 40, 45, 50, 55, 60],
            "income": [
                20000, 22000, 25000, 30000, 35000,
                40000, 45000, 50000, 55000, 60000
            ]
        })

        y = pd.Series([
            "No", "No","No", "No","No",
            "Yes", "Yes","Yes", "Yes","Yes"
        ])


        preprocessor = self.service._build_preprocessor(X)


        results = self.service._compare_models(
            X,
            y,
            preprocessor,
            MLProblemType.CLASSIFICATION
        )

        assert results

        assert "LogisticRegression" in results
        assert "RandomForestClassifier" in results

        for model_name, result in results.items():
            assert "meanScore" in result
            assert "standardDeviation" in result

            assert 0 <= result["meanScore"] <= 1
            assert result["standardDeviation"] >= 0


    def test_compare_regression_models(self):

        X = pd.DataFrame({
            "age":[20, 22, 25, 28, 30, 35, 40, 45, 50, 55],
            "experience": [1, 2, 3, 5, 6, 8, 10, 12, 15, 18],
            "income": [
                20000,
                22000,
                26000, 
                30000, 
                33000, 
                38000, 
                45000, 
                50000,
                58000,
                65000
            ]
        })

        y = pd.Series([
            25000,
            27000,
            30000,
            34000,
            37000,
            43000,
            50000,
            56000,
            65000,
            72000
        ])

        preprocessor = self.service._build_preprocessor(X)
        
        
        results = self.service._compare_models(
            X,
            y,
            preprocessor,
            MLProblemType.REGRESSION
        )

        assert results

        assert "LinearRegression" in results
        assert "RandomForestRegressor" in results

        for model_name, results in results.items():
            assert "meanScore" in results
            assert "standardDeviation" in results

            assert results["meanScore"] >= 0
            assert results["standardDeviation"] >= 0


    def test_select_best_classification_model(self):

        comparison_results = {
            "LogisticRegression": {
                "meanScore": 0.82,
                "standardDeviation": 0.05
            },

            "RandomForestClassifier":{
                "meanScore": 0.91,
                "standardDeviation": 0.03
            }
        }

        best_model = self.service._select_best_model(
            comparison_results,
            MLProblemType.CLASSIFICATION
        )

        assert best_model == "RandomForestClassifier"

    def test_select_best_regression_model(self):

        comparison_results = {
            "LinearRegression" :
            {
                "meanScore": 4500.0,
                "standardDeviation": 500.0
            },
            "RandomForestRegressor":
            {
                "meanScore": 3200.0,
                "standardDeviation": 300.0
            }
        }

        best_model = self.service._select_best_model(
            comparison_results,
            MLProblemType.REGRESSION
        )

        assert best_model == "RandomForestRegressor"

    def test_select_best_model_raises_error_for_empty_results(self):

        with pytest.raises(ValueError) as exc_info:
            self.service._select_best_model(
                {},
                MLProblemType.CLASSIFICATION
            )

        assert "model comparison results" in str(exc_info.value)

        

              
import pandas as pd

from app.services.analysis_service import AnalysisService
from app.loaders.dataset_loader import DatasetLoader
from app.models.ml_problem_type import MLProblemType
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (accuracy_score, mean_absolute_error, mean_squared_error)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

class MLAnalysisService(AnalysisService):

    def _detect_problem_type(
            self,
            target: pd.Series
    ) -> MLProblemType:

        if not pd.api.types.is_numeric_dtype(target):
            return MLProblemType.CLASSIFICATION

        unique_count = target.nunique()

        if unique_count == 2:
            return MLProblemType.CLASSIFICATION

        return MLProblemType.REGRESSION
    

    def __init__(self, dataset_loader: DatasetLoader):
        self.dataset_loader = dataset_loader 

    def _train_model(
            self,
            df: pd.DataFrame,
            target_column: str,
            problem_type: MLProblemType
    )->dict :

        data = df.dropna(subset=[target_column])

        X = data.drop(columns=[target_column])
        y = data[target_column]


        if X.empty:
            raise ValueError(
                "Dataset must have at least one feature column"
            )

        if len(data) < 4:
            raise ValueError(
                "Dataset must have at least 4 rows for training"
            )

        numeric_features = X.select_dtypes(include=['number']).columns.tolist()
        categorical_features = X.select_dtypes(exclude=['number']).columns.tolist()

        numeric_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='median'))
        ])

        categorical_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('encoder', OneHotEncoder(handle_unknown='ignore'))
        ])

        preprocessor = ColumnTransformer(
            transformers = [
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

        if problem_type == MLProblemType.CLASSIFICATION:

            if y.nunique() < 2:
                raise ValueError(
                    "Classification target must contain atleast two classes"
                )

            model = LogisticRegression(max_iter=1000)

        else:
            model = LinearRegression()

        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('model', model)
        ])

        test_size = 0.2 

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,    
            random_state=42
        )

        pipeline.fit(X_train, y_train)

        predictions = pipeline.predict(X_test)

        if problem_type == MLProblemType.CLASSIFICATION:

            return {
                "model":"LogisticRegression",
                "metrics": {
                    "accuracy": round(float(
                        accuracy_score(y_test, predictions)
                    ), 4)
                }
            }
        mse = mean_squared_error(y_test, predictions)

        return {
            "model":"LinearRegression",
            "metrics": {
                "mean_squared_error": round(float(mse), 4),
                "mean_absolute_error": round(float(
                    mean_absolute_error(y_test, predictions)
                ), 4),
                "root_mean_squared_error": round(float(mse ** 0.5), 4)
            }
        }

    def analyze(
            self,
            dataset_path: str,
            file_type: str | None = None,
            target_column: str | None = None
    ) -> dict :

        if not target_column:
            raise ValueError(
                "Target column is required for machine learning analysis." 
                )

        df = self.dataset_loader.load(
            dataset_path,
            file_type
        )

        if df.empty:
            raise ValueError(
                "Dataset cannot be empty"
            )

        if target_column not in df.columns:
            raise ValueError(
                f"Target column '{target_column}' not found in dataset."
            )

        target = df[target_column]

        if target.isnull().all():
            raise ValueError(
                "Target column cannot be empty"
            )

        target = target.dropna()

        if len(target) < 2:
            raise ValueError(
                "Target column must have atleast two values"
            )

        problem_type = self._detect_problem_type(target)

        training_results = self._train_model(
            df,
            target_column,
            problem_type
        )

        return {
            "targetColumn": target_column,
            "rowCount": len(df),
            "columnCount": len(df.columns),
            "problemType": problem_type.value,
            "training": training_results,
        }

    
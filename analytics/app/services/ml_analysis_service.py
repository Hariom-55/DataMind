import pandas as pd

from app.services.analysis_service import AnalysisService
from app.loaders.dataset_loader import DatasetLoader
from app.models.ml_problem_type import MLProblemType
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score, 
    recall_score, 
    f1_score, 
    r2_score
    )

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    KFold,
    cross_val_score
)
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

    def _analyze_class_distribution(
            self,
            target: pd.Series
    ) -> dict:

        class_counts = target.value_counts()
        total = len(target)

        class_distribution = {
            str(label): round(float(count/total), 4)
            for label, count in class_counts.items()
        }

        minority_ratio = float(
            class_counts.min() / total
        )

        return {
            "distribution": class_distribution,
            "imbalanceDetected": minority_ratio < 0.20
        }

    def _cross_validate_model(
            self,
            pipeline:Pipeline,
            X: pd.DataFrame,
            y: pd.Series,
            problem_type: MLProblemType
    ) -> dict | None:

        

        if problem_type == MLProblemType.CLASSIFICATION:
            class_counts = y.value_counts()
            min_class_count = class_counts.min()
            
            if min_class_count < 2:
                return None
            
            n_splits = min(5, min_class_count)
            cv = StratifiedKFold(
                n_splits=n_splits,
                shuffle=True,
                random_state=42
            )

            scores = cross_val_score(
                pipeline,
                X,
                y,
                cv=cv,
                scoring="accuracy"
            )

        else:

            if len(y) < 2:
                return None

            n_splits = min(5, len(y))

            cv =KFold(
                n_splits= n_splits,
                shuffle=True,
                random_state=42
            )

            scores = cross_val_score(
                pipeline,
                X,
                y,
                cv=cv,
                scoring="neg_mean_absolute_error"
            )

            scores = -scores

        return {
            "meanScore": round(float(scores.mean()), 4),
            "standardDeviation": round(float(scores.std()), 4)
        }

    def _get_transformed_feature_names(
            self,
            pipeline: Pipeline
    ) -> list[str] :

        preprocessor = pipeline.named_steps["preprocessor"]

        return preprocessor.get_feature_names_out().tolist()

    def _get_feature_importance(
            self,
            pipeline: Pipeline
    ) -> list[dict]:

        model = pipeline.named_steps["model"]

        feature_names = self._get_transformed_feature_names(pipeline)

        original_feature_names = self._get_original_feature_names(pipeline)

        coefficients = model.coef_

        if coefficients.ndim == 1:
            importance_values = abs(coefficients)

        else:
            importance_values = abs(coefficients).mean(axis=0)

        transformed_importance = [
            {
                "feature": feature_name,
                "importance": round(
                    float(value),
                    4
                )
            }
            for feature_name, value in zip(feature_names, importance_values)
        ]

        return self._aggregate_feature_importance(
            transformed_importance,
            original_feature_names
        )

    def _aggregate_feature_importance(
            self,
            feature_importance: list[dict],
            original_feature_names: list[str]
    ) -> list[dict]:

        aggregated = {}

        for item, original_feature in zip(feature_importance, original_feature_names):

            importance = item["importance"]

            if original_feature not in aggregated:
                aggregated[original_feature] = 0.0

            aggregated[original_feature] += importance ** 2

        result = [
            {
                "feature": feature,
                "importance": round(
                    value** 0.5,
                    4
                )
            }for feature, value in aggregated.items()
        ]

        result.sort(
            key=lambda item: item["importance"],
            reverse=True
        )

        return result


    def _get_feature_mapping(
            self,
            pipeline: Pipeline
    ) -> list[tuple[str,str]] :

        preprocessor = pipeline.named_steps["preprocessor"]

        mapping = []

        for transformers_name, transformer, columns in (
            preprocessor.transformers_
        ):
            if transformer == "drop":
                continue

            if transformer == "passthrough":
                for column in columns:
                    mapping.append(
                        (column, column)
                    )
                continue

            if hasattr(transformer, "named_steps"):
                final_transformer = transformer.steps[-1][1]
            else :
                final_transformer = transformer

            if hasattr(
                final_transformer,
                "get_features_names_out"
            ):
                transformed_names = (
                    final_transformer.get_feature_names_out(
                        columns
                    )
                )

                for transformed_name, column in zip(
                    transformed_name, columns
                ): 
                    mapping.append(
                        (transformed_name, column)
                    )
            else :
                for column in columns:
                    mapping.append(
                        (column, column)
                    )

        return mapping

    def _get_original_feature_names(
            self,
            pipeline: Pipeline
    ) -> list[str] :

        preprocessor = pipeline.named_steps["preprocessor"]

        feature_names = []

        for transformer_name, transformer, columns in (preprocessor.transformers_):

            if transformer == "drop":
                continue

            if transformer == "passthrough":
                feature_names.extend(columns)
                continue

            if transformer_name == "numeric":
                feature_names.extend(columns)

            elif transformer_name == "categorical":

                encoder = transformer.named_steps["encoder"]

                for column, categories in zip(
                    columns,
                    encoder.categories
                ):
                    feature_names.extend(
                        [column] * len(categories)
                    )

        return feature_names

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

        test_size = max(0.2, 2 / len(X))

        if problem_type == MLProblemType.CLASSIFICATION:
            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=test_size,
                random_state=42,
                stratify=y
            )

        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=test_size,    
                random_state=42
            )

        pipeline.fit(X_train, y_train)

        predictions = pipeline.predict(X_test)

        cross_validation_results = self._cross_validate_model(
            pipeline,
            X_train,
            y_train,
            problem_type
        )

        feature_importance = self._get_feature_importance(pipeline)

        if problem_type == MLProblemType.CLASSIFICATION:

            return {
                "model":"LogisticRegression",
                "metrics": {
                    "accuracy": round(float(
                        accuracy_score(y_test, predictions)
                    ), 4),
                    "precision": round(float(
                        precision_score(y_test, predictions, average='weighted', zero_division=0)
                    ), 4),
                    "recall": round(float(
                        recall_score(y_test, predictions, average='weighted', zero_division=0)
                    ), 4),
                    "f1_score": round(float(
                        f1_score(y_test, predictions, average='weighted', zero_division=0)
                    ), 4)
                },
                "crossValidation": cross_validation_results,
                "featureImportance": feature_importance
            }
        mse = mean_squared_error(y_test, predictions)

        return {
            "model":"LinearRegression",
            "metrics": {
                "mean_squared_error": round(float(mse), 4),
                "mean_absolute_error": round(float(
                    mean_absolute_error(y_test, predictions)
                ), 4),
                "root_mean_squared_error": round(float(mse ** 0.5), 4),
                "r2Score": round(float(
                    r2_score(y_test, predictions)
                ),4)
            },
            "crossValidation": cross_validation_results,
            "featureImportance": feature_importance
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

        class_distribution = None

        if problem_type == MLProblemType.CLASSIFICATION:
            class_distribution = self._analyze_class_distribution(target)
        

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
            "classDistribution": class_distribution,
            "training": training_results,
        }

    
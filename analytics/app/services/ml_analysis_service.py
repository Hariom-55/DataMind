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
    GridSearchCV,
    cross_val_score
)


from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
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

        if hasattr(model, "coef_"):
            coefficients = model.coef_

            if coefficients.ndim == 1:
                importance_values = abs(coefficients)

            else:
                importance_values = abs(coefficients).mean(axis=0)

        elif hasattr(model, "feature_importances_"):
            importance_values = model.feature_importances_

        else :
            return []

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

    def  _build_preprocessor(
            self,
            X:pd.DataFrame
    )-> ColumnTransformer:

        numeric_features = X.select_dtypes(
            include =["number"]
        ).columns.tolist()

        categorical_features = X.select_dtypes(
            exclude=["number"]
        ).columns.tolist()

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

        return ColumnTransformer(
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

    def _get_candidate_models(
            self,
            problem_type: MLProblemType
    ) -> dict:

        if problem_type == MLProblemType.CLASSIFICATION:
            return{
                "LogisticRegression": LogisticRegression(
                    max_iter=1000
                ),
                "RandomForestClassifier": RandomForestClassifier(
                    n_estimators=100,
                    random_state=42
                )
            }

        return {
            "LinearRegression": LinearRegression(),
            "RandomForestRegressor": RandomForestRegressor(
                n_estimators=100,
                random_state=42
            )
        }

    def _compare_models(
            self,
            X: pd.DataFrame,
            y: pd.Series,
            preprocessor: ColumnTransformer,
            problem_type: MLProblemType
    ) -> dict :

        candidate_models = self._get_candidate_models(problem_type)

        results = {}

        for model_name, model in candidate_models.items():

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

            cross_validation_results = self._cross_validate_model(pipeline, X , y, problem_type)

            if cross_validation_results is not None:
                results[model_name] = cross_validation_results

        return results

    def _select_best_model (
            self,
            comparison_results: dict,
            problem_type: MLProblemType
    )-> str :

        if not comparison_results:
            raise ValueError(
                "No model comparison results availabe"
            )

        if problem_type == MLProblemType.CLASSIFICATION:
            return max(
                comparison_results,
                key=lambda model:comparison_results[model]["meanScore"]
            )

        return min(
            comparison_results,
            key=lambda model:comparison_results[model]["meanScore"]
        )

    def _build_cv(self, y, problem_type):

        if problem_type == MLProblemType.CLASSIFICATION:
            class_counts = y.value_counts()

            if class_counts.empty:
                return None

            min_class_count = class_counts.min()

            if min_class_count < 2:
                return None

            n_splits = min(5, int(min_class_count))

            return StratifiedKFold(
                n_splits=n_splits,
                shuffle=True,
                random_state=42
            )

        if problem_type == MLProblemType.REGRESSION:

            if len(y) < 2 :
                return None

            n_splits = min(5, len(y))

            return KFold(
                n_splits=n_splits,
                shuffle=True,
                random_state=42
            )

        raise ValueError(
            f"Unsupported problem Type: {problem_type}"
        )

    
    def _tune_random_forest(
            self,
            X_train,
            y_train,
            preprocessor,
            problem_type
    ):

        if problem_type == MLProblemType.CLASSIFICATION:

            pipeline = Pipeline(
                steps = [
                    ("preprocessor", preprocessor),
                    ("model", RandomForestClassifier(
                        random_state=42
                    ))
                ]
            )

            param_grid = {
                "model__n_estimators": [50, 100],
                "model__max_depth": [None, 10],
                "model__min_samples_split": [2, 5]
            }

            cv = self._build_cv(
                y_train,
                problem_type
            )

            if cv is None:
                raise ValueError(
                    "Not enough data for hyperparameter tunning"
                )

            grid_serach = GridSearchCV(
                estimator=pipeline,
                param_grid=param_grid,
                scoring="accuracy",
                cv=cv,
                n_jobs=1
            )

            grid_serach.fit(X_train, y_train)

            return {
                "model": "RandomForestClassifier",
                "bestParameters": grid_serach.best_params_,
                "bestScore":float(grid_serach.best_score_),
                "bestEstimator": grid_serach.best_estimator_
            }

        if problem_type == MLProblemType.REGRESSION:

            pipeline = Pipeline(
                steps=[
                    ("preprocessor", preprocessor),
                    ("model", RandomForestRegressor(
                        random_state=42
                    ))
                ]
            )

            param_grid = {
                "model__n_estimators": [50, 100],
                "model__max_depth": [None, 10],
                "model__min_samples_split": [2, 5]
            }

            cv = self._build_cv(y_train, problem_type)

            if cv is None:
                raise ValueError(
                    "Not enough data for hyperparamter tuning"
                )

            grid_search = GridSearchCV(
                estimator=pipeline,
                param_grid=param_grid,
                scoring="neg_mean_absolute_error",
                cv=cv,
                n_jobs=1
            )

            grid_search.fit(X_train, y_train)

            return {
                "model": "RandomForestRegressor",
                "bestParameter": grid_search.best_params_,
                "bestScore": float (-grid_search.best_score_),
                "bestEstimator": grid_search.best_estimator_
            }

        raise ValueError(
            "Unsupported problem type for Random Forest Tuning"
        )

    def _train_model(
            self,
            df: pd.DataFrame,
            target_column: str,
            problem_type: MLProblemType
    )->dict :

        #prepare data

        data = df.dropna(subset=[target_column])

        X = data.drop(columns=[target_column])
        y = data[target_column]

        #validate dataset
        if X.empty:
            raise ValueError(
                "Dataset must have at least one feature column"
            )

        if len(data) < 4:
            raise ValueError(
                "Dataset must have at least 4 rows for training"
            )

        if problem_type ==MLProblemType.CLASSIFICATION:

            if y.nunique() < 2 :
                raise ValueError(
                    "classification target must cpnatin atleast two classes"
                )

        #split dataset
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

        #preprocessing pipeline
        preprocessor = self._build_preprocessor(X_train)

        #compare candidate models using training data
        comparison_results = self._compare_models(
            X_train,
            y_train,
            preprocessor,
            problem_type
        )

        if not comparison_results:
            raise ValueError(
                "Unable to compare models with available dataset"
            )

        #selecting best model 

        best_model_name = self._select_best_model(comparison_results, problem_type)

        #getting candidate model
        candidate_models = self._get_candidate_models(problem_type)

        best_model = candidate_models[best_model_name]


        #hyperparameter tuning 
        tuning_result = None

        if best_model_name in (
            "RandomForestClassifier",
            "RandomForestRegressor"
        ):
            tuning_result = self._tune_random_forest(
                X_train,
                y_train,
                preprocessor,
                problem_type
            )

            pipeline = tuning_result["bestEstimator"]

        #Building final pipeline using selected model    

        else:
            pipeline = Pipeline([
                (
                    "preprocessor",
                    preprocessor
                ),
                (
                    "model",
                    best_model
                )
            ])

        #training selected model
        pipeline.fit(X_train, y_train)

        #Evaluating the model
        predictions = pipeline.predict(X_test)

        #calculating Feature Importance
        feature_importance = self._get_feature_importance(pipeline) 

        #serialization

        tuning_response = None

        if tuning_result is not None:
            tuning_response = {
                "bestParameters": tuning_result["bestParameters"],
                "bestScore": round(
                    float(tuning_result["bestScore"]), 4
                )
            }

        #Classification results 

        if problem_type == MLProblemType.CLASSIFICATION:

            return {
                "model": best_model_name,
                "modelComparison": comparison_results,
                "tuning": tuning_response,

                "metrics": {
                    "accuracy": round(
                        float(accuracy_score(y_test, predictions)) , 4
                    ),
                    "precision": round(
                        float(precision_score(y_test, predictions, average= "weighted", zero_division=0)), 4
                    ),
                    "recall": round(
                        float(recall_score(y_test, predictions, average="weighted", zero_division=0)), 4
                    ),
                    "f1_score": round(
                        float(f1_score(y_test, predictions, average="weighted", zero_division=0)), 4
                    )
                    
                },
                "featureImportance": feature_importance
            }

        mse = mean_squared_error(y_test, predictions)

        return {
            "model":best_model_name,
            "modelComparison": comparison_results,
            "tuning": tuning_response,
            
            "metrics": {
                "mean_squared_error": round(
                    float(mse), 4
                ),
                "mean_absolute_error": round(
                    float(
                    mean_absolute_error(y_test, predictions)), 4
                ),
                "root_mean_squared_error": round(
                    float(mse ** 0.5), 4
                ),
                "r2Score": round(
                    float(r2_score(y_test, predictions)),4
                )
            },
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


from app.services.data_cleaning_recommendation_service import DataCleaningRecommendationService
from app.services.data_cleaning_engine import DataCleaningEngine
from app.services.cleaned_dataset_result_service import CleanedDatasetResultService
from app.services.data_cleaning_change_tracker import DataCleaningChangeTracker


class DataCleaningWorkflowService:

    def __init__(
            self,
            cleaning_service,
            recommendation_service=None,
            cleaning_engine=None,
            change_tracker=None,
            cleaned_dataset_result_service=None
    ):

        self.cleaning_service = cleaning_service

        self.recommendation_service = (
            recommendation_service
            or DataCleaningRecommendationService()
        )

        self.cleaning_engine = (
            cleaning_engine
            or DataCleaningEngine()
        )

        self.change_tracker = (
            change_tracker
            or DataCleaningChangeTracker()
        )

        self.cleaned_dataset_result_service = (
            cleaned_dataset_result_service
            or CleanedDatasetResultService()
        )

    def assess_dataset(
            self,
            df
    ) -> dict:

        quality_report = (
            self.cleaning_service.assess_quality(df)
        )

        recommendations = (
            self.recommendation_service
            .generate_recommendations(
                quality_report["issues"]
            )
        )

        return {
            "totalRows": quality_report["totalRows"],
            "totalColumns": quality_report["totalColumns"],
            "issueCount": quality_report["issueCount"],
            "issues": quality_report["issues"],
            "recommendations": recommendations
        }

    def clean_dataset(
            self,
            df,
            operations: list
    ) -> dict:

        cleaned_df = df.copy()

        changes = []

        for operation_request in operations:

            operation = operation_request.get(
                "operation"
            )

            column = operation_request.get(
                "column"
            )

            before = cleaned_df.copy()

            cleaned_df = (
                self.cleaning_engine.apply_operation(
                    cleaned_df,
                    operation,
                    column
                )
            )

            change = (
                self.change_tracker.track(
                    before=before,
                    after=cleaned_df,
                    operation=operation,
                    column=column
                )
            )

            changes.append(change)

        return {
            "originalRows": len(df),
            "cleanedRows": len(cleaned_df),
            "originalColumns": len(df.columns),
            "cleanedColumns": len(cleaned_df.columns),
            "operationsApplied": len(operations),
            "changes": changes,
            "data": cleaned_df
        }

    def clean_dataset_result(
            self,
            df,
            operations: list,
            extension: str = "csv"
    ):

        cleaning_result = self.clean_dataset(
            df,
            operations
        )

        return (
            self.cleaned_dataset_result_service
            .build_result(
                cleaning_result,
                extension
            )
        )
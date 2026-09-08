from app.models.clean_dataset_request import CleanDatasetRequest
from app.services.data_cleaning_workflow_service import DataCleaningWorkflowService
from app.services.cleaned_dataset_response_service import CleanedDatasetResponseService

class DatasetCleaningService:

    def __init__(
            self,
            dataset_loader,
            cleaning_workflow_service: DataCleaningWorkflowService,
            response_service: CleanedDatasetResponseService
    ):

        self.dataset_loader = dataset_loader
        self.cleaning_workflow_service = (
            cleaning_workflow_service
        )
        self.response_service = response_service

    def clean_dataset(
            self,
            request: CleanDatasetRequest
    ):

        df = self.dataset_loader.load(
            request.dataset_path
        )

        result = (
            self.cleaning_workflow_service
            .clean_dataset_result(
                df,
                request.operations,
                request.extension
            )
        )

        return self.response_service.build_response(
            result
        )
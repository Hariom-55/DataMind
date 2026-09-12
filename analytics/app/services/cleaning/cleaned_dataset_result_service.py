import pandas as pd

from app.schemas.cleaned_dataset_result import CleanedDatasetResult
from app.services.cleaning.cleaned_dataset_serializer import CleanedDatasetSerializer
from app.services.dataset.content_hash_service import DatasetContentHashService



class CleanedDatasetResultService:

    def __init__(
            self,
            serializer=None,
            hash_service=None
    ):

        self.serializer = (
            serializer
            or CleanedDatasetSerializer()
        )

        self.hash_service = (
            hash_service
            or DatasetContentHashService()
        )

    def build_result(
        self,
        cleaning_result: dict,
        extension: str = "csv"
    ) -> CleanedDatasetResult:

        cleaned_df = cleaning_result["data"]

        if not isinstance(cleaned_df, pd.DataFrame):
            raise ValueError(
                "Cleaning result must contain a pandas DataFrame"
            )

        content = self.serializer.to_csv_bytes(
            cleaned_df
        )

        content_hash = self.hash_service.calculate_hash(
            content
        )

        normalized_extension = extension.lstrip(".")

        return CleanedDatasetResult(
            content=content,
            content_hash=content_hash,
            extension=normalized_extension,
            original_rows=cleaning_result["originalRows"],
            cleaned_rows=cleaning_result["cleanedRows"],
            original_columns=cleaning_result["originalColumns"],
            cleaned_columns=cleaning_result["cleanedColumns"],
            operations_applied=cleaning_result["operationsApplied"],
            changes=cleaning_result["changes"]
        )
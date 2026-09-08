import base64

from app.models.cleaned_dataset_response import CleanedDatasetResponse
from app.models.cleaned_dataset_result import CleanedDatasetResult


class CleanedDatasetResponseService:

    def build_response(
            self,
            result: CleanedDatasetResult
    ) -> CleanedDatasetResponse:

        encoded_content = base64.b64encode(
            result.content
        ).decode("utf-8")

        return CleanedDatasetResponse(
            content=encoded_content,
            content_hash=result.content_hash,
            extension=result.extension,
            original_rows=result.original_rows,
            cleaned_rows=result.cleaned_rows,
            original_columns=result.original_columns,
            cleaned_columns=result.cleaned_columns,
            operations_applied=result.operations_applied,
            changes=result.changes
        )
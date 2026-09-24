from app.schemas.cleaned_dataset_response import CleanedDatasetResponse
from app.schemas.cleaned_dataset_result import CleanedDatasetResult
from app.services.cleaning.cleaning_artifact_store import CleaningArtifactStore


class CleanedDatasetResponseService:

    def __init__(self, artifact_store: CleaningArtifactStore | None = None):
        self.artifact_store = artifact_store or CleaningArtifactStore()

    def build_response(
            self,
            result: CleanedDatasetResult
    ) -> CleanedDatasetResponse:

        artifact_id = self.artifact_store.store(result.content)

        return CleanedDatasetResponse(
            artifact_id=artifact_id,
            sha256=result.content_hash,
            extension=result.extension,
            format="CSV",
            content_type="text/csv",
            size_bytes=len(result.content),
            original_rows=result.original_rows,
            cleaned_rows=result.cleaned_rows,
            original_columns=result.original_columns,
            cleaned_columns=result.cleaned_columns,
            operations_applied=result.operations_applied,
            changes=result.changes
        )

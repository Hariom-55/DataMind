import pandas as pd

from app.schemas.cleaned_dataset_result import CleanedDatasetResult
from app.services.cleaning.cleaned_dataset_response_service import CleanedDatasetResponseService
from app.services.cleaning.cleaning_artifact_store import CleaningArtifactStore


class TestCleanedDatasetResponseService:

    def test_should_return_artifact_reference_instead_of_content(self, tmp_path):

        content = b"name,age\nHariom,22\n"

        result = CleanedDatasetResult(
            content=content,
            content_hash="abc123",
            extension="csv",
            original_rows=2,
            cleaned_rows=1,
            original_columns=2,
            cleaned_columns=2,
            operations_applied=1,
            changes=[]
        )

        service = CleanedDatasetResponseService(CleaningArtifactStore(tmp_path))

        response = service.build_response(result)

        assert response.artifact_id
        assert response.size_bytes == len(content)
        assert (tmp_path / f"{response.artifact_id}.csv").read_bytes() == content


    def test_should_preserve_result_metadata(self, tmp_path):

        result = CleanedDatasetResult(
            content=b"name\nHariom\n",
            content_hash="abc123",
            extension="csv",
            original_rows=10,
            cleaned_rows=8,
            original_columns=3,
            cleaned_columns=2,
            operations_applied=2,
            changes=[
                {
                    "operation": "REMOVE_DUPLICATES",
                    "rowsAffected": 2
                }
            ]
        )

        service = CleanedDatasetResponseService(CleaningArtifactStore(tmp_path))

        response = service.build_response(result)

        assert response.sha256 == "abc123"
        assert response.extension == "csv"
        assert response.format == "CSV"
        assert response.content_type == "text/csv"

        assert response.original_rows == 10
        assert response.cleaned_rows == 8

        assert response.original_columns == 3
        assert response.cleaned_columns == 2

        assert response.operations_applied == 2
        assert response.changes == result.changes


    def test_should_store_raw_csv_bytes_for_download(self, tmp_path):

        content = b"name,age\nHariom,22\n"

        result = CleanedDatasetResult(
            content=content,
            content_hash="abc123",
            extension="csv",
            original_rows=1,
            cleaned_rows=1,
            original_columns=2,
            cleaned_columns=2,
            operations_applied=0,
            changes=[]
        )

        service = CleanedDatasetResponseService(CleaningArtifactStore(tmp_path))

        response = service.build_response(result)

        assert (tmp_path / f"{response.artifact_id}.csv").read_bytes() == content

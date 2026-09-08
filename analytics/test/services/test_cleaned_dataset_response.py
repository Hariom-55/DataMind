import base64
import pandas as pd

from app.models.cleaned_dataset_result import CleanedDatasetResult
from app.services.cleaned_dataset_response_service import CleanedDatasetResponseService


class TestCleanedDatasetResponseService:

    def test_should_encode_content_as_base64(self):

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

        service = CleanedDatasetResponseService()

        response = service.build_response(result)

        expected = base64.b64encode(
            content
        ).decode("utf-8")

        assert response.content == expected


    def test_should_preserve_result_metadata(self):

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

        service = CleanedDatasetResponseService()

        response = service.build_response(result)

        assert response.content_hash == "abc123"
        assert response.extension == "csv"

        assert response.original_rows == 10
        assert response.cleaned_rows == 8

        assert response.original_columns == 3
        assert response.cleaned_columns == 2

        assert response.operations_applied == 2
        assert response.changes == result.changes


    def test_should_produce_decodable_base64_content(self):

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

        service = CleanedDatasetResponseService()

        response = service.build_response(result)

        decoded_content = base64.b64decode(
            response.content
        )

        assert decoded_content == content
import pandas as pd

from app.services.cleaning.cleaned_dataset_result_service import (
    CleanedDatasetResultService
)
from app.services.cleaning.cleaned_dataset_serializer import (
    CleanedDatasetSerializer
)
from app.services.dataset.content_hash_service import (
    DatasetContentHashService
)


class TestCleanedDatasetResultService:

    def test_should_build_cleaned_dataset_result(self):

        cleaned_df = pd.DataFrame({
            "name": ["Hariom", "Alice"],
            "age": [22, 25]
        })

        cleaning_result = {
            "originalRows": 3,
            "cleanedRows": 2,
            "originalColumns": 2,
            "cleanedColumns": 2,
            "operationsApplied": 1,
            "changes": [
                {
                    "operation": "REMOVE_DUPLICATES",
                    "column": None,
                    "rowsAffected": 1
                }
            ],
            "data": cleaned_df
        }

        service = CleanedDatasetResultService(
            CleanedDatasetSerializer(),
            DatasetContentHashService()
        )

        result = service.build_result(
            cleaning_result
        )

        assert result.extension == "csv"

        assert result.original_rows == 3
        assert result.cleaned_rows == 2

        assert result.original_columns == 2
        assert result.cleaned_columns == 2

        assert result.operations_applied == 1

        assert result.changes == cleaning_result["changes"]

        assert isinstance(result.content, bytes)

        assert len(result.content_hash) == 64


    def test_should_generate_hash_from_serialized_content(self):

        cleaned_df = pd.DataFrame({
            "name": ["Hariom"],
            "age": [22]
        })

        cleaning_result = {
            "originalRows": 1,
            "cleanedRows": 1,
            "originalColumns": 2,
            "cleanedColumns": 2,
            "operationsApplied": 0,
            "changes": [],
            "data": cleaned_df
        }

        serializer = CleanedDatasetSerializer()
        hash_service = DatasetContentHashService()

        service = CleanedDatasetResultService(
            serializer,
            hash_service
        )

        result = service.build_result(
            cleaning_result
        )

        expected_content = serializer.to_csv_bytes(
            cleaned_df
        )

        expected_hash = hash_service.calculate_hash(
            expected_content
        )

        assert result.content == expected_content
        assert result.content_hash == expected_hash


    def test_should_normalize_extension(self):

        cleaning_result = {
            "originalRows": 1,
            "cleanedRows": 1,
            "originalColumns": 1,
            "cleanedColumns": 1,
            "operationsApplied": 0,
            "changes": [],
            "data": pd.DataFrame({
                "name": ["Hariom"]
            })
        }

        service = CleanedDatasetResultService(
            CleanedDatasetSerializer(),
            DatasetContentHashService()
        )

        result = service.build_result(
            cleaning_result,
            ".csv"
        )

        assert result.extension == "csv"


    def test_should_reject_invalid_cleaning_result(self):

        cleaning_result = {
            "originalRows": 1,
            "cleanedRows": 1,
            "originalColumns": 1,
            "cleanedColumns": 1,
            "operationsApplied": 0,
            "changes": [],
            "data": "not a dataframe"
        }

        service = CleanedDatasetResultService(
            CleanedDatasetSerializer(),
            DatasetContentHashService()
        )

        try:
            service.build_result(cleaning_result)
            assert False
        except ValueError as exception:
            assert str(exception) == (
                "Cleaning result must contain a pandas DataFrame"
            )
import pytest
from pydantic import ValidationError

from app.schemas.clean_dataset_request import CleanDatasetRequest


def test_cleaning_operation_accepts_explicit_imputation_parameters():
    request = CleanDatasetRequest.model_validate({
        "dataset_version_id": "version-1",
        "dataset_path": "file.csv",
        "operations": [{
            "operation": "IMPUTE_MISSING_VALUES",
            "column": "age",
            "parameters": {"strategy": "MEAN"},
        }],
    })

    assert request.operations[0].parameters == {"strategy": "MEAN"}


@pytest.mark.parametrize("parameters", [
    {"strategy": "UNKNOWN"},
    {"strategy": "CONSTANT"},
    {"unexpected": True},
])
def test_cleaning_operation_rejects_invalid_parameters(parameters):
    with pytest.raises(ValidationError):
        CleanDatasetRequest.model_validate({
            "dataset_version_id": "version-1",
            "dataset_path": "file.csv",
            "operations": [{
                "operation": "IMPUTE_MISSING_VALUES",
                "column": "age",
                "parameters": parameters,
            }],
        })

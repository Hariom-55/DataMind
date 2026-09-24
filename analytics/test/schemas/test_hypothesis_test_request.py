import pytest
from pydantic import ValidationError

from app.schemas.hypothesis_test_request import HypothesisTestRequest


@pytest.mark.parametrize("test_input", [
    {"test": "ONE_SAMPLE_T_TEST", "column": "age", "referenceValue": 0},
    {"test": "INDEPENDENT_T_TEST", "valueColumn": "age", "groupColumn": "team"},
    {"test": "PAIRED_T_TEST", "column1": "before", "column2": "after"},
    {"test": "CHI_SQUARE_INDEPENDENCE", "column1": "region", "column2": "product"},
])
def test_supported_hypothesis_test_inputs_validate(test_input):
    assert HypothesisTestRequest.model_validate(test_input).alpha == 0.05


def test_hypothesis_test_rejects_missing_test_inputs():
    with pytest.raises(ValidationError):
        HypothesisTestRequest.model_validate({"test": "ONE_SAMPLE_T_TEST", "column": "age"})


def test_hypothesis_test_rejects_invalid_alpha():
    with pytest.raises(ValidationError):
        HypothesisTestRequest.model_validate({
            "test": "ONE_SAMPLE_T_TEST", "column": "age", "referenceValue": 0, "alpha": 1,
        })

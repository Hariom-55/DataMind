import pandas as pd
import pytest

from app.models.ml_problem_type import MLProblemType
from app.services.machine_learning.feature_selection_service import FeatureSelectionService


def test_feature_selection_removes_identifiers_and_constants_but_keeps_features():
    service = FeatureSelectionService()
    X = pd.DataFrame({
        "customer_id": [1, 2, 3, 4, 5, 6],
        "age": [20, 21, 22, 23, 24, 25],
        "income": [10, 20, 30, 40, 50, 60],
        "constant": [1, 1, 1, 1, 1, 1],
    })
    y = pd.Series([0, 0, 1, 1, 1, 0])

    selected, metadata = service.select(X, y, MLProblemType.CLASSIFICATION)

    assert list(selected.columns) == ["age", "income"]
    assert metadata["method"] == "DETERMINISTIC_FILTERS"
    assert metadata["selectedFeatures"] == ["age", "income"]
    assert {item["feature"] for item in metadata["removedFeatures"]} == {
        "customer_id",
        "constant",
    }


def test_feature_selection_can_apply_redundancy_filter_explicitly():
    service = FeatureSelectionService()
    X = pd.DataFrame({
        "age": [20, 21, 22, 23, 24, 25],
        "age_copy": [20, 21, 22, 23, 24, 25],
        "income": [10, 30, 20, 40, 50, 60],
    })
    y = pd.Series([0, 0, 1, 1, 1, 0])

    selected, metadata = service.select(
        X,
        y,
        MLProblemType.CLASSIFICATION,
        {"redundancy": True, "correlationThreshold": 0.95},
    )

    assert "age" in selected.columns
    assert "age_copy" not in selected.columns
    assert any(item["reason"].startswith("REDUNDANT_CORRELATION") for item in metadata["removedFeatures"])


def test_feature_selection_rejects_a_dataset_with_no_usable_features():
    service = FeatureSelectionService()
    X = pd.DataFrame({"constant": [1, 1, 1, 1]})
    y = pd.Series([0, 1, 0, 1])

    with pytest.raises(ValueError, match="removed all feature columns"):
        service.select(X, y, MLProblemType.CLASSIFICATION)

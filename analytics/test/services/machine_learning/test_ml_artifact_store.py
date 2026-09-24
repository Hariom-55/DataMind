import json

from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from app.services.machine_learning.ml_artifact_store import MLArtifactStore


def test_ml_artifact_store_persists_reproducibility_artifacts(tmp_path):
    store = MLArtifactStore(tmp_path)
    pipeline = Pipeline([
        ("preprocessor", StandardScaler()),
        ("model", LinearRegression()),
    ])

    run_id = store.create_run("job-123")
    result = store.save(
        run_id,
        pipeline,
        {
            "method": "DETERMINISTIC_FILTERS",
            "selectedFeatures": ["age"],
            "removedFeatures": [],
            "configuration": {"constant": True},
        },
        {"targetColumn": "sales", "problemType": "REGRESSION"},
        {"r2Score": 0.91},
    )

    run_dir = tmp_path / run_id
    assert (run_dir / "model.joblib").exists()
    assert (run_dir / "preprocessor.joblib").exists()
    assert (run_dir / "feature_selector.joblib").exists()
    assert (run_dir / "metadata.json").exists()
    assert result["runId"] == run_id
    assert result["artifactErrors"] == {}

    metadata = json.loads((run_dir / "metadata.json").read_text())
    assert metadata["featureSelection"]["selectedFeatures"] == ["age"]
    assert metadata["trainingConfiguration"]["targetColumn"] == "sales"

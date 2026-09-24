from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

import joblib
from pickle import PicklingError


class MLArtifactStore:
    """Filesystem artifact store for V1 ML run artifacts.

    The store is intentionally isolated behind this class so production object
    storage can replace it later without changing the ML orchestration layer.
    """

    def __init__(self, directory: str | Path | None = None):
        self.directory = Path(
            directory
            or os.getenv(
                "DATAMIND_ML_ARTIFACT_DIR",
                str(Path(os.getenv("TEMP", "/tmp")) / "datamind-ml-artifacts"),
            )
        )
        self.directory.mkdir(parents=True, exist_ok=True)

    def create_run(self, job_id: UUID | str | None = None) -> str:
        return str(job_id or uuid4())

    def save(
        self,
        run_id: str,
        pipeline,
        feature_selection: dict,
        training_configuration: dict,
        metrics: dict,
    ) -> dict:
        run_dir = self.directory / str(run_id)
        run_dir.mkdir(parents=True, exist_ok=True)

        artifact_errors = {}
        try:
            joblib.dump(pipeline, run_dir / "model.joblib")
        except (PicklingError, TypeError, AttributeError) as exc:
            artifact_errors["model"] = str(exc)

        try:
            joblib.dump(
                pipeline.named_steps.get("preprocessor"),
                run_dir / "preprocessor.joblib",
            )
        except (PicklingError, TypeError, AttributeError) as exc:
            artifact_errors["preprocessor"] = str(exc)

        joblib.dump(feature_selection, run_dir / "feature_selector.joblib")

        metadata = {
            "runId": str(run_id),
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "trainingConfiguration": training_configuration,
            "featureSelection": feature_selection,
            "metrics": metrics,
            "artifacts": {
                "model": "model.joblib",
                "preprocessor": "preprocessor.joblib",
                "featureSelector": "feature_selector.joblib",
                "metadata": "metadata.json",
            },
            "artifactErrors": artifact_errors,
        }
        (run_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2, default=str),
            encoding="utf-8",
        )
        return {
            "runId": str(run_id),
            "storage": "FILESYSTEM",
            "artifacts": metadata["artifacts"],
            "artifactErrors": artifact_errors,
            "createdAt": metadata["createdAt"],
        }

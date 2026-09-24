import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID, uuid4


class CleaningArtifactStore:
    """Short-lived local storage used to transfer cleaned files to Java."""

    def __init__(self, directory: str | Path | None = None, retention_hours: int = 24):
        configured_directory = directory or os.getenv(
            "DATAMIND_ARTIFACT_DIR",
            str(Path(tempfile.gettempdir()) / "datamind-cleaning-artifacts"),
        )
        self.directory = Path(configured_directory).resolve()
        self.retention = timedelta(hours=retention_hours)

    def store(self, content: bytes) -> str:
        self.directory.mkdir(parents=True, exist_ok=True)
        self.cleanup_expired()
        artifact_id = uuid4()
        self.path_for(artifact_id).write_bytes(content)
        return str(artifact_id)

    def path_for(self, artifact_id: str | UUID) -> Path:
        safe_id = UUID(str(artifact_id))
        artifact_path = self.directory / f"{safe_id}.csv"
        if artifact_path.exists():
            modified = datetime.fromtimestamp(artifact_path.stat().st_mtime, timezone.utc)
            if modified < datetime.now(timezone.utc) - self.retention:
                artifact_path.unlink(missing_ok=True)
        return artifact_path

    def delete(self, artifact_id: str | UUID) -> None:
        self.path_for(artifact_id).unlink(missing_ok=True)

    def cleanup_expired(self) -> None:
        cutoff = datetime.now(timezone.utc) - self.retention
        for artifact in self.directory.glob("*.csv"):
            modified = datetime.fromtimestamp(artifact.stat().st_mtime, timezone.utc)
            if modified < cutoff:
                artifact.unlink(missing_ok=True)

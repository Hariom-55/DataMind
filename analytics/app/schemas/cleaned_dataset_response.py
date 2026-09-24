from dataclasses import dataclass


@dataclass
class CleanedDatasetResponse:

    artifact_id: str
    sha256: str
    extension: str
    format: str
    content_type: str
    size_bytes: int

    original_rows: int
    cleaned_rows: int

    original_columns: int
    cleaned_columns: int

    operations_applied: int
    changes: list

from dataclasses import dataclass


@dataclass
class CleanedDatasetResponse:

    content: str
    content_hash: str
    extension: str

    original_rows: int
    cleaned_rows: int

    original_columns: int
    cleaned_columns: int

    operations_applied: int
    changes: list
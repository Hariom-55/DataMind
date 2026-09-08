from dataclasses import dataclass
from typing import Any



@dataclass
class CleanedDatasetResult:

    content: bytes
    content_hash: str
    extension: str

    original_rows: int
    cleaned_rows: int

    original_columns: int
    cleaned_columns: int

    operations_applied: int
    changes: list[dict[str, Any]]
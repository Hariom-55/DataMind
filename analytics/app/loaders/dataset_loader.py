from pathlib import Path

import pandas as pd

class DatasetLoader:

    MIME_TYPE_MAP = {
        "text/csv": ".csv",
        "application/json": ".json",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        "application/vnd.ms-excel": ".xls",
        "application/x-parquet": ".parquet",
    }

    SUPPORTED_EXTENSIONS = {
        ".csv",
        ".xlsx",
        ".xls",
        ".json",
        ".parquet",
    }

    def load(self, dataset_path: str, file_type: str | None = None) -> pd.DataFrame:

        path = Path(dataset_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Dataset file not found: {dataset_path}"
            )

        extension = path.suffix.lower()

        if file_type:
            extension = self.MIME_TYPE_MAP.get(file_type, extension)

        if extension == ".csv":
            return pd.read_csv(path)

        if extension in {".xlsx", ".xls"}:
            return pd.read_excel(path)

        if extension == ".json":
            return pd.read_json(path)

        if extension == ".parquet":
            return pd.read_parquet(path)

        raise ValueError(
            f"Unsupported dataset format: {extension or 'unknown'}"
        )
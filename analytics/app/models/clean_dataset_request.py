from pydantic import BaseModel, Field


class CleanDatasetRequest(BaseModel):

    dataset_id: str

    dataset_path: str

    operations: list[dict] = Field(
        default_factory=list
    )

    extension: str = "csv"
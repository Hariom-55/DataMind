from typing import Any

from pydantic import AliasChoices, BaseModel, Field, model_validator


class CleaningOperation(BaseModel):
    operation: str = Field(min_length=1, max_length=64)
    column: str | None = Field(default=None, max_length=255)
    parameters: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_parameters(self):
        operation_parameters = {
            "IMPUTE_MISSING_VALUES": {"strategy", "value"},
            "NORMALIZE_CATEGORIES": {"trim", "lowercase"},
        }
        allowed = operation_parameters.get(self.operation, set())
        unknown = set(self.parameters) - allowed
        if unknown:
            raise ValueError(
                f"Unsupported parameters for {self.operation}: {', '.join(sorted(unknown))}"
            )
        if self.operation == "IMPUTE_MISSING_VALUES":
            strategy = self.parameters.get("strategy", "AUTO")
            if strategy not in {"AUTO", "MEDIAN", "MEAN", "MODE", "CONSTANT"}:
                raise ValueError("Imputation strategy must be AUTO, MEDIAN, MEAN, MODE, or CONSTANT")
            if strategy == "CONSTANT" and "value" not in self.parameters:
                raise ValueError("A value is required for CONSTANT imputation")
            if strategy != "CONSTANT" and "value" in self.parameters:
                raise ValueError("A value can only be supplied for CONSTANT imputation")
        if self.operation == "NORMALIZE_CATEGORIES" and any(
            not isinstance(value, bool) for value in self.parameters.values()
        ):
            raise ValueError("Category normalization parameters must be booleans")
        return self


class CleanDatasetRequest(BaseModel):

    dataset_version_id: str = Field(
        validation_alias=AliasChoices("dataset_version_id", "dataset_id")
    )

    dataset_path: str

    operations: list[CleaningOperation] = Field(
        default_factory=list
    )

    extension: str = "csv"

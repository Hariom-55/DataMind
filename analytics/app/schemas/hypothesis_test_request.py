from typing import Literal

from pydantic import BaseModel, Field, model_validator


class HypothesisTestRequest(BaseModel):
    test: Literal[
        "ONE_SAMPLE_T_TEST",
        "INDEPENDENT_T_TEST",
        "PAIRED_T_TEST",
        "CHI_SQUARE_INDEPENDENCE",
    ]
    column: str | None = None
    valueColumn: str | None = None
    groupColumn: str | None = None
    column1: str | None = None
    column2: str | None = None
    referenceValue: float | None = None
    alpha: float = Field(default=0.05, gt=0, lt=1)

    @model_validator(mode="after")
    def validate_test_columns(self):
        requirements = {
            "ONE_SAMPLE_T_TEST": ("column", "referenceValue"),
            "INDEPENDENT_T_TEST": ("valueColumn", "groupColumn"),
            "PAIRED_T_TEST": ("column1", "column2"),
            "CHI_SQUARE_INDEPENDENCE": ("column1", "column2"),
        }
        missing = [name for name in requirements[self.test] if getattr(self, name) is None]
        if missing:
            raise ValueError(f"{self.test} requires: {', '.join(missing)}")
        return self

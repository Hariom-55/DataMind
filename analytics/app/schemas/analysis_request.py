
from uuid import UUID
from pydantic import AliasChoices, BaseModel, Field

from app.models.analysis_type import AnalysisType
from app.schemas.hypothesis_test_request import HypothesisTestRequest


class AnalysisRequest(BaseModel):
    jobId: UUID
    datasetVersionId: UUID = Field(
        validation_alias=AliasChoices("datasetVersionId", "datasetId")
    )
    analysisType: AnalysisType
    datasetPath: str 
    fileType: str | None = None
    targetColumn: str | None= None
    enableHyperparameterTuning: bool = False
    hypothesisTests: list[HypothesisTestRequest] = Field(default_factory=list, max_length=10)
    featureSelectionConfiguration: dict | None = None

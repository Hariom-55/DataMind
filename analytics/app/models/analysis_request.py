from uuid import UUID
from pydantic import BaseModel

from app.models.analysis_type import AnalysisType

class AnalysisRequest(BaseModel):
    jobId: UUID
    datasetId: UUID
    analysisType: AnalysisType
    datasetPath: str
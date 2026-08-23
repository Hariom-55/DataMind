from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel 

router = APIRouter()

class AnalysisRequest(BaseModel):
    jobId: UUID
    datasetId: UUID
    analysisType: str

@router.post("/internal/analyze")
def analyze(request: AnalysisRequest):

    return {
        "status" : "RECEIVED",
        "result" : {
            "jobId" : str(request.jobId),
            "datasetId" : str(request.datasetId),
            "analysisType" : request.analysisType
        },
        "error" : None
    }
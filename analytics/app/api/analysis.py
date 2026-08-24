
from uuid import UUID
from pathlib import Path
from fastapi import APIRouter,HTTPException
from pydantic import BaseModel 
from app.services.eda_service import EDAService

router = APIRouter()
eda_service = EDAService()

class AnalysisRequest(BaseModel):
    jobId: UUID
    datasetId: UUID
    analysisType: str
    datasetPath: str

@router.post("/internal/analyze")
def analyze(request: AnalysisRequest):

    dataset_path = Path(request.datasetPath)

    if not dataset_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Dataset file not found"
        )

    if request.analysisType != "EDA":
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported analysis type :{request.analysisType}"
        )

    try:
        result = eda_service.analyze(str(dataset_path))

        return {
            "status": "COMPLETED",
            "result": result,
            "error":None
        }

    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )


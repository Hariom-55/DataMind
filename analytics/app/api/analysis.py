
from uuid import UUID
from pathlib import Path
from fastapi import APIRouter,HTTPException

from app.models.analysis_request import AnalysisRequest
from app.services.eda_service import EDAService
from app.services.statistical_service import StatisticalAnalysisService
from app.models.analysis_response import AnalysisResponse


router = APIRouter()
eda_service = EDAService()
statistical_service = StatisticalAnalysisService()




@router.post("/internal/analyze")
def analyze(request: AnalysisRequest):

    dataset_path = Path(request.datasetPath)

    if not dataset_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Dataset file not found"
        )

    try:

        if request.analysisType == "EDA":

            result = eda_service.analyze(
                str(dataset_path)
            )

        elif request.analysisType == "STATISTICAL":

            result = statistical_service.analyze(
                str(dataset_path)
            )

        else:

            raise HTTPException(
                status_code=400,
                detail=f"Unsupported analysis type: {request.analysisType}"
            )

    except HTTPException:
        raise

    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )

    return {
        "status": "COMPLETED",
        "result":result,
        "error": None
    }


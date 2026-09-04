
from uuid import UUID
from pathlib import Path
from fastapi import APIRouter,HTTPException

from app.models.analysis_request import AnalysisRequest
from app.services.eda_service import EDAService
from app.services.statistical_service import StatisticalAnalysisService
from app.services.analysis_registry import AnalysisRegistry
from app.loaders.dataset_loader import DatasetLoader
from app.services.data_quality_service import DataQualityService
from app.services.ml_analysis_service import MLAnalysisService

router = APIRouter()

dataset_loader = DatasetLoader()
data_quality_service = DataQualityService()
eda_service = EDAService(dataset_loader, data_quality_service)
statistical_service = StatisticalAnalysisService(dataset_loader)
analysis_registry = AnalysisRegistry()
ml_analysis_service = MLAnalysisService(dataset_loader)

analysis_registry.register(
    "EDA",
    eda_service
)

analysis_registry.register(
    "STATISTICAL",
    statistical_service
)

analysis_registry.register(
    "MACHINE_LEARNING",
    ml_analysis_service
)

@router.post("/internal/analyze")
def analyze(request: AnalysisRequest):

    dataset_path = Path(request.datasetPath)

    if not dataset_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Dataset file not found"
        )

    try:

        service = analysis_registry.get_service(
            request.analysisType.value
        )

        result = service.analyze(
            str(dataset_path),
            request.fileType,
            request.targetColumn
        )

    except ValueError as ex:
        raise HTTPException(
            status_code=400,
            detail=str(ex)
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


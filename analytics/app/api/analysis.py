
from uuid import UUID
from pathlib import Path
from fastapi import APIRouter, HTTPException

from app.schemas.analysis_request import AnalysisRequest
from app.services.profiling.eda_service import EDAService
from app.services.statistical.statistical_service import StatisticalAnalysisService
from app.registry.analysis_registry import AnalysisRegistry
from app.loaders.dataset_loader import DatasetLoader
from app.services.profiling.data_quality_service import DataQualityService
from app.services.machine_learning.ml_analysis_service import MLAnalysisService
from app.schemas.clean_dataset_request import CleanDatasetRequest
from app.services.cleaning.dataset_cleaning_service import DatasetCleaningService
from app.services.cleaning.cleaning_workflow_service import DataCleaningWorkflowService
from app.services.profiling.data_quality_service import DataQualityService
from app.services.cleaning.cleaning_service import DataCleaningService
from app.services.cleaning.cleaned_dataset_response_service import CleanedDatasetResponseService
from app.services.insight.insight_engine import InsightEngine
from app.services.insight.insight_orchestration_service import InsightOrchestrationService


router = APIRouter()

#shared services
dataset_loader = DatasetLoader()
data_quality_service = DataQualityService()
eda_service = EDAService(dataset_loader, data_quality_service)
statistical_service = StatisticalAnalysisService(dataset_loader)
analysis_registry = AnalysisRegistry()
ml_analysis_service = MLAnalysisService(dataset_loader)
insight_engine = InsightEngine()

insight_orchestration_service = InsightOrchestrationService(
    eda_service,
    statistical_service,
    ml_analysis_service,
    insight_engine
)


#analysis registry
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

analysis_registry.register(
    "INSIGHT",
    insight_orchestration_service
)


# Data Cleaning service
cleaning_service = DataCleaningService()
cleaning_workflow_service = DataCleaningWorkflowService(cleaning_service)

cleaned_dataset_response_service = CleanedDatasetResponseService()

dataset_cleaning_service = DatasetCleaningService(dataset_loader, cleaning_workflow_service, cleaned_dataset_response_service)


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

#cleaning endpoint 

@router.post("/internal/clean")
def clean_dataset(request: CleanDatasetRequest):
    dataset_path = Path(request.dataset_path)

    if not dataset_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Dataset file not found"
        )

    try:
        return dataset_cleaning_service.clean_dataset(request)

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



from uuid import UUID
from pathlib import Path
import logging
from fastapi import APIRouter,Depends, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from uuid import UUID

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
from app.services.cleaning.cleaned_dataset_response_service import CleanedDatasetResponseService
from app.services.cleaning.cleaning_artifact_store import CleaningArtifactStore
from app.services.insight.insight_engine import InsightEngine
from app.services.insight.insight_orchestration_service import InsightOrchestrationService
from app.services.visualization.visualization_orchestration_service import VisualizationOrchestrationService
from app.core.analysis import require_internal_api_key

router = APIRouter(
    dependencies=[Depends(require_internal_api_key)]
)
logger = logging.getLogger(__name__)

#shared services
dataset_loader = DatasetLoader()
data_quality_service = DataQualityService()
eda_service = EDAService(dataset_loader, data_quality_service)
statistical_service = StatisticalAnalysisService(dataset_loader)
analysis_registry = AnalysisRegistry()
ml_analysis_service = MLAnalysisService(dataset_loader)
insight_engine = InsightEngine()
visualization_service = VisualizationOrchestrationService()

insight_orchestration_service = InsightOrchestrationService(
    eda_service,
    statistical_service,
    ml_analysis_service,
    insight_engine,
    visualization_service

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


# Quality detection, recommendations, and data changes have separate owners.
cleaning_workflow_service = DataCleaningWorkflowService(data_quality_service)

cleaning_artifact_store = CleaningArtifactStore()
cleaned_dataset_response_service = CleanedDatasetResponseService(cleaning_artifact_store)

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

        if request.analysisType.value == "MACHINE_LEARNING":
            result = service.analyze(
                str(dataset_path),
                request.fileType,
                request.targetColumn,
                enable_hyperparameter_tuning=request.enableHyperparameterTuning,
                job_id=request.jobId,
                feature_selection_configuration=request.featureSelectionConfiguration,
            )
        elif request.analysisType.value == "STATISTICAL":
            result = service.analyze(
                str(dataset_path),
                request.fileType,
                request.targetColumn,
                request.hypothesisTests,
            )
        else:
            result = service.analyze(
                str(dataset_path),
                request.fileType,
                request.targetColumn
            )

        # Individual analysis services return domain results directly. Add
        # visualization specs here so the specialized dashboards receive the
        # same renderable contract as INSIGHT analysis.
        visualization_key = {
            "EDA": "eda",
            "STATISTICAL": "statistical",
            "MACHINE_LEARNING": "machineLearning",
        }.get(request.analysisType.value)
        if visualization_key and isinstance(result, dict):
            generated = visualization_service.generate({visualization_key: result})
            result = {**result, "visualizations": generated["visualizations"]}

    except ValueError as ex:
        raise HTTPException(
            status_code=400,
            detail=str(ex)
        )


    except HTTPException:
        raise

    except Exception as ex:
        logger.exception("Analysis request failed")
        raise HTTPException(
            status_code=500,
            detail="Analysis failed"
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
        logger.exception("Cleaning request failed")
        raise HTTPException(
            status_code=500,
            detail="Cleaning failed"
        )


@router.get("/internal/artifacts/{artifact_id}")
def download_cleaning_artifact(artifact_id: UUID):
    artifact_path = cleaning_artifact_store.path_for(artifact_id)
    if not artifact_path.is_file():
        raise HTTPException(status_code=404, detail="Cleaning artifact not found")
    return FileResponse(
        artifact_path,
        media_type="text/csv",
        filename=f"{artifact_id}.csv",
        background=BackgroundTask(cleaning_artifact_store.delete, artifact_id),
    )


@router.post("/internal/clean/assessment")
def assess_cleaning(request: CleanDatasetRequest):
    dataset_path = Path(request.dataset_path)

    if not dataset_path.exists():
        raise HTTPException(status_code=404, detail="Dataset file not found")

    try:
        df = dataset_loader.load(str(dataset_path))
        return cleaning_workflow_service.assess_dataset(df)
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except Exception as ex:
        logger.exception("Cleaning assessment failed")
        raise HTTPException(status_code=500, detail="Cleaning assessment failed")


@router.post("/internal/clean/preview")
def preview_cleaning(request: CleanDatasetRequest):
    dataset_path = Path(request.dataset_path)

    if not dataset_path.exists():
        raise HTTPException(status_code=404, detail="Dataset file not found")
    if not request.operations:
        raise HTTPException(status_code=400, detail="At least one cleaning operation is required")

    try:
        df = dataset_loader.load(str(dataset_path))
        result = cleaning_workflow_service.clean_dataset(df, request.operations)
        return {
            "originalRows": result["originalRows"],
            "cleanedRows": result["cleanedRows"],
            "originalColumns": result["originalColumns"],
            "cleanedColumns": result["cleanedColumns"],
            "operationsApplied": result["operationsApplied"],
            "changes": result["changes"],
        }
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except Exception as ex:
        logger.exception("Cleaning preview failed")
        raise HTTPException(status_code=500, detail="Cleaning preview failed")


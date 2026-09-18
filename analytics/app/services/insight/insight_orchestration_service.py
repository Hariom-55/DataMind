from app.core.analysis_service import AnalysisService
from app.services.insight.insight_engine import InsightEngine
from app.services.machine_learning.ml_analysis_service import MLAnalysisService
from app.services.profiling.eda_service import EDAService
from app.services.statistical.statistical_service import StatisticalAnalysisService
from app.services.visualization.visualization_orchestration_service import VisualizationOrchestrationService

class InsightOrchestrationService(AnalysisService):

    def __init__(
        self,
        eda_service: EDAService,
        statistical_service: StatisticalAnalysisService,
        ml_service: MLAnalysisService,
        insight_engine: InsightEngine,
        visualization_service: VisualizationOrchestrationService,
    ):

        self.eda_service = eda_service
        self.statistical_service = statistical_service
        self.ml_service = ml_service
        self.insight_engine = insight_engine
        self.visualization_service = visualization_service

    def analyze(
        self,
        dataset_path: str,
        file_type: str | None = None,
        target_column: str | None = None
    ) -> dict:

        analysis_results = {}

        eda_result = self.eda_service.analyze(
            dataset_path,
            file_type,
            target_column
        )

        analysis_results["eda"] = eda_result

   

        statistical_result = (
            self.statistical_service.analyze(
                dataset_path,
                file_type,
                target_column
            )
        )

        analysis_results["statistical"] = (
            statistical_result
        )

     
        if target_column:

            ml_result = self.ml_service.analyze(
                dataset_path,
                file_type,
                target_column
            )

            analysis_results["machineLearning"] = (
                ml_result
            )

        insight_result = self.insight_engine.generate(
            analysis_results
        )


        visualization_result = (
            self.visualization_service.generate(
                analysis_results
            )
        )

        return {
            "analysis": analysis_results,
            "insights": insight_result,
            "visualizations": visualization_result,
        }
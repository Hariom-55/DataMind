from app.loaders.dataset_loader import DatasetLoader
from app.core.analysis_service import AnalysisService
from app.services.statistical.descriptive_service import DescriptiveStatisticsService
from app.services.statistical.correlation_service import CorrelationService


class StatisticalAnalysisService(AnalysisService):

    def __init__(self, dataset_loader: DatasetLoader):
        self.dataset_loader = dataset_loader
        self.descriptive_service = DescriptiveStatisticsService()
        self.correlation_service = CorrelationService()

    def analyze(
            self,
            dataset_path: str,
            file_type: str | None = None,
            target_column: str | None = None
    ) -> dict:
        # target_column is accepted (and unused) only to satisfy the shared
        # AnalysisService interface

        #1.Load Dataset
        df = self.dataset_loader.load(dataset_path, file_type=file_type)

        #2.Select numerical columns
        numeric_df = df.select_dtypes(include="number")

        #3. Descriptive statistics - delegated
        descriptive_statistics = self.descriptive_service.calculate(numeric_df)

        #4. Correlation matrices + analysis - delegated
        correlation_result = self.correlation_service.calculate(numeric_df)

        return {
            "descriptiveStatistics": descriptive_statistics,
            "correlations": {
                "pearson": correlation_result["pearson"],
                "spearman": correlation_result["spearman"]
            },
            "correlationAnalysis": correlation_result["correlationAnalysis"]
        }

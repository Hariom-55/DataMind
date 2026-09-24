from app.loaders.dataset_loader import DatasetLoader
from app.core.analysis_service import AnalysisService
from app.services.statistical.descriptive_service import DescriptiveStatisticsService
from app.services.statistical.correlation_service import CorrelationService
from app.services.statistical.distribution_service import DistributionAnalysisService
from app.services.statistical.hypothesis_service import HypothesisTestingService


class StatisticalAnalysisService(AnalysisService):
    CONTRACT_VERSION = "v1"

    def __init__(self, dataset_loader: DatasetLoader):
        self.dataset_loader = dataset_loader
        self.descriptive_service = DescriptiveStatisticsService()
        self.correlation_service = CorrelationService()
        self.distribution_service = DistributionAnalysisService()
        self.hypothesis_service = HypothesisTestingService()

    def analyze(
        self,
        dataset_path: str,
        file_type: str | None = None,
        target_column: str | None = None,
        hypothesis_tests: list[dict] | None = None,
    ) -> dict:
        df = self.dataset_loader.load(dataset_path, file_type=file_type)
        numeric_df = df.select_dtypes(include="number")

        descriptive_statistics = self.descriptive_service.calculate(numeric_df)
        correlation_result = self.correlation_service.calculate(numeric_df)
        distribution_result = self.distribution_service.analyze(numeric_df)
        hypothesis_results = [
            self._run_hypothesis_test(df, test)
            for test in (hypothesis_tests or [])
        ]

        return {
            "contractVersion": self.CONTRACT_VERSION,
            "sampleSize": int(len(df)),
            "numericColumnCount": int(numeric_df.shape[1]),
            "excludedNonNumericColumns": [
                column for column in df.columns if column not in numeric_df.columns
            ],
            "descriptiveStatistics": descriptive_statistics,
            "correlations": {
                "pearson": correlation_result["pearson"],
                "spearman": correlation_result["spearman"],
            },
            "correlationAnalysis": correlation_result["correlationAnalysis"],
            "distributions": distribution_result["distributions"],
            "hypothesisTests": hypothesis_results,
        }

    def _run_hypothesis_test(self, df, request: dict) -> dict:
        if hasattr(request, "model_dump"):
            request = request.model_dump(exclude_none=True)
        test_type = request["test"]
        alpha = request.get("alpha", 0.05)
        if test_type == "ONE_SAMPLE_T_TEST":
            return self.hypothesis_service.perform_one_sample_t_test(
                df, request["column"], request["referenceValue"], alpha
            )
        if test_type == "INDEPENDENT_T_TEST":
            return self.hypothesis_service.perform_independent_t_test(
                df, request["valueColumn"], request["groupColumn"], alpha
            )
        if test_type == "PAIRED_T_TEST":
            return self.hypothesis_service.perform_paired_t_test(
                df, request["column1"], request["column2"], alpha
            )
        if test_type == "CHI_SQUARE_INDEPENDENCE":
            return self.hypothesis_service.perform_chi_square_test(
                df, request["column1"], request["column2"], alpha
            )
        raise ValueError(f"Unsupported hypothesis test: {test_type}")

from app.services.visualization.eda_visualization_generator import EDAVisualizationGenerator
from app.services.visualization.distribution_visualization_generator import DistributionVisualizationGenerator
from app.services.visualization.ml_visualization_generator import MLVisualizationGenerator
from app.services.visualization.statistical_visualization_generator import StatisticalVisualizationGenerator



class VisualizationOrchestrationService:

    def __init__(
        self,
        eda_generator: EDAVisualizationGenerator | None = None,
        statistical_generator: StatisticalVisualizationGenerator | None = None,
        distribution_generator: DistributionVisualizationGenerator | None = None,
        ml_generator: MLVisualizationGenerator | None = None,
    ):
        self.eda_generator = (
            eda_generator
            if eda_generator is not None
            else EDAVisualizationGenerator()
        )

        self.statistical_generator = (
            statistical_generator
            if statistical_generator is not None
            else StatisticalVisualizationGenerator()
        )

        self.distribution_generator = (
            distribution_generator
            if distribution_generator is not None
            else DistributionVisualizationGenerator()
        )

        self.ml_generator = (
            ml_generator
            if ml_generator is not None
            else MLVisualizationGenerator()
        )

    def generate(
        self,
        analysis_results: dict
    ) -> dict:

        if not isinstance(analysis_results, dict):
            raise ValueError(
                "analysis_results must be a dictionary"
            )

        visualizations = []

        # EDA visualizations
        eda_results = analysis_results.get("eda")

        if eda_results is not None:
            visualizations.extend(
                self.eda_generator.generate(
                    eda_results
                )
            )

        # Statistical + Distribution visualizations
        statistical_results = analysis_results.get(
            "statistical"
        )

        if statistical_results is not None:

            visualizations.extend(
                self.statistical_generator.generate(
                    statistical_results
                )
            )

            visualizations.extend(
                self.distribution_generator.generate(
                    statistical_results
                )
            )

        # Machine Learning visualizations
        ml_results = analysis_results.get(
            "machineLearning"
        )

        if ml_results is not None:
            visualizations.extend(
                self.ml_generator.generate(
                    ml_results
                )
            )

        return {
            "visualizations": visualizations
        }
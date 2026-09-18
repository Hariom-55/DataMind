import pytest

from app.services.visualization.statistical_visualization_generator import StatisticalVisualizationGenerator
from app.services.visualization.visualization_types import VisualizationType

class TestStatisticalVisualizationGenerator:

    def setup_method(self):
        self.generator = StatisticalVisualizationGenerator()

    def test_should_generate_pearson_correlation_heatmap(self):

        analysis_results = {
            "correlations": {
                "pearson": {
                    "age": {
                        "age": 1.0,
                        "salary": 0.95,
                    },
                    "salary": {
                        "age": 0.95,
                        "salary": 1.0,
                    },
                },
                "spearman": {}
            },
            "correlationAnalysis": {
                "pearson": {},
                "spearman": {}
            },
            "descriptiveStatistics": {},
            "distributions": {},
        }

        result = self.generator.generate(analysis_results)

        heatmaps = [
            visualization
            for visualization in result
            if visualization["metadata"].get("metric") == "pearson"
        ]

        assert len(heatmaps) == 1

        visualization = heatmaps[0]

        assert visualization["type"] == VisualizationType.HEATMAP.value
        assert visualization["title"] == "Pearson Correlation Matrix"
        assert visualization["metadata"]["source"] == "STATISTICS"
        assert visualization["metadata"]["metric"] == "pearson"

    def test_should_generate_spearman_correlation_heatmap(self):

        analysis_results = {
            "correlations": {
                "pearson": {},
                "spearman": {
                    "age": {
                        "age": 1.0,
                        "salary": 0.90,
                    },
                    "salary": {
                        "age": 0.90,
                        "salary": 1.0,
                    },
                },
            },
            "correlationAnalysis": {
                "pearson": {},
                "spearman": {},
            },
            "descriptiveStatistics": {},
            "distributions": {},
        }



        result = self.generator.generate(analysis_results)

        heatmaps = [
            visualization
            for visualization in result
            if visualization["metadata"].get("metric") == "spearman"
        ]

        assert len(heatmaps) == 1

        visualization = heatmaps[0]

        assert visualization["type"] == VisualizationType.HEATMAP.value
        assert visualization["title"] == "Spearman Correlation Matrix"

    def test_should_preserve_correlation_matrix_values(self):

        analysis_results = {
            "correlations": {
                "pearson": {
                    "age": {
                        "age": 1.0,
                        "salary": 0.95,
                    },
                    "salary": {
                        "age": 0.95,
                        "salary": 1.0,
                    },
                },
                "spearman": {},
            },
            "correlationAnalysis": {
                "pearson": {},
                "spearman": {},
            },
            "descriptiveStatistics": {},
            "distributions": {},
        }


        result = self.generator.generate(analysis_results)

        visualization = result[0]

        assert visualization["data"] == [
            {
                "row": "age",
                "age": 1.0,
                "salary": 0.95,
            },
            {
                "row": "salary",
                "age": 0.95,
                "salary": 1.0,
            },
        ]

    def test_should_not_generate_heatmap_when_correlation_is_empty(self):

        analysis_results = {
            "correlations": {
                "pearson": {},
                "spearman": {},
            },
            "correlationAnalysis": {
                "pearson": {},
                "spearman": {},
            },
            "descriptiveStatistics": {},
            "distributions": {},
        }

        result = self.generator.generate(analysis_results)

        assert result == []

    def test_should_not_mutate_analysis_results(self):

        analysis_results = {
            "correlations": {
                "pearson": {
                    "age": {
                        "age": 1.0,
                        "salary": 0.95,
                    },
                    "salary": {
                        "age": 0.95,
                        "salary": 1.0,
                    },
                },
                "spearman": {},
            },
            "correlationAnalysis": {
                "pearson": {},
                "spearman": {},
            },
            "descriptiveStatistics": {},
            "distributions": {},
        }

        original = {
            "correlations": {
                "pearson": {
                    "age": {
                        "age": 1.0,
                        "salary": 0.95,
                    },
                    "salary": {
                        "age": 0.95,
                        "salary": 1.0,
                    },
                },
                "spearman": {},
            },
            "correlationAnalysis": {
                "pearson": {},
                "spearman": {},
            },
            "descriptiveStatistics": {},
            "distributions": {},
        }


        self.generator.generate(analysis_results)

        assert analysis_results == original


    def test_should_reject_invalid_analysis_results(self):

        with pytest.raises(ValueError):
            self.generator.generate([])  # type: ignore[arg-type]
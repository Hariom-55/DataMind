from app.services.visualization.eda_visualization_generator import EDAVisualizationGenerator
from app.services.visualization.visualization_types import VisualizationType
from app.services.visualization.visualization_generator import VisualizationGenerator


class TestEdaVisualizationGenerator:
    def setup_method(self):
        self.generate = EDAVisualizationGenerator()

    def test_should_generate_missing_values_visualization(self):

        analysis_results = {
            "missingValues": {
                "name": 0,
                "age": 2,
                "salary": 5,
            },
            "missingPercentages": {
                "name": 0.0,
                "age": 20.0,
                "salary": 50.0,
            },
            "numericStatistics": {},
            "categoricalStatistics": {},
        }

        result = self.generate.generate(analysis_results)

        assert len(result) == 1

        visualization = result[0]

        assert visualization["type"] == VisualizationType.BAR.value
        assert visualization["title"] == "Missing Values by Column"
        assert visualization["x"] == "column"
        assert visualization["y"] == "missingCount"

        assert visualization["data"] == [
            {
                "column": "name",
                "missingCount": 0,
                "missingPercentage": 0.0,
            },
            {
                "column": "age",
                "missingCount": 2,
                "missingPercentage": 20.0,
            },
            {
                "column": "salary",
                "missingCount": 5,
                "missingPercentage": 50.0,
            },
        ]

    def test_should_generate_numeric_distribution_visualizations(self):

        analysis_results = {
            "missingValues": {},
            "missingPercentages": {},
            "numericStatistics": {
                "age": {
                    "count": 5.0,
                    "mean": 30.0,
                    "std": 5.0,
                    "min": 20.0,
                    "25%": 25.0,
                    "50%": 30.0,
                    "75%": 35.0,
                    "max": 40.0,
                },
                "salary": {
                    "count": 5.0,
                    "mean": 30000.0,
                    "std": 5000.0,
                    "min": 20000.0,
                    "25%": 25000.0,
                    "50%": 30000.0,
                    "75%": 35000.0,
                    "max": 40000.0,
                },
            },
            "categoricalStatistics": {},
        }

        result = self.generate.generate(analysis_results)

        assert len(result) == 2

        assert result[0]["type"] == VisualizationType.HISTOGRAM.value
        assert result[0]["title"] == "Age Distribution"
        assert result[0]["x"] == "age"

        assert result[1]["type"] == VisualizationType.HISTOGRAM.value
        assert result[1]["title"] == "Salary Distribution"
        assert result[1]["x"] == "salary"

    def test_should_generate_categorical_visualization(self):

        analysis_results = {
            "missingValues": {},
            "missingPercentages": {},
            "numericStatistics": {},
            "categoricalStatistics": {
                "city": {
                    "uniqueCount": 3,
                    "topValues": {
                        "Delhi": 10,
                        "Mumbai": 7,
                        "Pune": 3,
                    },
                }
            },
        }

        result = self.generate.generate(analysis_results)

        assert len(result) == 1

        visualization = result[0]

        assert visualization["type"] == VisualizationType.BAR.value
        assert visualization["title"] == "Top Values for City"
        assert visualization["x"] == "value"
        assert visualization["y"] == "count"

        assert visualization["data"] == [
            {
                "value": "Delhi",
                "count": 10,
            },
            {
                "value": "Mumbai",
                "count": 7,
            },
            {
                "value": "Pune",
                "count": 3,
            },
        ]

    def test_should_generate_multiple_eda_visualizations(self):

        analysis_results = {
            "missingValues": {
                "age": 2,
            },
            "missingPercentages": {
                "age": 20.0,
            },
            "numericStatistics": {
                "age": {
                    "count": 5.0,
                    "mean": 30.0,
                }
            },
            "categoricalStatistics": {
                "city": {
                    "uniqueCount": 2,
                    "topValues": {
                        "Delhi": 3,
                        "Mumbai": 2,
                    },
                }
            },
        }

        result = self.generate.generate(analysis_results)

        assert len(result) == 3

        visualization_types = [
            visualization["type"]
            for visualization in result
        ]

        assert VisualizationType.BAR.value in visualization_types
        assert VisualizationType.HISTOGRAM.value in visualization_types

    def test_should_handle_empty_eda_results(self):

        result = self.generate.generate({})

        assert result == []

    def test_should_not_mutate_analysis_results(self):

        analysis_results = {
            "missingValues": {
                "age": 2,
            },
            "missingPercentages": {
                "age": 20.0,
            },
            "numericStatistics": {},
            "categoricalStatistics": {},
        }

        original = {
            "missingValues": {
                "age": 2,
            },
            "missingPercentages": {
                "age": 20.0,
            },
            "numericStatistics": {},
            "categoricalStatistics": {},
        }

        self.generate.generate(analysis_results)

        assert analysis_results == original
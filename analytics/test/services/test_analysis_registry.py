import pytest

from app.services.analysis_service import AnalysisService
from app.services.analysis_registry import AnalysisRegistry

class FakeAnalysisService(AnalysisService):

    def analyze(
            self, 
            dataset_path: str,
            file_type: str | None = None
        ) -> dict:
        return {"status": "ok"}

class TestAnalysisRegistry:

    def setup_method(self):

        self.registry = AnalysisRegistry()
        self.service = FakeAnalysisService()

    def test_should_register_and_retrieve_service(self):

        self.registry.register(
            "EDA",
            self.service
        )

        result = self.registry.get_service("EDA")

        assert result is self.service

    def test_should_raise_error_for_unsupported_analysis_type(self):
        with pytest.raises(
            ValueError,
            match="Unsupported analysis type"
        ):
            self.registry.get_service("UNKNOWN")
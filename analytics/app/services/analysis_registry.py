from app.services.analysis_service import AnalysisService

class AnalysisRegistry:

    def __init__(self):
        self.services: dict[str, AnalysisService] = {}

    def register(
            self,
            analysis_type: str,
            service: AnalysisService
    )-> None:
        self.services[analysis_type] = service

    def get_service(self, analysis_type: str) -> AnalysisService:

        service = self.services.get(analysis_type)

        if service is None:
            raise ValueError(
                f"Unsupported analysis type: {analysis_type}"
            )

        return service
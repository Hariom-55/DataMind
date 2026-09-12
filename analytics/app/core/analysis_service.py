from abc import ABC, abstractmethod

class AnalysisService(ABC):

    @abstractmethod
    def analyze(
        self,
        dataset_path: str,
        file_type: str | None = None,
        target_column: str | None = None
    ) -> dict:
        pass
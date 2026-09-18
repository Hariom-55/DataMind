from abc import ABC, abstractmethod

class VisualizationGenerator(ABC):

    @abstractmethod
    def generate(
        self,
        analysis_results: dict
    ) -> list[dict]:

        raise NotImplementedError
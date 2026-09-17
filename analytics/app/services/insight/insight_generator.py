from abc import ABC , abstractmethod

class InsightGenerator(ABC):

    @abstractmethod
    def generate(self, analysis_result: dict) -> list[dict]:

        raise NotImplementedError
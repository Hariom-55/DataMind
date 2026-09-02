from enum import Enum

class MLProblemType(str, Enum):
    CLASSIFICATION = "CLASSIFICATION"
    REGRESSION = "REGRESSION"
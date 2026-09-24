from app.services.machine_learning.cross_validation_service import CrossValidationService
from app.services.machine_learning.feature_selection_service import FeatureSelectionService
from app.services.machine_learning.hyperparameter_tuning_service import HyperparameterTuningService
from app.services.machine_learning.model_selection_service import ModelSelectionService
from app.services.machine_learning.preprocessing_service import PreprocessingService
from app.services.machine_learning.problem_detection_service import ProblemDetectionService


def test_ml_service_boundaries_are_constructible():
    cv = CrossValidationService()
    assert isinstance(ModelSelectionService(cv), ModelSelectionService)
    assert isinstance(HyperparameterTuningService(cv), HyperparameterTuningService)
    assert isinstance(PreprocessingService(), PreprocessingService)
    assert isinstance(ProblemDetectionService(), ProblemDetectionService)
    assert isinstance(FeatureSelectionService(), FeatureSelectionService)

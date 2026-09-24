from uuid import uuid4

from app.models.analysis_type import AnalysisType
from app.schemas.analysis_request import AnalysisRequest
from app.schemas.clean_dataset_request import CleanDatasetRequest


def test_analysis_request_uses_dataset_version_id_and_accepts_legacy_alias():
    version_id = uuid4()
    common = {
        "jobId": uuid4(),
        "analysisType": AnalysisType.EDA,
        "datasetPath": "dataset.csv",
    }

    canonical = AnalysisRequest(**common, datasetVersionId=version_id)
    legacy = AnalysisRequest(**common, datasetId=version_id)

    assert canonical.datasetVersionId == version_id
    assert legacy.datasetVersionId == version_id


def test_cleaning_request_uses_version_scoped_identifier_and_legacy_alias():
    version_id = str(uuid4())
    common = {"dataset_path": "dataset.csv"}

    canonical = CleanDatasetRequest(**common, dataset_version_id=version_id)
    legacy = CleanDatasetRequest(**common, dataset_id=version_id)

    assert canonical.dataset_version_id == version_id
    assert legacy.dataset_version_id == version_id

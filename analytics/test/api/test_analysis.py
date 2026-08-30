import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.analysis import eda_service


client = TestClient(app)

TEST_JOB_ID = "11111111-1111-1111-1111-111111111111"
TEST_DATASET_ID = "22222222-2222-2222-2222-222222222222"


class TestAnalysisAPI:

    def test_should_run_eda_analysis(self, tmp_path):

        dataset = pd.DataFrame({
            "name": ["Hariom", "Rahul", "Aman"],
            "age": [22, 24, 21]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        response = client.post(
            "/internal/analyze",
            json={
                "jobId": TEST_JOB_ID,
                "datasetId": TEST_DATASET_ID,
                "analysisType": "EDA",
                "datasetPath": str(file_path)
            }
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "COMPLETED"
        assert body["error"] is None

        assert body["result"]["overview"]["rowCount"] == 3
        assert body["result"]["overview"]["columnCount"] == 2


    def test_should_run_statistical_analysis(self, tmp_path):

        dataset = pd.DataFrame({
            "age": [20, 30, 40, 50, 60],
            "salary": [20000, 30000, 40000, 50000, 60000]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        response = client.post(
            "/internal/analyze",
            json={
                "jobId": TEST_JOB_ID,
                "datasetId": TEST_DATASET_ID,
                "analysisType": "STATISTICAL",
                "datasetPath": str(file_path)
            }
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "COMPLETED"
        assert body["error"] is None

        result = body["result"]

        assert "age" in result["descriptiveStatistics"]
        assert "salary" in result["descriptiveStatistics"]

        assert "pearson" in result["correlations"]
        assert "spearman" in result["correlations"]


    def test_should_return_404_when_dataset_does_not_exist(self, tmp_path):

        file_path = tmp_path / "does-not-exist.csv"

        response = client.post(
            "/internal/analyze",
            json={
                "jobId": TEST_JOB_ID,
                "datasetId": TEST_DATASET_ID,
                "analysisType": "EDA",
                "datasetPath": str(file_path)
            }
        )

        assert response.status_code == 404

        body = response.json()

        assert body["detail"] == "Dataset file not found"


    def test_should_return_400_for_unsupported_analysis_type(self, tmp_path):

        dataset = pd.DataFrame({
            "age": [20, 30, 40]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        response = client.post(
            "/internal/analyze",
            json={
                "jobId": TEST_JOB_ID,
                "datasetId": TEST_DATASET_ID,
                "analysisType": "MACHINE_LEARNING",
                "datasetPath": str(file_path)
            }
        )

        assert response.status_code == 400

        body = response.json()

        assert "Unsupported analysis type" in body["detail"]


    def test_should_return_422_for_invalid_request(self):

        response = client.post(
            "/internal/analyze",
            json={
                "jobId": "invalid-id",
                "datasetId": "invalid-id",
                "analysisType": "EDA"
            }
        )

        assert response.status_code == 422


    def test_should_return_500_when_analysis_service_fails(
            self,
            tmp_path,
            monkeypatch
    ):

        dataset = pd.DataFrame({
            "age": [20, 30, 40]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        def failing_analysis(_):
            raise RuntimeError("Analysis service failed")

        monkeypatch.setattr(
            eda_service,
            "analyze",
            failing_analysis
        )

        response = client.post(
            "/internal/analyze",
            json={
                "jobId": TEST_JOB_ID,
                "datasetId": TEST_DATASET_ID,
                "analysisType": "EDA",
                "datasetPath": str(file_path)
            }
        )

        assert response.status_code == 500

        body = response.json()

        assert body["detail"] == "Analysis service failed"
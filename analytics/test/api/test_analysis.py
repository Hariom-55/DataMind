import base64

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.analysis import eda_service, dataset_cleaning_service


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
                "analysisType": "TIME_SERIES",
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

        def failing_analysis(dataset_path: str, file_type: str | None = None, taregt_column = None):
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
                "datasetPath": str(file_path),
                "fileType": "text/csv"
            }
        )

        assert response.status_code == 500
    

        body = response.json()

        assert body["detail"] == "Analysis service failed"

    def test_should_run_eda_analysis_on_xlsx(self, tmp_path):
        dataset = pd.DataFrame({
            "name": ["Hariom", "Rahul", "Amit"],
            "age": [22, 23, 24]
        })

        file_path = tmp_path / "test.xlsx"
        dataset.to_excel(file_path, index=False)

        response = client.post(
            "/internal/analyze",
            json={
                "jobId": str(TEST_JOB_ID),
                "datasetId": str(TEST_DATASET_ID),
                "analysisType": "EDA",
                "datasetPath": str(file_path),
                "fileType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "COMPLETED"
        assert body["result"]["overview"]["rowCount"] == 3
        assert body["result"]["overview"]["columnCount"] == 2    


    def test_should_run_eda_analysis_on_json(self, tmp_path):
        dataset = pd.DataFrame({
            "name": ["Hariom", "Rahul", "Amit"],
            "age": [22, 23, 24]
        })

        file_path = tmp_path / "test.json"
        dataset.to_json(file_path, orient="records")

        response = client.post(
            "/internal/analyze",
            json={
                "jobId": str(TEST_JOB_ID),
                "datasetId": str(TEST_DATASET_ID),
                "analysisType": "EDA",
                "datasetPath": str(file_path),
                "fileType": "application/json"
            }
        )

        assert response.status_code == 200

        body = response.json()

        assert body["status"] == "COMPLETED" 
        assert body["result"]["overview"]["rowCount"] == 3
        assert body["result"]["overview"]["columnCount"] == 2 

    def test_should_clean_dataset(self, tmp_path):

        dataset = pd.DataFrame({
            "name": ["Hariom", "Rahul", "Amit"],
            "age": [22, None, 24]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        response = client.post(
            "/internal/clean",
            json={
                "dataset_id": TEST_DATASET_ID,
                "dataset_path": str(file_path),
                "operations": [
                    {
                        "operation": "IMPUTE_MISSING_VALUES",
                        "column": "age"
                    }
                ],
                "extension": "csv"
            }
        )

        assert response.status_code == 200

        body = response.json()

        assert "content" in body
        assert "content_hash" in body

        assert body["extension"] == "csv"

        assert body["original_rows"] == 3
        assert body["cleaned_rows"] == 3

        assert body["original_columns"] == 2
        assert body["cleaned_columns"] == 2

        assert body["operations_applied"] == 1

        assert len(body["changes"]) == 1

        change = body["changes"][0]

        assert change["operation"] == "IMPUTE_MISSING_VALUES"
        assert change["column"] == "age"
        assert change["rowsAffected"] == 1

    def test_should_remove_duplicate_rows(self, tmp_path):

        dataset = pd.DataFrame({
            "name": ["Hariom", "Rahul", "Hariom"],
            "age": [22, 24, 22]
        })

        file_path = tmp_path / "duplicates.csv"
        dataset.to_csv(file_path, index=False)

        response = client.post(
            "/internal/clean",
            json={
                "dataset_id": TEST_DATASET_ID,
                "dataset_path": str(file_path),
                "operations": [
                    {
                        "operation": "REMOVE_DUPLICATES"
                    }
                ],
                "extension": "csv"
            }
        )

        assert response.status_code == 200

        body = response.json()

        assert body["original_rows"] == 3
        assert body["cleaned_rows"] == 2
        assert body["operations_applied"] == 1

        change = body["changes"][0]

        assert change["operation"] == "REMOVE_DUPLICATES"
        assert change["rowsAffected"] == 1

    def test_should_apply_multiple_cleaning_operations(self, tmp_path):

        dataset = pd.DataFrame({
            "name": [" Hariom ", "Rahul", "Hariom"],
            "age": [22, None, 22]
        })

        file_path = tmp_path / "multiple_issues.csv"
        dataset.to_csv(file_path, index=False)

        response = client.post(
            "/internal/clean",
            json={
                "dataset_id": TEST_DATASET_ID,
                "dataset_path": str(file_path),
                "operations": [
                    {
                        "operation": "NORMALIZE_CATEGORIES",
                        "column": "name"
                    },
                    {
                        "operation": "IMPUTE_MISSING_VALUES",
                        "column": "age"
                    },
                    {
                        "operation": "REMOVE_DUPLICATES"
                    }
                ],
                "extension": "csv"
            }
        )

        assert response.status_code == 200

        body = response.json()

        assert body["operations_applied"] == 3
        assert len(body["changes"]) == 3

        assert body["cleaned_rows"] <= body["original_rows"]

    def test_should_return_404_when_clean_dataset_does_not_exist(
            self,
            tmp_path
    ):

        file_path = tmp_path / "does-not-exist.csv"

        response = client.post(
            "/internal/clean",
            json={
                "dataset_id": TEST_DATASET_ID,
                "dataset_path": str(file_path),
                "operations": [],
                "extension": "csv"
            }
        )

        assert response.status_code == 404

        body = response.json()

        assert body["detail"] == "Dataset file not found"

    def test_should_return_400_for_invalid_cleaning_operation(
            self,
            tmp_path
    ):

        dataset = pd.DataFrame({
            "name": ["Hariom", "Rahul", "Amit"]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        response = client.post(
            "/internal/clean",
            json={
                "dataset_id": TEST_DATASET_ID,
                "dataset_path": str(file_path),
                "operations": [
                    {
                        "operation": "INVALID_OPERATION"
                    }
                ],
                "extension": "csv"
            }
        )

        assert response.status_code == 400

        body = response.json()

        assert "Unsupported cleaning operation" in body["detail"]

    def test_should_return_422_for_invalid_clean_request(self):

        response = client.post(
            "/internal/clean",
            json={}
        )

        assert response.status_code == 422

    def test_should_return_base64_encoded_cleaned_dataset(
            self,
            tmp_path
    ):

        dataset = pd.DataFrame({
            "name": ["Hariom", "Rahul"],
            "age": [22, 24]
        })

        file_path = tmp_path / "test.csv"
        dataset.to_csv(file_path, index=False)

        response = client.post(
            "/internal/clean",
            json={
                "dataset_id": TEST_DATASET_ID,
                "dataset_path": str(file_path),
                "operations": [],
                "extension": "csv"
            }
        )

        assert response.status_code == 200

        body = response.json()

        decoded_content = base64.b64decode(
            body["content"]
        ).decode("utf-8")

        assert "name,age" in decoded_content
        assert "Hariom,22" in decoded_content
        assert "Rahul,24" in decoded_content
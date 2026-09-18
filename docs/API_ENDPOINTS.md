# DataMind API Endpoints

> **Status:** Current implementation documentation\
> **Scope:** Spring Boot public API and Python internal analysis API

## 1. Overview

DataMind currently exposes two API boundaries:

``` text
Client / Frontend
        |
        v
Spring Boot REST API
        |
        v
PostgreSQL + Job Worker
        |
        v
Python FastAPI internal API
```

The Spring Boot API is the client-facing application boundary. The
Python API is an internal service boundary used by the Java analysis
worker.

------------------------------------------------------------------------

# 2. Spring Boot API

Base URL during local development:

``` text
http://localhost:8080
```

## 2.1 Dataset Endpoints

### POST `/api/datasets`

Uploads a dataset using multipart form data.

**Request**

``` http
POST /api/datasets
Content-Type: multipart/form-data
```

Multipart field:

``` text
file
```

Example:

``` bash
curl -X POST http://localhost:8080/api/datasets \
  -F "file=@dataset.csv"
```

**Success response**

``` text
200 OK
```

Response body: `DatasetResponse`

### GET `/api/datasets/{id}`

Retrieves a dataset by UUID.

``` http
GET /api/datasets/{id}
```

**Success response**

``` text
200 OK
```

Response body: `DatasetResponse`

### GET `/api/datasets`

Retrieves all registered datasets.

``` http
GET /api/datasets
```

**Success response**

``` text
200 OK
```

Response body:

``` text
List<DatasetResponse>
```

------------------------------------------------------------------------

## 2.2 Dataset Lineage Endpoint

### GET `/api/datasets/{datasetId}/lineage`

Retrieves lineage records associated with a dataset.

``` http
GET /api/datasets/{datasetId}/lineage
```

**Success response**

``` text
200 OK
```

Response body:

``` text
List<DatasetLineageResponse>
```

------------------------------------------------------------------------

# 3. Analysis Job API

Base path:

``` text
/api/analysis/jobs
```

## 3.1 POST `/api/analysis/jobs`

Creates an asynchronous analysis job.

**Request**

``` http
POST /api/analysis/jobs
Content-Type: application/json
```

Example:

``` json
{
  "datasetId": "93e48716-70f6-468e-8c34-9efe055926eb",
  "analysisType": "EDA",
  "targetColumn": null
}
```

`datasetId` and `analysisType` are required.

`targetColumn` is optional and is relevant to analysis types that
require a target.

**Success response**

``` text
202 Accepted
```

Response body: `AnalysisJobResponse`

------------------------------------------------------------------------

## 3.2 GET `/api/analysis/jobs/{id}`

Retrieves the current state of an analysis job.

``` http
GET /api/analysis/jobs/{id}
```

**Success response**

``` text
200 OK
```

Response body: `AnalysisJobResponse`

The frontend uses this endpoint for job-status polling.

------------------------------------------------------------------------

## 3.3 GET `/api/analysis/jobs/{jobId}/result`

Retrieves the persisted analysis result for a job.

``` http
GET /api/analysis/jobs/{jobId}/result
```

**Success response**

``` text
200 OK
```

Response body: `AnalysisResultResponse`

The result is stored as structured JSON/JSONB and can contain EDA,
statistical, machine-learning, insight, and visualization output
depending on the analysis workflow.

------------------------------------------------------------------------

# 4. Python Internal API

Base URL during local development:

``` text
http://127.0.0.1:8000
```

These endpoints are internal service endpoints and are called by the
backend rather than directly by the frontend.

## 4.1 POST `/internal/analyze`

Executes an analysis against a stored dataset.

``` http
POST /internal/analyze
Content-Type: application/json
```

The request contains:

-   dataset path
-   file type
-   analysis type
-   optional target column

The analysis registry selects the appropriate Python analysis service.

Current registered analysis types in the inspected Python service:

``` text
EDA
STATISTICAL
MACHINE_LEARNING
```

The wider Java enum also defines:

``` text
TIME_SERIES
TEXT_ANALYSIS
```

These are part of the analysis-type model but are not registered in the
inspected Python analysis registry yet.

**Success response**

``` json
{
  "status": "COMPLETED",
  "result": {},
  "error": null
}
```

**Failure handling**

``` text
404 → dataset file not found
400 → invalid analysis request / ValueError
500 → unexpected internal analysis error
```

------------------------------------------------------------------------

## 4.2 POST `/internal/clean`

Executes the internal dataset-cleaning workflow.

``` http
POST /internal/clean
Content-Type: application/json
```

The endpoint validates the dataset path and delegates to the
dataset-cleaning service.

**Failure handling**

``` text
404 → dataset file not found
400 → invalid cleaning request
500 → unexpected internal error
```

------------------------------------------------------------------------

# 5. Endpoint Summary

  -------------------------------------------------------------------------------------------
  Method            Endpoint                              Boundary          Purpose
  ----------------- ------------------------------------- ----------------- -----------------
  POST              `/api/datasets`                       Spring Boot       Upload dataset

  GET               `/api/datasets/{id}`                  Spring Boot       Retrieve dataset

  GET               `/api/datasets`                       Spring Boot       List datasets

  GET               `/api/datasets/{datasetId}/lineage`   Spring Boot       Retrieve dataset
                                                                            lineage

  POST              `/api/analysis/jobs`                  Spring Boot       Create analysis
                                                                            job

  GET               `/api/analysis/jobs/{id}`             Spring Boot       Retrieve job
                                                                            status

  GET               `/api/analysis/jobs/{jobId}/result`   Spring Boot       Retrieve
                                                                            persisted result

  POST              `/internal/analyze`                   FastAPI           Execute analysis

  POST              `/internal/clean`                     FastAPI           Execute cleaning
                                                                            workflow
  -------------------------------------------------------------------------------------------

------------------------------------------------------------------------

# 6. Request Flow

\`\`\`text Frontend \| \| POST /api/datasets v Spring Boot \| v
DatasetService \| v PostgreSQL + File Storage

Frontend \| \| POST /api/analysis/jobs v AnalysisJobService \| v
PostgreSQL \| v AnalysisJobWorker \| \| POST /internal/analyze v Python
FastAPI \| v Analytics Engine \| v AnalysisResult \| v PostgreSQL \| \|
GET /api/analysis/jobs/{jobId}/result v Frontend

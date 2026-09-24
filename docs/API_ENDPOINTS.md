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

To append a new file as a version of an existing logical dataset, include
the `logicalDatasetId` multipart query parameter. `datasetId` remains
accepted as a compatibility alias.

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

### GET `/api/datasets/{datasetVersionId}`

Retrieves a dataset by UUID.

``` http
GET /api/datasets/{datasetVersionId}
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

### GET `/api/datasets/{datasetVersionId}/lineage`

Retrieves lineage records for a concrete dataset version. Each lineage item
uses `datasetVersionId` and `parentDatasetVersionId`; legacy `datasetId` and
`parentDatasetId` aliases remain deprecated during the compatibility period.

``` http
GET /api/datasets/{datasetVersionId}/lineage
```

**Success response**

``` text
200 OK
```

Response body:

``` text
List<DatasetLineageResponse>
```

## 2.3 Cleaning Workflow

All cleaning routes require a logical dataset ID and a concrete dataset
version ID. Assessment and preview are read-only; applying operations
creates a child version and returns the new `DatasetResponse` plus lineage.

```text
GET  /api/datasets/{logicalDatasetId}/versions/{datasetVersionId}/cleaning/recommendations
POST /api/datasets/{logicalDatasetId}/versions/{datasetVersionId}/cleaning/preview
POST /api/datasets/{logicalDatasetId}/versions/{datasetVersionId}/cleaning
```

Preview and apply accept `{ "operations": [{ "operation": "REMOVE_DUPLICATES", "column": null, "parameters": {} }] }`.
Imputation operations accept `parameters.strategy` values `AUTO`, `MEDIAN`,
`MEAN`, `MODE`, or `CONSTANT` (with a required `value` for `CONSTANT`). The
`AUTO` strategy uses median for numeric data and mode for categorical data.
Category normalization accepts `trim` and `lowercase` booleans. The API rejects
unsupported or malformed operation parameters.
Operations must be selected explicitly; preview does not persist a version.
Applying an operation returns `dataset` with the canonical version fields
and `lineage` entries recording the operation and the exact `operationConfig`
used to create it.
Cleaned outputs are normalized to CSV. The response includes `format: "CSV"`,
`extension: "csv"`, and `contentType: "text/csv"`; the returned dataset's
`fileType` is `text/csv`, its name ends in `.csv`, and its stored file uses the
`.csv` extension. Input datasets may use other supported formats.

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
  "logicalDatasetId": "93e48716-70f6-468e-8c34-9efe055926eb",
  "datasetVersionId": "f528134c-110c-441c-a693-a09955d07698",
  "analysisType": "EDA",
  "targetColumn": null,
  "enableHyperparameterTuning": false,
  "hypothesisTests": []
}
```

`logicalDatasetId`, `datasetVersionId`, and `analysisType` are required.
The version must belong to the specified logical dataset. This pins the
job to the exact uploaded or cleaned version even when a newer version is
created before the job runs. `datasetId` remains accepted as a request
alias for `logicalDatasetId`.

`targetColumn` is optional and is relevant to analysis types that
require a target.
`enableHyperparameterTuning` is optional and defaults to `false`. Set it to
`true` for supervised machine learning to run the random forest grid search
when a random forest model is selected. It has no effect on other analysis
types or targetless clustering.
For `STATISTICAL`, optional `hypothesisTests` can request supported tests and
parameters; see the [analysis request contract](API_CONTRACTS%281%29.md) for
supported kinds and required columns.

**Success response**

``` text
202 Accepted
```

Response body: `AnalysisJobResponse`

Responses expose canonical `logicalDatasetId`, `datasetVersionId`, and
`versionNumber` fields. Older `datasetId` and `datasetVersion` aliases
remain during migration.

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

## 3.3 GET `/api/analysis/jobs`

List recent analysis jobs for a logical dataset. Supports optional filters
`datasetVersionId`, `analysisType`, and `status`; `limit` defaults to 50 and is
capped at 100.

``` http
GET /api/analysis/jobs?logicalDatasetId={logicalDatasetId}&datasetVersionId={datasetVersionId}&analysisType=EDA&status=COMPLETED&limit=50
```

Returns an array of `AnalysisJobResponse` objects ordered newest first. The
existing `GET /api/analysis/jobs/{jobId}/result` endpoint retrieves a completed
job's result for reopening.

## 3.4 GET `/api/analysis/jobs/{jobId}/result`

Retrieves the persisted analysis result for a job.

``` http
GET /api/analysis/jobs/{jobId}/result
```

**Success response**

``` text
200 OK
```

Response body: `AnalysisResultResponse`, using the shared `v1` envelope:
`contractVersion`, `jobId`, `logicalDatasetId`, `datasetVersionId`,
`versionNumber`, `analysisType`, `status`, `createdAt`, and analysis-specific
`result`. Legacy `id`, `datasetId`, and `datasetVersion` fields remain available
as compatibility aliases.

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

-   `datasetVersionId` for the concrete file (legacy `datasetId` is accepted)
-   dataset path
-   file type
-   analysis type
-   optional target column
-   optional `enableHyperparameterTuning` (defaults to `false`)

The analysis registry selects the appropriate Python analysis service.

Current registered analysis types in the inspected Python service:

``` text
EDA
STATISTICAL
MACHINE_LEARNING
INSIGHT
```

`TIME_SERIES` and `TEXT_ANALYSIS` are not currently supported. Requests using
either value receive HTTP 400 until the corresponding analysis implementation
is available.

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
dataset-cleaning service. The response output is always normalized to CSV,
regardless of the input dataset format or requested extension: `format` is
`CSV`, `extension` is `csv`, and `content_type` is `text/csv`. The JSON
contains `artifact_id`, `sha256`, and `size_bytes`, plus cleaning metadata; it
does not contain the file bytes. Download the one-time artifact from
`GET /internal/artifacts/{artifact_id}`. A successful download removes it;
undownloaded artifacts expire after 24 hours.

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

  GET               `/api/datasets/{datasetVersionId}`    Spring Boot       Retrieve version

  GET               `/api/datasets`                       Spring Boot       List datasets

  GET               `/api/datasets/{datasetVersionId}/lineage` Spring Boot   Retrieve version
                                                                            lineage

  POST              `/api/analysis/jobs`                  Spring Boot       Create analysis
                                                                            job

  GET               `/api/analysis/jobs/{id}`             Spring Boot       Retrieve job
                                                                            status

  GET               `/api/analysis/jobs/{jobId}/result`   Spring Boot       Retrieve
                                                                            persisted result

  POST              `/internal/analyze`                   FastAPI           Execute analysis

  POST              `/internal/clean`                     FastAPI           Return cleaning
                                                                            artifact metadata
  GET               `/internal/artifacts/{artifactId}`     FastAPI           Download one-time
                                                                            cleaning artifact
  -------------------------------------------------------------------------------------------

------------------------------------------------------------------------

# 6. Request Flow

\`\`\`text Frontend \| \| POST /api/datasets v Spring Boot \| v
DatasetService \| v PostgreSQL + File Storage

Frontend \| \| POST /api/analysis/jobs v AnalysisJobService \| v
PostgreSQL \| v AnalysisJobWorker \| \| POST /internal/analyze v Python
FastAPI \| v Analytics Engine \| v AnalysisResult \| v PostgreSQL \| \|
GET /api/analysis/jobs/{jobId}/result v Frontend

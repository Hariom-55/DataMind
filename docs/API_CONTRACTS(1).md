# DataMind API Contracts

> **Status:** Current implementation documentation\
> **Principle:** API contracts are separated from persistence entities
> through DTOs.

## 1. Contract Architecture

``` text
HTTP Request
     |
     v
Controller
     |
     v
Request DTO
     |
     v
Service
     |
     v
Entity / Domain
     |
     v
Repository
```

Responses follow the reverse direction:

``` text
Entity
   |
   v
Response DTO
   |
   v
JSON
```

The database entity is therefore not used as the public API contract.

------------------------------------------------------------------------

# 2. Dataset Contracts

## 2.1 Upload Request

Endpoint:

``` http
POST /api/datasets
Content-Type: multipart/form-data
```

Multipart parameter:

  Name     Type              Required
  -------- ----------------- ----------
  `file`   `MultipartFile`   Yes

The backend performs validation and content-hash based duplicate
detection.

------------------------------------------------------------------------

## 2.2 DatasetResponse

``` json
{
  "id": "UUID",
  "name": "dataset.csv",
  "contentHash": "SHA-256 hash",
  "fileSize": 12345,
  "fileType": "text/csv",
  "status": "UPLOADED",
  "createdAt": "2026-09-18T20:00:00",
  "processedAt": null
}
```

Fields:

  Field           Type                 Description
  --------------- -------------------- ----------------------------
  `id`            UUID                 Dataset identifier
  `name`          String               Original dataset name
  `contentHash`   String               Content fingerprint
  `fileSize`      Long                 File size
  `fileType`      String               MIME/content type
  `status`        DatasetStatus        Dataset lifecycle status
  `createdAt`     LocalDateTime        Registration time
  `processedAt`   LocalDateTime/null   Processing completion time

Current dataset statuses:

``` text
UPLOADED
PROCESSING
COMPLETED
FAILED
```

------------------------------------------------------------------------

# 3. Dataset Lineage Contract

## DatasetLineageResponse

``` json
{
  "datasetId": "UUID",
  "parentDatasetId": "UUID",
  "operation": "remove_missing_values",
  "columnName": "Age",
  "rowsAffected": 177,
  "details": "details",
  "createdAt": "2026-09-18T20:00:00"
}
```

Fields:

  Field               Type
  ------------------- ---------------
  `datasetId`         UUID
  `parentDatasetId`   UUID
  `operation`         String
  `columnName`        String/null
  `rowsAffected`      Integer/null
  `details`           String/null
  `createdAt`         LocalDateTime

------------------------------------------------------------------------

# 4. Analysis Job Contracts

## 4.1 CreateAnalysisJobRequest

``` json
{
  "datasetId": "UUID",
  "analysisType": "EDA",
  "targetColumn": null
}
```

Fields:

  Field            Type           Required
  ---------------- -------------- ----------
  `datasetId`      UUID           Yes
  `analysisType`   AnalysisType   Yes
  `targetColumn`   String         No

------------------------------------------------------------------------

## 4.2 AnalysisType

The Java analysis-type enum currently defines:

``` text
EDA
STATISTICAL
MACHINE_LEARNING
TIME_SERIES
TEXT_ANALYSIS
```

The currently inspected Python registry registers:

``` text
EDA
STATISTICAL
MACHINE_LEARNING
```

Therefore `TIME_SERIES` and `TEXT_ANALYSIS` are modelled as analysis
types but are not yet connected to the inspected Python registry.

------------------------------------------------------------------------

## 4.3 AnalysisJobResponse

``` json
{
  "id": "UUID",
  "datasetId": "UUID",
  "analysisType": "EDA",
  "status": "PENDING",
  "createdAt": "2026-09-18T20:00:00",
  "startedAt": null,
  "completedAt": null,
  "errorMessage": null,
  "retryCount": 0
}
```

Fields:

  Field            Type
  ---------------- --------------------
  `id`             UUID
  `datasetId`      UUID
  `analysisType`   AnalysisType
  `status`         AnalysisJobStatus
  `createdAt`      LocalDateTime
  `startedAt`      LocalDateTime/null
  `completedAt`    LocalDateTime/null
  `errorMessage`   String/null
  `retryCount`     Integer

Job statuses:

``` text
PENDING
PROCESSING
COMPLETED
FAILED
```

------------------------------------------------------------------------

# 5. Analysis Result Contract

## AnalysisResultResponse

``` json
{
  "id": "UUID",
  "jobId": "UUID",
  "result": {},
  "createdAt": "2026-09-18T20:00:00"
}
```

Fields:

  Field         Type
  ------------- -----------------------
  `id`          UUID
  `jobId`       UUID
  `result`      Map\<String, Object\>
  `createdAt`   LocalDateTime

The `result` field is intentionally structured as a flexible map because
different analysis engines produce different result schemas.

------------------------------------------------------------------------

# 6. Python Analysis Contract

## Analysis request

The internal analysis request contains:

``` text
datasetPath
fileType
analysisType
targetColumn
```

The Python service:

1.  validates the dataset path;
2.  resolves the analysis service from `AnalysisRegistry`;
3.  executes the analysis;
4.  returns a standard wrapper.

## Analysis response

``` json
{
  "status": "COMPLETED",
  "result": {},
  "error": null
}
```

This wrapper allows the Java integration layer to distinguish execution
status from analysis-specific result content.

------------------------------------------------------------------------

# 7. Aggregated Insight Result

The current frontend architecture consumes the aggregated insight
workflow using:

``` text
result
├── analysis
├── insights
└── visualizations
```

The insight structure includes:

``` json
{
  "summary": {
    "total": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "info": 0
  },
  "insights": []
}
```

Individual insights are structured with fields including:

``` text
id
category
severity
source
title
description
evidence
recommendation
```

------------------------------------------------------------------------

# 8. Visualization Contract

Visualization output is represented as structured specifications rather
than frontend-specific chart code.

A visualization specification contains:

``` text
type
title
data
x
y
description
metadata
```

Current visualization types include:

``` text
BAR
LINE
SCATTER
HISTOGRAM
BOX_PLOT
PIE
HEATMAP
TABLE
```

The frontend renderer maps visualization types to React visualization
components.

------------------------------------------------------------------------

# 9. Frontend Consumption Contract

The current frontend flow is:

``` text
uploadDataset(file)
        |
        v
DatasetResponse
        |
        v
dataset.id
        |
        v
createAnalysisJob()
        |
        v
AnalysisJobResponse
        |
        v
poll job status
        |
        v
getAnalysisResult()
        |
        v
AnalysisResultResponse
        |
        v
AnalysisResultView
```

The frontend does not calculate the dataset content hash. The backend
remains authoritative for dataset identity and duplicate detection.

------------------------------------------------------------------------

# 10. Contract Design Rules

### Rule 1 --- DTOs are API boundaries

Database entities should not become accidental API contracts.

### Rule 2 --- UUIDs identify persistent resources

Datasets, jobs, and results use UUID identifiers.

### Rule 3 --- Job creation is asynchronous

`POST /api/analysis/jobs` returns `202 Accepted`.

### Rule 4 --- Results are retrieved separately

Job status and result retrieval are separate operations.

### Rule 5 --- Analysis result schemas are extensible

The persisted result uses structured JSON/JSONB so new analysis modules
can add result sections without creating a large rigid Java DTO
hierarchy.

### Rule 6 --- Frontend renders contracts

Visualization and insight components consume structured results rather
than depending on Python implementation details.

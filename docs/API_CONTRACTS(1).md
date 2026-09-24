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
  "logicalDatasetId": "UUID",
  "datasetVersionId": "UUID",
  "versionNumber": 1,
  "currentVersionId": "UUID",
  "id": "UUID (compatibility alias for logicalDatasetId)",
  "versionId": "UUID (deprecated alias for datasetVersionId)",
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

  Field                 Type                 Description
  --------------------- -------------------- ----------------------------
  `logicalDatasetId`    UUID                 Stable identity for the dataset family
  `datasetVersionId`    UUID                 Identity for this exact version
  `versionNumber`       Integer              Version sequence within the family
  `currentVersionId`    UUID/null            Current version identity
  `id`                  UUID                 Deprecated logicalDatasetId alias
  `versionId`           UUID                 Deprecated datasetVersionId alias
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
  "datasetVersionId": "UUID",
  "parentDatasetVersionId": "UUID",
  "datasetId": "UUID (deprecated alias for datasetVersionId)",
  "parentDatasetId": "UUID (deprecated alias for parentDatasetVersionId)",
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
  `datasetVersionId`         UUID  Child version identity
  `parentDatasetVersionId`   UUID  Parent version identity
  `datasetId`                UUID  Deprecated alias for datasetVersionId
  `parentDatasetId`          UUID  Deprecated alias for parentDatasetVersionId
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
  "logicalDatasetId": "UUID",
  "datasetVersionId": "UUID",
  "analysisType": "EDA",
  "targetColumn": null,
  "enableHyperparameterTuning": false,
  "hypothesisTests": []
}
```

Fields:

  Field               Type           Required
  ------------------- -------------- ----------
  `logicalDatasetId`  UUID           Yes
  `datasetVersionId`  UUID           Yes
  `analysisType`      AnalysisType   Yes
  `targetColumn`      String         No
  `enableHyperparameterTuning` Boolean No (defaults to false)
  `hypothesisTests`   Array          No (STATISTICAL only; max 10)

`datasetId` is accepted as a request alias for `logicalDatasetId` during
the compatibility period. The selected version must belong to that
logical dataset.
Set `enableHyperparameterTuning` to `true` only to opt supervised machine
learning into random forest grid search when a random forest model is selected.

------------------------------------------------------------------------

## 4.2 AnalysisType

The API accepts these analysis types:

``` text
EDA
STATISTICAL
MACHINE_LEARNING
INSIGHT
```

The Java enum retains `TIME_SERIES` and `TEXT_ANALYSIS` for stored data
compatibility, but job creation rejects them with HTTP 400 until implementations
are registered. Python's internal registry likewise returns an explicit 400 for
those unsupported request values.

The Python registry registers:

``` text
EDA
STATISTICAL
MACHINE_LEARNING
INSIGHT
```

------------------------------------------------------------------------

## 4.3 AnalysisJobResponse

``` json
{
  "id": "UUID",
  "logicalDatasetId": "UUID",
  "datasetVersionId": "UUID",
  "versionNumber": 1,
  "datasetId": "UUID (deprecated alias)",
  "datasetVersion": 1,
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
  `logicalDatasetId` UUID
  `datasetVersionId` UUID
  `versionNumber`  Integer
  `datasetId`      UUID (deprecated alias)
  `datasetVersion` Integer (deprecated alias)
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

## 4.4 Cleaning Workflow Contracts

Public cleaning routes are version-pinned:

```text
GET  /api/datasets/{logicalDatasetId}/versions/{datasetVersionId}/cleaning/recommendations
POST /api/datasets/{logicalDatasetId}/versions/{datasetVersionId}/cleaning/preview
POST /api/datasets/{logicalDatasetId}/versions/{datasetVersionId}/cleaning
```

Preview and apply request body:

```json
{
  "operations": [
    { "operation": "REMOVE_DUPLICATES", "column": null, "parameters": {} }
  ]
}
```

Operations may carry an explicit `parameters` object. For example:

```json
{
  "operation": "IMPUTE_MISSING_VALUES",
  "column": "age",
  "parameters": { "strategy": "MEDIAN" }
}
```

Imputation strategies are `AUTO`, `MEDIAN`, `MEAN`, `MODE`, and `CONSTANT`;
`CONSTANT` requires a `value`. `AUTO` uses the median for numeric columns and
the mode for categorical columns. Category normalization accepts optional
`trim` and `lowercase` booleans. Unsupported parameters are rejected.

Assessment returns row/column totals, quality issues, and supported
recommendations. Preview returns before/after dimensions and change
details without persisting a new version. Apply returns those details,
the newly created `dataset` response, and recorded `lineage` entries,
including the exact `operationConfig` values applied to create the version.
Operations are required and capped at 25 per request.

------------------------------------------------------------------------

# 5. Analysis Result Contract

## AnalysisResultResponse

``` json
{
  "contractVersion": "v1",
  "jobId": "UUID",
  "logicalDatasetId": "UUID",
  "datasetVersionId": "UUID",
  "versionNumber": 2,
  "analysisType": "EDA",
  "status": "COMPLETED",
  "createdAt": "2026-09-18T20:00:00",
  "result": {}
}
```

The response uses this same outer envelope for every analysis type. `result`
contains the analysis-specific payload. Legacy `id`, `datasetId`, and
`datasetVersion` properties remain available as compatibility aliases; clients
should use `jobId`, `logicalDatasetId`, and `versionNumber`.

``` json
{
  "id": "UUID",
  "datasetId": "UUID",
  "datasetVersion": 2,
  "jobId": "UUID",
  "logicalDatasetId": "UUID",
  "datasetVersionId": "UUID",
  "versionNumber": 2,
  "analysisType": "EDA",
  "contractVersion": "v1",
  "status": "COMPLETED",
  "result": {},
  "createdAt": "2026-09-18T20:00:00"
}
```

Fields:

  Field                  Type
  ---------------------- -----------------------
  `contractVersion`      String (`v1`)
  `jobId`                UUID
  `logicalDatasetId`     UUID
  `datasetVersionId`     UUID
  `versionNumber`        Integer
  `analysisType`         AnalysisType
  `status`               AnalysisJobStatus
  `createdAt`            LocalDateTime
  `result`               Map\<String, Object\>

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
datasetVersionId
targetColumn
enableHyperparameterTuning
hypothesisTests (optional; STATISTICAL only)
```

Statistical jobs may include up to 10 `hypothesisTests`. Supported test kinds
are `ONE_SAMPLE_T_TEST` (`column`, `referenceValue`), `INDEPENDENT_T_TEST`
(`valueColumn`, `groupColumn`), `PAIRED_T_TEST` (`column1`, `column2`), and
`CHI_SQUARE_INDEPENDENCE` (`column1`, `column2`). All accept `alpha` in the
exclusive range `(0, 1)`, defaulting to `0.05`. Statistical assumptions and
column types/sample sizes are checked when each test runs; invalid requests
fail the analysis job with a validation reason. Results are returned under
`result.hypothesisTests` with the test statistic, p-value, decision, and
interpretation.

The Python service:

1.  validates the dataset path;
2.  resolves the analysis service from `AnalysisRegistry`;
3.  executes the analysis;
4.  returns a standard wrapper.

The internal analysis request optionally accepts
`enableHyperparameterTuning` (default `false`). Cleaning responses contain an
artifact reference with format, extension, content type, SHA-256, and size
metadata. Java retrieves bytes separately from `/internal/artifacts/{artifactId}`;
cleaned bytes are no longer embedded as Base64 in JSON.
The internal analysis request names the concrete file identifier
`datasetVersionId`; `datasetId` is accepted temporarily as a compatibility
alias. The internal cleaning request uses `dataset_version_id`, with
`dataset_id` accepted as a legacy alias.

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

`BOX_PLOT` uses a five-number numeric summary in `data` (`min`, `q1`,
`median`, `q3`, `max`), with `column` as an optional label and `lowerBound` /
`upperBound` as optional IQR fence values. The renderer displays the observed
whiskers and quartile box and reports missing or inconsistent summaries as an
explicit invalid-data state.

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

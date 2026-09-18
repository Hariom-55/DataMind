# DataMind Use Cases and Workflows

> **Status:** Current architecture and workflow documentation

## 1. System Purpose

DataMind is being developed as an autonomous data-intelligence platform
that separates application orchestration from analytical workloads.

``` text
Spring Boot
    |
    | API + persistence + orchestration
    v
PostgreSQL
    ^
    |
Python FastAPI
    |
    | analysis + statistics + ML
    v
Structured Results
```

------------------------------------------------------------------------

# 2. Primary Actors

  -----------------------------------------------------------------------
  Actor                               Responsibility
  ----------------------------------- -----------------------------------
  User                                Uploads datasets and requests
                                      analysis

  Frontend                            Provides UI and calls the Spring
                                      Boot API

  Spring Boot API                     Validates requests and orchestrates
                                      application workflows

  Analysis Worker                     Processes pending analysis jobs

  Python Analytics Service            Executes data analysis

  PostgreSQL                          Persists application state and
                                      results

  File Storage                        Stores uploaded dataset files
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 3. Use Case UC-01 --- Upload Dataset

## Goal

Register a dataset and store the uploaded file.

## Preconditions

-   Spring Boot API is running.
-   Dataset file is supplied as multipart form data.

## Workflow

``` text
User
  |
  | Select file
  v
Frontend
  |
  | POST /api/datasets
  v
DatasetController
  |
  v
DatasetService
  |
  +--> Validate file
  |
  +--> Calculate SHA-256 content hash
  |
  +--> Check duplicate
  |
  +--> Store file
  |
  +--> Persist Dataset
  |
  v
DatasetResponse
  |
  v
Frontend
```

## Duplicate path

``` text
Upload
  |
  v
Calculate contentHash
  |
  v
Existing hash?
  |
  +---- YES ---> Return existing Dataset
  |
  +---- NO ----> Create new Dataset
```

------------------------------------------------------------------------

# 4. Use Case UC-02 --- View Dataset

## Goal

Retrieve dataset metadata.

``` text
Frontend
   |
   | GET /api/datasets/{id}
   v
DatasetController
   |
   v
DatasetService
   |
   v
DatasetRepository
   |
   v
PostgreSQL
   |
   v
DatasetResponse
```

------------------------------------------------------------------------

# 5. Use Case UC-03 --- List Datasets

``` text
Frontend
   |
   | GET /api/datasets
   v
DatasetController
   |
   v
DatasetService
   |
   v
DatasetRepository
   |
   v
List<DatasetResponse>
```

------------------------------------------------------------------------

# 6. Use Case UC-04 --- Request Analysis

## Goal

Create an asynchronous analysis job without blocking the HTTP request
until the analysis completes.

## Workflow

``` text
User
  |
  | Select analysis type
  v
Frontend
  |
  | POST /api/analysis/jobs
  v
AnalysisJobController
  |
  v
AnalysisJobService
  |
  v
Create AnalysisJob
  |
  v
PostgreSQL
  |
  | PENDING
  v
202 Accepted
  |
  v
Frontend
```

The returned job ID is used to track execution.

------------------------------------------------------------------------

# 7. Use Case UC-05 --- Process Analysis Job

The worker periodically looks for pending work.

``` text
PostgreSQL
    |
    | PENDING job
    v
AnalysisJobWorker
    |
    | mark PROCESSING
    v
AnalysisExecutionService
    |
    v
PythonAnalysisClient
    |
    | HTTP
    v
FastAPI /internal/analyze
    |
    v
Analysis Registry
    |
    +---- EDA
    |
    +---- Statistical
    |
    +---- Machine Learning
    |
    v
Analysis Result
```

On success:

``` text
PENDING
   ↓
PROCESSING
   ↓
COMPLETED
   ↓
AnalysisResult persisted
```

On failure:

``` text
PROCESSING
   ↓
FAILED
```

The current worker also contains retry handling, returning eligible
failed executions to `PENDING` while incrementing the retry counter.

------------------------------------------------------------------------

# 8. Use Case UC-06 --- Retrieve Job Status

The frontend polls the job status.

``` text
Frontend
   |
   | GET /api/analysis/jobs/{id}
   v
Spring Boot
   |
   v
AnalysisJobResponse
```

The frontend can continue polling while:

``` text
PENDING
PROCESSING
```

and stop when the job reaches:

``` text
COMPLETED
FAILED
```

------------------------------------------------------------------------

# 9. Use Case UC-07 --- Retrieve Analysis Result

After completion:

``` text
Frontend
   |
   | GET /api/analysis/jobs/{jobId}/result
   v
AnalysisResultController
   |
   v
AnalysisResultService
   |
   v
AnalysisResultRepository
   |
   v
PostgreSQL JSONB
   |
   v
AnalysisResultResponse
   |
   v
Frontend
```

------------------------------------------------------------------------

# 10. Use Case UC-08 --- Generate Insights

The current insight architecture aggregates analytical outputs.

Conceptually:

``` text
EDA
 |
Statistical Analysis
 |
Machine Learning
 |
Data Quality
 |
 v
Insight Engine
 |
 v
Structured Insights
```

The output contains:

``` text
summary
insights[]
```

Each insight contains structured information such as:

``` text
severity
category
source
title
description
evidence
recommendation
```

The current implementation uses deterministic rule-based insight
generation rather than making an LLM the primary decision mechanism.

------------------------------------------------------------------------

# 11. Use Case UC-09 --- Generate Visualizations

Visualization generation consumes structured analysis output.

``` text
Analysis Results
      |
      v
Visualization Generators
      |
      +---- EDA
      +---- Statistical
      +---- Distribution
      +---- ML
      |
      v
VisualizationSpec[]
      |
      v
Frontend Renderer
```

The frontend selects a renderer based on the visualization type:

``` text
BAR
HEATMAP
TABLE
...
```

The visualization layer is intentionally decoupled from the Python
implementation.

------------------------------------------------------------------------

# 12. End-to-End User Workflow

The current frontend workflow is:

``` text
                 START
                   |
                   v
             Upload Dataset
                   |
                   v
          DatasetResponse
                   |
                   v
          Receive Dataset ID
                   |
                   v
          Select Analysis Type
                   |
                   v
          Create Analysis Job
                   |
                   v
                PENDING
                   |
                   v
              PROCESSING
                   |
                   v
           Python Analytics
                   |
                   v
              COMPLETED
                   |
                   v
          Retrieve Result
                   |
                   v
       AnalysisResultResponse
                   |
          +--------+--------+
          |        |        |
          v        v        v
        Summary Insights Visualizations
```

------------------------------------------------------------------------

# 13. Full System Workflow

``` text
                         USER
                           |
                           v
                     React Frontend
                           |
              +------------+------------+
              |                         |
              v                         v
       Dataset API                Analysis API
              |                         |
              v                         v
       DatasetService          AnalysisJobService
              |                         |
              v                         v
       DatasetRepository       AnalysisJobRepository
              |                         |
              +------------+------------+
                           |
                           v
                       PostgreSQL
                           |
                           v
                    AnalysisJobWorker
                           |
                           v
                 PythonAnalysisClient
                           |
                           v
                    FastAPI /internal
                           |
                           v
                  Analysis Registry
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
         EDA         Statistical           ML
          |                |                |
          +----------------+----------------+
                           |
                           v
                  Structured Result
                           |
          +----------------+----------------+
          |                                 |
          v                                 v
    Insight Engine                 Visualization Layer
          |                                 |
          +----------------+----------------+
                           |
                           v
                  AnalysisResult JSONB
                           |
                           v
                    Spring Boot API
                           |
                           v
                    React Frontend
```

------------------------------------------------------------------------

# 14. Dataset Cleaning Workflow

The Python service also exposes an internal cleaning workflow.

``` text
Dataset
   |
   v
POST /internal/clean
   |
   v
Dataset Cleaning Service
   |
   +--> Cleaning workflow
   |
   +--> Track changes
   |
   +--> Serialize cleaned result
   |
   v
Cleaned Dataset Result
```

Dataset lineage is designed to preserve the relationship between source
and derived datasets:

``` text
Parent Dataset
      |
      | operation
      v
Child Dataset
```

------------------------------------------------------------------------

# 15. Failure Workflows

## Dataset not found

``` text
Request
  |
  v
Dataset lookup
  |
  X
Not Found
  |
  v
DatasetNotFoundException
  |
  v
HTTP error response
```

## Analysis dataset file missing

``` text
Worker
  |
  v
PythonAnalysisClient
  |
  v
FastAPI
  |
  X
Dataset file not found
  |
  v
404
  |
  v
Worker failure/retry handling
```

## Analysis execution failure

``` text
PROCESSING
    |
    X
Python / execution failure
    |
    v
Failure handling
    |
    +---- retry eligible → PENDING
    |
    +---- terminal failure → FAILED
```

------------------------------------------------------------------------

# 16. Current Product Pipeline

The broader intended DataMind pipeline is:

``` text
UPLOAD
   ↓
PROFILE
   ↓
DATA QUALITY
   ↓
CLEAN
   ↓
ANALYZE
   ↓
MODEL
   ↓
EVALUATE
   ↓
EXPLAIN
   ↓
INSIGHTS
   ↓
VISUALIZE
```

Not every stage is exposed as a complete end-user workflow yet. The
implementation is being built incrementally.

------------------------------------------------------------------------

# 17. Design Principles

### Asynchronous analysis

Long-running analysis is represented as a persisted job rather than a
long-running HTTP request.

### Separation of concerns

``` text
Spring Boot → application orchestration
Python → analytics
PostgreSQL → persistence
React → presentation
```

### Structured outputs

Analysis, insight, and visualization results are represented as
structured data so they can be consumed by APIs and frontend components.

### Test-first development

Each milestone follows:

``` text
Contract
   ↓
Tests
   ↓
Implementation
   ↓
Focused tests
   ↓
Full suite
   ↓
Documentation
   ↓
Commit
```

### Extensibility

New analysis engines can be registered without redesigning the entire
application architecture.

------------------------------------------------------------------------

# 18. Current vs Planned

## Implemented / integrated

-   Dataset upload
-   Dataset metadata persistence
-   Content-hash duplicate detection
-   Dataset retrieval
-   Dataset listing
-   Dataset lineage API
-   Analysis job creation
-   Job status retrieval
-   Worker-based asynchronous execution
-   Python analysis integration
-   EDA
-   Statistical analysis
-   Machine learning analysis infrastructure
-   Persisted analysis results
-   Insight generation
-   Visualization specification generation
-   React upload → analysis workflow
-   Frontend visualization rendering

## Planned / ongoing

-   Rich production dashboard
-   Additional visualization renderers
-   More advanced statistical assumption checks
-   Statistical significance interpretation
-   Relationship analysis
-   Automated interpretation improvements
-   Expanded ML workflows
-   Authentication and authorization
-   Production hardening
-   Observability and deployment
-   AI/GenAI intelligence layer

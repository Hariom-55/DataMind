# DataMind

> **Autonomous Data Intelligence Platform**

DataMind is a production-oriented data intelligence platform designed to automate the journey from raw datasets to structured analytical insights.

The system separates application orchestration from data-science workloads:

- **Java + Spring Boot** — backend API, persistence, orchestration, job management
- **Python + FastAPI** — data analysis and machine-learning workloads
- **PostgreSQL** — persistent application state
- **pandas** — dataset loading, exploratory data analysis, statistical analysis
- **scikit-learn** — machine-learning preprocessing, modeling, and evaluation
- **REST/HTTP** — Java ↔ Python communication

---

## Project Vision

The long-term goal of DataMind is to allow a user to upload a dataset and request analysis without manually performing the complete data-science workflow.

The intended pipeline is:

```text
Dataset
   ↓
Validation
   ↓
Content Hashing / Deduplication
   ↓
Persistent Storage
   ↓
Analysis Job
   ↓
Worker
   ↓
Python Analysis Engine
   ↓
EDA / Statistical Analysis / ML
   ↓
Analysis Result
   ↓
Insights / API / AI Layer
```

DataMind is being developed incrementally, with architecture, testing, reliability, and observability treated as first-class engineering concerns.

---

# Architecture

```text
                         DataMind
                            │
             ┌──────────────┴──────────────┐
             │                             │
             ▼                             ▼
      Spring Boot API                Python Analytics
           Java                         FastAPI
             │                             │
             ├── Dataset Management        ├── Analysis API
             ├── Analysis Jobs             ├── Dataset Loader
             ├── Worker                    ├── EDA Engine
             └── Orchestration              ├── Statistical Engine
                                            └── ML Engine
                    │
                    │ HTTP / REST
                    ▼
             Python Analysis Service
                    │
                    ▼
              Analysis Result
                    │
                    ▼
                PostgreSQL
```

---

# Technology Stack

## Backend

- Java
- Spring Boot
- Spring Data JPA
- Hibernate
- Maven
- REST APIs

## Analytics

- Python
- FastAPI
- pandas
- NumPy
- SciPy
- scikit-learn

## Database

- PostgreSQL

## Testing

- JUnit 5
- Mockito
- Spring Boot Test
- MockMvc
- PostgreSQL integration tests
- Java ↔ Python end-to-end tests

---

# Repository Structure

```text
DataMind/
│
├── backend/
│   └── datamind-api/
│       ├── src/
│       │   ├── main/
│       │   │   └── java/
│       │   │       └── com/datamind/datamind_api/
│       │   │           ├── analysis/
│       │   │           ├── dataset/
│       │   │           └── exception/
│       │   │
│       │   └── test/
│       │       └── java/
│       │
│       └── pom.xml
│
├── analytics/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   └── services/
│   │
│   └── requirements.txt
│
└── README.md
```

---

# Development Journey

## Phase 1 — Project Foundation

DataMind was started with the goal of building a production-oriented data intelligence platform rather than a collection of independent data-science scripts.

The initial architecture separated responsibilities between two services:

```text
Java
 └── API + orchestration + persistence

Python
 └── data science + analysis
```

This separation allows each ecosystem to be used where it is strongest:

- Java/Spring Boot for application architecture, persistence, orchestration, and service reliability
- Python for data analysis, statistical computing, machine learning, and future AI workloads

---

# Phase 2 — Dataset Management

The first major backend capability was dataset management.

A dataset stores information including:

- original filename
- content hash
- storage path
- file size
- file type
- processing status
- creation timestamp
- processing timestamp

The dataset lifecycle includes:

```text
UPLOADED
   ↓
PROCESSING
   ↓
COMPLETED
```

or:

```text
UPLOADED
   ↓
PROCESSING
   ↓
FAILED
```

---

## Dataset Validation

Uploaded files are validated before processing.

The service rejects:

- null files
- empty files
- files without a valid filename

Invalid requests are converted into appropriate HTTP `400 Bad Request` responses at the API boundary.

---

## Content Hashing

DataMind uses SHA-256 content hashing to identify datasets by their content rather than their filename.

For example:

```text
customers.csv
customers-copy.csv
customers-final.csv
```

may contain identical data.

Their filenames are different, but their content hash is identical.

This allows DataMind to detect duplicate datasets reliably.

---

## Duplicate Protection

The `content_hash` column is protected by a database-level unique constraint.

The application performs an initial lookup:

```text
findByContentHash()
```

If a dataset already exists, the existing record is returned.

The database provides the final concurrency guarantee:

```text
Request A ───────────────┐
                         │
Request B ───────────────┤
                         ▼
                  PostgreSQL
                         │
                UNIQUE(content_hash)
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
          INSERT                  violation
             │                       │
             ▼                       ▼
          success              re-fetch row
```

This protects the system from concurrent duplicate inserts.

The behavior is verified against real PostgreSQL rather than only through mocks.

---

# Phase 3 — Dataset Storage

Uploaded datasets are stored using their content hash as the primary stored filename.

For example:

```text
Original:
customers.csv

Content hash:
abc123...

Stored:
abc123....csv
```

The original file extension is preserved.

Files without an extension are also handled correctly.

Storage tests use isolated temporary directories so tests do not modify the application's real dataset storage directory.

---

# Phase 4 — Analysis Jobs

After dataset management, DataMind introduced an asynchronous analysis-job model.

An analysis job connects:

```text
Dataset
   +
Analysis Type
   ↓
Analysis Job
```

The job lifecycle is:

```text
PENDING
   ↓
PROCESSING
   ↓
COMPLETED
```

or:

```text
PENDING
   ↓
PROCESSING
   ↓
FAILED
```

Transient failures are handled through retry logic.

The current retry policy allows up to three failed attempts:

```text
Attempt 1 → retry
Attempt 2 → retry
Attempt 3 → FAILED
```

---

# Phase 5 — Analysis Worker

The Java backend contains a worker responsible for processing pending analysis jobs.

The worker:

1. Claims a pending job
2. Marks it as `PROCESSING`
3. Calls the Python analysis service
4. Handles the Python response
5. Persists successful analysis results
6. Marks successful jobs as `COMPLETED`
7. Handles analysis failures
8. Applies retry logic
9. Marks permanently failed jobs as `FAILED`

The pending-job selection uses database row locking with:

```sql
FOR UPDATE SKIP LOCKED
```

This allows multiple worker instances to safely compete for jobs without processing the same row simultaneously.

---

# Phase 6 — Java ↔ Python Integration

The Python analytics service was introduced as a separate FastAPI application.

Java communicates with Python through HTTP.

An analysis request contains information such as:

```json
{
  "jobId": "...",
  "datasetId": "...",
  "analysisType": "EDA",
  "datasetPath": "...",
  "fileType": "text/csv"
}
```

The Java backend acts as the orchestration layer while Python performs the actual analytical computation.

The initial supported analysis type is:

```text
EDA
```

---

# Phase 7 — Exploratory Data Analysis

The first Python analysis implementation is Exploratory Data Analysis.

The EDA engine uses pandas to load the supplied dataset and generate structured analytical information.

The analysis includes information such as:

- dataset overview
- row and column counts
- data types
- missing values
- duplicate rows
- descriptive statistics
- column-level analysis

The structured result is returned through FastAPI to the Java service and persisted as an `AnalysisResult`.

---

# Phase 8 — Multi-Format Dataset Loading & Data Quality Profiling

The analytics layer was refactored so analysis services no longer depend directly on `pandas.read_csv()`.

A centralized `DatasetLoader` now supports:

- CSV
- XLSX
- XLS
- JSON
- Parquet

The loader accepts the dataset path and optional MIME type. When a recognized MIME type is available, it is preferred; otherwise the file extension is used as a fallback.

This makes dataset loading reusable across EDA, statistical analysis, and machine-learning workloads.

## Data Quality Profiling

The EDA layer now produces a structured data-quality profile including:

- missing-value counts
- missing-value percentages
- unique-value counts
- duplicate-row count
- numeric statistics
- categorical statistics
- data-quality score
- completeness information

The data-quality calculation is also covered by service and end-to-end tests.

An XLSX dataset has been validated through the real Java → Python E2E pipeline, proving that non-CSV datasets can pass through storage, job processing, Python loading, analysis, and result persistence.

---

# Phase 9 — Machine Learning Foundation

DataMind has now entered the Machine Learning implementation phase.

The initial ML service is designed around supervised learning. A user supplies a target column and the service validates the dataset before determining the baseline problem type.

The current ML flow is:

```text
Dataset
   ↓
Target Column
   ↓
Validation
   ↓
Problem-Type Detection
   ├── Classification
   └── Regression
           ↓
     Preprocessing
           ↓
     Train/Test Split
           ↓
       Baseline Model
           ↓
       Predictions
           ↓
        Metrics
```

## Current ML capabilities

### Target Validation

The ML service validates:

- target-column presence
- non-empty dataset
- usable target values
- minimum target observations
- presence of feature columns

### Problem-Type Detection

The current baseline heuristic is:

```text
Non-numeric target
       ↓
Classification

Numeric target
   ├── exactly 2 unique values → Classification
   └── otherwise              → Regression
```

This is intentionally treated as a baseline heuristic. Future versions will allow explicit user selection of classification or regression.

### Preprocessing

The ML pipeline currently supports heterogeneous datasets through scikit-learn:

- numeric features → median imputation
- categorical features → most-frequent imputation
- categorical features → one-hot encoding
- `ColumnTransformer` → combines feature-specific preprocessing
- `Pipeline` → keeps preprocessing and model training together

### Baseline Models

| Problem Type | Baseline Model | Current Metrics |
|---|---|---|
| Classification | Logistic Regression | Accuracy |
| Regression | Linear Regression | MAE, MSE, RMSE |

The baseline approach is deliberately simple. It establishes a reference point before adding more complex models.

### ML Reliability Work

Classification training is being hardened with stratified train/test splitting and validation for classes with insufficient observations.

The ML service has dedicated unit tests covering validation, problem-type detection, classification training, regression training, and failure cases.

## ML Theory Notes

A separate Machine Learning theory pack has been prepared alongside the implementation. It covers the concepts used in DataMind and the next stages of development, including supervised learning, preprocessing, model evaluation, cross-validation, class imbalance, feature engineering, hyperparameter tuning, and model persistence.

---

# Phase 10 — Centralized Exception Handling

DataMind uses a centralized Spring `@RestControllerAdvice` for API-level exception handling.

Current application-level mappings include:

| Exception | HTTP Status |
|---|---:|
| `DatasetNotFoundException` | 404 |
| `AnalysisJobNotFoundException` | 404 |
| `AnalysisResultNotFoundException` | 404 |
| `IllegalArgumentException` | 400 |
| `MissingServletRequestPartException` | 400 |
| Validation errors | 400 |
| Malformed request body | 400 |
| Unexpected exceptions | 500 |

This keeps HTTP error handling consistent across the application.

---

# Testing Strategy

DataMind follows a layered testing strategy.

```text
                    E2E
                     ▲
                     │
              Integration
                     ▲
                     │
                   Unit
```

The objective is not simply to maximize test count.

Each layer verifies a different responsibility.

---

## Unit Tests

Unit tests validate individual components and business logic.

Examples:

- dataset upload behavior
- duplicate detection logic
- SHA-256 hashing
- file storage behavior

Mockito is used where external dependencies should be isolated.

---

## HTTP / Controller Tests

Spring `MockMvc` tests verify the HTTP layer.

Examples:

```text
POST /api/datasets
GET  /api/datasets/{id}
```

These tests verify:

- request mapping
- multipart handling
- HTTP status codes
- controller/service interaction
- exception-to-HTTP mapping

---

## Database Integration Tests

Real PostgreSQL is used for database-level integration testing.

The most important database test verifies:

```text
UNIQUE(content_hash)
```

by attempting to persist two datasets with the same content hash.

The test expects PostgreSQL/Hibernate to raise:

```text
DataIntegrityViolationException
```

This proves the uniqueness guarantee exists in the actual database rather than merely being assumed by application code.

---

# Java ↔ Python E2E Testing

DataMind includes real end-to-end tests across the Java/Python service boundary.

The Python service is **not mocked** in these tests.

The pipeline is:

```text
Java Spring Boot
      ↓
AnalysisJobWorker
      ↓
PythonAnalysisClient
      ↓
HTTP
      ↓
FastAPI
      ↓
EDAService
      ↓
pandas
      ↓
EDA result
      ↓
Java
      ↓
AnalysisResult
      ↓
PostgreSQL
```

This verifies the complete cross-language integration.

---

# E2E Scenarios

## Successful Analysis

The happy path verifies:

```text
PENDING
   ↓
PROCESSING
   ↓
Python EDA
   ↓
AnalysisResult persisted
   ↓
COMPLETED
```

This proves that Java can successfully send a real dataset to Python, Python can perform the analysis, and Java can persist the resulting analysis.

---

## Python Failure + Retry

A missing dataset path is used to trigger a real Python-side failure.

The pipeline becomes:

```text
PENDING
   ↓
PROCESSING
   ↓
Python failure
   ↓
Java receives analysis failure
   ↓
retryCount = 1
   ↓
PENDING
```

This verifies that the Java worker does not permanently fail a job after a single transient failure.

---

## Retry Exhaustion

The retry policy is tested end-to-end:

```text
Attempt 1
   ↓
PENDING / retryCount = 1

Attempt 2
   ↓
PENDING / retryCount = 2

Attempt 3
   ↓
FAILED / retryCount = 3
```

This verifies that permanently failing analysis jobs do not enter an infinite retry loop.

---

# Current Test Baseline

The current Java backend test suite contains:

```text
64 tests
64 passed
0 failures
0 errors
0 skipped
```

The complete Maven test suite currently passes with:

```text
BUILD SUCCESS
```

Run the complete regression suite with:

```bash
mvnw.cmd test
```

The current `64/64` result is the baseline for the project at this milestone.

---

# Completed Milestone

## Milestone 1 — Core Analysis Pipeline + E2E Testing Foundation

**Status: Completed**

### Dataset Management

- [x] Dataset upload
- [x] Dataset validation
- [x] SHA-256 content hashing
- [x] Duplicate dataset detection
- [x] Database-level duplicate protection
- [x] Dataset filesystem storage
- [x] File extension preservation

### Analysis Pipeline

- [x] Analysis job creation
- [x] Job status lifecycle
- [x] Pending-job worker
- [x] PostgreSQL row locking
- [x] Python analysis client
- [x] FastAPI analysis service
- [x] EDA execution using pandas
- [x] Multi-format dataset loading
- [x] MIME-type-aware dataset loading
- [x] Data quality profiling
- [x] Statistical analysis
- [x] Analysis registry
- [x] Analysis result persistence
- [x] Retry mechanism
- [x] Retry exhaustion handling

### API

- [x] Dataset upload endpoint
- [x] Dataset retrieval endpoint
- [x] Centralized exception handling
- [x] HTTP validation/error mapping

### Testing

- [x] Unit tests
- [x] Service tests
- [x] Storage tests
- [x] Controller tests
- [x] PostgreSQL integration tests
- [x] Java ↔ Python E2E happy-path test
- [x] Java ↔ Python failure-path test
- [x] Retry exhaustion E2E test
- [x] Full Java regression suite: 64/64 passing
- [x] Full Python regression suite passing

---

# Current Milestone

## Milestone 2 — Analytics Expansion + ML Foundation

**Status: In Progress**

### Dataset Analytics

- [x] Multi-format dataset loading
- [x] MIME-type-aware loading
- [x] EDA data-quality profiling
- [x] Statistical analysis service
- [x] Analysis registry

### Machine Learning

- [x] ML service foundation
- [x] Target-column validation
- [x] Classification/regression detection baseline
- [x] Numeric feature imputation
- [x] Categorical feature imputation
- [x] One-hot encoding
- [x] `ColumnTransformer` preprocessing
- [x] Scikit-learn `Pipeline` integration
- [x] Logistic Regression baseline
- [x] Linear Regression baseline
- [x] Classification accuracy
- [x] Regression MAE/MSE/RMSE
- [x] Classification split safeguards
- [ ] Cross-validation
- [ ] Advanced classification metrics
- [ ] Model comparison
- [ ] Class-imbalance handling
- [ ] Feature engineering
- [ ] Hyperparameter tuning
- [ ] Model persistence
- [ ] ML API integration
- [ ] Java ↔ Python ML E2E validation

---

# Complete Current System Flow

```text
                         USER
                           │
                           │ Upload Dataset
                           ▼
                  ┌─────────────────┐
                  │  Spring Boot    │
                  │      API        │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ DatasetService  │
                  └────────┬────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
          Validate      SHA-256      Duplicate
           File         Hashing       Check
              │            │            │
              └────────────┼────────────┘
                           │
                           ▼
                 Dataset Storage
                           │
                           ▼
                      PostgreSQL
                           │
                           ▼
                    Analysis Job
                           │
                           ▼
                  AnalysisJobWorker
                           │
                           ▼
                PythonAnalysisClient
                           │
                           │ HTTP
                           ▼
                     FastAPI
                           │
                           ▼
                  Analysis Registry
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          EDAService   Statistical    ML Service
              │         Service          │
              └────────────┼────────────┘
                           ▼
                    DatasetLoader
                           │
                           ▼
                    Analysis Result
                           │
                           ▼
                     Java Backend
                           │
                  ┌────────┴────────┐
                  ▼                 ▼
          AnalysisResult       Job Status
             persisted          COMPLETED
```

---

# Reliability Flow

```text
Analysis Job
     │
     ▼
  PROCESSING
     │
     ▼
Python Analysis
     │
     ├─────────────── Success ───────────────► COMPLETED
     │
     └─────────────── Failure
                      │
                      ▼
                  retryCount
                      │
              ┌───────┴───────┐
              │               │
           < 3 retries       >= 3
              │               │
              ▼               ▼
           PENDING          FAILED
```

---

# Roadmap

The next stages of DataMind will expand the analysis platform.

## Analysis Capabilities

- [x] Statistical analysis
- [ ] Machine learning analysis (API integration in progress)
- [ ] Time-series analysis
- [ ] Text analysis
- [x] Advanced dataset profiling
- [ ] Automated feature analysis

## Machine Learning

- [x] ML service foundation
- [x] Target-column validation
- [x] Classification/regression detection baseline
- [x] Numeric/categorical preprocessing
- [x] Logistic Regression baseline
- [x] Linear Regression baseline
- [x] Baseline evaluation metrics
- [x] Stratified classification split safeguards
- [ ] Cross-validation
- [ ] Precision / recall / F1 / confusion matrix
- [ ] Model comparison
- [ ] Class-imbalance strategies
- [ ] Feature engineering framework
- [ ] Hyperparameter tuning
- [ ] Model persistence
- [ ] ML API integration
- [ ] Java ↔ Python ML E2E validation

## Intelligence Layer

- [ ] AI-generated analytical insights
- [ ] Natural-language data querying
- [ ] Dataset question answering
- [ ] Automated insight generation
- [ ] Recommendation engine

## Platform Engineering

- [ ] Authentication and authorization
- [ ] Improved API documentation
- [ ] Structured logging
- [ ] Metrics and observability
- [ ] Distributed tracing
- [ ] Dockerized development environment
- [ ] CI/CD pipeline
- [ ] Production deployment

## Scalability

- [ ] Dedicated job queue
- [ ] Multiple worker instances
- [ ] Better job scheduling
- [ ] Object storage integration
- [ ] Horizontal scaling
- [ ] Service health monitoring

---

# Development Philosophy

DataMind is being developed incrementally using a production-oriented workflow.

Each major capability should follow:

```text
Feature
  ↓
Implementation
  ↓
Unit Tests
  ↓
Integration Tests
  ↓
E2E Validation
  ↓
Regression Suite
  ↓
Milestone
```

The objective is to build a system that demonstrates not only data-science
knowledge, but also:

- backend engineering
- distributed-service integration
- database design
- testing
- reliability
- API design
- asynchronous processing
- production-oriented architecture

DataMind is intended to evolve from a data-analysis backend into an
autonomous data intelligence platform.

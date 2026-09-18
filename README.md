# DataMind — Product Definition Document

**Version:** 1.0  
**Scope:** Dataset Intelligence → Exploratory Data Analysis → Statistical Analysis → Machine Learning  
**Status:** Product Baseline  
**Primary Stack:** Java Spring Boot, Python/FastAPI, PostgreSQL, Pandas/NumPy, Scikit-learn  
**Architecture:** Java API + asynchronous analysis job worker + Python analytics/ML service

---

## 1. Product Overview

DataMind is a data intelligence platform designed to allow users to upload datasets, inspect their structure and quality, perform exploratory and statistical analysis, and eventually build and evaluate machine-learning models through a controlled analysis pipeline.

Version 1 is intentionally defined as a staged platform:

```text
Dataset
   ↓
Ingestion & Storage
   ↓
Data Profiling
   ↓
EDA / Insights
   ↓
Statistical Analysis
   ↓
Machine Learning
```

# 2. Product Vision

Build a reliable platform that converts a raw dataset into progressively more useful analytical intelligence.

The system should hide unnecessary infrastructure complexity from the user while keeping the underlying architecture modular enough for future expansion.

The long-term direction is:

```text
Raw Data
   ↓
Understand Data
   ↓
Find Patterns
   ↓
Test Hypotheses
   ↓
Build Models
   ↓
Evaluate Predictions
   ↓
Generate Actionable Intelligence
```

---

# 3. Product Goals

## 3.1 Primary Goals

DataMind Version 1 must:

1. Accept dataset uploads through an HTTP API.
2. Persist dataset metadata in PostgreSQL.
3. Store uploaded files safely on the configured filesystem.
4. Detect duplicate datasets using content hashing.
5. Create analysis jobs independently from the HTTP request lifecycle.
6. Process analysis jobs asynchronously through a worker.
7. Execute Python-based analytical workloads.
8. Perform automated EDA.
9. Produce statistical summaries and analytical measurements.
10. Provide a foundation for supervised and unsupervised machine learning.
11. Track analysis/job lifecycle and failures.
12. Support retryable background processing.
13. Maintain a clean separation between API, persistence, orchestration, analytics, and ML responsibilities.

---

# 4. Non-Goals for Version 1

The following are deliberately outside the V1 scope:

- Deep learning
- Large Language Model integration
- Agentic AI
- Autonomous data science agents
- Real-time streaming analytics
- Distributed GPU training
- Production model serving
- Kubernetes-based deployment
- Feature-store infrastructure
- Full experiment tracking platform
- Automated cloud deployment
- AutoML at enterprise scale
- Multi-tenant enterprise security
- Billing/subscription infrastructure
- Real-time collaborative analysis

These may be considered in future product versions.

---

# 5. Target Users

## Primary User — Data Analyst / Student / Junior Data Scientist

Needs to:

- upload datasets,
- understand dataset structure,
- identify data-quality issues,
- explore distributions and relationships,
- obtain statistical summaries,
- experiment with machine-learning algorithms,
- evaluate model performance.

## Secondary User — Developer / Data Engineering Learner

Uses DataMind to understand:

- REST API design,
- asynchronous job processing,
- database modeling,
- service-to-service communication,
- Python analytics integration,
- ML pipeline architecture.

---

# 6. Core Product Modules

Version 1 consists of the following logical modules:

```text
┌──────────────────────────────────────────┐
│              DataMind API                │
├──────────────────────────────────────────┤
│ Dataset Management                       │
│ Analysis Management                      │
│ Job Management                            │
│ Insight Management                        │
└──────────────────┬───────────────────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ PostgreSQL          │
        │                     │
        │ datasets            │
        │ analysis_jobs       │
        │ analysis_results    │
        │ insights            │
        └─────────────────────┘

                   │
                   ▼

        ┌─────────────────────┐
        │ Java Job Worker     │
        │                     │
        │ PENDING → PROCESSING│
        │ Retry / Failure     │
        └──────────┬──────────┘
                   │
                   ▼

        ┌─────────────────────┐
        │ Python Service      │
        │                     │
        │ EDA                 │
        │ Statistics          │
        │ ML                  │
        └─────────────────────┘
```

---

# 7. Module 1 — Dataset Ingestion

## Objective

Provide a reliable mechanism for importing datasets into DataMind.

## Initial Supported Format

Version 1 initially focuses on:

- CSV

Future formats can include:

- Excel
- JSON
- Parquet

## Upload Flow

```text
POST /api/datasets/upload
          │
          ▼
DatasetController
          │
          ▼
DatasetService
          │
          ├── Validate file
          ├── Calculate SHA-256
          ├── Check duplicate
          ├── Store physical file
          └── Persist metadata
                    │
                    ▼
                PostgreSQL
```

## Dataset Identity

Every uploaded file receives a SHA-256 content hash.

Example:

```text
customers.csv
     ↓
SHA-256
     ↓
b97b7b89c02b61724304a1daf94b1cec...
```

The hash is stored as a unique value in the database.

This allows DataMind to identify duplicate file contents independently of the original filename.

---

# 8. Dataset Entity

The conceptual Dataset model contains:

```text
Dataset
├── id
├── name
├── contentHash
├── storagePath
├── fileSize
├── fileType
├── status
├── createdAt
└── processedAt
```

## Dataset Lifecycle

```text
UPLOADED
    │
    ▼
PROCESSING
    │
    ▼
COMPLETED

        or

PROCESSING
    │
    ▼
FAILED
```

---

# 9. Module 2 — Analysis Job Management

Analysis must not depend on the lifetime of the original HTTP request.

Instead, DataMind creates an `AnalysisJob`.

## Job Lifecycle

```text
PENDING
   │
   ▼
PROCESSING
   │
   ├──────────────► COMPLETED
   │
   └──────────────► FAILED
```

## Job Responsibilities

An analysis job records:

- job ID,
- dataset ID,
- analysis type,
- status,
- retry count,
- created timestamp,
- started timestamp,
- completed timestamp.

## Analysis Types

The architecture defines:

```text
EDA
STATISTICAL
MACHINE_LEARNING
TIME_SERIES
TEXT_ANALYSIS
```

The implementation priority for the core V1 pipeline is:

```text
EDA
   ↓
STATISTICAL
   ↓
MACHINE_LEARNING
```

Time-series and text analysis remain extensibility points and should not delay the core V1 pipeline.

---

# 10. Asynchronous Worker Architecture

The worker is a central architectural component.

Instead of:

```text
HTTP Request
   ↓
Java
   ↓
Python
   ↓
Wait
   ↓
Response
```

DataMind uses:

```text
HTTP Request
   ↓
Create AnalysisJob
   ↓
Return
   ↓
PENDING
   ↓
Worker picks job
   ↓
PROCESSING
   ↓
Python analysis
   ↓
Result
   ↓
COMPLETED / FAILED
```

## Why the Worker Exists

The worker provides:

- asynchronous execution,
- failure isolation,
- retries,
- job status tracking,
- controlled processing,
- separation of API traffic from compute workloads.

This architecture also prepares the system for future horizontal scaling.

---

# 11. Module 3 — Exploratory Data Analysis

EDA is the first major analytical capability.

## EDA Objectives

### Dataset-level information

- number of rows,
- number of columns,
- memory usage where available,
- duplicate rows,
- missing values.

### Column-level information

For each column:

- name,
- data type,
- null count,
- null percentage,
- unique value count,
- cardinality characteristics.

### Numerical analysis

For numerical columns:

- count,
- mean,
- standard deviation,
- minimum,
- maximum,
- quartiles,
- median,
- distribution information.

### Categorical analysis

For categorical columns:

- unique values,
- frequency distribution,
- top categories,
- rare categories.

---

# 12. Data Quality Analysis

EDA should identify common quality problems.

Examples:

```text
Missing Values
Duplicate Rows
Constant Columns
High Cardinality
Potential Outliers
Incorrect Data Types
Potentially Invalid Values
```

The output should distinguish between:

```text
Observed fact
```

and:

```text
Potential issue / heuristic
```

For example:

```text
Observed:
column age contains 17 null values.

Potential issue:
column age contains values outside an explicitly configured expected range.
```

The system should not silently assume domain rules without explicit configuration.

---

# 13. Module 4 — Statistical Analysis

Statistical analysis extends EDA from descriptive inspection toward quantitative analysis.

## Version 1 Statistical Capabilities

### Descriptive Statistics

- mean,
- median,
- mode where appropriate,
- variance,
- standard deviation,
- range,
- quartiles,
- interquartile range,
- skewness,
- kurtosis where supported.

### Relationship Analysis

- covariance,
- correlation,
- correlation matrices.

### Distribution Analysis

Where applicable:

- distribution summaries,
- normality-related diagnostics,
- quantiles,
- outlier statistics.

### Inferential Statistics

The architecture should allow future implementation of:

- hypothesis tests,
- confidence intervals,
- t-tests,
- chi-square tests,
- ANOVA.

Inferential methods should only be applied when their assumptions and data requirements are satisfied.

---

# 14. Module 5 — Machine Learning

Machine Learning is the final major capability in Version 1.

The ML module should provide a structured ML workflow rather than simply exposing algorithms.

```text
Dataset
   ↓
Problem Definition
   ↓
Target Selection
   ↓
Feature Selection
   ↓
Data Validation
   ↓
Preprocessing
   ↓
Train/Test Split
   ↓
Model Training
   ↓
Evaluation
   ↓
Results
```

---

# 15. Machine Learning Problem Types

## Supervised Learning

### Regression

Initial algorithms may include:

- Linear Regression
- Ridge Regression
- Lasso Regression
- Decision Tree Regressor
- Random Forest Regressor
- Gradient Boosting Regressor

### Classification

Initial algorithms may include:

- Logistic Regression
- Decision Tree Classifier
- Random Forest Classifier
- K-Nearest Neighbors
- Naive Bayes
- Gradient Boosting
- Support Vector Machine where appropriate

---

# 16. Unsupervised Learning

Version 1 can provide foundational unsupervised capabilities.

## Clustering

Initial algorithm:

- K-Means

Potential extensions:

- Hierarchical clustering
- DBSCAN

## Dimensionality Reduction

Initial capability:

- PCA

---

# 17. ML Preprocessing

The ML pipeline must explicitly separate preprocessing from model training.

Potential preprocessing operations:

```text
Missing-value handling
       ↓
Categorical encoding
       ↓
Numerical scaling
       ↓
Feature selection
       ↓
Train/test split
```

Common transformations:

### Numerical

- StandardScaler
- MinMaxScaler

### Categorical

- One-hot encoding
- ordinal encoding where justified

### Missing Values

- mean,
- median,
- mode,
- explicit missing category,
- configurable strategies.

The preprocessing pipeline must avoid data leakage.

---

# 18. Train/Test Strategy

The default supervised-learning workflow should use a train/test split.

```text
Dataset
   │
   ├───────────────┐
   ▼               ▼
Training Set      Test Set
   │               │
   ▼               │
Preprocessing      │
   │               │
   ▼               │
Model Training     │
   │               │
   └───────┬───────┘
           ▼
       Evaluation
```

Preprocessing parameters must be learned from the training data and then applied to the test data.

This prevents information leakage.

---

# 19. Model Evaluation

Evaluation depends on the problem type.

## Regression Metrics

Potential V1 metrics:

- MAE
- MSE
- RMSE
- R²

## Classification Metrics

Potential V1 metrics:

- Accuracy
- Precision
- Recall
- F1 Score
- Confusion Matrix
- ROC-AUC where applicable

## Clustering Metrics

Potential metrics:

- Silhouette Score
- Inertia for K-Means

Metrics should be returned together with enough metadata to explain which dataset split and model produced them.

---

# 20. ML Result Concept

A machine-learning result should conceptually contain:

```text
MLResult
├── jobId
├── problemType
├── targetColumn
├── featureColumns
├── algorithm
├── preprocessing
├── trainingConfiguration
├── metrics
├── featureInformation
├── modelMetadata
└── createdAt
```

The persisted representation may evolve as the ML module is implemented.

---

# 21. End-to-End Product Pipeline

The complete Version 1 pipeline is:

```text
                        USER
                          │
                          ▼
                ┌──────────────────┐
                │ Dataset Upload   │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Dataset Service  │
                └────────┬─────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       File Storage             PostgreSQL
              │                     │
              └──────────┬──────────┘
                         │
                         ▼
                  Analysis Job
                     PENDING
                         │
                         ▼
                   Job Worker
                         │
                         ▼
                    PROCESSING
                         │
                         ▼
                 Python Analytics
                         │
             ┌───────────┼────────────┐
             ▼           ▼            ▼
            EDA      Statistics       ML
             │           │            │
             └───────────┼────────────┘
                         ▼
                    Analysis Result
                         │
                         ▼
                     COMPLETED
```

---

# 22. Java / Python Responsibility Boundary

## Java / Spring Boot

Responsible for:

- REST APIs,
- request validation,
- dataset metadata,
- PostgreSQL persistence,
- job creation,
- job scheduling,
- job lifecycle,
- retry handling,
- orchestration,
- API responses.

## Python / FastAPI

Responsible for:

- Pandas-based data processing,
- NumPy calculations,
- EDA,
- statistical computation,
- preprocessing,
- Scikit-learn ML,
- model evaluation,
- analytical result generation.

## PostgreSQL

Responsible for durable application state:

```text
datasets
analysis_jobs
analysis_results
insights
```

The database should not be used as a replacement for physical dataset storage.

---

# 23. Storage Architecture

DataMind uses two forms of storage.

## Metadata Storage

PostgreSQL:

```text
Dataset
Job
Result
Insight
```

## Dataset Storage

Filesystem/object storage:

```text
data/
└── datasets/
    ├── <sha256>.csv
    ├── <sha256>.csv
    └── ...
```

The database stores the path/reference to the physical dataset.

This separation allows object storage to replace the local filesystem later without fundamentally changing the data model.

---

# 24. Reliability Requirements

The system should treat failure as a normal operating condition.

Possible failures:

```text
Invalid dataset
      │
      ▼
Validation failure

Python unavailable
      │
      ▼
Retry

Analysis exception
      │
      ▼
Retry / FAILED

Database failure
      │
      ▼
Transaction failure

Worker interruption
      │
      ▼
Recoverable job state
```

## Retry Model

Each job contains:

```text
retryCount
```

A configurable maximum retry count should be introduced.

Example:

```text
PENDING
  ↓
PROCESSING
  ↓
FAILED
  ↓
retryCount < maxRetries
  ↓
PENDING
```

After the retry limit:

```text
FAILED
```

---

# 25. Idempotency

DataMind should avoid processing the same logical operation unnecessarily.

Dataset-level idempotency is provided through:

```text
SHA-256 contentHash
```

Job-level idempotency should ensure that retries do not create duplicate persistent results.

A future result record can use the job ID as a unique logical identifier.

---

# 26. API Design Principles

The API should follow REST-oriented principles.

Examples:

```text
POST   /api/datasets/upload
GET    /api/datasets
GET    /api/datasets/{id}

POST   /api/analysis
GET    /api/analysis/{jobId}
GET    /api/analysis/{jobId}/status
GET    /api/analysis/{jobId}/result
```

Internal Python endpoints are separate from public APIs:

```text
/internal/analyze
```

Internal endpoints should not be exposed as the primary user-facing API.

---

# 27. API Response Philosophy

API responses should expose business state rather than internal implementation details.

Example:

```json
{
  "jobId": "uuid",
  "status": "PENDING"
}
```

The client does not need to know:

```text
which Java thread
which scheduler thread
which Python process
which Pandas object
```

was used internally.

---

# 28. Security Baseline

Version 1 should establish the following foundations:

- validate uploaded files,
- restrict supported file types,
- enforce upload size limits,
- prevent unsafe path construction,
- avoid executing uploaded files,
- sanitize filename usage,
- avoid returning sensitive filesystem information unnecessarily,
- keep internal Python endpoints separate from public endpoints.

Authentication and authorization can be added as a subsequent security layer.

---

# 29. Performance and Scalability

The architectural target is to support high API concurrency while keeping expensive analysis asynchronous.

The key principle is:

```text
API throughput ≠ ML computation throughput
```

A large number of API requests should not result in an equal number of immediately executing Python processes.

Instead:

```text
Many API Requests
       │
       ▼
    Job Queue
       │
       ▼
Controlled Workers
       │
       ▼
Python Compute
```

The exact concurrency configuration should be established through load testing rather than assumed from a fixed number.

---

# 30. Observability

Each job should be traceable through:

```text
jobId
datasetId
```

Logs should make it possible to answer:

- when was the job created?
- when did processing start?
- which analysis type ran?
- how many retries occurred?
- when did it complete?
- why did it fail?

Example:

```text
JOB_CREATED
JOB_PROCESSING
PYTHON_ANALYSIS_STARTED
PYTHON_ANALYSIS_COMPLETED
JOB_COMPLETED
```

For failures:

```text
JOB_PROCESSING
PYTHON_ANALYSIS_FAILED
RETRY_SCHEDULED
```

---

# 31. Version 1 Feature Boundary

## V1.0 — Dataset Foundation

```text
✓ Dataset upload
✓ File storage
✓ SHA-256 hashing
✓ Duplicate detection
✓ Dataset metadata
✓ PostgreSQL persistence
```

## V1.1 — Job Infrastructure

```text
✓ AnalysisJob
✓ Job lifecycle
✓ Worker
✓ Retry mechanism
✓ Job status
✓ Python execution boundary
```

## V1.2 — EDA

```text
✓ Dataset profiling
✓ Missing-value analysis
✓ Duplicate analysis
✓ Numerical statistics
✓ Categorical statistics
✓ Data-quality insights
```

## V1.3 — Statistical Analysis

```text
✓ Descriptive statistics
✓ Correlation
✓ Covariance
✓ Distribution analysis
✓ Statistical diagnostics
```

## V1.4 — Machine Learning

```text
✓ Regression
✓ Classification
✓ Clustering
✓ Preprocessing
✓ Train/test split
✓ Model evaluation
✓ ML result persistence
```

---

# 32. Definition of Done for V1

DataMind Version 1 is functionally complete when a user can:

```text
1. Upload a CSV
        ↓
2. Dataset is stored
        ↓
3. Dataset metadata is persisted
        ↓
4. Create an analysis job
        ↓
5. Worker picks the job
        ↓
6. Job becomes PROCESSING
        ↓
7. Python performs the requested analysis
        ↓
8. Results are returned/persisted
        ↓
9. Job becomes COMPLETED
        ↓
10. User can retrieve the result
```

For ML:

```text
Dataset
   ↓
Select target
   ↓
Determine problem type
   ↓
Prepare features
   ↓
Preprocess
   ↓
Train model
   ↓
Evaluate
   ↓
Persist result
```

---

# 33. Future Product Evolution

After Version 1:

```text
V1
Dataset → EDA → Statistics → ML
                │
                ▼
              V2
        Advanced ML + Explainability
                │
                ▼
              V3
        Deep Learning + NLP
                │
                ▼
              V4
       Generative AI / LLM Layer
                │
                ▼
              V5
          Agentic DataMind
```

Possible future capabilities include:

- automated feature engineering,
- model comparison,
- hyperparameter optimization,
- explainable AI,
- model registry,
- experiment tracking,
- model serving,
- deep learning,
- NLP,
- LLM-assisted analysis,
- natural-language querying,
- autonomous analytical agents.

These are future extensions and are not part of the V1 commitment.

---

# 34. Product Design Principles

### 1. Separation of concerns

API, orchestration, storage, analytics, and ML remain independently testable.

### 2. Asynchronous compute

Long-running workloads must not unnecessarily block API requests.

### 3. Explicit state

Jobs and datasets have explicit lifecycle states.

### 4. Reproducibility

Analysis results should be traceable to:

```text
dataset
job
analysis type
configuration
```

### 5. Failure tolerance

Failures should produce observable states and controlled retries.

### 6. Incremental complexity

Build the simplest reliable version before introducing distributed infrastructure.

### 7. Extensibility

EDA, statistics, and ML should be modules rather than tightly coupled application logic.

---

# 35. Current Implementation Baseline

The Dataset foundation currently established includes:

```text
✓ Spring Boot API
✓ PostgreSQL connection
✓ Dataset entity
✓ Dataset repository
✓ Dataset service
✓ Dataset controller
✓ Multipart upload
✓ SHA-256 hashing
✓ Duplicate dataset detection
✓ Physical dataset storage
✓ Dataset metadata persistence
```

The next implementation boundary is:

```text
AnalysisJob
      ↓
Job Worker
      ↓
Python Analysis
      ↓
Result Persistence
```

The previous direct synchronous Python test path should remain a development/debugging mechanism only, not the core production architecture.

---

# 36. Final Product Definition

**DataMind V1 is a data intelligence platform that manages the lifecycle from dataset ingestion through exploratory analysis, statistical analysis, and foundational machine learning.**

Its architectural core is:

```text
Spring Boot
    │
    ├── REST API
    ├── Dataset Management
    ├── Job Orchestration
    └── Worker
          │
          ▼
       FastAPI
          │
          ├── EDA
          ├── Statistics
          └── Machine Learning
          │
          ▼
      PostgreSQL
```

The product boundary deliberately ends at **Machine Learning**.

This provides a coherent V1 product while leaving a clean architectural path toward Deep Learning, Generative AI, and Agentic AI in future versions.

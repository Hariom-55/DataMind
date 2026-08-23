# DataMind

**DataMind** is an Autonomous Data Intelligence Platform designed to register datasets, detect duplicate content, create analysis jobs, execute those jobs asynchronously through a Spring worker, communicate with a Python/FastAPI analysis engine, and expose job state through a REST API.

> **Current milestone:** Dataset persistence and duplicate detection are implemented. Analysis jobs are persisted and processed by a scheduled Spring worker. Java → FastAPI communication is working end-to-end. The Python endpoint is currently an acknowledgement/stub; the real EDA engine is the next major implementation step.

---

## 1. Architecture

```text
Client / Postman / Frontend
            |
            | REST / JSON
            v
   +--------------------+
   |   Spring Boot API  |
   |       :8080        |
   +---------+----------+
             |
      +------+------+
      |             |
      v             v
 Dataset Module   Analysis Job Module
      |             |
      +------+------+
             v
      +--------------+
      |  PostgreSQL  |
      |     :5432    |
      +------+-------+
             |
       PENDING job
             |
             v
      +--------------+
      | AnalysisJob   |
      |    Worker     |
      +------+-------+
             |
       PROCESSING
             |
             v
      +--------------+
      | Python Client |
      | Spring        |
      +------+-------+
             |
          HTTP/JSON
             |
             v
      +--------------+
      | FastAPI       |
      | Analysis      |
      | Engine :8000  |
      +------+-------+
             |
          result
             |
             v
      COMPLETED / FAILED
             |
             v
         PostgreSQL
```

The key architectural decision is that **analysis execution is asynchronous**. The API creates a persistent job and returns it; a scheduled worker later claims the job and invokes Python.

---

## 2. Repository Structure

```text
DataMind/
│
├── analytics/
│   ├── app/
│   │   ├── main.py
│   │   └── api/
│   │       └── analysis.py
│   └── requirements.txt
│
├── backend/
│   └── datamind-api/
│       ├── pom.xml
│       └── src/
│           ├── main/
│           │   ├── java/com/datamind/datamind_api/
│           │   │
│           │   ├── DatamindApiApplication.java
│           │   │
│           │   ├── analysis/
│           │   │   ├── config/
│           │   │   │   ├── PythonClientConfig.java
│           │   │   │   └── PythonRequestLoggingInterceptor.java
│           │   │   ├── controller/
│           │   │   │   └── AnalysisJobController.java
│           │   │   ├── dto/
│           │   │   │   ├── CreateAnalysisJobRequest.java
│           │   │   │   └── AnalysisJobResponse.java
│           │   │   ├── entity/
│           │   │   │   ├── AnalysisJob.java
│           │   │   │   └── enums/
│           │   │   │       ├── AnalysisJobStatus.java
│           │   │   │       └── AnalysisType.java
│           │   │   ├── exception/
│           │   │   │   └── AnalysisJobNotFoundException.java
│           │   │   ├── integration/python/
│           │   │   │   ├── PythonAnalysisClient.java
│           │   │   │   ├── PythonAnalysisException.java
│           │   │   │   └── dto/
│           │   │   │       ├── PythonAnalysisRequest.java
│           │   │   │       └── PythonAnalysisResponse.java
│           │   │   ├── repository/
│           │   │   │   └── AnalysisJobRepository.java
│           │   │   ├── service/
│           │   │   │   └── AnalysisJobService.java
│           │   │   └── worker/
│           │   │       └── AnalysisJobWorker.java
│           │   │
│           │   ├── dataset/
│           │   │   ├── controller/DatasetController.java
│           │   │   ├── dto/
│           │   │   │   ├── DatasetCreateRequest.java
│           │   │   │   └── DatasetResponse.java
│           │   │   ├── entity/
│           │   │   │   ├── Dataset.java
│           │   │   │   └── DatasetStatus.java
│           │   │   ├── exception/DatasetNotFoundException.java
│           │   │   ├── repository/DatasetRepository.java
│           │   │   └── service/DatasetService.java
│           │   │
│           │   └── exception/
│           │       ├── ErrorResponse.java
│           │       └── GlobalExceptionHandler.java
│           │
│           └── resources/application.properties
│
├── datasets/
├── docs/
├── frontend/
│   └── Request.http
└── README.md
```

Runtime/generated directories such as `.git`, `target`, and the Python `.venv` are not part of the conceptual source structure and should not be committed.

---

## 3. Backend Layered Architecture

The Spring Boot application follows:

```text
Controller
    ↓
Service
    ↓
Repository
    ↓
JPA / Hibernate
    ↓
PostgreSQL
```

### Controller

Maps HTTP requests to application operations. It receives DTOs and returns DTOs/HTTP responses. It does not contain database/business logic.

### Service

Contains business logic and coordinates repositories and other services.

### Repository

Uses Spring Data JPA for persistence and custom database queries/locking.

### Entity

Represents persistent database state.

### DTO

Defines API contracts separately from database entities.

---

## 4. Dataset Module

### `Dataset`

Maps to the `datasets` table and contains:

| Field | Purpose |
|---|---|
| `id` | UUID primary key |
| `name` | Dataset name |
| `contentHash` | Content fingerprint |
| `fileSize` | Size of dataset |
| `fileType` | File type |
| `status` | Dataset lifecycle |
| `createdAt` | Registration timestamp |
| `processedAt` | Processing completion timestamp |

### Dataset status

```text
UPLOADED → PROCESSING → COMPLETED
                    └──→ FAILED
```

The entity provides transition methods `markProcessing()`, `markCompleted()`, and `markFailed()`.

### Duplicate detection

`contentHash` is `NOT NULL` and `UNIQUE`. `DatasetRepository` exposes `findByContentHash()`.

The service therefore performs:

```text
POST /api/datasets
        ↓
findByContentHash()
        │
   +----+----+
   |         |
 Exists     New
   |         |
 return   create
 existing  Dataset
```

This prevents duplicate registration of identical dataset content.

### Dataset endpoints

```http
POST /api/datasets
GET  /api/datasets/{id}
GET  /api/datasets
```

Example create request:

```json
{
  "name": "sales.csv",
  "contentHash": "abc123...",
  "fileSize": 1048576,
  "fileType": "csv"
}
```

---

## 5. Analysis Job Module

`AnalysisJob` maps to `analysis_jobs`.

```text
Dataset 1 ───────< AnalysisJob
```

A dataset can have multiple independent analysis jobs, for example EDA, statistical analysis, and machine learning.

### Job fields

| Field | Purpose |
|---|---|
| `id` | Job identifier |
| `dataset` | Dataset being analyzed |
| `analysisType` | Requested analysis |
| `status` | Job lifecycle |
| `retryCount` | Failed attempt count |
| `createdAt` | Queue time |
| `startedAt` | Processing start |
| `completedAt` | Completion/failure time |

### Job states

```text
PENDING
   ↓
PROCESSING
   ↓
COMPLETED
```

Failure:

```text
PROCESSING → FAILED
```

Current retry count is incremented on failure, but automatic re-queue/retry policy is **not yet implemented**.

### Analysis types

```text
EDA
STATISTICAL
MACHINE_LEARNING
TIME_SERIES
TEXT_ANALYSIS
```

### Analysis job endpoints

```http
POST /api/analysis/jobs
GET  /api/analysis/jobs/{id}
```

Create request:

```json
{
  "datasetId": "0978c4d6-37f0-4ecb-b00e-ea5b8d40ea9c",
  "analysisType": "EDA"
}
```

The service validates the dataset, creates a `PENDING` job, and saves it.

---

## 6. Job Worker

`AnalysisJobWorker` is a Spring `@Component` executed every 5 seconds using:

```java
@Scheduled(fixedDelay = 5000)
```

The worker does not receive an HTTP request directly. It polls persistent job state.

### Worker flow

```text
Every 5 seconds
      ↓
claimNextPendingJob()
      ↓
Find oldest PENDING job
      ↓
Pessimistic lock
      ↓
PENDING → PROCESSING
      ↓
Call Python
      ↓
COMPLETED / FAILED
```

### FIFO selection

The repository query uses:

```sql
ORDER BY job.createdAt ASC
```

so the oldest pending job is selected first.

### Database locking

The query uses:

```java
@Lock(LockModeType.PESSIMISTIC_WRITE)
```

This establishes the basis for preventing concurrent workers from claiming the same row.

---

## 7. Java → Python Integration

Python-specific communication is isolated under:

```text
analysis/integration/python/
```

### `PythonAnalysisClient`

Responsible for the HTTP call:

```http
POST http://127.0.0.1:8000/internal/analyze
Content-Type: application/json
```

Request model:

```json
{
  "jobId": "...",
  "datasetId": "...",
  "analysisType": "EDA"
}
```

`PythonAnalysisClient` catches `RestClientException` and converts it to `PythonAnalysisException`, allowing the worker to handle service failures consistently.

### `PythonClientConfig`

Creates the Spring `RestClient` using the configured Python base URL and attaches `PythonRequestLoggingInterceptor`.

### Logging interceptor

During development it logs outgoing method, URI, headers, request body, and response status. This was used to diagnose the previous 422 issue and confirm the current request is actually reaching FastAPI as JSON.

---

## 8. Python Analysis Engine

The Python service is a separate FastAPI application:

```text
analytics/
├── app/
│   ├── main.py
│   └── api/
│       └── analysis.py
└── requirements.txt
```

### `main.py`

Creates the FastAPI application and registers the analysis router.

Health endpoint:

```http
GET /health
```

Response:

```json
{
  "status": "UP",
  "service": "datamind-analysis"
}
```

### `/internal/analyze`

The endpoint currently accepts:

```python
class AnalysisRequest(BaseModel):
    jobId: UUID
    datasetId: UUID
    analysisType: str
```

and returns an acknowledgement:

```json
{
  "status": "RECEIVED",
  "result": {
    "jobId": "...",
    "datasetId": "...",
    "analysisType": "EDA"
  },
  "error": null
}
```

**Important:** this is currently an integration stub. It does not yet load a dataset or perform actual EDA/ML computation.

---

## 9. Complete End-to-End Pipeline

For an EDA request:

```text
1. Client
      |
      | POST /api/analysis/jobs
      v
2. AnalysisJobController
      |
      v
3. AnalysisJobService
      |
      | validate dataset
      | create PENDING job
      v
4. PostgreSQL
      |
      | analysis_jobs.status = PENDING
      v
5. AnalysisJobWorker
      |
      | scheduled every 5 sec
      | claim oldest PENDING job
      v
6. PostgreSQL
      |
      | PENDING → PROCESSING
      v
7. PythonAnalysisClient
      |
      | POST /internal/analyze
      v
8. FastAPI
      |
      | Pydantic validation
      | analysis execution (stub currently)
      v
9. PythonAnalysisResponse
      |
      v
10. AnalysisJobWorker
      |
      +---- success ----> COMPLETED
      |
      └---- exception ---> FAILED
             |
             v
11. PostgreSQL
```

The client can then poll:

```http
GET /api/analysis/jobs/{jobId}
```

to observe the job state.

---

## 10. Error Handling

Centralized handling is provided by `GlobalExceptionHandler`.

Current domain exceptions include:

```text
DatasetNotFoundException
AnalysisJobNotFoundException
PythonAnalysisException
```

The REST API uses an `ErrorResponse` containing:

```text
status
error
message
timestamp
```

---

## 11. Technology Stack

### Java backend

- Java 21
- Spring Boot 4.1
- Spring MVC
- Spring Data JPA
- Hibernate
- Spring RestClient
- Spring Scheduling
- Jackson
- Maven

### Database

- PostgreSQL

### Python analytics service

- Python
- FastAPI
- Pydantic
- Uvicorn
- Pandas
- NumPy
- Scikit-learn

---

## 12. Configuration

`application.properties` currently contains:

```properties
spring.application.name=datamind-api

spring.datasource.url=jdbc:postgresql://localhost:5432/datamind
spring.datasource.username=postgres
spring.datasource.password=${DB_PASSWORD}

spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true

datamind.python.base-url=http://127.0.0.1:8000
```

The database password is externalized through `DB_PASSWORD`. Do not commit credentials.

---

## 13. Running Locally

### PostgreSQL

Create/run the `datamind` database on PostgreSQL `localhost:5432` and configure:

```powershell
$env:DB_PASSWORD="your_password"
```

### Python

From `analytics/`:

```powershell
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

FastAPI docs:

```text
http://127.0.0.1:8000/docs
```

### Spring Boot

From `backend/datamind-api/`:

```powershell
.\mvnw.cmd spring-boot:run
```

API:

```text
http://localhost:8080
```

---

## 14. Current API Summary

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/datasets` | Register dataset |
| GET | `/api/datasets/{id}` | Get dataset |
| GET | `/api/datasets` | List datasets |
| POST | `/api/analysis/jobs` | Create analysis job |
| GET | `/api/analysis/jobs/{id}` | Get analysis job/status |
| GET | `/health` | Python service health |
| POST | `/internal/analyze` | Internal Java → Python call |

The `/internal/analyze` endpoint is an internal service-to-service endpoint, not a frontend-facing API.

---

## 15. Why the Job Worker Architecture?

The system deliberately avoids making a user HTTP request wait for a potentially expensive data-science operation.

Instead of:

```text
HTTP request → Python analysis → wait → response
```

DataMind uses:

```text
HTTP request
    ↓
Create persistent job
    ↓
Return job
    ↓
Worker executes asynchronously
    ↓
Client polls job status
```

This provides a foundation for:

- long-running analysis
- multiple workers
- retries
- parallel processing
- independent Python execution
- queue/broker migration later

PostgreSQL is currently the persistent job source of truth. A dedicated broker such as RabbitMQ/Kafka can be introduced later if scale requires it.

---

## 16. Current Implementation Status

### Implemented

- [x] Spring Boot backend
- [x] PostgreSQL/JPA persistence
- [x] Dataset registration
- [x] Duplicate detection using content hash
- [x] Dataset lifecycle model
- [x] Analysis job creation
- [x] Persistent analysis jobs
- [x] Job status lifecycle
- [x] Scheduled analysis worker
- [x] Oldest-pending-job selection
- [x] Pessimistic database locking
- [x] Java → FastAPI HTTP integration
- [x] Python request/response contract
- [x] FastAPI health endpoint
- [x] Centralized exception handling
- [x] Python request logging

### Not yet implemented

- [ ] Real EDA execution
- [ ] Dataset file loading in Python
- [ ] Statistical analysis
- [ ] Machine-learning pipeline
- [ ] Time-series analysis
- [ ] Text analysis
- [ ] Persistent analysis result storage
- [ ] Result retrieval API
- [ ] Automatic retry/requeue policy
- [ ] Production-grade worker concurrency controls
- [ ] Authentication/authorization
- [ ] File upload/storage pipeline
- [ ] Frontend
- [ ] Production deployment/observability

---

## 17. Next Major Pipeline: Real EDA

The current Python acknowledgement should eventually become:

```text
AnalysisJob
    ↓
Worker
    ↓
Python
    ↓
Load dataset
    ↓
Validate schema
    ↓
Profile columns
    ↓
Missing-value analysis
    ↓
Duplicate analysis
    ↓
Descriptive statistics
    ↓
Outlier detection
    ↓
Correlation analysis
    ↓
Distribution analysis
    ↓
Generate structured analysis result
    ↓
Persist result
    ↓
COMPLETED
```

That will turn the current integration skeleton into the first real DataMind intelligence pipeline.

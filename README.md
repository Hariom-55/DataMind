# DataMind — Autonomous Data Intelligence Platform

DataMind is a production-oriented data intelligence platform being built with **Java/Spring Boot**, **Python**, and **PostgreSQL**. The system accepts datasets, creates analysis jobs, executes analysis asynchronously through a Python service, and persists structured results.

## Current Architecture

```text
Client / Postman
      |
      v
Spring Boot API (Java 21)
      |
      +----> PostgreSQL
      |       |- datasets
      |       |- analysis_jobs
      |       `- analysis_results
      |
      v
Scheduled AnalysisJobWorker
      |
      v
Python Analytics Service
      |
      v
EDA Result
      |
      v
PostgreSQL JSON result
```

## Milestones Completed

### 1. Backend Foundation
- Maven + Spring Boot project
- Java 21
- Spring Web
- Dependency Injection / IoC
- Constructor injection
- Service and repository layers
- REST API fundamentals

### 2. PostgreSQL + JPA
- PostgreSQL integration
- JPA/Hibernate
- UUID identifiers
- Entity relationships
- Transactions
- Enum persistence
- JSON result persistence

### 3. Dataset & Analysis Job Domain
Implemented dataset and analysis-job management.

Analysis types currently supported:

```text
EDA
STATISTICAL
MACHINE_LEARNING
TIME_SERIES
TEXT_ANALYSIS
```

Analysis job lifecycle:

```text
PENDING -> PROCESSING -> COMPLETED
                                         -> FAILED -> PENDING (retry)
```

`AnalysisJob` currently tracks:
- job ID
- dataset
- analysis type
- status
- retry count
- created/started/completed timestamps
- error message

### 4. Asynchronous Worker
Implemented `AnalysisJobWorker` using:

```java
@Scheduled(fixedDelay = 5000)
```

The worker:
1. Finds the next pending job.
2. Claims it.
3. Marks it as `PROCESSING`.
4. Calls the Python analysis service.
5. Persists successful results.
6. Handles failures.

Pending-job selection uses pessimistic locking:

```java
@Lock(LockModeType.PESSIMISTIC_WRITE)
```

This introduced practical concepts around concurrency and job claiming.

### 5. Java ↔ Python Integration
Implemented the integration layer using:
- `PythonAnalysisClient`
- `PythonAnalysisResponse`
- `PythonAnalysisException`

Flow:

```text
Java Spring Boot -> Python Analytics Service -> Java Spring Boot
```

### 6. Python EDA Engine
Implemented `EDAService` using Pandas.

Current EDA output includes:

**Dataset overview**
- row count
- column count
- columns

**Data types**
- detected dtype for every column

**Data quality**
- missing-value counts
- missing-value percentages
- duplicate rows

**Cardinality**
- unique-value counts

**Numerical statistics**
- count
- mean
- standard deviation
- min
- 25%
- 50%
- 75%
- max

**Categorical statistics**
- unique count
- top values
- frequencies

Categorical analysis currently supports:

```python
["object", "category", "bool"]
```

### 7. End-to-End EDA Test
The complete pipeline has been successfully tested with a dataset containing:

```text
20 rows
9 columns
```

The result correctly reported:
- 0 duplicate rows
- 0 missing values
- missing percentages
- unique-value counts
- numerical statistics
- categorical statistics

The structured result was successfully persisted in PostgreSQL's `analysis_results` table.

### 8. Retry Handling
Basic retry handling is implemented with:

```java
private static final int MAX_RETRIES = 3;
```

The current implementation:
- increments retry count
- returns failed jobs to `PENDING` while retrying
- clears previous error/completion state
- eventually marks the job as `FAILED`

Retry semantics will be refined later.

## What We Have Learned

### Backend Engineering
- Spring Boot
- IoC / Dependency Injection
- REST APIs
- DTOs
- service/repository architecture
- scheduled workers
- asynchronous job processing
- exception handling
- job state management

### Database Engineering
- PostgreSQL
- JPA
- Hibernate
- entity relationships
- transactions
- UUIDs
- JSON persistence
- pessimistic locking

### Data Science / Data Engineering
- Pandas
- DataFrame inspection
- missing-value analysis
- duplicate detection
- cardinality analysis
- descriptive statistics
- categorical frequency analysis
- dtype detection
- structured EDA results

### Distributed-System Concepts
- Java ↔ Python service communication
- service boundaries
- worker-based processing
- failure handling
- retries
- state transitions

### Engineering Workflow
- Git/GitHub
- staged-diff review
- meaningful commits
- Postman API testing
- direct PostgreSQL verification

## Current Status

| Component | Status |
|---|---|
| Spring Boot backend | Done |
| PostgreSQL integration | Done |
| Dataset domain | Done |
| Analysis job domain | Done |
| Job lifecycle | Done |
| Scheduled worker | Done |
| Java ↔ Python integration | Done |
| Python EDA engine | Done |
| Result persistence | Done |
| End-to-end EDA test | Done |
| Basic retry handling | Done |
| Analysis Result API | **Next** |

## Next Milestone — Analysis Result API

The next milestone is to expose persisted analysis results through the Spring Boot API.

Planned flow:

```text
Client
  |
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
PostgreSQL
  |
  v
Result DTO
  |
  v
Client
```

### Planned tasks

1. Implement `AnalysisResultRepository`.
2. Implement `AnalysisResultService`.
3. Create result DTOs.
4. Create `AnalysisResultController`.
5. Add an endpoint to fetch results by job ID.
6. Add an endpoint to fetch analysis-job status.
7. Add proper exception handling.
8. Test with Postman.
9. Verify responses against PostgreSQL.
10. Commit the milestone.

This will complete the core:

```text
SUBMIT -> PROCESS -> PERSIST -> RETRIEVE
```

## Long-Term Roadmap

```text
[✓] Backend Foundation
[✓] Database + Dataset Management
[✓] Analysis Job System
[✓] Java ↔ Python Pipeline
[✓] EDA Engine
[✓] Async Worker + Result Persistence
[ ] Analysis Result API          <- NEXT
[ ] Frontend / Analysis Dashboard
[ ] Statistical Analysis
[ ] Machine Learning Pipeline
[ ] Time-Series Analysis
[ ] Text Analysis
[ ] Authentication & Authorization
[ ] Production Hardening
[ ] Deployment + Observability
[ ] AI / GenAI Data Intelligence
```

## Project Vision

DataMind is intended to grow beyond a simple EDA application into an **Autonomous Data Intelligence Platform**.

The long-term goal is to build a system that can understand a dataset, select appropriate analysis workflows, execute them, persist structured results, and eventually generate actionable insights for users.

The project is being developed incrementally so that every milestone adds both a meaningful product capability and practical software-engineering knowledge.

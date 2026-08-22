# DataMind API — Backend Foundation

DataMind is an **Autonomous Data Intelligence Platform** designed to accept datasets, identify whether a dataset has already been processed, create processing jobs for new datasets, run analytics, and return/reuse stored analysis results.

This repository contains the **Spring Boot backend API**.

> **Current milestone:** Dataset registration, PostgreSQL persistence, JPA/Hibernate integration, REST API, and duplicate-dataset detection are implemented and verified end-to-end.

---

## 1. What We Built Today

Today's development focused on building the first working backend vertical slice:

```text
Client
  |
  | POST /api/datasets
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
JPA / Hibernate
  |
  v
PostgreSQL
```

The API can now:

1. Receive dataset metadata as JSON.
2. Convert the JSON request into a Java DTO.
3. Pass the request through the Controller → Service → Repository layers.
4. Persist a dataset in PostgreSQL.
5. Generate a UUID for the dataset.
6. Track the dataset status.
7. Detect whether the same dataset has already been registered using `contentHash`.
8. Return the existing dataset instead of creating a duplicate record.

---

# 2. DataMind Architecture

The backend follows a layered architecture.

```text
                 HTTP / REST
                     |
                     v
             +----------------+
             |   Controller   |
             +----------------+
                     |
                     v
             +----------------+
             |    Service     |
             +----------------+
                     |
                     v
             +----------------+
             |   Repository   |
             +----------------+
                     |
                     v
             +----------------+
             | JPA / Hibernate|
             +----------------+
                     |
                     v
             +----------------+
             |  PostgreSQL    |
             +----------------+
```

## Responsibility of Each Layer

### Controller

Responsible for:

- Receiving HTTP requests
- Mapping URLs to Java methods
- Reading request bodies
- Returning HTTP responses

It should **not** contain database logic.

### Service

Responsible for:

- Business logic
- Business decisions
- Coordinating repositories and other services

Example:

```text
Does this dataset already exist?
    |
    +-- YES --> return existing dataset
    |
    +-- NO ---> create new dataset
```

### Repository

Responsible for:

- Communicating with the database through Spring Data JPA
- Saving entities
- Searching entities
- Updating/deleting entities

### Entity

Represents the database model in Java.

### DTO

Represents the API contract.

This keeps the external API model separate from the internal database model.

---

# 3. Technology Stack

| Technology | Purpose |
|---|---|
| Java | Backend programming language |
| Spring Boot | Application framework |
| Spring Web | REST API development |
| Spring Data JPA | Database abstraction |
| Hibernate | ORM implementation |
| PostgreSQL | Relational database |
| Maven | Dependency management and build |
| VS Code | Development environment |

---

# 4. Project Structure

Current backend structure:

```text
datamind-api/
│
├── .mvn/
│
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── datamind/
│   │   │           └── datamind_api/
│   │   │               │
│   │   │               ├── DatamindApiApplication.java
│   │   │               │
│   │   │               └── dataset/
│   │   │                   ├── controller/
│   │   │                   │   └── DatasetController.java
│   │   │                   │
│   │   │                   ├── dto/
│   │   │                   │   ├── DatasetCreateRequest.java
│   │   │                   │   └── DatasetResponse.java
│   │   │                   │
│   │   │                   ├── entity/
│   │   │                   │   ├── Dataset.java
│   │   │                   │   └── DatasetStatus.java
│   │   │                   │
│   │   │                   ├── repository/
│   │   │                   │   └── DatasetRepository.java
│   │   │                   │
│   │   │                   └── service/
│   │   │                       └── DatasetService.java
│   │   │
│   │   └── resources/
│   │       └── application.properties
│   │
│   ├── test/
│   │
│   └── target/
│
├── pom.xml
├── mvnw
├── mvnw.cmd
├── .gitignore
└── README.md
```

---

# 5. Maven

Maven manages the Java project's:

- Dependencies
- Build lifecycle
- Compilation
- Testing
- Spring Boot execution

The project contains Maven Wrapper files:

```text
mvnw
mvnw.cmd
```

This allows the project to use the Maven version configured by the project without requiring a separate Maven installation.

On Windows:

```powershell
.\mvnw.cmd spring-boot:run
```

Compile the project:

```powershell
.\mvnw.cmd compile
```

Run tests:

```powershell
.\mvnw.cmd test
```

---

# 6. PostgreSQL Configuration

The application connects to:

```text
Database: datamind
Host: localhost
Port: 5432
User: postgres
```

Example configuration:

```properties
spring.application.name=datamind-api

spring.datasource.url=jdbc:postgresql://localhost:5432/datamind
spring.datasource.username=postgres
spring.datasource.password=YOUR_PASSWORD

spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
```

## What These Properties Mean

### `spring.datasource.url`

Tells Spring where PostgreSQL is running.

```text
jdbc:postgresql://localhost:5432/datamind
```

Breakdown:

```text
jdbc
  |
  +-- PostgreSQL
        |
        +-- localhost
        +-- port 5432
        +-- database datamind
```

### `spring.datasource.username`

Database user.

### `spring.datasource.password`

Database password.

**Never commit a real database password to GitHub.**

For a real project, secrets should be supplied through environment variables or a secret-management system.

### `spring.jpa.hibernate.ddl-auto=update`

Hibernate automatically updates the database schema based on entity changes.

Useful during development.

For production systems, schema migration tools such as Flyway or Liquibase should be considered instead of relying on automatic schema updates.

### `spring.jpa.show-sql=true`

Shows generated SQL in the console.

Useful for learning and debugging.

### `spring.jpa.properties.hibernate.format_sql=true`

Formats generated SQL to make it easier to read.

---

# 7. Entity Layer

The `Dataset` class represents the dataset database record.

Conceptually:

```text
Java Object
    |
    | JPA mapping
    v
PostgreSQL Row
```

The entity contains fields such as:

```text
id
contentHash
createdAt
fileSize
fileType
name
processedAt
status
```

---

# 8. UUID Primary Key

The dataset uses a UUID as its primary key.

Conceptually:

```text
0978c4d6-37f0-4ecb-b000-ea5b8d40ea9c
```

Advantages:

- Very low collision probability
- Does not expose simple sequential IDs
- Suitable for distributed systems
- Useful when multiple services may create records

Hibernate is responsible for generating the UUID according to the entity configuration.

We therefore don't manually create the ID in the service.

---

# 9. Dataset Status

The dataset has a lifecycle status.

Current statuses include:

```text
UPLOADED
PROCESSING
COMPLETED
FAILED
```

Current implementation starts a new dataset as:

```text
UPLOADED
```

Future lifecycle:

```text
UPLOADED
    |
    v
PROCESSING
    |
    +----------------+
    |                |
    v                v
COMPLETED          FAILED
```

This status will become important when the DataMind job-processing system is implemented.

---

# 10. Why `contentHash` Exists

This is one of the most important design decisions in DataMind.

Suppose a user uploads:

```text
sales.csv
```

DataMind processes it.

Later the same dataset is uploaded again.

Without duplicate detection:

```text
Upload 1
   ↓
Process
   ↓
Store result

Upload 2
   ↓
Process again
   ↓
Waste computation
```

We don't want this.

Instead, we calculate a deterministic hash of the dataset content.

Example:

```text
Dataset
   |
   v
Hash Function
   |
   v
contentHash
```

Then:

```text
Incoming hash
      |
      v
Search database
      |
      +---- Found ----> Reuse existing dataset/analysis
      |
      +---- Not found -> Create new dataset/job
```

This improves:

- Processing efficiency
- Response time
- Infrastructure cost
- User experience

---

# 11. Database-Level Duplicate Protection

Application-level checking alone is not enough.

We also added a unique constraint on:

```text
content_hash
```

Therefore there are two layers of protection.

```text
Application
    |
    | findByContentHash()
    v
Check duplicate
    |
    v
Database
    |
    | UNIQUE(content_hash)
    v
Final protection
```

Why both?

Because two requests could theoretically arrive at almost the same time:

```text
Request A ---> check ---> not found
Request B ---> check ---> not found
Request A ---> insert
Request B ---> insert
```

The database uniqueness constraint protects against the final race condition.

Later, we'll also handle the resulting constraint violation appropriately if necessary.

---

# 12. Repository Layer

`DatasetRepository` extends:

```java
JpaRepository<Dataset, UUID>
```

This gives us standard database operations such as:

```text
save()
findById()
findAll()
delete()
existsById()
```

We also created a custom derived query:

```java
Optional<Dataset> findByContentHash(String contentHash);
```

## Spring Data JPA Derived Query

Spring interprets the method name.

```text
findByContentHash
   |
   +-- find
   |
   +-- By
   |
   +-- contentHash
```

It matches the entity field:

```java
private String contentHash;
```

Spring Data generates the appropriate query automatically.

No manual SQL was required.

### Important

Java naming matters.

Correct:

```java
findByContentHash(...)
```

Incorrect:

```java
findbyContentHash(...)
```

The incorrect capitalization caused a startup failure because Spring could not resolve the property correctly.

---

# 13. Service Layer

`DatasetService` is a Spring-managed component.

It is annotated with:

```java
@Service
```

This tells Spring:

> Create and manage this class as a service bean.

---

# 14. Dependency Injection

The service depends on `DatasetRepository`.

Instead of:

```java
new DatasetRepository();
```

we use constructor injection:

```java
private final DatasetRepository datasetRepository;

public DatasetService(DatasetRepository datasetRepository) {
    this.datasetRepository = datasetRepository;
}
```

Spring provides the repository automatically.

Conceptually:

```text
Spring Container
      |
      +-- DatasetRepository Bean
      |
      +-- DatasetService Bean
                |
                +-- receives DatasetRepository
```

This is **Dependency Injection**.

Benefits:

- Loose coupling
- Easier testing
- Better maintainability
- Spring manages object lifecycle

---

# 15. Why `Optional<Dataset>`?

The repository method returns:

```java
Optional<Dataset>
```

because a dataset may or may not exist.

Instead of returning `null`, we explicitly represent the two possible states:

```text
Optional<Dataset>
      |
      +-- Dataset exists
      |
      +-- Empty
```

This makes the absence of a record explicit.

---

# 16. DTO Layer

We created two DTOs.

```text
DatasetCreateRequest
DatasetResponse
```

## Request DTO

Represents what the client sends:

```json
{
  "name": "sales.csv",
  "contentHash": "abc123",
  "fileSize": 2450120,
  "fileType": "CSV"
}
```

## Response DTO

Represents what the API returns:

```json
{
  "id": "0978c4d6-37f0-4ecb-b000-ea5b8d40ea9c",
  "name": "sales.csv",
  "contentHash": "abc123",
  "fileSize": 2450120,
  "fileType": "CSV",
  "status": "UPLOADED",
  "createdAt": "...",
  "processedAt": null
}
```

---

# 17. Why Not Return the Entity Directly?

We could technically return:

```text
Dataset
```

directly from the controller.

But that creates tight coupling between:

```text
Database model
        =
API model
```

That's undesirable.

Instead:

```text
Database Entity
       |
       v
DatasetResponse
       |
       v
JSON
```

This gives us freedom to change the database model without automatically changing the public API.

---

# 18. REST Controller

The controller exposes:

```http
POST /api/datasets
```

It is defined using:

```java
@RestController
@RequestMapping("/api/datasets")
```

The method uses:

```java
@PostMapping
```

and:

```java
@RequestBody DatasetCreateRequest request
```

Spring/Jackson converts JSON into our Java request object.

---

# 19. API Contract

## Create/Register Dataset

### Endpoint

```http
POST /api/datasets
```

### Request

```json
{
  "name": "sales.csv",
  "contentHash": "abc123",
  "fileSize": 2450120,
  "fileType": "CSV"
}
```

### Successful response

```json
{
  "id": "0978c4d6-37f0-4ecb-b000-ea5b8d40ea9c",
  "name": "sales.csv",
  "contentHash": "abc123",
  "fileSize": 2450120,
  "fileType": "CSV",
  "status": "UPLOADED",
  "createdAt": "2026-08-20T22:58:13.5589151",
  "processedAt": null
}
```

---

# 20. End-to-End Request Flow

The complete request lifecycle is:

```text
1. Client sends JSON
          |
          v
2. POST /api/datasets
          |
          v
3. DatasetController
          |
          v
4. Jackson converts JSON → DatasetCreateRequest
          |
          v
5. Controller calls DatasetService
          |
          v
6. Service checks contentHash
          |
          +------ Existing ------> return existing Dataset
          |
          +------ New -----------> create Dataset
                                      |
                                      v
                              DatasetRepository
                                      |
                                      v
                                   Hibernate
                                      |
                                      v
                                 PostgreSQL
                                      |
                                      v
                                   Dataset
                                      |
                                      v
                              DatasetResponse
                                      |
                                      v
                                    JSON
```

---

# 21. Testing the API

PowerShell's native HTTP client was used because quoting JSON through `curl` caused malformed JSON during testing.

Working test:

```powershell
$body = @{
    name = "sales.csv"
    contentHash = "abc123"
    fileSize = 2450120
    fileType = "CSV"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:8080/api/datasets" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

Expected response contains:

```text
name         : sales.csv
contentHash  : abc123
fileSize     : 2450120
fileType     : CSV
status       : UPLOADED
```

---

# 22. Database Verification

Connect to PostgreSQL:

```powershell
psql -U postgres -d datamind
```

Then:

```sql
SELECT id, name, content_hash, file_size, file_type, status
FROM dataset;
```

After the first request:

```text
1 row
```

After submitting the same dataset again:

```text
1 row
```

This verified that duplicate detection works.

---

# 23. Debugging Lessons From Today

Today we encountered several real development errors.

## Maven Command Not Found

Initially:

```text
mvn : The term 'mvn' is not recognized
```

The project already contained Maven Wrapper files, so we used:

```powershell
.\mvnw.cmd spring-boot:run
```

Lesson:

> Maven Wrapper makes the project easier to run without depending on a globally installed Maven command.

---

## PostgreSQL `psql` Not Found

Initially:

```text
psql : The term 'psql' is not recognized
```

PostgreSQL was installed, but its executable directory wasn't available directly through the shell PATH.

After locating:

```text
C:\Program Files\PostgreSQL\18\bin\psql.exe
```

we were able to connect successfully.

Lesson:

> Installed software and shell PATH availability are separate concerns.

---

## Repository Naming Error

We had:

```java
findbyContentHash(...)
```

instead of:

```java
findByContentHash(...)
```

Spring failed during startup because the repository query method could not be resolved.

Lesson:

> Spring Data JPA derives queries from method names, so naming conventions are part of the framework's behavior.

---

## Malformed JSON

The initial PowerShell/curl request caused:

```text
JSON parse error
```

The server received malformed JSON.

We switched to:

```powershell
Invoke-RestMethod
```

with:

```powershell
ConvertTo-Json
```

Lesson:

> When debugging an API, distinguish between a client/request problem and a server/application problem before changing backend code.

---

# 24. Important Concepts Learned

Today's implementation connected these concepts to a real project:

### Spring Boot

Framework for building the backend application.

### Spring Container

Manages Spring beans and their lifecycle.

### Dependency Injection

Spring supplies dependencies instead of classes creating them manually.

### `@Service`

Marks a class as a service-layer Spring bean.

### `@RestController`

Marks a class as a REST API controller.

### `@RequestMapping`

Defines a base URL.

### `@PostMapping`

Maps HTTP POST requests to a Java method.

### `@RequestBody`

Converts incoming JSON into a Java object.

### DTO

Separates API contracts from database entities.

### Entity

Maps Java objects to database tables.

### Repository

Provides database access through Spring Data JPA.

### JPA

Java persistence specification.

### Hibernate

ORM implementation used by Spring Boot.

### PostgreSQL

Relational database used for persistent storage.

### ORM

Maps:

```text
Java Objects ↔ Database Tables
```

### Derived Query

Spring generates database queries from repository method names.

### UUID

Unique identifier used as the dataset primary key.

### Database Constraint

Database-level protection such as:

```text
UNIQUE(content_hash)
```

### Layered Architecture

Separates:

```text
Controller
Service
Repository
Database
```

---

# 25. Current DataMind Dataset Architecture

Current implementation:

```text
                  DATASET API
                      |
                      v
             +------------------+
             | DatasetController|
             +------------------+
                      |
                      v
             +------------------+
             |  DatasetService  |
             +------------------+
                /           \
               /             \
              v               v
   findByContentHash()    create Dataset
              |               |
              v               v
       Existing Dataset   DatasetRepository
                              |
                              v
                           Hibernate
                              |
                              v
                         PostgreSQL
```

---

# 26. Current Database Model

```text
Dataset
--------------------------------
id              UUID PK
content_hash    VARCHAR UNIQUE
created_at      TIMESTAMP
file_size       BIGINT
file_type       VARCHAR
name            VARCHAR
processed_at    TIMESTAMP
status          VARCHAR
```

Status constraint:

```text
UPLOADED
PROCESSING
COMPLETED
FAILED
```

---

# 27. What Is NOT Implemented Yet?

The current implementation is deliberately only the foundation.

Not yet implemented:

- Actual file upload
- Dataset storage
- Job table
- Job queue
- Processing worker
- Analytics pipeline
- Python analytics integration
- Analysis result storage
- Analysis retrieval API
- Dataset processing lifecycle
- Failure/retry system
- Authentication/authorization
- API validation
- Global exception handling
- Logging strategy
- Automated tests
- Docker deployment
- Production configuration

These will be implemented incrementally.

---

# 28. Planned DataMind Architecture

The architecture we are moving toward is:

```text
                    USER
                     |
                     v
               Dataset Upload
                     |
                     v
             +---------------+
             | Dataset API   |
             +---------------+
                     |
                     v
              Calculate Hash
                     |
                     v
             Check Dataset DB
                /         \
               /           \
           EXISTS          NEW
             |              |
             v              v
       Retrieve stored   Create Dataset
          analysis          |
             |              v
             |          Create Job
             |              |
             |              v
             |         Job Processing
             |              |
             |              v
             |       Python Analytics
             |              |
             |              v
             |       Store Analysis
             |              |
             +------<--------+
                     |
                     v
                API Response
```

---

# 29. Next Development Milestone

The next major backend feature should be the **Job System**.

We will introduce a separate job model:

```text
Job
--------------------------------
id
dataset_id
status
created_at
started_at
completed_at
error_message
```

Then:

```text
Dataset
   |
   +---- Job
          |
          +---- PROCESSING
          |
          +---- COMPLETED
          |
          +---- FAILED
```

This will allow DataMind to distinguish:

```text
Dataset
=
The data being analyzed
```

from:

```text
Job
=
A particular processing attempt for that dataset
```

This distinction becomes important for retries, asynchronous processing, monitoring, and future distributed architecture.

---

# 30. Development Philosophy

The goal of DataMind is not to build everything at once.

We are following:

```text
Learn Concept
     ↓
Understand Why
     ↓
Design
     ↓
Implement
     ↓
Run
     ↓
Test
     ↓
Debug
     ↓
Document
     ↓
Extend
```

Today's implementation is the first complete cycle of that process.

The important result is not just that the API works.

The important result is understanding **why each layer exists and how the layers communicate**.

---

# 31. Current Milestone

```text
[████████████████████] Dataset persistence foundation

✓ Spring Boot project
✓ Maven
✓ PostgreSQL
✓ Database connection
✓ JPA/Hibernate
✓ Dataset entity
✓ Dataset status
✓ Repository
✓ Derived query
✓ Service layer
✓ Dependency Injection
✓ Request DTO
✓ Response DTO
✓ REST Controller
✓ POST /api/datasets
✓ PostgreSQL persistence
✓ Content hash duplicate detection
✓ Database verification
✓ End-to-end API verification
```

---

# 32. Revision Checklist

Before moving to the next module, make sure you can explain these without looking at the code:

- What problem does Spring Boot solve?
- What is the Spring Container?
- What is a Bean?
- What is Dependency Injection?
- Why use constructor injection?
- What is the responsibility of a Controller?
- What is the responsibility of a Service?
- What is the responsibility of a Repository?
- What is an Entity?
- What is JPA?
- What is Hibernate?
- What is ORM?
- Why use DTOs?
- Why shouldn't the entity automatically become the API contract?
- What does `@RestController` do?
- What does `@RequestBody` do?
- What does `@PostMapping` do?
- How does Spring Data derive a query from `findByContentHash()`?
- Why does `Optional<Dataset>` make sense?
- Why do we need `contentHash`?
- Why is duplicate detection useful?
- Why do we need both application-level checking and a database `UNIQUE` constraint?
- What happens when a POST request reaches the backend?
- How does a Java object eventually become a PostgreSQL row?
- How does a PostgreSQL row eventually become JSON?

If you can explain these concepts in your own words, today's implementation has achieved its learning objective.

---

# 33. Final Takeaway

The most important architecture learned today is:

```text
HTTP
 ↓
Controller
 ↓
DTO
 ↓
Service
 ↓
Entity
 ↓
Repository
 ↓
JPA / Hibernate
 ↓
PostgreSQL
```

And the most important DataMind business rule implemented today is:

```text
Dataset
   ↓
contentHash
   ↓
Already processed/registered?
   |
   +---- YES → Reuse existing record
   |
   +---- NO → Create new dataset
```

This foundation will support the next major feature:

```text
Dataset → Job → Processing → Analysis → Stored Result
```

---

## Status

**Milestone:** `Dataset API + Persistence + Duplicate Detection`

**Backend:** Spring Boot

**Database:** PostgreSQL 18

**Next milestone:** Job Management and Processing Pipeline


---

# 34. Development Log — 2026-08-23

Today's work extended the backend from basic dataset persistence into the first working **asynchronous analysis-job pipeline**.

## Analysis Job Module

Implemented the analysis-job domain with:

```text
AnalysisJob
├── id
├── dataset_id
├── analysis_type
├── status
├── retry_count
├── created_at
├── started_at
└── completed_at
```

The job lifecycle is:

```text
PENDING
   |
   v
PROCESSING
   |
   +------------+
   |            |
   v            v
COMPLETED     FAILED
```

## Analysis Job API

Implemented and tested:

```http
POST /api/analysis/jobs
GET  /api/analysis/jobs/{id}
```

The API was tested using **Postman** for clearer JSON responses and easier request management.

Invalid job IDs are handled by the global exception system and return:

```json
{
  "status": 404,
  "error": "ANALYSIS_JOB_NOT_FOUND",
  "message": "..."
}
```

## Global Exception Handling

Created an application-wide exception package:

```text
exception/
├── ErrorResponse.java
└── GlobalExceptionHandler.java
```

The global handler currently handles:

```text
DatasetNotFoundException
AnalysisJobNotFoundException
```

`ErrorResponse` was moved out of the Dataset DTO package because it is an application-wide API error contract rather than a Dataset-specific DTO.

## Controlled Job State Transitions

Added domain methods to `AnalysisJob`:

```java
markAsProcessing()
markAsCompleted()
markAsFailed()
incrementRetryCount()
```

This keeps job lifecycle changes inside meaningful domain operations.

## Retry Support

Added:

```text
retry_count INTEGER NOT NULL DEFAULT 0
```

to `analysis_jobs`.

This prepares the system for retry handling when the Python analysis service is temporarily unavailable.

## Database Verification

Verified the PostgreSQL schema and analysis jobs. The worker successfully changes jobs from:

```text
PENDING → PROCESSING
```

with:

```text
retry_count = 0
started_at  = populated
completed_at = NULL
```

## First Job Worker

Implemented:

```text
analysis/worker/
└── AnalysisJobWorker.java
```

using:

```java
@Scheduled(fixedDelay = 5000)
```

Current flow:

```text
Every 5 seconds
      |
      v
Find oldest PENDING job
      |
      v
Mark PROCESSING
      |
      v
Save to PostgreSQL
```

The database is currently acting as the persistent job queue rather than an in-memory Java `List`.

## FIFO Job Selection

The repository now selects the oldest pending job using:

```text
findNextPendingJob(...)
```

Conceptually:

```sql
SELECT *
FROM analysis_jobs
WHERE status = 'PENDING'
ORDER BY created_at ASC
LIMIT 1;
```

This establishes FIFO processing behavior.

## Current Execution Architecture

```text
Client
   |
   | POST /api/analysis/jobs
   v
AnalysisJobController
   |
   v
AnalysisJobService
   |
   v
PostgreSQL
   |
   | PENDING
   v
AnalysisJobWorker
   |
   | PROCESSING
   v
Python Analysis API
   |
   | Analysis result
   v
AnalysisJobWorker
   |
   +---- COMPLETED
   |
   +---- FAILED
   |
   v
PostgreSQL
```

The Python integration is the next major implementation step.

## Important Development Lessons

### DTO Responsibility

Feature-specific DTOs remain inside their modules:

```text
dataset/dto/
analysis/dto/
```

Application-wide error contracts belong in the cross-cutting exception package:

```text
exception/ErrorResponse.java
```

### Database Schema Evolution

Adding a Java entity field does not replace proper database migration management.

For development, the new column was added with:

```sql
ALTER TABLE analysis_jobs
ADD COLUMN retry_count INTEGER NOT NULL DEFAULT 0;
```

For production, the project should eventually use Flyway or Liquibase.

### Repository Naming

Spring Data JPA derives repository behavior from method names. A naming mismatch can prevent the application from starting.

Example:

```text
findByContentHash()    ✓
findbyContentHash()    ✗
```

## Current Milestone

```text
[████████████████████] Backend Job Foundation

✓ Dataset API
✓ Dataset persistence
✓ Duplicate detection
✓ Global exception handling
✓ Error response contract
✓ Analysis Job entity
✓ Analysis Job API
✓ Analysis Job persistence
✓ Job status lifecycle
✓ Retry counter
✓ Postman API testing
✓ PostgreSQL job verification
✓ Database-backed job polling
✓ PENDING → PROCESSING worker
□ Transaction-safe job claiming
□ Java → Python API contract
□ Python/FastAPI analysis service
□ EDA execution
□ PROCESSING → COMPLETED
□ PROCESSING → FAILED
□ Retry execution
□ Analysis result storage
```

## Next Development Session

The next implementation step is **transaction-safe job claiming** so multiple workers cannot claim the same pending job.

After that, we will implement the Java → Python API contract and connect the first `EDA` execution pipeline.


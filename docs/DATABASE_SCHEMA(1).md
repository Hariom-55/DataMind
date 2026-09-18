# DataMind Database Schema

> **Status:** Current entity-level schema documentation\
> **Database:** PostgreSQL\
> **ORM:** Spring Data JPA / Hibernate

## 1. Database Architecture

DataMind uses PostgreSQL for persistent application state.

The core persistence model is:

``` text
Dataset
   |
   +--------------------+
   |                    |
   v                    v
AnalysisJob        DatasetLineage
   |
   v
AnalysisResult
```

The inspected Java entities map to four core tables:

``` text
datasets
dataset_lineage
analysis_jobs
analysis_results
```

> Column names shown below follow the explicit JPA mappings plus the
> project's Hibernate naming convention. The entity definitions are the
> source of truth; a live database inspection should be used before
> treating this document as a migration specification.

------------------------------------------------------------------------

# 2. Entity Relationship Diagram

``` mermaid
erDiagram
    DATASETS ||--o{ ANALYSIS_JOBS : "has"
    DATASETS ||--o{ DATASET_LINEAGE : "parent"
    DATASETS ||--o| DATASET_LINEAGE : "child"
    ANALYSIS_JOBS ||--o| ANALYSIS_RESULTS : "produces"

    DATASETS {
        UUID id PK
        VARCHAR name
        VARCHAR content_hash UK
        VARCHAR storage_path
        BIGINT file_size
        VARCHAR file_type
        VARCHAR status
        TIMESTAMP created_at
        TIMESTAMP processed_at
    }

    ANALYSIS_JOBS {
        UUID id PK
        UUID dataset_id FK
        VARCHAR analysis_type
        VARCHAR status
        INTEGER retry_count
        TIMESTAMP created_at
        TIMESTAMP started_at
        TIMESTAMP completed_at
        TEXT error_message
        VARCHAR target_column
    }

    ANALYSIS_RESULTS {
        UUID id PK
        UUID job_id FK UK
        JSONB result_data
        TIMESTAMP created_at
    }

    DATASET_LINEAGE {
        UUID id PK
        UUID parent_dataset_id FK
        UUID child_dataset_id FK UK
        VARCHAR operation
        VARCHAR column_name
        INTEGER rows_affected
        TEXT details
        TIMESTAMP created_at
    }
```

------------------------------------------------------------------------

# 3. `datasets`

Java entity:

``` text
Dataset
```

Table:

``` text
datasets
```

  -----------------------------------------------------------------------
  Field             Database role     Constraints       Purpose
  ----------------- ----------------- ----------------- -----------------
  `id`              Primary key       PK                Dataset
                                                        identifier

  `name`            Dataset name      NOT NULL          Original filename

  `content_hash`    Content           NOT NULL, UNIQUE  Duplicate
                    fingerprint                         detection

  `storage_path`    File location     NOT NULL          Stored dataset
                                                        path

  `file_size`       File size         ---               Size of uploaded
                                                        file

  `file_type`       File type         ---               MIME/content type

  `status`          Lifecycle state   Enum as String    Dataset status

  `created_at`      Creation time     ---               Registration
                                                        timestamp

  `processed_at`    Completion time   ---               Processing
                                                        completion
                                                        timestamp
  -----------------------------------------------------------------------

## Dataset status

``` text
UPLOADED
   |
   v
PROCESSING
   |
   +-------> COMPLETED
   |
   +-------> FAILED
```

The dataset service calculates a SHA-256 content hash before creating a
new record.

The database `UNIQUE` constraint on `content_hash` provides a second
layer of protection against duplicate registration.

------------------------------------------------------------------------

# 4. `analysis_jobs`

Java entity:

``` text
AnalysisJob
```

Table:

``` text
analysis_jobs
```

  -----------------------------------------------------------------------
  Field             Database role     Constraints       Purpose
  ----------------- ----------------- ----------------- -----------------
  `id`              Primary key       PK                Job identifier

  `dataset_id`      Foreign key       NOT NULL          Dataset being
                                                        analyzed

  `analysis_type`   Analysis type     NOT NULL          Requested
                                                        analysis

  `status`          Job lifecycle     NOT NULL          Current job state

  `retry_count`     Retry counter     NOT NULL, default Number of retries
                                      0                 

  `created_at`      Creation time     NOT NULL          Job creation
                                                        timestamp

  `started_at`      Start time        Nullable          Processing start

  `completed_at`    Completion time   Nullable          Completion time

  `error_message`   Error details     TEXT              Failure
                                                        information

  `target_column`   ML target         Nullable          Optional target
                                                        column
  -----------------------------------------------------------------------

Relationship:

``` text
datasets.id
     |
     | 1
     |
     | N
analysis_jobs.dataset_id
```

One dataset can have multiple analysis jobs.

------------------------------------------------------------------------

# 5. `analysis_results`

Java entity:

``` text
AnalysisResult
```

Table:

``` text
analysis_results
```

  -----------------------------------------------------------------------
  Field             Database role     Constraints       Purpose
  ----------------- ----------------- ----------------- -----------------
  `id`              Primary key       PK                Result identifier

  `job_id`          Foreign key       NOT NULL, UNIQUE  Source analysis
                                                        job

  `result_data`     JSON result       NOT NULL, JSONB   Structured
                                                        analysis output

  `created_at`      Creation time     NOT NULL          Result creation
                                                        timestamp
  -----------------------------------------------------------------------

Relationship:

``` text
analysis_jobs.id
       |
       | 1
       |
       | 0..1
       v
analysis_results.job_id
```

The `job_id` unique constraint makes the relationship one-to-one at the
database level.

------------------------------------------------------------------------

# 6. `dataset_lineage`

Java entity:

``` text
DatasetLineage
```

Table:

``` text
dataset_lineage
```

  ---------------------------------------------------------------------------
  Field                 Database role     Constraints       Purpose
  --------------------- ----------------- ----------------- -----------------
  `id`                  Primary key       PK                Lineage record
                                                            identifier

  `parent_dataset_id`   Foreign key       NOT NULL          Source dataset

  `child_dataset_id`    Foreign key       NOT NULL, UNIQUE  Derived dataset

  `operation`           Operation name    NOT NULL          Transformation
                                                            performed

  `column_name`         Affected column   Nullable          Column involved

  `rows_affected`       Change count      Nullable          Number of
                                                            affected rows

  `details`             Metadata          TEXT              Additional
                                                            information

  `created_at`          Creation time     NOT NULL          Lineage timestamp
  ---------------------------------------------------------------------------

The child dataset relationship is unique in the current entity
definition.

Conceptually:

``` text
Parent Dataset
      |
      | transformation
      v
Child Dataset
```

Example:

``` text
raw.csv
   |
   | remove_missing_values
   v
cleaned.csv
```

------------------------------------------------------------------------

# 7. Foreign-Key Relationships

## Analysis jobs

``` text
analysis_jobs.dataset_id
        ↓
datasets.id
```

## Analysis results

``` text
analysis_results.job_id
        ↓
analysis_jobs.id
```

## Dataset lineage

``` text
dataset_lineage.parent_dataset_id
        ↓
datasets.id

dataset_lineage.child_dataset_id
        ↓
datasets.id
```

------------------------------------------------------------------------

# 8. JSONB Result Storage

`analysis_results.result_data` is stored as PostgreSQL `JSONB`.

Conceptually:

``` text
AnalysisResult
     |
     v
Map<String, Object>
     |
     v
PostgreSQL JSONB
```

This supports heterogeneous analysis output such as:

``` text
EDA
Statistical Analysis
Machine Learning
Insights
Visualizations
```

without requiring a separate relational table for every result
structure.

------------------------------------------------------------------------

# 9. Database Responsibilities

PostgreSQL provides:

-   persistent dataset metadata
-   duplicate protection
-   analysis-job persistence
-   job state persistence
-   retry state
-   analysis-result persistence
-   structured JSON result storage
-   dataset lineage persistence
-   transactional consistency

The database is also used as the persistent source of pending analysis
jobs rather than relying on an in-memory queue.

------------------------------------------------------------------------

# 10. Development Schema Management

Current development configuration uses:

``` properties
spring.jpa.hibernate.ddl-auto=update
```

This is convenient during development.

For production deployment, schema evolution should eventually be managed
through explicit migrations such as Flyway or Liquibase.

------------------------------------------------------------------------

# 11. Data Lifecycle

``` text
UPLOAD
  |
  v
datasets
  |
  v
CREATE ANALYSIS JOB
  |
  v
analysis_jobs
  |
  v
WORKER PROCESSING
  |
  v
Python Analysis
  |
  v
analysis_results
```

Dataset transformations can additionally create:

``` text
parent dataset
      |
      v
dataset_lineage
      |
      v
child dataset
```

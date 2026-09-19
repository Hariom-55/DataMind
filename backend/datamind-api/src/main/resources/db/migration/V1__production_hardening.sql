
CREATE TABLE IF NOT EXISTS datasets (
                                        id uuid NOT NULL PRIMARY KEY,
                                        name varchar(255) NOT NULL,
    content_hash varchar(255) NOT NULL,
    storage_path varchar(255) NOT NULL,
    file_size bigint,
    file_type varchar(255),
    status varchar(255),
    created_at timestamp,
    processed_at timestamp
    );

CREATE TABLE IF NOT EXISTS analysis_jobs (
                                             id uuid NOT NULL PRIMARY KEY,
                                             dataset_id uuid NOT NULL,
                                             analysis_type varchar(255) NOT NULL,
    status varchar(255) NOT NULL,
    retry_count integer NOT NULL DEFAULT 0,
    created_at timestamp NOT NULL,
    started_at timestamp,
    completed_at timestamp,
    error_message text,
    target_column varchar(255)
    );

CREATE TABLE IF NOT EXISTS analysis_results (
                                                id uuid NOT NULL PRIMARY KEY,
                                                job_id uuid NOT NULL,
                                                result_data jsonb NOT NULL,
                                                created_at timestamp NOT NULL
);

CREATE TABLE IF NOT EXISTS dataset_lineage (
                                               id uuid NOT NULL PRIMARY KEY,
                                               parent_dataset_id uuid NOT NULL,
                                               child_dataset_id uuid NOT NULL,
                                               operation varchar(255) NOT NULL,
    column_name varchar(255),
    rows_affected integer,
    details text,
    created_at timestamp NOT NULL
    );


ALTER TABLE analysis_jobs DROP CONSTRAINT IF EXISTS analysis_jobs_analysis_type_check;
ALTER TABLE analysis_jobs
    ADD CONSTRAINT analysis_jobs_analysis_type_check
        CHECK (analysis_type IN ('EDA', 'STATISTICAL', 'MACHINE_LEARNING', 'INSIGHT', 'TIME_SERIES', 'TEXT_ANALYSIS'));

ALTER TABLE analysis_jobs DROP CONSTRAINT IF EXISTS analysis_jobs_status_check;
ALTER TABLE analysis_jobs
    ADD CONSTRAINT analysis_jobs_status_check
        CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED'));

ALTER TABLE analysis_jobs DROP CONSTRAINT IF EXISTS analysis_jobs_retry_count_check;
ALTER TABLE analysis_jobs
    ADD CONSTRAINT analysis_jobs_retry_count_check
        CHECK (retry_count >= 0);

ALTER TABLE datasets DROP CONSTRAINT IF EXISTS datasets_content_hash_key;
ALTER TABLE datasets
    ADD CONSTRAINT datasets_content_hash_key UNIQUE (content_hash);

ALTER TABLE analysis_results DROP CONSTRAINT IF EXISTS analysis_results_job_id_key;
ALTER TABLE analysis_results
    ADD CONSTRAINT analysis_results_job_id_key UNIQUE (job_id);

ALTER TABLE analysis_jobs DROP CONSTRAINT IF EXISTS analysis_jobs_dataset_id_fkey;
ALTER TABLE analysis_jobs
    ADD CONSTRAINT analysis_jobs_dataset_id_fkey
        FOREIGN KEY (dataset_id) REFERENCES datasets(id);

ALTER TABLE dataset_lineage DROP CONSTRAINT IF EXISTS dataset_lineage_parent_dataset_id_fkey;
ALTER TABLE dataset_lineage
    ADD CONSTRAINT dataset_lineage_parent_dataset_id_fkey
        FOREIGN KEY (parent_dataset_id) REFERENCES datasets(id);

ALTER TABLE dataset_lineage DROP CONSTRAINT IF EXISTS dataset_lineage_child_dataset_id_fkey;
ALTER TABLE dataset_lineage
    ADD CONSTRAINT dataset_lineage_child_dataset_id_fkey
        FOREIGN KEY (child_dataset_id) REFERENCES datasets(id);

ALTER TABLE dataset_lineage DROP CONSTRAINT IF EXISTS dataset_lineage_child_dataset_id_key;
ALTER TABLE dataset_lineage
    ADD CONSTRAINT dataset_lineage_child_dataset_id_key UNIQUE (child_dataset_id);

ALTER TABLE analysis_results DROP CONSTRAINT IF EXISTS analysis_results_job_id_fkey;
ALTER TABLE analysis_results
    ADD CONSTRAINT analysis_results_job_id_fkey
        FOREIGN KEY (job_id) REFERENCES analysis_jobs(id);

CREATE INDEX IF NOT EXISTS idx_analysis_jobs_status_created_at
    ON analysis_jobs(status, created_at, id);

CREATE INDEX IF NOT EXISTS idx_analysis_jobs_dataset_id
    ON analysis_jobs(dataset_id);

CREATE INDEX IF NOT EXISTS idx_analysis_jobs_status_started_at
    ON analysis_jobs(status, started_at);

CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at
    ON analysis_results(created_at);

CREATE INDEX IF NOT EXISTS idx_dataset_lineage_parent_dataset_id
    ON dataset_lineage(parent_dataset_id);

CREATE INDEX IF NOT EXISTS idx_dataset_lineage_created_at
    ON dataset_lineage(created_at);


ALTER TABLE datasets ADD COLUMN IF NOT EXISTS logical_dataset_id uuid;
ALTER TABLE datasets ADD COLUMN IF NOT EXISTS version_number integer;
ALTER TABLE datasets ADD COLUMN IF NOT EXISTS current_version_id uuid;

UPDATE datasets
SET logical_dataset_id = id
WHERE logical_dataset_id IS NULL;

UPDATE datasets
SET version_number = 1
WHERE version_number IS NULL;

UPDATE datasets
SET current_version_id = id
WHERE current_version_id IS NULL;

ALTER TABLE datasets ALTER COLUMN logical_dataset_id SET NOT NULL;
ALTER TABLE datasets ALTER COLUMN version_number SET NOT NULL;

ALTER TABLE datasets DROP CONSTRAINT IF EXISTS datasets_content_hash_key;
ALTER TABLE datasets DROP CONSTRAINT IF EXISTS uk_datasets_logical_hash;
ALTER TABLE datasets DROP CONSTRAINT IF EXISTS uk_datasets_logical_version;

ALTER TABLE datasets
    ADD CONSTRAINT uk_datasets_logical_hash
        UNIQUE (logical_dataset_id, content_hash);

ALTER TABLE datasets
    ADD CONSTRAINT uk_datasets_logical_version
        UNIQUE (logical_dataset_id, version_number);

CREATE INDEX IF NOT EXISTS idx_datasets_logical_dataset_id
    ON datasets(logical_dataset_id);

CREATE INDEX IF NOT EXISTS idx_datasets_logical_current_version
    ON datasets(logical_dataset_id, current_version_id);

ALTER TABLE datasets
    ADD CONSTRAINT datasets_version_number_check
        CHECK (version_number > 0);

-- Pin analysis jobs to the immutable version used by the worker.
ALTER TABLE analysis_jobs ADD COLUMN IF NOT EXISTS dataset_version_id uuid;

UPDATE analysis_jobs
SET dataset_version_id = dataset_id
WHERE dataset_version_id IS NULL;

ALTER TABLE analysis_jobs ALTER COLUMN dataset_version_id SET NOT NULL;

ALTER TABLE analysis_jobs
DROP CONSTRAINT IF EXISTS analysis_jobs_dataset_version_id_fkey;

ALTER TABLE analysis_jobs
    ADD CONSTRAINT analysis_jobs_dataset_version_id_fkey
        FOREIGN KEY (dataset_version_id) REFERENCES datasets(id);

CREATE INDEX IF NOT EXISTS idx_analysis_jobs_dataset_version_id
    ON analysis_jobs(dataset_version_id);

-- Dataset lineage remains version-to-version; a child version can have one parent.
ALTER TABLE dataset_lineage DROP CONSTRAINT IF EXISTS dataset_lineage_child_dataset_id_key;

ALTER TABLE dataset_lineage
    ADD CONSTRAINT dataset_lineage_child_dataset_id_key
        UNIQUE (child_dataset_id);

-- Contract metadata for result consumers.
ALTER TABLE analysis_results
    ADD COLUMN IF NOT EXISTS contract_version varchar(32);

UPDATE analysis_results
SET contract_version = 'v1'
WHERE contract_version IS NULL;

ALTER TABLE analysis_results
    ALTER COLUMN contract_version SET NOT NULL;

CREATE INDEX IF NOT EXISTS idx_analysis_results_contract_version
    ON analysis_results(contract_version);

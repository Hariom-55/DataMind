ALTER TABLE analysis_jobs
    ADD COLUMN IF NOT EXISTS enable_hyperparameter_tuning boolean NOT NULL DEFAULT false;

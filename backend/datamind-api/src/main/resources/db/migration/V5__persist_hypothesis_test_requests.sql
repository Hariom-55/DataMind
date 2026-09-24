ALTER TABLE analysis_jobs
    ADD COLUMN IF NOT EXISTS hypothesis_tests jsonb NOT NULL DEFAULT '[]'::jsonb;

ALTER TABLE dataset_lineage
    ADD COLUMN IF NOT EXISTS operation_config jsonb NOT NULL DEFAULT '[]'::jsonb;

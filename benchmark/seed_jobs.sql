-- seed_jobs.sql
-- Seeds N PENDING analysis jobs against your FIRST existing dataset, purely to
-- test concurrent job CLAIMING (not to test analysis correctness at scale).
-- Adjust the LIMIT in the generate_series() call to control how many jobs.
--
-- Run: psql -U postgres -d datamind -f seed_jobs.sql

DO $$
DECLARE
  target_dataset_id UUID;
  i INT;
BEGIN
  SELECT id INTO target_dataset_id FROM datasets LIMIT 1;

  IF target_dataset_id IS NULL THEN
    RAISE EXCEPTION 'No datasets found — upload at least one dataset first.';
  END IF;

  FOR i IN 1..150 LOOP
    INSERT INTO analysis_jobs (id, dataset_id, dataset_version_id, analysis_type, status, retry_count, created_at)
    VALUES (gen_random_uuid(), target_dataset_id, target_dataset_id, 'EDA', 'PENDING', 0, now());
  END LOOP;
END $$;

SELECT COUNT(*) AS pending_jobs_seeded FROM analysis_jobs WHERE status = 'PENDING';

-- queries.sql
-- Run against your datamind Postgres DB after a batch of test jobs.
-- psql -U postgres -d datamind -f queries.sql

-- 1. Job success rate
SELECT
  COUNT(*) FILTER (WHERE status = 'COMPLETED')::float
    / NULLIF(COUNT(*), 0) * 100 AS success_rate_pct,
  COUNT(*) AS total_jobs,
  COUNT(*) FILTER (WHERE status = 'COMPLETED') AS completed,
  COUNT(*) FILTER (WHERE status = 'FAILED') AS failed
FROM analysis_jobs;
-- Resume: "99.X% job success rate across N processed jobs"

-- 2. Average / p95 processing time (COMPLETED jobs only)
SELECT
  AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) AS avg_seconds,
  PERCENTILE_CONT(0.95) WITHIN GROUP (
    ORDER BY EXTRACT(EPOCH FROM (completed_at - started_at))
  ) AS p95_seconds
FROM analysis_jobs
WHERE status = 'COMPLETED' AND started_at IS NOT NULL AND completed_at IS NOT NULL;
-- Resume: "Processed datasets in avg Xs (p95 Ys)"

-- 3. Processing time bucketed by dataset size
SELECT
  CASE
    WHEN d.file_size < 1000000 THEN '<1MB'
    WHEN d.file_size < 10000000 THEN '1-10MB'
    WHEN d.file_size < 100000000 THEN '10-100MB'
    ELSE '100MB+'
  END AS size_bucket,
  COUNT(*) AS job_count,
  AVG(EXTRACT(EPOCH FROM (j.completed_at - j.started_at))) AS avg_seconds
FROM analysis_jobs j
JOIN datasets d ON d.id = j.dataset_id
WHERE j.status = 'COMPLETED'
GROUP BY size_bucket
ORDER BY MIN(d.file_size);
-- Resume: "Handled datasets up to XMB, processing in Ys avg"

-- 4. Retry recovery rate (jobs that eventually completed after at least 1 retry)
SELECT
  COUNT(*) FILTER (WHERE status = 'COMPLETED' AND retry_count > 0)::float
    / NULLIF(COUNT(*) FILTER (WHERE retry_count > 0), 0) * 100 AS recovery_rate_pct,
  COUNT(*) FILTER (WHERE retry_count > 0) AS jobs_that_retried
FROM analysis_jobs;
-- Resume: "Automatic retry recovered X% of transient failures"

-- 5. Duplicate detection hit rate (how often dedup saved a reprocess)
-- Requires logging or a reused-count column; if you don't have one yet,
-- add: ALTER TABLE datasets ADD COLUMN reuse_count INT DEFAULT 0;
-- and increment it in DatasetService when contentHash is found.
SELECT
  COUNT(*) AS total_datasets,
  SUM(reuse_count) AS total_reuses,
  ROUND(SUM(reuse_count)::numeric / NULLIF(COUNT(*), 0), 2) AS avg_reuse_per_dataset
FROM datasets;
-- Resume: "Content-hash dedup avoided N redundant analysis runs"

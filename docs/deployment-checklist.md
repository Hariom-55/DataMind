# Production deployment checklist

This checklist is a deployment preparation aid. It contains no credentials. Do not deploy the current revision until the storage and security blockers below are resolved.

## Target services

| Service | Provider | Build / health |
| --- | --- | --- |
| React + Vite frontend | Vercel | Root directory `frontend/datamind-web`; `npm ci`; `npm run build` |
| Spring Boot API | Render | Dockerfile `backend/datamind-api/Dockerfile`; port `$PORT` |
| FastAPI analytics | Render | Dockerfile `analytics/Dockerfile`; `GET /health` |
| PostgreSQL | Neon | PostgreSQL connection variables below; Flyway enabled |
| Object storage | Cloudflare R2 | Not implemented in this revision; deployment is blocked |

## Environment variables

Set these in each provider's secret/configuration UI. Do not commit `.env` files or paste secret values into this document.

### Spring Boot

- `SPRING_PROFILES_ACTIVE=prod`
- `SPRING_DATASOURCE_URL` — Neon JDBC URL
- `SPRING_DATASOURCE_USERNAME`
- `SPRING_DATASOURCE_PASSWORD`
- `DATAMIND_PYTHON_BASE_URL` — private FastAPI service URL
- `DATAMIND_INTERNAL_API_KEY` — same private value configured for FastAPI
- `DATAMIND_CORS_ALLOWED_ORIGINS` — exact HTTPS Vercel origin, no wildcard
- `DATAMIND_DATASET_STORAGE_PATH` — current implementation still uses local disk; this must be replaced by durable object storage before production

### FastAPI

- `DATAMIND_INTERNAL_API_KEY` — same value configured for Spring Boot
- R2 storage settings — not supported by the current implementation

### Vercel

- `VITE_API_BASE_URL` — public HTTPS Spring Boot API URL
- Never set `DATAMIND_INTERNAL_API_KEY` or any server credential in Vercel's `VITE_*` environment.

## Provisioning order

1. Create the Neon database and verify the production migrations against a disposable empty database.
2. Implement and provision R2 object storage for dataset versions, cleaned datasets, and cleaning artifacts.
3. Deploy FastAPI privately; verify `/health`, unauthenticated internal routes return `401`, and authenticated Spring requests succeed.
4. Deploy Spring Boot with `prod`, Neon, FastAPI, and exact CORS configuration; verify Flyway and Hibernate validation.
5. Deploy the Vercel frontend with `VITE_API_BASE_URL`; set the final Vercel origin in Spring CORS and restart Spring.
6. Run the complete workflow and restart/persistence checks in `agents.md` before calling the service live.

## Current gate

- [x] Production CORS reads an environment-driven origin list.
- [x] FastAPI internal router requires `X-Internal-API-Key`; `/health` is public.
- [x] Spring client attaches the internal key and redacts it from logged headers.
- [x] Spring production profile uses `ddl-auto=validate` with Flyway enabled.
- [x] Container definitions and Vercel SPA configuration exist.
- [x] Backend tests pass locally: 126/126.
- [x] Analytics tests pass locally: 382/382.
- [x] Frontend lint, tests (60/60), and production build complete.
- [x] Java↔FastAPI local E2E tests pass: 12/12.
- [ ] Durable storage abstraction and R2 persistence for uploads and cleaning artifacts.
- [ ] Validate that analytics accepts only application-owned dataset object keys or files inside an approved staging root.
- [ ] Concurrent dataset version creation integration test.
- [ ] Production row/column and concurrent job limits.
- [ ] Docker image builds and runtime smoke tests.
- [ ] Neon/R2/Render/Vercel resources, URLs, credentials, and smoke tests.
- [ ] Full E2E workflow and restart/persistence test.

Deployment status: **blocked; not live**.

## Rollback plan

Before each production release, record the previous working Git revision and container image digests. If an application smoke test fails, redeploy those known-good images and restore the previous frontend deployment. Keep Neon and R2 data intact. Do not roll back by deleting or resetting the database. If a Flyway migration is incompatible with the previous application version, use a forward corrective migration or restore a verified database backup under the approved recovery procedure. Recheck API health, CORS, and dataset reads after rollback.

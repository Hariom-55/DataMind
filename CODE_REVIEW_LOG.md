# DataMind Architecture Gap and Change Log

**Review date:** 2026-09-24  
**Scope approval:** P0 workflow closure, approved by the user  
**Reference:** `DataMind_Current_State_vs_Required_Changes.md` supplied by the user

This log compares the approved gaps with the changes made. The attached
document was treated as review material; its recommendations were not treated
as instructions. Larger P1/P2 items remain outside the approved scope.

## Approved gap closure

| Before: gap found in the current architecture | Change made | Gap filled / verification |
|---|---|---|
| Dataset responses exposed `id` and `versionId` with ambiguous meanings. | Added `logicalDatasetId` and `datasetVersionId`; retained `id` and deprecated `versionId` compatibility aliases. Upload accepts canonical `logicalDatasetId` and the old `datasetId` query alias. | Version API consumers can distinguish the dataset family from a concrete file version. Frontend uses the canonical identity fields. |
| Analysis requests could omit a version and silently resolve to the current version; the UI had no version selector. | Public job requests now require `logicalDatasetId` and `datasetVersionId`; the service verifies family membership. The UI loads history/current version, allows explicit selection, and sends the selected version. | Controller validation covers missing version; page test asserts the exact selected version is submitted. A legacy service overload remains for internal callers and resolves current version. |
| Cleaning existed behind the Python service and backend orchestration, but users had no public workflow. | Added public recommendations, preview, and apply endpoints, with family/version validation. Apply records a new version and returns cleaning changes and lineage. | Added Python API tests, Java controller contract tests, and a live Java→Python public workflow E2E test covering recommendations, preview, apply, version 2, and lineage. |
| The frontend did not expose cleaning or lineage. | Added a version-pinned cleaning panel with manual-review-only recommendations disabled, selected-operation preview, apply flow, and version refresh. Added lineage display and selected-version analysis context. | Frontend tests cover assessment→preview→apply and assert requests remain pinned to the selected version. |
| README and API contract docs did not describe the now-available version-pinned public workflows. | Updated README capability descriptions and API endpoint/contract docs with canonical IDs, request requirements, cleaning endpoints, and compatibility aliases. | Documentation matches the implemented P0 contracts and workflow. |

## Verification log

| Pipeline | Command / setup | Outcome |
|---|---|---|
| Frontend unit tests | Vitest through the bundled Node runtime | **40 passed** across 12 files. |
| Frontend production build | Vite production build (Oxlint runs in the build) | **Passed.** Existing bundle-size warning remains: main JS chunk is about 662 kB minified. |
| Analytics tests | pytest using the configured Data Science Python environment | **348 passed.** Two environment/dependency warnings: Starlette `httpx` deprecation and Windows logical-core fallback from joblib. |
| Backend tests | Maven with local PostgreSQL (`datamind_test`) and Python analytics service on port 8000 | **119 passed**, 0 failures/errors/skips across 27 test classes. Includes the public cleaning E2E workflow. A final focused controller/DTO check also passed (13 tests). |
| Diff whitespace check | `git diff --check` | **Passed.** |

The Python analytics process started for verification was stopped after the
test run.

## Coding-agent execution plan — phase log

### Phase 01 — Repository and Generated-Artifact Cleanup (2026-09-24)

- Added a repository-root `.gitignore` covering Python, Java, frontend build
  outputs, local `.env` files, generated backend datasets, and IDE/OS files.
- Added `frontend/datamind-web/.env.example` with the existing local API URL.
- Removed three generated CSV datasets from Git tracking while preserving the
  local files.
- Verification: confirmed the files remain on disk and the ignore rules match
  the datasets and frontend `.env`.
- Tests: not run for this phase.

### Phase 02 — Remove Duplicate Python Models/Schemas (2026-09-24)

- The plan's listed `app/models` paths do not exist; the candidate files are in
  `analytics/app/schemas`.
- Removed `analysis_response.py` and `ml_analysis_request.py` after confirming
  they had no application or test imports/usages. Kept the cleaning schemas,
  which are used by current API and cleaning-service paths.
- Verification: repository-wide targeted usage search before removal.
- Tests: `pytest` attempted from `analytics`; collection could not start because
  the active Python lacks FastAPI and the import path did not resolve `app`.
  The analytics `.venv` is broken (its configured Python 3.12 executable is
  missing), and the bundled Python also lacks FastAPI. Result: **BLOCKED** by
  unavailable project dependencies; no test assertions ran.
- Next phase: paused at Phase 02 per the plan's rule not to proceed with
  unresolved verification failures.

### Phase 03 — Remove Dead ML Code (2026-09-24)

- Confirmed `_get_feature_mapping()` had no call sites or external references;
  removed the unused method from `ml_analysis_service.py`.
- Verification: targeted repository search confirms no remaining reference.
- Tests: not run because the analytics test runtime remains unavailable as
  recorded under Phase 02. ML behavior paths were not changed.
- Next phase: Phase 04, per the user's direction to continue past the
  environment-blocked Phase 02 test run.

### Phase 04 — Fix Categorical Feature-Importance Bug (2026-09-24)

- Updated original feature-name extraction to read fitted
  `OneHotEncoder.categories_`.
- Reused the existing regression test that fits a mixed numeric/categorical
  pipeline and extracts aggregated feature importance; it asserts the
  categorical source feature is returned.
- Also guarded the no-categorical-column case, where the encoder is correctly
  left unfitted by scikit-learn and has no `categories_` attribute.
- Tests: ML service suite — **27 passed**. Pytest emitted environment warnings
  for joblib core detection, Windows MKL/KMeans, and an unwritable pytest cache;
  no assertions failed.
- Next phase: Phase 05.

### Phase 05 — Consolidate Cross-Validation Logic (2026-09-24)

- `_cross_validate_model()` now delegates fold construction to `_build_cv()`
  and only selects the scoring metric based on problem type.
- Added a regression test for classification/regression strategy, split count,
  and deterministic random state.
- Tests: ML service suite — **27 passed** (same run noted under Phase 04).
- Next phase: Phase 06.

### Phase 06 — Remove Double-Fitting After GridSearchCV (2026-09-24)

- Tuned execution now uses GridSearchCV's refitted `best_estimator_` directly;
  only non-tuned models are fitted after model selection.
- Added a regression test that counts calls to `fit()` on the tuned estimator.
- Tests: ML service suite — **28 passed**. The same non-blocking environment
  warnings noted in Phase 05 appeared.
- Next phase: Phase 07.

### Phase 07 — Make Hyperparameter Tuning Explicitly Opt-In (2026-09-24)

- Hyperparameter tuning now defaults to off in the Python request and ML
  service. Added an explicit frontend checkbox for supervised ML.
- Persisted the setting on Java analysis jobs, forwarded it to Python, exposed
  it in job responses, and added a Flyway migration with a false default for
  existing jobs.
- Documented the request field in README and both API contract documents.
- Tests: analytics ML service suite — **30 passed**; frontend suite — **41
  passed**; focused Java controller/service/worker/Python-client tests — **34
  passed**. The Python FastAPI route test file could not run because FastAPI is
  not installed in the available Python interpreter. Existing joblib, Windows
  KMeans, and pytest-cache warnings were non-failing.
- Next phase: Phase 08.

### Phase 08 — Freeze Cleaning Output Format Contract (2026-09-24)

- Cleaning serialization now always emits CSV bytes and reports `format=CSV`,
  `extension=csv`, and `content_type=text/csv`, regardless of the requested or
  source extension.
- Java validates that metadata, stores the artifact with `.csv`, records
  `text/csv` as the version file type, and normalizes cleaned version names to
  end in `.csv`. Public cleaning responses expose matching format metadata.
- Updated API docs and regression tests for an `.xlsx` request returning CSV.
- Tests: Python cleaning services — **20 passed**; focused Java cleaning
  controller/orchestration tests — **10 passed**. FastAPI route tests were not
  run because FastAPI is missing from the active interpreter.
- Next phase: Phase 09.

### Phase 09 — Replace Base64 Dataset Transport (2026-09-24)

- Python cleaning now writes CSV bytes to a configurable short-lived artifact
  store and returns an artifact ID, SHA-256, size, and format metadata. A
  one-time download endpoint streams the CSV and removes the artifact after
  delivery; abandoned artifacts expire after 24 hours.
- Java retrieves bytes separately, verifies size and SHA-256, and writes the
  artifact into durable dataset storage. No cleaned file bytes are placed in
  the JSON response.
- Updated the internal/public cleaning API docs and tests.
- Tests: Python cleaning unit suite — **23 passed**; focused Java artifact,
  orchestration, and controller tests — **15 passed**. The FastAPI route test
  module could not run because FastAPI is unavailable in the current Python
  interpreter. The artifact directory can be configured with
  `DATAMIND_ARTIFACT_DIR`; deployments with multiple Python instances need a
  shared mount or routing affinity for reference retrieval.
- Next phase: Phase 10.

### Phase 10 — Simplify Cleaning Result Layers (2026-09-24)

- Inspected each layer after the artifact-transfer change. The workflow service
  applies operations and records changes; the result service validates,
  serializes, hashes, and packages output metadata; the serializer owns CSV
  byte formatting; the response service stores a short-lived artifact and
  creates its reference; the artifact store owns file lifecycle.
- These responsibilities are distinct and have independent callers/tests.
  No layer was removed because doing so would merge separate concerns rather
  than remove a pass-through abstraction.
- Tests: Python cleaning service suite — **23 passed** (same run as Phase 09).
- Next phase: Phase 11.

### Phase 11 — Remove or Wire Unused Frontend Dataset APIs (2026-09-24)

- Repository-wide searches showed `getDataset()`, `getDatasetVersion()`, and
  `getDatasets()` had no call sites. Removed those unused methods and exports;
  version-list/current-version/lineage/cleaning/upload APIs remain in use.
- Tests: frontend suite — **41 passed** across 12 files.
- Next phase: Phase 12.

### Phase 12 — Freeze Dataset Identity Contract (2026-09-24)

- Kept canonical logical/version fields in dataset and job responses, and
  clarified dataset-version identifiers in Python service requests, Java
  integration DTOs, lineage paths, and lineage response fields.
- Deprecated lineage response aliases remain temporarily; Python accepts the
  older `datasetId` / `dataset_id` request fields as compatibility aliases.
  API docs now state which identifier each field/path denotes.
- Updated README analysis examples to include both logical dataset and version
  IDs.
- Tests: Python identifier and ML service tests — **32 passed**; focused Java
  client/controller/service identifier tests — **20 passed**.
- Next phase: Phase 13.

### Phase 13 — Freeze Analysis Result Contract (2026-09-24)

- Aligned `AnalysisResultResponse` with the shared `v1` envelope: contract
  version, job and dataset identities, version number, analysis type, status,
  creation time, and analysis-specific result payload.
- Kept legacy `id`, `datasetId`, and `datasetVersion` response fields for
  compatibility and documented their canonical replacements.
- Confirmed frontend result normalization unwraps the envelope's `result`
  payload and added a focused contract test.
- Tests: focused Java analysis result DTO/service tests — **5 passed**;
  frontend result normalization tests — **5 passed**.
- Next phase: Phase 14.

### Phase 14 — Remove Analysis-Type Inference (2026-09-24)

- Dashboard selection now uses explicit analysis type metadata passed by the
  job or result envelope. Result normalization unwraps only the canonical
  `result` field; it no longer inspects payload keys. Unknown types show an
  explicit unsupported state.
- Tests: focused frontend result view, normalization, and dashboard router
  tests — **12 passed**.
- Next phase: Phase 15.

### Phase 15 — Explicitly Reject Unsupported Analysis Types (2026-09-24)

- The frontend advertises only EDA, statistical, machine-learning, and insight
  workflows, matching the Python registry.
- Java job creation now rejects `TIME_SERIES` and `TEXT_ANALYSIS` with an
  explicit HTTP 400 validation response. The enum values remain defined so
  existing stored jobs can still be read.
- Updated API contract documentation and added a Java service rejection test.
- Tests: focused Java job controller/service suite — **25 passed**. The
  Python API test module could not be collected because FastAPI is unavailable
  in the configured Python interpreter; its existing unsupported-type test
  already expects HTTP 400 from the registry.
- Next phase: Phase 16.

### Phase 16 — Build Dataset Workspace (2026-09-24)

- Extracted dataset-centric UI into `DatasetWorkspace`. It groups logical and
  version identity, version history/selection, version metadata, cleaning
  actions, and lineage/cleaning history. Analysis configuration remains
  available in the adjacent workflow panel.
- Added responsive layout for dataset metadata and focused workspace tests.
- Tests: workspace, page integration, and cleaning workflow tests — **6
  passed**.
- Next phase: Phase 17.

### Phase 17 — Build Analysis History (2026-09-24)

- Added `GET /api/analysis/jobs` with required logical dataset identity,
  optional version/type/status filters, newest-first ordering, and a bounded
  result count (maximum 100). Individual completed results continue to use the
  existing result endpoint.
- Added a frontend history panel with filters and an open action that loads
  the saved result and restores it in the analysis view without rerunning.
- Tests: focused Java controller/service history tests — **27 passed**;
  frontend history, page integration, and workspace tests — **5 passed**.
- Next phase: Phase 18.

### Phase 18 — Make Frontend State Recoverable (2026-09-24)

- Persists the active logical dataset ID in browser storage and restores the
  current version and available version list after refresh.
- Looks for active jobs first, then the latest completed result, and resumes
  polling or reloads the saved result through backend APIs.
- Tests: frontend restore, analysis history, and dataset workspace tests — **6
  passed**.
- Next phase: Phase 19.

### Phase 19 — Parameterize Cleaning Operations (2026-09-24)

- Added validated `parameters` maps to cleaning requests. Imputation now
  supports `AUTO`, `MEDIAN`, `MEAN`, `MODE`, and `CONSTANT`; category
  normalization accepts explicit trim/lowercase flags. The UI exposes
  imputation strategies and requires a value for constant replacement.
- Persisted the exact operation configuration in JSONB dataset lineage and
  return/display it with lineage history. Added migration V4.
- Tests: Python cleaning/schema suite — **96 passed**; focused Java cleaning,
  version, and lineage tests — **16 passed**; frontend cleaning/workspace
  tests — **5 passed**.
- Next phase: Phase 20.

### Phase 20 — Separate Data Quality From Data Cleaning (2026-09-24)

- Consolidated quality scores and issue detection behind `DataQualityService`.
  The cleaning workflow now receives the quality service, translates findings
  through the separate recommendation service, then applies operations through
  the cleaning engine.
- Removed the old `DataCleaningService` issue-detector name/module and updated
  consumers/tests to use the quality service.
- Tests: cleaning and profiling quality/EDA suites — **110 passed**.
- Next phase: Phase 21.

### Phase 21 — Integrate Statistical Hypothesis Testing (2026-09-24)

- Connected the existing one-sample t-test, Welch independent t-test, paired
  t-test, and chi-square independence service to statistical analysis jobs.
  Requests define required column fields and `alpha` (default 0.05, strictly
  between 0 and 1); Java persists and forwards up to 10 requested tests.
- The statistical UI exposes all four existing tests and their required
  inputs. Results appear under `result.hypothesisTests`; no ANOVA was added
  because there is no implementation to integrate.
- Tests: Python statistical and request-schema tests — **92 passed**; focused
  Java analysis job/controller/worker/client tests — **38 passed**; frontend
  analysis page tests — **4 passed**. Python API route collection remains
  unavailable because FastAPI is missing from the configured interpreter.
- Next phase: Phase 22.

### Phase 22 — Implement Real Box Plot Visualization (2026-09-24)

- Replaced the table fallback with a numeric box-and-whisker SVG renderer
  using min, Q1, median, Q3, and max values. Missing and out-of-order values
  display explicit invalid-data states.
- Documented the canonical box-plot payload; the Python EDA generator already
  emits the five-number summary and IQR fences when outliers are detected.
- Tests: Python EDA/orchestration visualization tests — **19 passed**;
  frontend box-plot rendering/invalid-payload tests — **2 passed**.
- Next phase: Phase 23.

### Phase 23 — Complete Visualization Tests (2026-09-24)

- Added payload validation and renderer-selection coverage for Bar, Line,
  Scatter, Histogram, Pie, BoxPlot, Heatmap, and Table renderers, including
  empty and malformed payload states and an unsupported type.
- Tests: full frontend suite — **60 passed** across 15 files.
- Next phase: Phase 24.

### Phase 24 — Add Visualization Payload Limits (2026-09-24)

- In progress.

## Remaining gaps outside this approval

- Version immutability is still a convention in the existing `Dataset` row model; callers can mutate historical records, and version-number allocation still has a concurrent-write race. A dedicated `DatasetVersion` model or database-level enforcement needs a separate migration plan.
- Analysis history/resume UX and persisted hypothesis-test integration were P1 items and were not part of the approved P0 scope.
- `BOX_PLOT` still routes to the existing table visualization renderer.
- Large-dataset sampling/artifact delivery, storage orphan cleanup, service authentication/rate limits, and further production hardening remain follow-up work.
- Cleaning that produces identical content resolves to the existing content version because duplicate content is unique within a logical dataset family; it does not create a redundant version.

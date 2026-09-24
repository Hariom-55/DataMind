import { useState } from "react";
import {
  applyDatasetCleaning,
  getCleaningRecommendations,
  previewDatasetCleaning,
} from "../../api/datasetApi";

const MANUAL_REVIEW_OPERATIONS = new Set([
  "REVIEW_OUTLIERS",
  "REVIEW_FEATURE",
  "REVIEW_CARDINALITY",
  "CONVERT_DATA_TYPE",
  "REVIEW_ISSUE",
]);

function operationKey(operation) {
  return `${operation.operation}:${operation.column || "*"}`;
}

function defaultParameters(operationName) {
  if (operationName === "IMPUTE_MISSING_VALUES") return { strategy: "AUTO" };
  if (operationName === "NORMALIZE_CATEGORIES") return { trim: true, lowercase: true };
  return {};
}

function CleaningWorkflowPanel({ logicalDatasetId, datasetVersion, onVersionCreated }) {
  const [assessment, setAssessment] = useState(null);
  const [selectedOperations, setSelectedOperations] = useState([]);
  const [preview, setPreview] = useState(null);
  const [status, setStatus] = useState("IDLE");
  const [error, setError] = useState(null);

  async function loadRecommendations() {
    setStatus("LOADING_RECOMMENDATIONS");
    setError(null);
    setPreview(null);
    try {
      const result = await getCleaningRecommendations(
        logicalDatasetId,
        datasetVersion.datasetVersionId,
      );
      setAssessment(result);
      setSelectedOperations([]);
      setStatus("READY");
    } catch (requestError) {
      setStatus("ERROR");
      setError(requestError.message);
    }
  }

  function toggleOperation(recommendation) {
    const operation = {
      operation: recommendation.operation,
      column: recommendation.column || null,
      parameters: defaultParameters(recommendation.operation),
    };
    const key = operationKey(operation);
    setSelectedOperations((current) => current.some((item) => operationKey(item) === key)
      ? current.filter((item) => operationKey(item) !== key)
      : [...current, operation]);
    setPreview(null);
  }

  function updateOperation(operation, parameters) {
    const key = operationKey(operation);
    setSelectedOperations((current) => current.map((item) =>
      operationKey(item) === key ? { ...item, parameters: { ...item.parameters, ...parameters } } : item,
    ));
    setPreview(null);
  }

  async function handlePreview() {
    setStatus("PREVIEWING");
    setError(null);
    try {
      const result = await previewDatasetCleaning(
        logicalDatasetId,
        datasetVersion.datasetVersionId,
        selectedOperations,
      );
      setPreview(result);
      setStatus("PREVIEW_READY");
    } catch (requestError) {
      setStatus("ERROR");
      setError(requestError.message);
    }
  }

  async function handleApply() {
    setStatus("APPLYING");
    setError(null);
    try {
      const result = await applyDatasetCleaning(
        logicalDatasetId,
        datasetVersion.datasetVersionId,
        selectedOperations,
      );
      setStatus(result.dataset?.datasetVersionId === datasetVersion.datasetVersionId ? "UNCHANGED" : "APPLIED");
      setPreview(null);
      await onVersionCreated?.(result.dataset);
    } catch (requestError) {
      setStatus("ERROR");
      setError(requestError.message);
    }
  }

  const recommendations = assessment?.recommendations || [];
  const isBusy = ["LOADING_RECOMMENDATIONS", "PREVIEWING", "APPLYING"].includes(status);

  return (
    <section className="cleaning-workflow-card" aria-labelledby="cleaning-title">
      <div className="cleaning-heading">
        <div>
          <span className="eyebrow">DATA PREPARATION</span>
          <h2 id="cleaning-title">Review and clean this version</h2>
          <p>Cleaning creates a new version and records its lineage. The selected source version stays unchanged.</p>
        </div>
        <button type="button" className="secondary-button" onClick={loadRecommendations} disabled={isBusy}>
          {status === "LOADING_RECOMMENDATIONS" ? "Reviewing…" : "Get recommendations"}
        </button>
      </div>

      {assessment && (
        <div className="cleaning-assessment">
          <p>
            {assessment.issueCount} quality {assessment.issueCount === 1 ? "issue" : "issues"} found in {assessment.totalRows} rows and {assessment.totalColumns} columns.
          </p>
          {recommendations.length === 0 ? (
            <p>No cleaning recommendations were found for this version.</p>
          ) : (
            <ul className="cleaning-recommendation-list">
              {recommendations.map((recommendation, index) => {
                const operation = {
                  operation: recommendation.operation,
                  column: recommendation.column || null,
                };
                const key = operationKey(operation);
                const manualReview = MANUAL_REVIEW_OPERATIONS.has(recommendation.operation);
                const checked = selectedOperations.some((item) => operationKey(item) === key);
                return (
                  <li key={`${key}:${index}`}>
                    <label className={manualReview ? "recommendation-manual" : ""}>
                      <input
                        type="checkbox"
                        checked={checked}
                        disabled={manualReview || isBusy}
                        onChange={() => toggleOperation(recommendation)}
                      />
                      <span>
                        <strong>{recommendation.issueType}{recommendation.column ? ` · ${recommendation.column}` : ""}</strong>
                        <small>{recommendation.recommendation}</small>
                        {manualReview && <small>Requires manual review; it cannot be applied automatically.</small>}
                      </span>
                    </label>
                    {checked && recommendation.operation === "IMPUTE_MISSING_VALUES" && (() => {
                      const selected = selectedOperations.find((item) => operationKey(item) === key);
                      const strategy = selected?.parameters?.strategy || "AUTO";
                      return (
                        <div className="operation-parameters">
                          <label>Imputation strategy
                            <select value={strategy} disabled={isBusy} onChange={(event) => {
                              const next = event.target.value;
                              updateOperation(operation, { strategy: next, ...(next === "CONSTANT" ? {} : { value: undefined }) });
                            }}>
                              {(["AUTO", "MEDIAN", "MEAN", "MODE", "CONSTANT"]).map((value) => <option key={value} value={value}>{value}</option>)}
                            </select>
                          </label>
                          {strategy === "CONSTANT" && <label>Replacement value
                            <input value={selected?.parameters?.value ?? ""} disabled={isBusy} onChange={(event) => updateOperation(operation, { value: event.target.value })} />
                          </label>}
                        </div>
                      );
                    })()}
                  </li>
                );
              })}
            </ul>
          )}
          <button
            type="button"
            className="primary-button"
            onClick={handlePreview}
            disabled={isBusy || selectedOperations.length === 0 || selectedOperations.some((item) => item.parameters?.strategy === "CONSTANT" && item.parameters?.value === "")}
          >
            {status === "PREVIEWING" ? "Preparing preview…" : "Preview selected changes"}
          </button>
        </div>
      )}

      {preview && (
        <div className="cleaning-preview" role="status">
          <h3>Preview for version v{preview.versionNumber}</h3>
          <p>
            Rows: {preview.originalRows} → {preview.cleanedRows} · Columns: {preview.originalColumns} → {preview.cleanedColumns}
          </p>
          <ul>
            {(preview.changes || []).map((change, index) => (
              <li key={`${change.operation}-${change.column || "all"}-${index}`}>
                {change.operation}{change.column ? ` (${change.column})` : ""}: {change.rowsAffected} rows affected — {change.details}
              </li>
            ))}
          </ul>
          <button type="button" className="primary-button" onClick={handleApply} disabled={isBusy}>
            {status === "APPLYING" ? "Creating version…" : "Apply and create new version"}
          </button>
        </div>
      )}

      {status === "APPLIED" && <p className="cleaning-success" role="status">Cleaned version created and added to version history.</p>}
      {status === "UNCHANGED" && <p className="cleaning-success" role="status">The selected operations did not change this version, so no new version was created.</p>}
      {error && <p className="cleaning-error" role="alert">{error}</p>}
    </section>
  );
}

export default CleaningWorkflowPanel;

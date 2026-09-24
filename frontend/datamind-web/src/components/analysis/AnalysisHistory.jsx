import { useEffect, useState } from "react";
import { getAnalysisHistory, getAnalysisResult } from "../../api/analysisApi";
import { ANALYSIS_JOB_STATUS, ANALYSIS_TYPES } from "../../api/analysisType";

const HISTORY_STATUSES = ["PENDING", "PROCESSING", "COMPLETED", "FAILED"];

function AnalysisHistory({ logicalDatasetId, versions, onOpen }) {
  const [datasetVersionId, setDatasetVersionId] = useState("");
  const [analysisType, setAnalysisType] = useState("");
  const [status, setStatus] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [openingJobId, setOpeningJobId] = useState(null);

  useEffect(() => {
    let current = true;
    setLoading(true);
    setError(null);
    getAnalysisHistory({ logicalDatasetId, datasetVersionId, analysisType, status })
      .then((items) => { if (current) setHistory(Array.isArray(items) ? items : []); })
      .catch((requestError) => { if (current) setError(requestError.message); })
      .finally(() => { if (current) setLoading(false); });
    return () => { current = false; };
  }, [logicalDatasetId, datasetVersionId, analysisType, status]);

  async function openResult(job) {
    setOpeningJobId(job.id);
    setError(null);
    try {
      const result = await getAnalysisResult(job.id);
      onOpen(job, result);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setOpeningJobId(null);
    }
  }

  return (
    <section className="analysis-history-card" aria-labelledby="analysis-history-title">
      <div className="section-heading">
        <div><span className="eyebrow">PAST RUNS</span><h2 id="analysis-history-title">Analysis history</h2><p>Open completed results without running the analysis again.</p></div>
      </div>
      <div className="history-filters">
        <label>Version
          <select value={datasetVersionId} onChange={(event) => setDatasetVersionId(event.target.value)}>
            <option value="">All versions</option>
            {versions.map((version) => <option key={version.datasetVersionId} value={version.datasetVersionId}>v{version.versionNumber}</option>)}
          </select>
        </label>
        <label>Analysis type
          <select value={analysisType} onChange={(event) => setAnalysisType(event.target.value)}>
            <option value="">All types</option>
            {Object.values(ANALYSIS_TYPES).map((type) => <option key={type} value={type}>{type.replaceAll("_", " ")}</option>)}
          </select>
        </label>
        <label>Status
          <select value={status} onChange={(event) => setStatus(event.target.value)}>
            <option value="">All statuses</option>
            {HISTORY_STATUSES.map((value) => <option key={value} value={value}>{value}</option>)}
          </select>
        </label>
      </div>
      {loading && <p role="status">Loading analysis history…</p>}
      {error && <p className="cleaning-error" role="alert">{error}</p>}
      {!loading && !error && history.length === 0 && <p>No analysis runs match these filters.</p>}
      {history.length > 0 && (
        <ul className="analysis-history-list">
          {history.map((job) => (
            <li key={job.id}>
              <div><strong>{job.analysisType?.replaceAll("_", " ")}</strong><span>v{job.versionNumber} · {job.status}</span><small>{job.completedAt || job.createdAt}</small></div>
              {job.status === ANALYSIS_JOB_STATUS.COMPLETED && (
                <button type="button" className="secondary-button" onClick={() => openResult(job)} disabled={openingJobId !== null}>
                  {openingJobId === job.id ? "Opening…" : "Open result"}
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default AnalysisHistory;

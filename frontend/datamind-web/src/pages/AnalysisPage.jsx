import { useEffect, useState } from "react";

import DatasetUpload from "../components/dataset/DatasetUpload";
import DatasetWorkspace from "../components/dataset/DatasetWorkspace";
import { ANALYSIS_TYPES } from "../api/analysisType";
import { getCurrentDatasetVersion, getDatasetLineage, getDatasetVersions } from "../api/datasetApi";
import { getAnalysisHistory } from "../api/analysisApi";
import { useAnalysis } from "../services/useAnalysis";
import AnalysisResultView from "../components/analysis/AnalysisResultView";
import AnalysisHistory from "../components/analysis/AnalysisHistory";

const ACTIVE_DATASET_STORAGE_KEY = "datamind.activeLogicalDatasetId";
const HYPOTHESIS_FIELDS = {
  ONE_SAMPLE_T_TEST: ["column", "referenceValue"],
  INDEPENDENT_T_TEST: ["valueColumn", "groupColumn"],
  PAIRED_T_TEST: ["column1", "column2"],
  CHI_SQUARE_INDEPENDENCE: ["column1", "column2"],
};

function HypothesisTestFields({ type, disabled, onChange }) {
  const [fields, setFields] = useState({ alpha: "0.05" });
  const fieldNames = HYPOTHESIS_FIELDS[type];

  useEffect(() => {
    setFields({ alpha: "0.05" });
    onChange(null);
  }, [type, onChange]);

  useEffect(() => {
    const alpha = Number(fields.alpha || 0.05);
    if (!fieldNames.every((name) => fields[name]?.trim()) || !(alpha > 0 && alpha < 1)) {
      onChange(null);
      return;
    }
    const request = { test: type, alpha };
    for (const name of fieldNames) {
      request[name] = name === "referenceValue" ? Number(fields[name]) : fields[name].trim();
    }
    onChange(request);
  }, [fields, fieldNames, type, onChange]);

  const labels = {
    column: "Numeric column",
    referenceValue: "Reference mean",
    valueColumn: "Numeric value column",
    groupColumn: "Grouping column",
    column1: "First column",
    column2: "Second column",
  };

  return (
    <>
      {fieldNames.map((name) => (
        <div className="field" key={name}>
          <label htmlFor={`hypothesis-${name}`}>{labels[name]}</label>
          <input id={`hypothesis-${name}`} value={fields[name] || ""} onChange={(event) => setFields((current) => ({ ...current, [name]: event.target.value }))} disabled={disabled} />
        </div>
      ))}
      <div className="field">
        <label htmlFor="hypothesis-alpha">Significance level (alpha)</label>
        <input id="hypothesis-alpha" type="number" min="0.000001" max="0.999999" step="0.01" value={fields.alpha} onChange={(event) => setFields((current) => ({ ...current, alpha: event.target.value }))} disabled={disabled} />
      </div>
    </>
  );
}

function AnalysisPage() {
  const [dataset, setDataset] = useState(null);
  const [versions, setVersions] = useState([]);
  const [selectedVersionId, setSelectedVersionId] = useState("");
  const [currentVersionId, setCurrentVersionId] = useState("");
  const [lineage, setLineage] = useState(null);
  const [datasetError, setDatasetError] = useState(null);
  const [analysisType, setAnalysisType] = useState(ANALYSIS_TYPES.INSIGHT);
  const [targetColumn, setTargetColumn] = useState("");
  const [enableHyperparameterTuning, setEnableHyperparameterTuning] = useState(false);
  const [hypothesisTest, setHypothesisTest] = useState(null);
  const [hypothesisTestType, setHypothesisTestType] = useState("");
  const { state, job, result, error, startAnalysis, resetAnalysis, openHistoricalAnalysis, resumeAnalysisJob } = useAnalysis();

  const selectedVersion = versions.find((version) => version.datasetVersionId === selectedVersionId);

  async function refreshVersions(logicalDatasetId, preferredVersionId) {
    const [versionList, current] = await Promise.all([
      getDatasetVersions(logicalDatasetId),
      getCurrentDatasetVersion(logicalDatasetId),
    ]);
    const availableVersions = Array.isArray(versionList) ? versionList : versionList.versions || [];
    setVersions(availableVersions);
    const preferred = preferredVersionId || current.datasetVersionId;
    setCurrentVersionId(current.datasetVersionId);
    setSelectedVersionId(availableVersions.some((version) => version.datasetVersionId === preferred)
      ? preferred
      : availableVersions[0]?.datasetVersionId || "");
  }

  useEffect(() => {
    let active = true;
    const logicalDatasetId = window.localStorage.getItem(ACTIVE_DATASET_STORAGE_KEY);
    if (!logicalDatasetId) return undefined;

    async function restoreWorkspace() {
      try {
        const current = await getCurrentDatasetVersion(logicalDatasetId);
        if (!active) return;
        setDataset(current);

        const [versionResult, processingJobsResult, pendingJobsResult, completedJobsResult, latestJobsResult] = await Promise.allSettled([
          getDatasetVersions(logicalDatasetId),
          getAnalysisHistory({ logicalDatasetId, status: "PROCESSING", limit: 1 }),
          getAnalysisHistory({ logicalDatasetId, status: "PENDING", limit: 1 }),
          getAnalysisHistory({ logicalDatasetId, status: "COMPLETED", limit: 1 }),
          getAnalysisHistory({ logicalDatasetId, limit: 1 }),
        ]);
        if (!active) return;

        const versionList = versionResult.status === "fulfilled" ? versionResult.value : [];
        const availableVersions = Array.isArray(versionList) ? versionList : versionList.versions || [];
        setVersions(availableVersions);
        setCurrentVersionId(current.datasetVersionId);
        setSelectedVersionId(current.datasetVersionId);

        const processingJobs = processingJobsResult.status === "fulfilled" ? processingJobsResult.value : [];
        const pendingJobs = pendingJobsResult.status === "fulfilled" ? pendingJobsResult.value : [];
        const completedJobs = completedJobsResult.status === "fulfilled" ? completedJobsResult.value : [];
        const latestJobs = latestJobsResult.status === "fulfilled" ? latestJobsResult.value : [];
        const jobToRestore = processingJobs[0] || pendingJobs[0] || completedJobs[0] || latestJobs[0];
        if (jobToRestore) resumeAnalysisJob(jobToRestore);
      } catch (requestError) {
        if (active) setDatasetError(`Saved dataset could not be restored: ${requestError.message}`);
      }
    }

    restoreWorkspace();
    return () => { active = false; };
  }, []);

  async function handleUploadSuccess(uploadedDataset) {
    const logicalId = uploadedDataset.logicalDatasetId;
    window.localStorage.setItem(ACTIVE_DATASET_STORAGE_KEY, logicalId);
    setDataset(uploadedDataset);
    setDatasetError(null);
    setLineage(null);
    resetAnalysis();
    try {
      await refreshVersions(logicalId, uploadedDataset.datasetVersionId);
    } catch (requestError) {
      setDatasetError(`Dataset uploaded, but version history could not be loaded: ${requestError.message}`);
    }
  }

  useEffect(() => {
    if (!dataset?.logicalDatasetId || !selectedVersionId) return;
    getDatasetLineage(selectedVersionId).then(setLineage).catch(() => setLineage(null));
  }, [dataset?.logicalDatasetId, selectedVersionId]);

  async function handleRunAnalysis() {
    if (!dataset?.logicalDatasetId || !selectedVersion?.datasetVersionId) return;
    try {
      await startAnalysis({
        logicalDatasetId: dataset.logicalDatasetId,
        datasetVersionId: selectedVersion.datasetVersionId,
        analysisType,
        targetColumn: targetColumn || null,
        enableHyperparameterTuning,
        ...(analysisType === ANALYSIS_TYPES.STATISTICAL && hypothesisTestType
          ? { hypothesisTests: [hypothesisTest] }
          : {}),
      });
    } catch {
      // Error is already exposed through useAnalysis().
    }
  }

  async function handleVersionCreated(createdVersion) {
    resetAnalysis();
    await refreshVersions(dataset.logicalDatasetId, createdVersion.datasetVersionId);
  }

  const isRunning = state === "STARTING" || state === "RUNNING";
  const hasResult = Boolean(result) && state === "RESULT_READY";

  return (
    <main className="datamind-app">
      <header className="app-header">
        <div><div className="brand-mark">DM</div><div><h1>DataMind</h1><p>Data Analysis &amp; Intelligence Workspace</p></div></div>
        {dataset && <div className="header-status"><span className="status-dot" />Dataset connected</div>}
      </header>
      <div className="app-shell">
        {!dataset ? (
          <section className="upload-workspace">
            <div className="workspace-intro"><span className="eyebrow">ANALYTICS WORKSPACE</span><h2>Turn your dataset into<br />actionable intelligence.</h2><p>Upload a dataset to begin exploratory analysis, statistical profiling and automated insights.</p></div>
            <DatasetUpload onUploadSuccess={handleUploadSuccess} />
          </section>
        ) : (
          <>
            {datasetError && <div className="error-banner" role="alert">{datasetError}</div>}
            <DatasetWorkspace
              dataset={dataset}
              versions={versions}
              selectedVersion={selectedVersion}
              selectedVersionId={selectedVersionId}
              currentVersionId={currentVersionId}
              lineage={lineage}
              disabled={isRunning}
              onVersionChange={(versionId) => { setSelectedVersionId(versionId); resetAnalysis(); }}
              onChooseAnother={() => { window.localStorage.removeItem(ACTIVE_DATASET_STORAGE_KEY); setDataset(null); setVersions([]); setSelectedVersionId(""); resetAnalysis(); }}
              onVersionCreated={handleVersionCreated}
            />
            <AnalysisHistory
              logicalDatasetId={dataset.logicalDatasetId}
              versions={versions}
              onOpen={openHistoricalAnalysis}
            />
            <section className="analysis-control-card">
              <div className="section-heading"><div><span className="eyebrow">ANALYSIS</span><h2>Configure analysis</h2><p>Choose an exact dataset version and analytical workflow.</p></div>{job?.id && <div className="job-reference"><span>JOB</span><code>{job.id}</code></div>}</div>
              <div className="analysis-form">
                <div className="field"><label htmlFor="analysis-type">Analysis type</label><select id="analysis-type" value={analysisType} onChange={(event) => setAnalysisType(event.target.value)} disabled={isRunning}>{Object.values(ANALYSIS_TYPES).map((type) => <option key={type} value={type}>{type.replaceAll("_", " ")}</option>)}</select></div>
                {analysisType === ANALYSIS_TYPES.MACHINE_LEARNING && <><div className="field"><label htmlFor="target-column">Target column</label><input id="target-column" value={targetColumn} onChange={(event) => setTargetColumn(event.target.value)} placeholder="e.g. target" disabled={isRunning} /><small>Leave blank to run KMeans clustering with numeric features.</small></div><div className="field"><label htmlFor="enable-hyperparameter-tuning"><input id="enable-hyperparameter-tuning" type="checkbox" checked={enableHyperparameterTuning} onChange={(event) => setEnableHyperparameterTuning(event.target.checked)} disabled={isRunning || !targetColumn.trim()} /> Enable random forest hyperparameter tuning</label><small>Off by default. Applies only when random forest is selected.</small></div></>}
                {analysisType === ANALYSIS_TYPES.STATISTICAL && <>
                  <div className="field"><label htmlFor="hypothesis-test-type">Optional hypothesis test</label><select id="hypothesis-test-type" value={hypothesisTestType} onChange={(event) => { setHypothesisTestType(event.target.value); setHypothesisTest(null); }} disabled={isRunning}><option value="">No hypothesis test</option>{["ONE_SAMPLE_T_TEST", "INDEPENDENT_T_TEST", "PAIRED_T_TEST", "CHI_SQUARE_INDEPENDENCE"].map((test) => <option key={test} value={test}>{test.replaceAll("_", " ")}</option>)}</select></div>
                  {hypothesisTestType && <HypothesisTestFields type={hypothesisTestType} disabled={isRunning} onChange={setHypothesisTest} />}
                </>}
                <div className="analysis-action"><button type="button" className="primary-button" onClick={handleRunAnalysis} disabled={isRunning || !selectedVersion || (analysisType === ANALYSIS_TYPES.STATISTICAL && hypothesisTestType && !hypothesisTest)}>{isRunning ? "Running analysis…" : "Run analysis"}</button></div>
              </div>
            </section>
            {state !== "IDLE" && <section className="job-status-card"><div className="status-main"><div className={`status-indicator status-${state.toLowerCase()}`} /><div><strong>{state === "RESULT_READY" ? "Analysis completed" : state === "FAILED" ? "Analysis failed" : state === "TIMEOUT" ? "Analysis timed out" : "Analysis in progress"}</strong><span>{state === "RESULT_READY" ? `Dataset version v${job?.versionNumber ?? selectedVersion?.versionNumber ?? "1"}` : isRunning ? "DataMind is processing your dataset." : error?.message || "Analysis status updated."}</span></div></div>{job?.id && <div className="job-meta"><span>JOB / VERSION</span><code>{job.id} · v{job.versionNumber ?? selectedVersion?.versionNumber}</code></div>}</section>}
            {error && state !== "RUNNING" && <div className="error-banner" role="alert"><strong>Analysis error</strong><span>{error.message}</span></div>}
            {hasResult && <AnalysisResultView result={result} analysisType={job?.analysisType || analysisType} />}
          </>
        )}
      </div>
    </main>
  );
}

export default AnalysisPage;

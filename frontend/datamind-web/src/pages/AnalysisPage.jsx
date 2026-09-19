import { useState } from "react";

import DatasetUpload from "../components/dataset/DatasetUpload";
import { ANALYSIS_TYPES } from "../api/analysisType";
import { useAnalysis } from "../services/useAnalysis";
import AnalysisResultView from "../components/analysis/AnalysisResultView";

function AnalysisPage() {
  const [dataset, setDataset] = useState(null);
  const [analysisType, setAnalysisType] = useState(
    ANALYSIS_TYPES.INSIGHT,
  );
  const [targetColumn, setTargetColumn] = useState("");

  const {
    state,
    job,
    result,
    error,
    startAnalysis,
    resetAnalysis,
  } = useAnalysis();

  function handleUploadSuccess(uploadedDataset) {
    setDataset(uploadedDataset);
    resetAnalysis();
  }

  async function handleRunAnalysis() {
    if (!dataset?.id) {
      return;
    }

    try {
      await startAnalysis({
        datasetId: dataset.id,
        analysisType,
        targetColumn: targetColumn || null,
      });
    } catch {
      // Error is already exposed through useAnalysis().
    }
  }

  const isRunning =
    state === "STARTING" ||
    state === "RUNNING";

  const hasResult =
    Boolean(result) &&
    state === "RESULT_READY";

  return (
    <main className="datamind-app">
      <header className="app-header">
        <div>
          <div className="brand-mark">
            DM
          </div>

          <div>
            <h1>DataMind</h1>
            <p>
              Data Analysis & Intelligence Workspace
            </p>
          </div>
        </div>

        {dataset && (
          <div className="header-status">
            <span className="status-dot" />
            Dataset connected
          </div>
        )}
      </header>

      <div className="app-shell">
        {!dataset ? (
          <section className="upload-workspace">
            <div className="workspace-intro">
              <span className="eyebrow">
                ANALYTICS WORKSPACE
              </span>

              <h2>
                Turn your dataset into
                <br />
                actionable intelligence.
              </h2>

              <p>
                Upload a dataset to begin exploratory
                analysis, statistical profiling and
                automated insights.
              </p>
            </div>

            <DatasetUpload
              onUploadSuccess={handleUploadSuccess}
            />
          </section>
        ) : (
          <>
            <section className="workspace-toolbar">
              <div className="dataset-context">
                <div className="dataset-icon">
                  CSV
                </div>

                <div>
                  <span className="eyebrow">
                    ACTIVE DATASET
                  </span>

                  <h2>{dataset.name}</h2>

                  <p>
                    {dataset.fileType || "Dataset"} ·{" "}
                    {dataset.status}
                  </p>
                </div>
              </div>

              <button
                type="button"
                className="secondary-button"
                onClick={() => {
                  setDataset(null);
                  resetAnalysis();
                }}
              >
                Choose another dataset
              </button>
            </section>

            <section className="analysis-control-card">
              <div className="section-heading">
                <div>
                  <span className="eyebrow">
                    ANALYSIS
                  </span>

                  <h2>Configure analysis</h2>

                  <p>
                    Select the analytical workflow you want
                    DataMind to execute.
                  </p>
                </div>

                {job?.id && (
                  <div className="job-reference">
                    <span>JOB</span>
                    <code>{job.id}</code>
                  </div>
                )}
              </div>

              <div className="analysis-form">
                <div className="field">
                  <label htmlFor="analysis-type">
                    Analysis type
                  </label>

                  <select
                    id="analysis-type"
                    value={analysisType}
                    onChange={(event) =>
                      setAnalysisType(event.target.value)
                    }
                    disabled={isRunning}
                  >
                    {Object.values(ANALYSIS_TYPES).map(
                      (type) => (
                        <option
                          key={type}
                          value={type}
                        >
                          {type.replaceAll("_", " ")}
                        </option>
                      ),
                    )}
                  </select>
                </div>

                {analysisType ===
                  ANALYSIS_TYPES.MACHINE_LEARNING && (
                  <div className="field">
                    <label htmlFor="target-column">
                      Target column
                    </label>

                    <input
                      id="target-column"
                      value={targetColumn}
                      onChange={(event) =>
                        setTargetColumn(event.target.value)
                      }
                      placeholder="e.g. target"
                      disabled={isRunning}
                    />
                  </div>
                )}

                <div className="analysis-action">
                  <button
                    type="button"
                    className="primary-button"
                    onClick={handleRunAnalysis}
                    disabled={isRunning}
                  >
                    {isRunning
                      ? "Running analysis..."
                      : "Run analysis"}
                  </button>
                </div>
              </div>
            </section>

            {state !== "IDLE" && (
              <section className="job-status-card">
                <div className="status-main">
                  <div
                    className={`status-indicator status-${state.toLowerCase()}`}
                  />

                  <div>
                    <strong>
                      {state === "RESULT_READY"
                        ? "Analysis completed"
                        : state === "FAILED"
                          ? "Analysis failed"
                          : state === "TIMEOUT"
                            ? "Analysis timed out"
                            : "Analysis in progress"}
                    </strong>

                    <span>
                      {state === "RESULT_READY"
                        ? "Your analytical results are ready."
                        : isRunning
                          ? "DataMind is processing your dataset."
                          : error?.message ||
                            "Analysis status updated."}
                    </span>
                  </div>
                </div>

                {job?.id && (
                  <div className="job-meta">
                    <span>Job ID</span>
                    <code>{job.id}</code>
                  </div>
                )}
              </section>
            )}

            {error && state !== "RUNNING" && (
              <div className="error-banner" role="alert">
                <strong>Analysis error</strong>
                <span>{error.message}</span>
              </div>
            )}

            {hasResult && (
              <AnalysisResultView
                result={result}
              />
            )}
          </>
        )}
      </div>
    </main>
  );
}

export default AnalysisPage;
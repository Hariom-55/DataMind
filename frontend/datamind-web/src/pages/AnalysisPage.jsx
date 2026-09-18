import { useState } from "react";
import DatasetUpload from "../components/dataset/DatasetUpload";
import { ANALYSIS_TYPES } from "../api/analysisType"; 
import { useAnalysis } from "../services/useAnalysis";
import AnalysisResultView from "../components/analysis/AnalysisResultView";

function AnalysisPage() {
  const [dataset, setDataset] = useState(null);
  const [analysisType, setAnalysisType] = useState(ANALYSIS_TYPES.EDA);
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

    await startAnalysis({
      datasetId: dataset.id,
      analysisType,
      targetColumn: targetColumn || null,
    });
  }

  return (
    <main>
      <h1>DataMind Analysis</h1>

      {!dataset ? (
        <DatasetUpload onUploadSuccess={handleUploadSuccess} />
      ) : (
        <section>
          <h2>Dataset</h2>

          <p>
            <strong>Name:</strong> {dataset.name}
          </p>

          <p>
            <strong>ID:</strong> {dataset.id}
          </p>

          <p>
            <strong>Status:</strong> {dataset.status}
          </p>

          <button
            type="button"
            onClick={() => {
              setDataset(null);
              resetAnalysis();
            }}
          >
            Choose Another Dataset
          </button>
        </section>
      )}

      {dataset && (
        <section>
          <h2>Analysis</h2>

          <label htmlFor="analysis-type">
            Analysis Type
          </label>

          <select
            id="analysis-type"
            value={analysisType}
            onChange={(event) => setAnalysisType(event.target.value)}
            disabled={state === "STARTING" || state === "RUNNING"}
          >
            {Object.values(ANALYSIS_TYPES).map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>

          {analysisType === ANALYSIS_TYPES.MACHINE_LEARNING && (
            <>
              <label htmlFor="target-column">
                Target Column
              </label>

              <input
                id="target-column"
                value={targetColumn}
                onChange={(event) => setTargetColumn(event.target.value)}
                placeholder="Enter target column"
              />
            </>
          )}

          <button
            type="button"
            onClick={handleRunAnalysis}
            disabled={state === "STARTING" || state === "RUNNING"}
          >
            {state === "STARTING" || state === "RUNNING"
              ? "Running Analysis..."
              : "Run Analysis"}
          </button>
        </section>
      )}

      {state !== "IDLE" && (
        <section>
          <h2>Analysis Status</h2>

          <p>Status: {state}</p>

          {job?.id && <p>Job ID: {job.id}</p>}

          {error && <p role="alert">{error}</p>}
        </section>
      )}

      {result &&
        <AnalysisResultView result = {result} /> 
      }
    </main>
  );
}

export default AnalysisPage;
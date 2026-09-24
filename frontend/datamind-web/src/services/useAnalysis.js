import { useState } from "react";
import { runAnalysis, waitForAnalysisJob } from "./analysisService";
import { ANALYSIS_STATE } from "./analysisState";
import { getAnalysisResult } from "../api/analysisApi";

function useAnalysis() {
  const [state, setState] = useState(ANALYSIS_STATE.IDLE);
  const [job, setJob] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function startAnalysis({
    logicalDatasetId,
    datasetVersionId,
    analysisType,
    targetColumn = null,
    enableHyperparameterTuning = false,
    hypothesisTests = [],
    options = {},
  }) {
    setState(ANALYSIS_STATE.STARTING);
    setJob(null);
    setResult(null);
    setError(null);

    try {
      setState(ANALYSIS_STATE.RUNNING);

      const analysisResponse = await runAnalysis({
        logicalDatasetId,
        datasetVersionId,
        analysisType,
        targetColumn,
        enableHyperparameterTuning,
        hypothesisTests,
        options,
      });

      setJob(analysisResponse.job);
      setResult(analysisResponse.result);
      setState(ANALYSIS_STATE.RESULT_READY);

      return analysisResponse;
    } catch (analysisError) {
      setError(analysisError);
      setState(
        analysisError.message === "Analysis job timed out"
          ? ANALYSIS_STATE.TIMEOUT
          : ANALYSIS_STATE.FAILED,
      );
      throw analysisError;
    }
  }

  function resetAnalysis() {
    setState(ANALYSIS_STATE.IDLE);
    setJob(null);
    setResult(null);
    setError(null);
  }

  function openHistoricalAnalysis(historicalJob, historicalResult) {
    setJob(historicalJob);
    setResult(historicalResult);
    setError(null);
    setState(ANALYSIS_STATE.RESULT_READY);
  }

  async function resumeAnalysisJob(existingJob) {
    setJob(existingJob);
    setResult(null);
    setError(null);
    if (existingJob.status === "COMPLETED") {
      const historicalResult = await getAnalysisResult(existingJob.id);
      openHistoricalAnalysis(existingJob, historicalResult);
      return;
    }
    if (existingJob.status === "FAILED") {
      setState(ANALYSIS_STATE.FAILED);
      setError(new Error(existingJob.errorMessage || "Analysis job failed"));
      return;
    }

    setState(ANALYSIS_STATE.RUNNING);
    try {
      const completedJob = await waitForAnalysisJob(existingJob.id);
      const completedResult = await getAnalysisResult(completedJob.id);
      openHistoricalAnalysis(completedJob, completedResult);
    } catch (analysisError) {
      setError(analysisError);
      setState(analysisError.message === "Analysis job timed out" ? ANALYSIS_STATE.TIMEOUT : ANALYSIS_STATE.FAILED);
    }
  }

  return {
    state,
    job,
    result,
    error,
    startAnalysis,
    openHistoricalAnalysis,
    resumeAnalysisJob,
    resetAnalysis,
  };
}

export { useAnalysis };

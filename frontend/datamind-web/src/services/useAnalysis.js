import { useState } from "react";

import { runAnalysis } from "./analysisService";
import { ANALYSIS_STATE } from "./analysisState";

function useAnalysis() {
  const [state, setState] = useState(
    ANALYSIS_STATE.IDLE,
  );

  const [job, setJob] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function startAnalysis({
    datasetId,
    analysisType,
    targetColumn = null,
    options = {},
  }) {
    setState(ANALYSIS_STATE.STARTING);
    setJob(null);
    setResult(null);
    setError(null);

    try {
      setState(ANALYSIS_STATE.RUNNING);

      const analysisResponse = await runAnalysis({
        datasetId,
        analysisType,
        targetColumn,
        options,
      });

      setJob(analysisResponse.job);

      setState(ANALYSIS_STATE.COMPLETED);

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

  return {
    state,
    job,
    result,
    error,
    startAnalysis,
    resetAnalysis,
  };
}

export { useAnalysis };
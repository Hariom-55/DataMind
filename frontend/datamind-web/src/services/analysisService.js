import {
  createAnalysisJob,
  getAnalysisJob,
  getAnalysisResult,
} from "../api/analysisApi";

import { ANALYSIS_JOB_STATUS } from "../api/analysisType";
const DEFAULT_POLL_INTERVAL = 1000;
const DEFAULT_TIMEOUT = 120000;

function wait(milliseconds) {
  return new Promise((resolve) => {
    setTimeout(resolve, milliseconds);
  });
}

async function waitForAnalysisJob(
  jobId,
  {
    pollInterval = DEFAULT_POLL_INTERVAL,
    timeout = DEFAULT_TIMEOUT,
  } = {},
) {
  const startTime = Date.now();

  while (true) {
    const job = await getAnalysisJob(jobId);

    if (job.status === ANALYSIS_JOB_STATUS.COMPLETED) {
      return job;
    }

    if (job.status === ANALYSIS_JOB_STATUS.FAILED) {
      throw new Error(
        job.errorMessage || "Analysis job failed",
      );
    }

    if (Date.now() - startTime >= timeout) {
      throw new Error("Analysis job timed out");
    }

    await wait(pollInterval);
  }
}

async function runAnalysis({
  datasetId,
  analysisType,
  targetColumn = null,
  options = {},
}) {
  const job = await createAnalysisJob({
    datasetId,
    analysisType,
    targetColumn,
  });

  const completedJob = await waitForAnalysisJob(
    job.id,
    options,
  );

  const result = await getAnalysisResult(
    completedJob.id,
  );

  return {
    job: completedJob,
    result,
  };
}

export {
  runAnalysis,
  waitForAnalysisJob,
};
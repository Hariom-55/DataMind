import { request } from "./client";

async function createAnalysisJob({
  datasetId,
  analysisType,
  targetColumn = null,
}) {
  return request("/api/analysis/jobs", {
    method: "POST",
    body: JSON.stringify({
      datasetId,
      analysisType,
      targetColumn,
    }),
  });
}

async function getAnalysisJob(jobId) {
  return request(`/api/analysis/jobs/${jobId}`, {
    method: "GET",
  });
}

async function getAnalysisResult(jobId) {
  return request(`/api/analysis/jobs/${jobId}/result`, {
    method: "GET",
  });
}

export {
  createAnalysisJob,
  getAnalysisJob,
  getAnalysisResult,
};
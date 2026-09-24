import { request } from "./client";

async function createAnalysisJob({
  logicalDatasetId,
  datasetVersionId,
  analysisType,
  targetColumn = null,
  enableHyperparameterTuning = false,
  hypothesisTests = [],
}) {
  return request("/api/analysis/jobs", {
    method: "POST",
    body: JSON.stringify({
      logicalDatasetId,
      datasetVersionId,
      analysisType,
      targetColumn,
      enableHyperparameterTuning,
      ...(hypothesisTests.length ? { hypothesisTests } : {}),
    }),
  });
}

async function getAnalysisJob(jobId) {
  return request(`/api/analysis/jobs/${jobId}`, { method: "GET" });
}

async function getAnalysisHistory({ logicalDatasetId, datasetVersionId, analysisType, status, limit = 50 }) {
  const params = new URLSearchParams({ logicalDatasetId, limit: String(limit) });
  if (datasetVersionId) params.set("datasetVersionId", datasetVersionId);
  if (analysisType) params.set("analysisType", analysisType);
  if (status) params.set("status", status);
  return request(`/api/analysis/jobs?${params.toString()}`, { method: "GET" });
}

async function getAnalysisResult(jobId) {
  return request(`/api/analysis/jobs/${jobId}/result`, { method: "GET" });
}

export { createAnalysisJob, getAnalysisJob, getAnalysisHistory, getAnalysisResult };

import { request } from "./client";

async function uploadDataset(file, logicalDatasetId = null) {
  const formData = new FormData();
  formData.append("file", file);

  const suffix = logicalDatasetId
    ? `?logicalDatasetId=${encodeURIComponent(logicalDatasetId)}`
    : "";

  return request(`/api/datasets${suffix}`, {
    method: "POST",
    body: formData,
  });
}

async function getCurrentDatasetVersion(datasetId) {
  return request(`/api/datasets/${datasetId}/current`, { method: "GET" });
}

async function getDatasetVersions(datasetId) {
  return request(`/api/datasets/${datasetId}/versions`, { method: "GET" });
}

async function getDatasetLineage(datasetVersionId) {
  return request(`/api/datasets/${datasetVersionId}/lineage`, { method: "GET" });
}

async function getCleaningRecommendations(logicalDatasetId, datasetVersionId) {
  return request(
    `/api/datasets/${logicalDatasetId}/versions/${datasetVersionId}/cleaning/recommendations`,
    { method: "GET" },
  );
}

async function previewDatasetCleaning(logicalDatasetId, datasetVersionId, operations) {
  return request(
    `/api/datasets/${logicalDatasetId}/versions/${datasetVersionId}/cleaning/preview`,
    { method: "POST", body: JSON.stringify({ operations }) },
  );
}

async function applyDatasetCleaning(logicalDatasetId, datasetVersionId, operations) {
  return request(
    `/api/datasets/${logicalDatasetId}/versions/${datasetVersionId}/cleaning`,
    { method: "POST", body: JSON.stringify({ operations }) },
  );
}

export {
  uploadDataset,
  getCurrentDatasetVersion,
  getDatasetVersions,
  getDatasetLineage,
  getCleaningRecommendations,
  previewDatasetCleaning,
  applyDatasetCleaning,
};

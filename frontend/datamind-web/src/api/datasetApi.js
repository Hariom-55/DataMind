import { request } from "./client";

async function uploadDataset(file, datasetId = null) {
  const formData = new FormData();
  formData.append("file", file);

  const suffix = datasetId
    ? `?datasetId=${encodeURIComponent(datasetId)}`
    : "";

  return request(`/api/datasets${suffix}`, {
    method: "POST",
    body: formData,
  });
}

async function getDataset(datasetId) {
  return request(`/api/datasets/${datasetId}`, { method: "GET" });
}

async function getCurrentDatasetVersion(datasetId) {
  return request(`/api/datasets/${datasetId}/current`, { method: "GET" });
}

async function getDatasetVersions(datasetId) {
  return request(`/api/datasets/${datasetId}/versions`, { method: "GET" });
}

async function getDatasetVersion(datasetId, versionNumber) {
  return request(
    `/api/datasets/${datasetId}/versions/${versionNumber}`,
    { method: "GET" },
  );
}

async function getDatasets() {
  return request("/api/datasets", { method: "GET" });
}

export {
  uploadDataset,
  getDataset,
  getCurrentDatasetVersion,
  getDatasetVersions,
  getDatasetVersion,
  getDatasets,
};

import { request } from "./client";

async function uploadDataset(file) {
  const formData = new FormData();

  formData.append("file", file);

  return request("/api/datasets", {
    method: "POST",
    body: formData,
  });
}

async function getDataset(datasetId) {
  return request(`/api/datasets/${datasetId}`, {
    method: "GET",
  });
}

async function getDatasets() {
  return request("/api/datasets", {
    method: "GET",
  });
}

export {
  uploadDataset,
  getDataset,
  getDatasets,
};
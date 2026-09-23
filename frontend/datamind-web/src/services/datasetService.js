import { uploadDataset } from "../api/datasetApi";

async function uploadDatasetFile(file, datasetId = null) {
  if (!(file instanceof File)) {
    throw new Error("A valid file is required.");
  }

  if (file.size === 0) {
    throw new Error("The selected file is empty.");
  }

  return datasetId
    ? uploadDataset(file, datasetId)
    : uploadDataset(file);
}

export { uploadDatasetFile };

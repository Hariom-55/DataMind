import { uploadDataset } from "../api/datasetApi";

async function uploadDatasetFile(file, logicalDatasetId = null) {
  if (!(file instanceof File)) {
    throw new Error("A valid file is required.");
  }

  if (file.size === 0) {
    throw new Error("The selected file is empty.");
  }

  return logicalDatasetId
    ? uploadDataset(file, logicalDatasetId)
    : uploadDataset(file);
}

export { uploadDatasetFile };

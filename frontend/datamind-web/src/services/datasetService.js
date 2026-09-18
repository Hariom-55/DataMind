import { uploadDataset } from "../api/datasetApi";

async function uploadDatasetFile(file) {
  if (!(file instanceof File)) {
    throw new Error("A valid file is required.");
  }

  if (file.size === 0) {
    throw new Error("The selected file is empty.");
  }

  return uploadDataset(file);
}

export { uploadDatasetFile };
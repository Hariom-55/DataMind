import { useState } from "react";
import { uploadDatasetFile } from "../../services/datasetService";

function DatasetUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("IDLE");
  const [error, setError] = useState(null);
  const [dataset, setDataset] = useState(null);

  function handleFileChange(event) {
    const selectedFile = event.target.files?.[0] ?? null;

    setFile(selectedFile);
    setError(null);
    setStatus("IDLE");
    setDataset(null);
  }

  async function handleUpload() {
    if (!file) {
      setError("Please select a file.");
      return;
    }

    setStatus("UPLOADING");
    setError(null);

    try {
      const uploadedDataset = await uploadDatasetFile(file);

      setDataset(uploadedDataset);
      setStatus("SUCCESS");

      onUploadSuccess?.(uploadedDataset);
    } catch (uploadError) {
      setStatus("ERROR");
      setError(uploadError.message);
    }
  }

  return (
    <section>
      <h2>Upload Dataset</h2>

      <input
        type="file"
        onChange={handleFileChange}
        aria-label="Dataset file"
      />

      {file && <p>Selected file: {file.name}</p>}

      <button
        type="button"
        onClick={handleUpload}
        disabled={!file || status === "UPLOADING"}
      >
        {status === "UPLOADING" ? "Uploading..." : "Upload Dataset"}
      </button>

      {status === "SUCCESS" && dataset && (
        <p role="status">
          Dataset uploaded successfully. ID: {dataset.id}
        </p>
      )}

      {error && <p role="alert">{error}</p>}
    </section>
  );
}

export default DatasetUpload;
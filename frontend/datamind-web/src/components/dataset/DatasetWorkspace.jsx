import CleaningWorkflowPanel from "./CleaningWorkflowPanel";

function DatasetWorkspace({
  dataset,
  versions,
  selectedVersion,
  selectedVersionId,
  currentVersionId,
  lineage,
  disabled,
  onVersionChange,
  onChooseAnother,
  onVersionCreated,
}) {
  return (
    <section className="dataset-workspace" aria-label="Dataset workspace">
      <section className="workspace-toolbar">
        <div className="dataset-context">
          <div className="dataset-icon">CSV</div>
          <div>
            <span className="eyebrow">ACTIVE DATASET</span>
            <h2>{dataset.name}</h2>
            <p>{dataset.fileType || "Dataset"} · {dataset.status}</p>
          </div>
        </div>
        <button type="button" className="secondary-button" onClick={onChooseAnother} disabled={disabled}>
          Choose another dataset
        </button>
      </section>

      <section className="analysis-control-card dataset-summary" aria-labelledby="dataset-summary-title">
        <div className="section-heading">
          <div><span className="eyebrow">DATASET IDENTITY</span><h2 id="dataset-summary-title">Dataset workspace</h2></div>
          <code>{dataset.logicalDatasetId}</code>
        </div>
        <div className="dataset-version-details">
          <div className="field">
            <label htmlFor="dataset-version">Version history</label>
            <select id="dataset-version" value={selectedVersionId} onChange={(event) => onVersionChange(event.target.value)} disabled={disabled || versions.length === 0}>
              {versions.map((version) => (
                <option key={version.datasetVersionId} value={version.datasetVersionId}>
                  v{version.versionNumber}{version.datasetVersionId === currentVersionId ? " (current)" : ""}
                </option>
              ))}
            </select>
          </div>
          {selectedVersion && (
            <dl className="dataset-metadata">
              <div><dt>Version</dt><dd>v{selectedVersion.versionNumber}{selectedVersionId === currentVersionId ? " · current" : ""}</dd></div>
              <div><dt>Version ID</dt><dd><code>{selectedVersion.datasetVersionId}</code></dd></div>
              <div><dt>File type</dt><dd>{selectedVersion.fileType || dataset.fileType || "Unknown"}</dd></div>
              <div><dt>Size</dt><dd>{selectedVersion.fileSize ?? dataset.fileSize ?? "Unknown"} bytes</dd></div>
              <div><dt>Created</dt><dd>{selectedVersion.createdAt ? new Date(selectedVersion.createdAt).toLocaleString() : "Unknown"}</dd></div>
              <div><dt>Status</dt><dd>{selectedVersion.status || dataset.status}</dd></div>
            </dl>
          )}
        </div>
      </section>

      {selectedVersion && (
        <CleaningWorkflowPanel
          key={selectedVersion.datasetVersionId}
          logicalDatasetId={dataset.logicalDatasetId}
          datasetVersion={selectedVersion}
          onVersionCreated={onVersionCreated}
        />
      )}

      {lineage && (
        <section className="lineage-card" aria-labelledby="lineage-title">
          <h2 id="lineage-title">Version lineage and cleaning history</h2>
          {lineage.length === 0 ? <p>This is an original version with no cleaning lineage.</p> : (
            <ol>{lineage.map((entry, index) => (
              <li key={`${entry.datasetVersionId || entry.datasetId}-${index}`}>
                <strong>{entry.operation}</strong>
                {entry.columnName ? ` · ${entry.columnName}` : ""}
                {entry.details ? ` — ${entry.details}` : ""}
                {entry.operationConfig?.length ? <pre>{JSON.stringify(entry.operationConfig, null, 2)}</pre> : null}
                {entry.createdAt ? <small> · {new Date(entry.createdAt).toLocaleString()}</small> : null}
              </li>
            ))}</ol>
          )}
        </section>
      )}
    </section>
  );
}

export default DatasetWorkspace;

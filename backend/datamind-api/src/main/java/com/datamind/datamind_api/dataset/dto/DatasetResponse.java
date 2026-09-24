package com.datamind.datamind_api.dataset.dto;

import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.entity.DatasetStatus;

import java.time.LocalDateTime;
import java.util.UUID;

public class DatasetResponse {
    private final UUID id;
    private final UUID logicalDatasetId;
    private final UUID datasetVersionId;
    /** @deprecated Use datasetVersionId. */
    @Deprecated
    private final UUID versionId;
    private final Integer versionNumber;
    private final UUID currentVersionId;
    private final String name;
    private final String contentHash;
    private final Long fileSize;
    private final String fileType;
    private final DatasetStatus status;
    private final LocalDateTime createdAt;
    private final LocalDateTime processedAt;

    public DatasetResponse(Dataset dataset) {
        this.id = dataset.getLogicalDatasetId() != null
                ? dataset.getLogicalDatasetId()
                : dataset.getId();
        this.logicalDatasetId = dataset.getLogicalDatasetId();
        this.datasetVersionId = dataset.getId();
        this.versionId = dataset.getId();
        this.versionNumber = dataset.getVersionNumber();
        this.currentVersionId = dataset.getCurrentVersionId();
        this.name = dataset.getName();
        this.contentHash = dataset.getContentHash();
        this.fileSize = dataset.getFileSize();
        this.fileType = dataset.getFileType();
        this.status = dataset.getStatus();
        this.createdAt = dataset.getCreatedAt();
        this.processedAt = dataset.getProcessedAt();
    }

    /** @deprecated Use logicalDatasetId for the family or datasetVersionId for a file version. */
    @Deprecated
    public UUID getId() { return id; }
    public UUID getLogicalDatasetId() { return logicalDatasetId; }
    public UUID getDatasetVersionId() { return datasetVersionId; }
    /** @deprecated Use datasetVersionId. */
    @Deprecated
    public UUID getVersionId() { return versionId; }
    public Integer getVersionNumber() { return versionNumber; }
    public UUID getCurrentVersionId() { return currentVersionId; }
    public String getName() { return name; }
    public String getContentHash() { return contentHash; }
    public Long getFileSize() { return fileSize; }
    public String getFileType() { return fileType; }
    public DatasetStatus getStatus() { return status; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getProcessedAt() { return processedAt; }
}

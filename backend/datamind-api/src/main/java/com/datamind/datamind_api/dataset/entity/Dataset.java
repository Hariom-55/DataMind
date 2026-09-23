package com.datamind.datamind_api.dataset.entity;

import jakarta.persistence.*;
import org.hibernate.annotations.UuidGenerator;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(
        name = "datasets",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_datasets_logical_hash",
                        columnNames = {"logical_dataset_id", "content_hash"}
                ),
                @UniqueConstraint(
                        name = "uk_datasets_logical_version",
                        columnNames = {"logical_dataset_id", "version_number"}
                )
        }
)
public class Dataset {

    @UuidGenerator
    @Id
    private UUID id;

    @Column(nullable = false)
    private String name;

    @Column(name = "content_hash", nullable = false)
    private String contentHash;

    @Column(name = "storage_path", nullable = false)
    private String storagePath;

    private Long fileSize;
    private String fileType;

    @Enumerated(EnumType.STRING)
    private DatasetStatus status;

    private LocalDateTime createdAt;
    private LocalDateTime processedAt;

    /**
     * Stable logical dataset family identifier.
     * All immutable versions of one logical dataset share this value.
     */
    @Column(name = "logical_dataset_id", nullable = false)
    private UUID logicalDatasetId;

    /**
     * Monotonic version number inside a logical dataset family.
     */
    @Column(name = "version_number", nullable = false)
    private Integer versionNumber;

    /**
     * Stored on every version so the logical dataset can be resolved
     * without a separate DatasetVersion table in the current schema.
     */
    @Column(name = "current_version_id")
    private UUID currentVersionId;

    public Dataset() {}

    public Dataset(String name, String contentHash, Long fileSize, String fileType) {
        this.name = name;
        this.contentHash = contentHash;
        this.fileSize = fileSize;
        this.fileType = fileType;
        this.status = DatasetStatus.UPLOADED;
        this.createdAt = LocalDateTime.now();
        this.versionNumber = 1;
    }

    public void initializeAsRootVersion() {
        if (this.id == null) {
            throw new IllegalStateException("Dataset must be persisted before version identity can be initialized");
        }
        if (this.logicalDatasetId == null) {
            this.logicalDatasetId = this.id;
        }
        if (this.versionNumber == null) {
            this.versionNumber = 1;
        }
        this.currentVersionId = this.id;
    }

    @PrePersist
    private void initializeVersionIdentityBeforeInsert() {
        // A generated UUID is normally assigned by Hibernate before this
        // callback. Assign one here as a fallback so the NOT NULL identity
        // fields are populated on the first insert as well.
        if (this.id == null) {
            this.id = UUID.randomUUID();
        }
        if (this.logicalDatasetId == null) {
            this.logicalDatasetId = this.id;
        }
        if (this.versionNumber == null) {
            this.versionNumber = 1;
        }
        if (this.currentVersionId == null && this.logicalDatasetId.equals(this.id)) {
            this.currentVersionId = this.id;
        }
    }

    public void configureAsVersion(UUID logicalDatasetId, int versionNumber) {
        if (logicalDatasetId == null) {
            throw new IllegalArgumentException("logicalDatasetId is required");
        }
        if (versionNumber < 1) {
            throw new IllegalArgumentException("versionNumber must be >= 1");
        }
        this.logicalDatasetId = logicalDatasetId;
        this.versionNumber = versionNumber;
    }

    public void pointCurrentVersionTo(UUID versionId) {
        this.currentVersionId = versionId;
    }

    public void markProcessing() {
        this.status = DatasetStatus.PROCESSING;
    }

    public void markCompleted() {
        this.status = DatasetStatus.COMPLETED;
        this.processedAt = LocalDateTime.now();
    }

    public void markFailed() {
        this.status = DatasetStatus.FAILED;
    }

    public UUID getId() { return id; }
    public String getName() { return name; }
    public String getContentHash() { return contentHash; }
    public Long getFileSize() { return fileSize; }
    public String getFileType() { return fileType; }
    public DatasetStatus getStatus() { return status; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getProcessedAt() { return processedAt; }
    public String getStoragePath() { return storagePath; }
    public UUID getLogicalDatasetId() { return logicalDatasetId; }
    public Integer getVersionNumber() { return versionNumber; }
    public UUID getCurrentVersionId() { return currentVersionId; }

    public void setStoragePath(String storagePath) { this.storagePath = storagePath; }
    public void setLogicalDatasetId(UUID logicalDatasetId) { this.logicalDatasetId = logicalDatasetId; }
    public void setVersionNumber(Integer versionNumber) { this.versionNumber = versionNumber; }
    public void setCurrentVersionId(UUID currentVersionId) { this.currentVersionId = currentVersionId; }
}

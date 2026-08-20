package com.datamind.datamind_api.dataset.dto;

import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.entity.DatasetStatus;

import java.time.LocalDateTime;
import java.util.UUID;

public class DatasetResponse 
{
    private final UUID id;
    private final String name;
    private final String contentHash;
    private final Long fileSize;
    private final String fileType;
    private final DatasetStatus status;
    private final LocalDateTime createdAt;
    private final LocalDateTime processedAt; 

    public DatasetResponse(Dataset dataset)
    {
        this.id = dataset.getId();
        this.name = dataset.getName();
        this.contentHash = dataset.getContentHash();
        this.fileSize = dataset.getFileSize();
        this.fileType = dataset.getFileType();
        this.status = dataset.getStatus();
        this.createdAt = dataset.getCreatedAt();
        this.processedAt = dataset.getProcessedAt();
    }

    public UUID getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getContentHash() {
        return contentHash;
    }

    public Long getFileSize() {
        return fileSize;
    }

    public String getFileType() {
        return fileType;
    }

    public DatasetStatus getStatus() {
        return status;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public LocalDateTime getProcessedAt() {
        return processedAt;
    }
    
}

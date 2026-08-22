package com.datamind.datamind_api.analysis.dto;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;

import java.time.LocalDateTime;
import java.util.UUID;

public class AnalysisJobResponse
{
    private UUID id;
    private UUID datasetId;
    private AnalysisType analysisType;
    private AnalysisJobStatus status;
    private LocalDateTime createdAt;
    private LocalDateTime startedAt;
    private LocalDateTime completedAt;

    public AnalysisJobResponse(AnalysisJob analysisJob)
    {
        this.id = analysisJob.getId();
        this.datasetId = analysisJob.getDataset().getId();
        this.analysisType = analysisJob.getAnalysisType();
        this.status = analysisJob.getStatus();
        this.createdAt = analysisJob.getCreatedAt();
        this.startedAt = analysisJob.getStartedAt();
        this.completedAt = analysisJob.getCompletedAt();

    }

    public UUID getId() {
        return id;
    }

    public LocalDateTime getCompletedAt() {
        return completedAt;
    }

    public LocalDateTime getStartedAt() {
        return startedAt;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public AnalysisJobStatus getStatus() {
        return status;
    }

    public AnalysisType getAnalysisType() {
        return analysisType;
    }

    public UUID getDatasetId() {
        return datasetId;
    }
}

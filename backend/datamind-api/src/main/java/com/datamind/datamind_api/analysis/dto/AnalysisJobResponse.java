package com.datamind.datamind_api.analysis.dto;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;

import java.time.LocalDateTime;
import java.util.UUID;
import java.util.List;
import java.util.Map;

public class AnalysisJobResponse {
    private UUID id;
    private UUID datasetId;
    private UUID logicalDatasetId;
    private UUID datasetVersionId;
    private Integer datasetVersion;
    private Integer versionNumber;
    private AnalysisType analysisType;
    private AnalysisJobStatus status;
    private LocalDateTime createdAt;
    private LocalDateTime startedAt;
    private LocalDateTime completedAt;
    private String errorMessage;
    private Integer retryCount;
    private boolean enableHyperparameterTuning;
    private List<Map<String, Object>> hypothesisTests;

    public AnalysisJobResponse(AnalysisJob analysisJob) {
        this.id = analysisJob.getId();
        this.logicalDatasetId = analysisJob.getDataset().getLogicalDatasetId() != null
                ? analysisJob.getDataset().getLogicalDatasetId()
                : analysisJob.getDataset().getId();
        this.datasetId = this.logicalDatasetId;

        var version = analysisJob.getDatasetVersion() != null
                ? analysisJob.getDatasetVersion()
                : analysisJob.getDataset();

        this.datasetVersionId = version.getId();
        this.datasetVersion = version.getVersionNumber();
        this.versionNumber = version.getVersionNumber();
        this.analysisType = analysisJob.getAnalysisType();
        this.status = analysisJob.getStatus();
        this.createdAt = analysisJob.getCreatedAt();
        this.startedAt = analysisJob.getStartedAt();
        this.completedAt = analysisJob.getCompletedAt();
        this.errorMessage = analysisJob.getErrorMessage();
        this.retryCount = analysisJob.getRetryCount();
        this.enableHyperparameterTuning = analysisJob.isEnableHyperparameterTuning();
        this.hypothesisTests = analysisJob.getHypothesisTests();
    }

    public UUID getId() { return id; }
    /** @deprecated Use logicalDatasetId. */
    @Deprecated
    public UUID getDatasetId() { return datasetId; }
    public UUID getLogicalDatasetId() { return logicalDatasetId; }
    public UUID getDatasetVersionId() { return datasetVersionId; }
    /** @deprecated Use versionNumber. */
    @Deprecated
    public Integer getDatasetVersion() { return datasetVersion; }
    public Integer getVersionNumber() { return versionNumber; }
    public LocalDateTime getCompletedAt() { return completedAt; }
    public LocalDateTime getStartedAt() { return startedAt; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public AnalysisJobStatus getStatus() { return status; }
    public AnalysisType getAnalysisType() { return analysisType; }
    public String getErrorMessage() { return errorMessage; }
    public Integer getRetryCount() { return retryCount; }
    public boolean isEnableHyperparameterTuning() { return enableHyperparameterTuning; }
    public List<Map<String, Object>> getHypothesisTests() { return hypothesisTests; }
}

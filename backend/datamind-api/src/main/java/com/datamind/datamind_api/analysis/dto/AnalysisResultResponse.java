package com.datamind.datamind_api.analysis.dto;

import com.datamind.datamind_api.analysis.entity.AnalysisResult;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;

public class AnalysisResultResponse {
    private final UUID id;
    private final UUID jobId;
    private final UUID datasetId;
    private final UUID logicalDatasetId;
    private final UUID datasetVersionId;
    private final Integer datasetVersion;
    private final Integer versionNumber;
    private final com.datamind.datamind_api.analysis.entity.enums.AnalysisType analysisType;
    private final com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus status;
    private final String contractVersion;
    private final Map<String, Object> result;
    private final LocalDateTime createdAt;

    public AnalysisResultResponse(AnalysisResult analysisResult) {
        this.id = analysisResult.getId();
        this.jobId = analysisResult.getJob().getId();
        this.logicalDatasetId = analysisResult.getJob().getDataset().getLogicalDatasetId() != null
                ? analysisResult.getJob().getDataset().getLogicalDatasetId()
                : analysisResult.getJob().getDataset().getId();
        this.datasetId = this.logicalDatasetId;

        var version = analysisResult.getJob().getDatasetVersion() != null
                ? analysisResult.getJob().getDatasetVersion()
                : analysisResult.getJob().getDataset();

        this.datasetVersionId = version.getId();
        this.datasetVersion = version.getVersionNumber();
        this.versionNumber = version.getVersionNumber();
        this.analysisType = analysisResult.getJob().getAnalysisType();
        this.status = analysisResult.getJob().getStatus();
        this.contractVersion = analysisResult.getContractVersion();
        this.result = analysisResult.getResultData();
        this.createdAt = analysisResult.getCreatedAt();
    }

    public UUID getId() { return id; }
    public UUID getJobId() { return jobId; }
    /** @deprecated Use logicalDatasetId. */
    @Deprecated
    public UUID getDatasetId() { return datasetId; }
    public UUID getLogicalDatasetId() { return logicalDatasetId; }
    public UUID getDatasetVersionId() { return datasetVersionId; }
    /** @deprecated Use versionNumber. */
    @Deprecated
    public Integer getDatasetVersion() { return datasetVersion; }
    public Integer getVersionNumber() { return versionNumber; }
    public com.datamind.datamind_api.analysis.entity.enums.AnalysisType getAnalysisType() { return analysisType; }
    public com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus getStatus() { return status; }
    public String getContractVersion() { return contractVersion; }
    public Map<String, Object> getResult() { return result; }
    public LocalDateTime getCreatedAt() { return createdAt; }
}

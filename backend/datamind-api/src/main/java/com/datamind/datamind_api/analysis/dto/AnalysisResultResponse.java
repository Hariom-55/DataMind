package com.datamind.datamind_api.analysis.dto;

import com.datamind.datamind_api.analysis.entity.AnalysisResult;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;

public class AnalysisResultResponse {
    private final UUID id;
    private final UUID jobId;
    private final UUID datasetId;
    private final UUID datasetVersionId;
    private final Integer datasetVersion;
    private final com.datamind.datamind_api.analysis.entity.enums.AnalysisType analysisType;
    private final String contractVersion;
    private final Map<String, Object> result;
    private final LocalDateTime createdAt;

    public AnalysisResultResponse(AnalysisResult analysisResult) {
        this.id = analysisResult.getId();
        this.jobId = analysisResult.getJob().getId();
        this.datasetId = analysisResult.getJob().getDataset().getLogicalDatasetId() != null
                ? analysisResult.getJob().getDataset().getLogicalDatasetId()
                : analysisResult.getJob().getDataset().getId();

        var version = analysisResult.getJob().getDatasetVersion() != null
                ? analysisResult.getJob().getDatasetVersion()
                : analysisResult.getJob().getDataset();

        this.datasetVersionId = version.getId();
        this.datasetVersion = version.getVersionNumber();
        this.analysisType = analysisResult.getJob().getAnalysisType();
        this.contractVersion = analysisResult.getContractVersion();
        this.result = analysisResult.getResultData();
        this.createdAt = analysisResult.getCreatedAt();
    }

    public UUID getId() { return id; }
    public UUID getJobId() { return jobId; }
    public UUID getDatasetId() { return datasetId; }
    public UUID getDatasetVersionId() { return datasetVersionId; }
    public Integer getDatasetVersion() { return datasetVersion; }
    public com.datamind.datamind_api.analysis.entity.enums.AnalysisType getAnalysisType() { return analysisType; }
    public String getContractVersion() { return contractVersion; }
    public Map<String, Object> getResult() { return result; }
    public LocalDateTime getCreatedAt() { return createdAt; }
}

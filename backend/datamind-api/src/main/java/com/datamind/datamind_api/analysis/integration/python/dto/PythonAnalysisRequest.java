package com.datamind.datamind_api.analysis.integration.python.dto;

import java.util.UUID;


public class PythonAnalysisRequest
{
    private UUID jobId;
    private UUID datasetId;
    private String analysisType;

    public PythonAnalysisRequest() {}

    public PythonAnalysisRequest(UUID jobId, UUID datasetId, String analysisType)
    {
        this.jobId = jobId;
        this.datasetId = datasetId;
        this.analysisType = analysisType;
    }

    public UUID getJobId() {
        return jobId;
    }

    public UUID getDatasetId() {
        return datasetId;
    }

    public String getAnalysisType() {
        return analysisType;
    }
}

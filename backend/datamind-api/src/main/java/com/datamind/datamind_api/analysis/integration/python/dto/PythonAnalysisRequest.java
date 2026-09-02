package com.datamind.datamind_api.analysis.integration.python.dto;

import java.util.UUID;


public class PythonAnalysisRequest
{
    private UUID jobId;
    private UUID datasetId;
    private String analysisType;
    private String datasetPath;
    private String fileType;

    public PythonAnalysisRequest() {}

    public PythonAnalysisRequest(UUID jobId, UUID datasetId, String analysisType, String datasetPath, String fileType)
    {
        this.jobId = jobId;
        this.datasetId = datasetId;
        this.analysisType = analysisType;
        this.datasetPath = datasetPath;
        this.fileType = fileType;
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

    public String getDatasetPath()
    {
        return datasetPath;
    }

    public String getFileType(){
        return fileType;
    }
}

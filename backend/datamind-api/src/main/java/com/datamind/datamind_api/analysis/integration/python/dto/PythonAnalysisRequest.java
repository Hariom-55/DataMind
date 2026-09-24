package com.datamind.datamind_api.analysis.integration.python.dto;

import java.util.UUID;
import java.util.List;
import java.util.Map;


public class PythonAnalysisRequest
{
    private UUID jobId;
    private UUID datasetVersionId;
    private String analysisType;
    private String datasetPath;
    private String fileType;
    private String targetColumn;
    private boolean enableHyperparameterTuning;
    private List<Map<String, Object>> hypothesisTests;

    public PythonAnalysisRequest() {}

    public PythonAnalysisRequest(UUID jobId, UUID datasetVersionId, String analysisType, String datasetPath, String fileType, String targetColumn) {
        this(jobId, datasetVersionId, analysisType, datasetPath, fileType, targetColumn, false, List.of());
    }

    public PythonAnalysisRequest(UUID jobId, UUID datasetVersionId, String analysisType, String datasetPath, String fileType, String targetColumn, boolean enableHyperparameterTuning)
    {
        this(jobId, datasetVersionId, analysisType, datasetPath, fileType, targetColumn, enableHyperparameterTuning, List.of());
    }

    public PythonAnalysisRequest(UUID jobId, UUID datasetVersionId, String analysisType, String datasetPath, String fileType, String targetColumn, boolean enableHyperparameterTuning, List<Map<String, Object>> hypothesisTests)
    {
        this.jobId = jobId;
        this.datasetVersionId = datasetVersionId;
        this.analysisType = analysisType;
        this.datasetPath = datasetPath;
        this.fileType = fileType;
        this.targetColumn = targetColumn;
        this.enableHyperparameterTuning = enableHyperparameterTuning;
        this.hypothesisTests = hypothesisTests == null ? List.of() : hypothesisTests;
    }

    public UUID getJobId() {
        return jobId;
    }

    public UUID getDatasetVersionId() {
        return datasetVersionId;
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

    public String getTargetColumn()
    {
        return targetColumn;
    }

    public boolean isEnableHyperparameterTuning() {
        return enableHyperparameterTuning;
    }

    public List<Map<String, Object>> getHypothesisTests() { return hypothesisTests; }
}

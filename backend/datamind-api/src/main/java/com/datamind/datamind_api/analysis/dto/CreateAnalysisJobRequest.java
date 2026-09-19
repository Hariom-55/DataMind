package com.datamind.datamind_api.analysis.dto;

import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.util.UUID;

public class CreateAnalysisJobRequest {
    @NotNull
    private UUID datasetId;

    @NotNull
    private AnalysisType analysisType;

    @Size(max = 255, message = "targetColumn must not exceed 255 characters")
    private String targetColumn;

    public CreateAnalysisJobRequest() {}

    public UUID getDatasetId() { return datasetId; }
    public AnalysisType getAnalysisType() { return analysisType; }
    public String getTargetColumn() { return targetColumn; }
    public void setDatasetId(UUID datasetId) { this.datasetId = datasetId; }
    public void setAnalysisType(AnalysisType analysisType) { this.analysisType = analysisType; }
    public void setTargetColumn(String targetColumn) { this.targetColumn = targetColumn; }
}

package com.datamind.datamind_api.analysis.dto;

import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import com.fasterxml.jackson.annotation.JsonAlias;

import java.util.UUID;
import java.util.List;
import java.util.Map;

public class CreateAnalysisJobRequest {
    @JsonAlias("datasetId")
    @NotNull
    private UUID logicalDatasetId;

    @NotNull
    private UUID datasetVersionId;

    @NotNull
    private AnalysisType analysisType;

    @Size(max = 255, message = "targetColumn must not exceed 255 characters")
    private String targetColumn;

    private boolean enableHyperparameterTuning;
    private List<Map<String, Object>> hypothesisTests = List.of();

    public CreateAnalysisJobRequest() {}

    /** @deprecated Use logicalDatasetId. */
    @Deprecated
    public UUID getDatasetId() { return logicalDatasetId; }
    public UUID getLogicalDatasetId() { return logicalDatasetId; }
    public UUID getDatasetVersionId() { return datasetVersionId; }
    public AnalysisType getAnalysisType() { return analysisType; }
    public String getTargetColumn() { return targetColumn; }
    public boolean isEnableHyperparameterTuning() { return enableHyperparameterTuning; }
    public List<Map<String, Object>> getHypothesisTests() { return hypothesisTests; }

    public void setDatasetId(UUID datasetId) { this.logicalDatasetId = datasetId; }
    public void setLogicalDatasetId(UUID logicalDatasetId) { this.logicalDatasetId = logicalDatasetId; }
    public void setDatasetVersionId(UUID datasetVersionId) { this.datasetVersionId = datasetVersionId; }
    public void setAnalysisType(AnalysisType analysisType) { this.analysisType = analysisType; }
    public void setTargetColumn(String targetColumn) { this.targetColumn = targetColumn; }
    public void setEnableHyperparameterTuning(boolean enableHyperparameterTuning) {
        this.enableHyperparameterTuning = enableHyperparameterTuning;
    }
    public void setHypothesisTests(List<Map<String, Object>> hypothesisTests) {
        this.hypothesisTests = hypothesisTests == null ? List.of() : hypothesisTests;
    }
}

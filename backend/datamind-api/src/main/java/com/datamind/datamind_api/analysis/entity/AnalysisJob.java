package com.datamind.datamind_api.analysis.entity;

import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import com.datamind.datamind_api.dataset.entity.Dataset;
import jakarta.persistence.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.UUID;
import java.util.List;
import java.util.Map;

@Entity
@Table(name = "analysis_jobs")
public class AnalysisJob {

    @Id
    @GeneratedValue
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "dataset_id", nullable = false)
    private Dataset dataset;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "dataset_version_id", nullable = false)
    private Dataset datasetVersion;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private AnalysisType analysisType;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    private AnalysisJobStatus status;

    @Column(nullable = false)
    private Integer retryCount = 0;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    private LocalDateTime startedAt;
    private LocalDateTime completedAt;

    @Column(columnDefinition = "TEXT")
    private String errorMessage;

    @Column(name = "target_column")
    private String targetColumn;

    @Column(name = "enable_hyperparameter_tuning", nullable = false)
    private boolean enableHyperparameterTuning;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "hypothesis_tests", columnDefinition = "jsonb", nullable = false)
    private List<Map<String, Object>> hypothesisTests = List.of();

    public AnalysisJob() {}

    public AnalysisJob(
            Dataset dataset,
            Dataset datasetVersion,
            AnalysisType analysisType,
            AnalysisJobStatus status
    ) {
        this.dataset = dataset;
        this.datasetVersion = datasetVersion;
        this.analysisType = analysisType;
        this.status = status;
        this.createdAt = LocalDateTime.now();
    }


    public AnalysisJob(
            Dataset dataset,
            AnalysisType analysisType,
            AnalysisJobStatus status
    ) {
        this(dataset, dataset, analysisType, status);
    }

    public UUID getId() { return id; }
    public LocalDateTime getCompletedAt() { return completedAt; }
    public LocalDateTime getStartedAt() { return startedAt; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public AnalysisJobStatus getStatus() { return status; }
    public AnalysisType getAnalysisType() { return analysisType; }
    public Dataset getDataset() { return dataset; }
    public Dataset getDatasetVersion() { return datasetVersion; }
    public Integer getRetryCount() { return retryCount; }
    public String getErrorMessage() { return errorMessage; }
    public String getTargetColumn() { return targetColumn; }
    public boolean isEnableHyperparameterTuning() { return enableHyperparameterTuning; }
    public List<Map<String, Object>> getHypothesisTests() { return hypothesisTests; }

    public void setStartedAt(LocalDateTime startedAt) { this.startedAt = startedAt; }
    public void setCompletedAt(LocalDateTime completedAt) { this.completedAt = completedAt; }
    public void setStatus(AnalysisJobStatus status) { this.status = status; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    public void setTargetColumn(String targetColumn) { this.targetColumn = targetColumn; }
    public void setEnableHyperparameterTuning(boolean enableHyperparameterTuning) {
        this.enableHyperparameterTuning = enableHyperparameterTuning;
    }
    public void setHypothesisTests(List<Map<String, Object>> hypothesisTests) {
        this.hypothesisTests = hypothesisTests == null ? List.of() : List.copyOf(hypothesisTests);
    }
    public void setDatasetVersion(Dataset datasetVersion) { this.datasetVersion = datasetVersion; }

    public void markAsProcessing() {
        this.status = AnalysisJobStatus.PROCESSING;
        this.startedAt = LocalDateTime.now();
        this.completedAt = null;
    }

    public void markAsCompleted() {
        this.status = AnalysisJobStatus.COMPLETED;
        this.completedAt = LocalDateTime.now();
        this.errorMessage = null;
    }

    public void markAsFailed(String errorMessage) {
        this.status = AnalysisJobStatus.FAILED;
        this.completedAt = LocalDateTime.now();
        this.errorMessage = truncateError(errorMessage);
    }

    public void incrementRetryCount() { this.retryCount++; }

    public void retry(String errorMessage) {
        this.status = AnalysisJobStatus.PENDING;
        this.completedAt = null;
        this.startedAt = null;
        this.errorMessage = truncateError(errorMessage);
    }

    private String truncateError(String message) {
        if (message == null) return null;
        return message.length() <= 4000 ? message : message.substring(0, 4000);
    }
}

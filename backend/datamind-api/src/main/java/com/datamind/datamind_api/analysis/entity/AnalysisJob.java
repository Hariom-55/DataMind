package com.datamind.datamind_api.analysis.entity;

import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import com.datamind.datamind_api.dataset.entity.Dataset;
import jakarta.persistence.*;

import java.util.UUID;
import java.time.LocalDateTime;

@Entity
@Table(name = "analysis_jobs")
public class AnalysisJob
{
    @Id
    @GeneratedValue
    private UUID id ;

    @ManyToOne
    @JoinColumn(name = "dataset_id" , nullable = false)
    private Dataset dataset;

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

    public AnalysisJob () {}

    public AnalysisJob (
            Dataset dataset ,
            AnalysisType analysisType,
            AnalysisJobStatus status
    ){
        this.dataset = dataset;
        this.analysisType = analysisType ;
        this.status = status;
        this.createdAt = LocalDateTime.now();
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

    public Dataset getDataset() {
        return dataset;
    }

    public Integer getRetryCount() {
        return retryCount;
    }

   public String getErrorMessage()
   {
       return errorMessage;
   }

    public void setStartedAt(LocalDateTime startedAt) {
        this.startedAt = startedAt;
    }

    public void setCompletedAt(LocalDateTime completedAt) {
        this.completedAt = completedAt;
    }

    public void setStatus(AnalysisJobStatus status) {
        this.status = status;
    }

    public void markAsProcessing()
    {
        this.status = AnalysisJobStatus.PROCESSING;
        this.startedAt = LocalDateTime.now();

    }

    public void markAsCompleted()
    {
        this.status = AnalysisJobStatus.COMPLETED;
        this.completedAt = LocalDateTime.now();
        this.errorMessage = null;

    }

    public void markAsFailed(String errorMessage)
    {
        this.status = AnalysisJobStatus.FAILED;
        this.startedAt = null;
        this.completedAt = LocalDateTime.now();
        this.errorMessage =errorMessage;
    }

    public void incrementRetryCount()
    {
        this.retryCount++;
    }

    public void retry()
    {
        this.status = AnalysisJobStatus.PENDING;
        this.completedAt = null;
        this.errorMessage = null;
    }
}

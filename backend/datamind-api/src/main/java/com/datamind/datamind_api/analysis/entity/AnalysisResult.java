package com.datamind.datamind_api.analysis.entity;


import jakarta.persistence.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;

@Entity
@Table(name = "analysis_results")
public class AnalysisResult
{
    @Id
    @GeneratedValue
    private UUID id;

    @OneToOne
    @JoinColumn(name = "job_id", nullable = false, unique = true)
    private AnalysisJob job;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "result_data", columnDefinition = "jsonb", nullable = false)
    private Map<String, Object> resultData;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    protected AnalysisResult() {}

    public AnalysisResult(
            AnalysisJob job,
            Map<String, Object> resultData
    ){
        this.job = job;
        this.resultData = resultData;
        this.createdAt = LocalDateTime.now();
    }

    public UUID getId() {
        return id;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public Map<String, Object> getResultData() {
        return resultData;
    }

    public AnalysisJob getJob() {
        return job;
    }
}

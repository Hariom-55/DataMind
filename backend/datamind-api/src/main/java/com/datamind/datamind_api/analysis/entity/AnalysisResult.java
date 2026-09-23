package com.datamind.datamind_api.analysis.entity;

import jakarta.persistence.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;

@Entity
@Table(name = "analysis_results")
public class AnalysisResult {
    public static final String CURRENT_CONTRACT_VERSION = "v1";

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

    @Column(name = "contract_version", nullable = false)
    private String contractVersion = CURRENT_CONTRACT_VERSION;

    protected AnalysisResult() {}

    public AnalysisResult(AnalysisJob job, Map<String, Object> resultData) {
        this.job = job;
        this.resultData = resultData;
        this.createdAt = LocalDateTime.now();
        this.contractVersion = CURRENT_CONTRACT_VERSION;
    }

    public UUID getId() { return id; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public Map<String, Object> getResultData() { return resultData; }
    public AnalysisJob getJob() { return job; }
    public String getContractVersion() { return contractVersion; }
}

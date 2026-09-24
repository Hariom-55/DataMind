package com.datamind.datamind_api.dataset.entity;

import jakarta.persistence.*;
import org.hibernate.annotations.UuidGenerator;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.UUID;
import java.util.List;
import java.util.Map;

@Entity
@Table(
        name = "dataset_lineage",
        uniqueConstraints = @UniqueConstraint(
                name = "uk_dataset_lineage_child_version",
                columnNames = "child_dataset_id"
        )
)
public class DatasetLineage {

    @UuidGenerator
    @Id
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "parent_dataset_id", nullable = false)
    private Dataset parentDataset;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "child_dataset_id", nullable = false)
    private Dataset childDataset;

    @Column(nullable = false)
    private String operation;

    private String columnName;
    private Integer rowsAffected;

    @Column(columnDefinition = "TEXT")
    private String details;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "operation_config", columnDefinition = "jsonb", nullable = false)
    private List<Map<String, Object>> operationConfig = List.of();

    @Column(nullable = false)
    private LocalDateTime createdAt;

    protected DatasetLineage() {}

    public DatasetLineage(
            Dataset parentDataset,
            Dataset childDataset,
            String operation,
            String columnName,
            Integer rowsAffected,
            String details
    ) {
        this(parentDataset, childDataset, operation, columnName, rowsAffected, details, List.of());
    }

    public DatasetLineage(
            Dataset parentDataset,
            Dataset childDataset,
            String operation,
            String columnName,
            Integer rowsAffected,
            String details,
            List<Map<String, Object>> operationConfig
    ) {
        this.parentDataset = parentDataset;
        this.childDataset = childDataset;
        this.operation = operation;
        this.columnName = columnName;
        this.rowsAffected = rowsAffected;
        this.details = details;
        this.operationConfig = operationConfig == null ? List.of() : operationConfig;
        this.createdAt = LocalDateTime.now();
    }

    public UUID getId() { return id; }
    public Dataset getParentDataset() { return parentDataset; }
    public Dataset getChildDataset() { return childDataset; }
    public String getOperation() { return operation; }
    public String getColumnName() { return columnName; }
    public Integer getRowsAffected() { return rowsAffected; }
    public String getDetails() { return details; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public List<Map<String, Object>> getOperationConfig() { return operationConfig; }
}

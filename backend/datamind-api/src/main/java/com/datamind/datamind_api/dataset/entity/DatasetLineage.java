package com.datamind.datamind_api.dataset.entity;

import jakarta.persistence.*;
import org.hibernate.annotations.UuidGenerator;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "dataset_lineage")
public class DatasetLineage {

    @UuidGenerator
    @Id
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(
            name = "parent_dataset_id",
            nullable = false
    )
    private Dataset parentDataset;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(
            name = "child_dataset_id",
            nullable = false,
            unique = true
    )
    private Dataset childDataset;

    @Column(nullable = false)
    private String operation;

    private String columnName;

    private Integer rowsAffected;

    @Column(columnDefinition = "TEXT")
    private String details;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    protected DatasetLineage() {
    }

    public DatasetLineage(
            Dataset parentDataset,
            Dataset childDataset,
            String operation,
            String columnName,
            Integer rowsAffected,
            String details
    ) {
        this.parentDataset = parentDataset;
        this.childDataset = childDataset;
        this.operation = operation;
        this.columnName = columnName;
        this.rowsAffected = rowsAffected;
        this.details = details;
        this.createdAt = LocalDateTime.now();
    }

    public UUID getId() {
        return id;
    }

    public Dataset getParentDataset() {
        return parentDataset;
    }

    public Dataset getChildDataset() {
        return childDataset;
    }

    public String getOperation() {
        return operation;
    }

    public String getColumnName() {
        return columnName;
    }

    public Integer getRowsAffected() {
        return rowsAffected;
    }

    public String getDetails() {
        return details;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
}
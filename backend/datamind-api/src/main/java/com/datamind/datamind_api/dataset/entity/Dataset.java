package com.datamind.datamind_api.dataset.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import java.util.UUID;  
import jakarta.persistence.Column;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import java.time.LocalDateTime;
import jakarta.persistence.Table;
import org.hibernate.annotations.UuidGenerator;


@Entity // Tells Hibernate to treat this java class as a persistent database entity
@Table(name = "datasets")
public class Dataset 
{
    @UuidGenerator
    @Id
    private UUID id;

    @Column(nullable = false)
    private String name; 

    @Column(
        name = "content_hash",
        nullable = false,
        unique = true
    )
    private String contentHash ;

    @Column(nullable = false)
    private String storagePath;

    private Long fileSize;
    private String fileType; 

   @Enumerated(EnumType.STRING)
    private DatasetStatus status;

    private LocalDateTime createdAt;
    private LocalDateTime processedAt; 

    protected Dataset(){} 

    public Dataset(
            String name,
            String contentHash,
            Long fileSize,
            String fileType
    ){
        this.name = name;
        this.contentHash = contentHash;
        this.fileSize = fileSize;
        this.fileType = fileType;
        this.status = DatasetStatus.UPLOADED;
        this.createdAt = LocalDateTime.now();
    }

    public void markProcessing()
    {
        this.status = DatasetStatus.PROCESSING;
    }

    public void markCompleted()
    {
        this.status = DatasetStatus.COMPLETED;
        this.processedAt = LocalDateTime.now();
    }

    public void markFailed()
    {
        this.status = DatasetStatus.FAILED;
    }

    public UUID getId()
    {
        return id;
    }

    public String getName()
    {
        return name;
    }

    public String getContentHash()
    {
        return contentHash;
    }

    public Long getFileSize()
    {
        return fileSize;
    }

    public String getFileType()
    {
        return fileType;
    }

    public DatasetStatus getStatus()
    {
        return status;
    }

    public LocalDateTime getCreatedAt()
    {
        return createdAt;
    }

    public LocalDateTime getProcessedAt()
    {
        return processedAt;
    }

    public String getStoragePath() {return storagePath;}

    public void setStoragePath(String storagePath){
        this.storagePath = storagePath;
    }

    
}

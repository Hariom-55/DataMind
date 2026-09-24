package com.datamind.datamind_api.dataset.service;

import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.entity.DatasetLineage;
import com.datamind.datamind_api.dataset.repository.DatasetLineageRepository;
import com.datamind.datamind_api.dataset.repository.DatasetRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.Map;

@Service
public class DatasetVersionService {

    private final DatasetRepository datasetRepository;
    private final DatasetLineageRepository lineageRepository;
    private final DatasetService datasetService;

    public DatasetVersionService(
            DatasetRepository datasetRepository,
            DatasetLineageRepository lineageRepository,
            DatasetService datasetService
    ) {
        this.datasetRepository = datasetRepository;
        this.lineageRepository = lineageRepository;
        this.datasetService = datasetService;
    }

    @Transactional
    public Dataset createVersion(
            Dataset parentDataset,
            String name,
            String contentHash,
            Long fileSize,
            String fileType,
            String storagePath,
            String operation,
            String columnName,
            Integer rowsAffected,
            String details
    ) {
        return createVersion(parentDataset, name, contentHash, fileSize, fileType,
                storagePath, operation, columnName, rowsAffected, details, List.of());
    }

    @Transactional
    public Dataset createVersion(
            Dataset parentDataset,
            String name,
            String contentHash,
            Long fileSize,
            String fileType,
            String storagePath,
            String operation,
            String columnName,
            Integer rowsAffected,
            String details,
            List<Map<String, Object>> operationConfig
    ) {
        if (parentDataset == null) {
            throw new IllegalArgumentException("Parent dataset is required");
        }

        java.util.UUID logicalId = parentDataset.getLogicalDatasetId() != null
                ? parentDataset.getLogicalDatasetId()
                : (parentDataset.getId() != null ? parentDataset.getId() : java.util.UUID.randomUUID());

        Dataset existing = datasetRepository.findByLogicalDatasetIdAndContentHash(
                logicalId,
                contentHash
        ).orElse(null);

        if (existing != null) {
            return existing;
        }

        int nextVersion = java.util.Optional.ofNullable(
                datasetRepository.findMaxVersionNumber(logicalId)
        ).orElse(0) + 1;

        Dataset childDataset = new Dataset(
                name,
                contentHash,
                fileSize,
                fileType
        );
        childDataset.configureAsVersion(
                logicalId,
                nextVersion
        );
        childDataset.setStoragePath(storagePath);

        childDataset = datasetRepository.save(childDataset);

        DatasetLineage lineage = new DatasetLineage(
                parentDataset,
                childDataset,
                operation,
                columnName,
                rowsAffected,
                details,
                operationConfig
        );
        lineageRepository.save(lineage);

        datasetService.pointRootToCurrentVersion(
                logicalId,
                childDataset.getId()
        );

        return childDataset;
    }
}

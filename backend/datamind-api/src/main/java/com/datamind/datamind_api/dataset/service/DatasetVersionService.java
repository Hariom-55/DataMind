package com.datamind.datamind_api.dataset.service;

import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.entity.DatasetLineage;
import com.datamind.datamind_api.dataset.repository.DatasetLineageRepository;
import com.datamind.datamind_api.dataset.repository.DatasetRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class DatasetVersionService {

    private final DatasetRepository datasetRepository;
    private final DatasetLineageRepository lineageRepository;

    public DatasetVersionService(
            DatasetRepository datasetRepository,
            DatasetLineageRepository lineageRepository
    ) {
        this.datasetRepository = datasetRepository;
        this.lineageRepository = lineageRepository;
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

        Dataset childDataset = new Dataset(
                name,
                contentHash,
                fileSize,
                fileType
        );

        childDataset.setStoragePath(storagePath);


        childDataset = datasetRepository.save(
                childDataset
        );

        DatasetLineage lineage = new DatasetLineage(
                parentDataset,
                childDataset,
                operation,
                columnName,
                rowsAffected,
                details
        );

        lineageRepository.save(lineage);

        return childDataset;
    }
}
package com.datamind.datamind_api.dataset.service;

import com.datamind.datamind_api.dataset.dto.DatasetLineageResponse;
import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.entity.DatasetLineage;
import com.datamind.datamind_api.dataset.repository.DatasetLineageRepository;
import com.datamind.datamind_api.dataset.repository.DatasetRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import com.datamind.datamind_api.dataset.exception.DatasetNotFoundException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

@Service
public class DatasetLineageService {

    private final DatasetRepository datasetRepository;
    private final DatasetLineageRepository lineageRepository;

    public DatasetLineageService(
            DatasetRepository datasetRepository,
            DatasetLineageRepository lineageRepository
    ) {
        this.datasetRepository = datasetRepository;
        this.lineageRepository = lineageRepository;
    }

    @Transactional(readOnly = true)
    public List<DatasetLineageResponse> getLineage(
            UUID datasetId
    ) {

        Dataset currentDataset = datasetRepository
                .findById(datasetId)
                .orElseThrow(() ->
                        new DatasetNotFoundException(
                                "Dataset not found: "
                                        + datasetId
                        )
                );

        List<DatasetLineageResponse> lineage =
                new ArrayList<>();

        Dataset childDataset = currentDataset;

        while (true) {

            DatasetLineage relationship =
                    lineageRepository
                            .findByChildDataset(
                                    childDataset
                            )
                            .orElse(null);

            if (relationship == null) {
                break;
            }

            lineage.add(
                    toResponse(relationship)
            );

            childDataset =
                    relationship.getParentDataset();
        }

        Collections.reverse(lineage);

        return lineage;
    }

    private DatasetLineageResponse toResponse(
            DatasetLineage lineage
    ) {

        return new DatasetLineageResponse(
                lineage.getChildDataset().getId(),
                lineage.getParentDataset().getId(),
                lineage.getOperation(),
                lineage.getColumnName(),
                lineage.getRowsAffected(),
                lineage.getDetails(),
                lineage.getCreatedAt()
        );
    }
}
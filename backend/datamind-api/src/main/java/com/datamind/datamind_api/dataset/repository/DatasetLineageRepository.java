package com.datamind.datamind_api.dataset.repository;

import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.entity.DatasetLineage;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface DatasetLineageRepository
        extends JpaRepository<DatasetLineage, UUID> {

    Optional<DatasetLineage> findByChildDataset(
            Dataset childDataset
    );

    List<DatasetLineage> findByParentDatasetOrderByCreatedAtAsc(
            Dataset parentDataset
    );
}
package com.datamind.datamind_api.dataset.repository;

import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.entity.DatasetLineage;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@Transactional
class DatasetLineageRepositoryTest {

    @Autowired
    private DatasetRepository datasetRepository;

    @Autowired
    private DatasetLineageRepository lineageRepository;

    @Test
    void shouldPersistAndRetrieveDatasetLineage() {

        Dataset parent = new Dataset(
                "customers.csv",
                "parent-hash-test",
                100L,
                "text/csv"
        );

        Dataset child = new Dataset(
                "customers_cleaned.csv",
                "child-hash-test",
                90L,
                "text/csv"
        );

        parent.setStoragePath(
                "/data/parent.csv"
        );

        child.setStoragePath(
                "/data/child.csv"
        );

        parent = datasetRepository.save(parent);
        child = datasetRepository.save(child);

        DatasetLineage lineage = new DatasetLineage(
                parent,
                child,
                "REMOVE_DUPLICATES",
                null,
                10,
                "10 duplicate rows removed"
        );

        lineageRepository.save(lineage);

        DatasetLineage saved = (
                lineageRepository
                        .findByChildDataset(child)
                        .orElseThrow()
        );

        assertEquals(
                "REMOVE_DUPLICATES",
                saved.getOperation()
        );

        assertEquals(
                10,
                saved.getRowsAffected()
        );

        assertEquals(
                parent.getId(),
                saved.getParentDataset().getId()
        );

        List<DatasetLineage> children = (
                lineageRepository
                        .findByParentDatasetOrderByCreatedAtAsc(
                                parent
                        )
        );

        assertEquals(
                1,
                children.size()
        );

        assertEquals(
                child.getId(),
                children.get(0)
                        .getChildDataset()
                        .getId()
        );
    }
}
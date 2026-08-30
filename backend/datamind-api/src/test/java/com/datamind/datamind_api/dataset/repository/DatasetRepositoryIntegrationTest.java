package com.datamind.datamind_api.dataset.repository;

import com.datamind.datamind_api.dataset.entity.Dataset;
import jakarta.transaction.Transactional;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.dao.DataIntegrityViolationException;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertThrows;

@SpringBootTest
@Transactional
public class DatasetRepositoryIntegrationTest
{
    @Autowired
    private DatasetRepository datasetRepository;

    @Test
    void shouldEnforceUniqueContentHashAtDatabaseLevel()
    {
        String uniqueContentHash =
                "test-hash-" + UUID.randomUUID();

        Dataset firstDataset = new Dataset(
                "first.csv",
                uniqueContentHash,
                100L,
                "text/csv"
        );

        firstDataset.setStoragePath(
                "/test/first.csv"
        );

        Dataset secondDataset = new Dataset(
                "second.csv",
                uniqueContentHash,
                200L,
                "text/csv"
        );

        secondDataset.setStoragePath(
                "/test/second.csv"
        );

        datasetRepository.saveAndFlush(firstDataset);

        assertThrows(
                DataIntegrityViolationException.class,
                () -> datasetRepository.saveAndFlush(secondDataset)
        );
    }

}

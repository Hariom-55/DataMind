package com.datamind.datamind_api.dataset.service;

import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.repository.DatasetLineageRepository;
import com.datamind.datamind_api.dataset.repository.DatasetRepository;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class DatasetVersioning2Test {

    @Test
    void sameLogicalDatasetAndSameHashMustReturnExistingVersion() {
        DatasetRepository datasetRepository = mock(DatasetRepository.class);
        DatasetLineageRepository lineageRepository = mock(DatasetLineageRepository.class);
        DatasetService datasetService = mock(DatasetService.class);

        Dataset parent = new Dataset("customers.csv", "hash-v1", 100L, "text/csv");
        UUID logicalId = UUID.randomUUID();
        parent.setLogicalDatasetId(logicalId);
        parent.setVersionNumber(1);

        Dataset existing = new Dataset("customers.csv", "hash-v1", 100L, "text/csv");
        existing.setLogicalDatasetId(logicalId);
        existing.setVersionNumber(1);

        when(datasetRepository.findByLogicalDatasetIdAndContentHash(
                logicalId, "hash-v1"
        )).thenReturn(Optional.of(existing));

        DatasetVersionService service = new DatasetVersionService(
                datasetRepository,
                lineageRepository,
                datasetService
        );

        Dataset result = service.createVersion(
                parent,
                "customers.csv",
                "hash-v1",
                100L,
                "text/csv",
                "/data/hash-v1.csv",
                "CLEAN_DATASET",
                null,
                0,
                "No changes"
        );

        assertSame(existing, result);
        verify(datasetRepository, never()).save(any(Dataset.class));
        verifyNoInteractions(lineageRepository);
    }

    @Test
    void changedContentMustCreateNextVersionAndLineage() {
        DatasetRepository datasetRepository = mock(DatasetRepository.class);
        DatasetLineageRepository lineageRepository = mock(DatasetLineageRepository.class);
        DatasetService datasetService = mock(DatasetService.class);

        UUID logicalId = UUID.randomUUID();
        Dataset parent = new Dataset("customers.csv", "hash-v1", 100L, "text/csv");
        parent.setLogicalDatasetId(logicalId);
        parent.setVersionNumber(1);

        Dataset child = new Dataset("customers.csv", "hash-v2", 90L, "text/csv");
        child.setLogicalDatasetId(logicalId);
        child.setVersionNumber(2);

        when(datasetRepository.findByLogicalDatasetIdAndContentHash(
                logicalId, "hash-v2"
        )).thenReturn(Optional.empty());
        when(datasetRepository.findMaxVersionNumber(logicalId)).thenReturn(1);
        when(datasetRepository.save(any(Dataset.class))).thenReturn(child);
        when(datasetRepository.findLogicalDatasetRoot(logicalId))
                .thenReturn(Optional.empty());

        DatasetVersionService service = new DatasetVersionService(
                datasetRepository,
                lineageRepository,
                datasetService
        );

        Dataset result = service.createVersion(
                parent,
                "customers.csv",
                "hash-v2",
                90L,
                "text/csv",
                "/data/hash-v2.csv",
                "REMOVE_DUPLICATES",
                null,
                10,
                "10 duplicate rows removed"
        );

        assertSame(child, result);

        ArgumentCaptor<Dataset> datasetCaptor =
                ArgumentCaptor.forClass(Dataset.class);
        verify(datasetRepository).save(datasetCaptor.capture());
        assertEquals(2, datasetCaptor.getValue().getVersionNumber());
        assertEquals(logicalId, datasetCaptor.getValue().getLogicalDatasetId());

        verify(lineageRepository).save(any());
        verify(datasetService).pointRootToCurrentVersion(logicalId, child.getId());
    }
}

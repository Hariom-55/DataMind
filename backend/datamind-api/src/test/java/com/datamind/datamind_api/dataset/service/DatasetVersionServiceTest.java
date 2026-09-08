package com.datamind.datamind_api.dataset.service;

import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.entity.DatasetLineage;
import com.datamind.datamind_api.dataset.repository.DatasetLineageRepository;
import com.datamind.datamind_api.dataset.repository.DatasetRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class DatasetVersionServiceTest {

    @Mock
    private DatasetRepository datasetRepository;

    @Mock
    private DatasetLineageRepository lineageRepository;

    @InjectMocks
    private DatasetVersionService service;

    @Test
    void shouldCreateNewDatasetVersionAndRecordLineage() {

        Dataset parentDataset = new Dataset(
                "customers.csv",
                "parent-hash",
                100L,
                "text/csv"
        );

        parentDataset.setStoragePath(
                "/data/customers.csv"
        );

        Dataset childDataset = new Dataset(
                "customers_cleaned.csv",
                "child-hash",
                90L,
                "text/csv"
        );

        childDataset.setStoragePath(
                "/data/customers_cleaned.csv"
        );

        when(
                datasetRepository.save(any(Dataset.class))
        ).thenReturn(childDataset);

        Dataset result = service.createVersion(
                parentDataset,
                "customers_cleaned.csv",
                "child-hash",
                90L,
                "text/csv",
                "/data/customers_cleaned.csv",
                "REMOVE_DUPLICATES",
                null,
                10,
                "10 duplicate rows removed"
        );

        assertSame(
                childDataset,
                result
        );

        ArgumentCaptor<Dataset> datasetCaptor =
                ArgumentCaptor.forClass(Dataset.class);

        verify(
                datasetRepository
        ).save(datasetCaptor.capture());

        Dataset savedDataset =
                datasetCaptor.getValue();

        assertEquals(
                "customers_cleaned.csv",
                savedDataset.getName()
        );

        assertEquals(
                "child-hash",
                savedDataset.getContentHash()
        );

        assertEquals(
                90L,
                savedDataset.getFileSize()
        );

        assertEquals(
                "text/csv",
                savedDataset.getFileType()
        );

        assertEquals(
                "/data/customers_cleaned.csv",
                savedDataset.getStoragePath()
        );

        ArgumentCaptor<DatasetLineage> lineageCaptor =
                ArgumentCaptor.forClass(
                        DatasetLineage.class
                );

        verify(
                lineageRepository
        ).save(lineageCaptor.capture());

        DatasetLineage lineage =
                lineageCaptor.getValue();

        assertSame(
                parentDataset,
                lineage.getParentDataset()
        );

        assertSame(
                childDataset,
                lineage.getChildDataset()
        );

        assertEquals(
                "REMOVE_DUPLICATES",
                lineage.getOperation()
        );

        assertNull(
                lineage.getColumnName()
        );

        assertEquals(
                10,
                lineage.getRowsAffected()
        );

        assertEquals(
                "10 duplicate rows removed",
                lineage.getDetails()
        );
    }


    @Test
    void shouldNotModifyParentDataset() {

        Dataset parentDataset = new Dataset(
                "customers.csv",
                "parent-hash",
                100L,
                "text/csv"
        );

        parentDataset.setStoragePath(
                "/data/customers.csv"
        );

        Dataset childDataset = new Dataset(
                "customers_cleaned.csv",
                "child-hash",
                90L,
                "text/csv"
        );

        childDataset.setStoragePath(
                "/data/customers_cleaned.csv"
        );

        when(
                datasetRepository.save(any(Dataset.class))
        ).thenReturn(childDataset);

        service.createVersion(
                parentDataset,
                "customers_cleaned.csv",
                "child-hash",
                90L,
                "text/csv",
                "/data/customers_cleaned.csv",
                "REMOVE_DUPLICATES",
                null,
                10,
                "10 duplicate rows removed"
        );

        assertEquals(
                "customers.csv",
                parentDataset.getName()
        );

        assertEquals(
                "parent-hash",
                parentDataset.getContentHash()
        );

        assertEquals(
                100L,
                parentDataset.getFileSize()
        );

        assertEquals(
                "/data/customers.csv",
                parentDataset.getStoragePath()
        );
    }
}
package com.datamind.datamind_api.dataset.service;

import com.datamind.datamind_api.dataset.dto.DatasetLineageResponse;
import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.entity.DatasetLineage;
import com.datamind.datamind_api.dataset.exception.DatasetNotFoundException;
import com.datamind.datamind_api.dataset.repository.DatasetLineageRepository;
import com.datamind.datamind_api.dataset.repository.DatasetRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class DatasetLineageServiceTest {

    @Mock
    private DatasetRepository datasetRepository;

    @Mock
    private DatasetLineageRepository lineageRepository;

    @InjectMocks
    private DatasetLineageService service;

    @Test
    void shouldReturnEmptyLineageForOriginalDataset() {

        UUID datasetId = UUID.randomUUID();

        Dataset dataset = new Dataset(
                "customers.csv",
                "original-hash",
                100L,
                "text/csv"
        );

        when(
                datasetRepository.findById(datasetId)
        ).thenReturn(Optional.of(dataset));

        when(
                lineageRepository.findByChildDataset(dataset)
        ).thenReturn(Optional.empty());

        List<DatasetLineageResponse> result =
                service.getLineage(datasetId);

        assertTrue(result.isEmpty());

        verify(
                lineageRepository
        ).findByChildDataset(dataset);
    }

    @Test
    void shouldReturnSingleLineageEntry() {

        UUID datasetId = UUID.randomUUID();

        Dataset parent = new Dataset(
                "customers.csv",
                "parent-hash",
                100L,
                "text/csv"
        );

        Dataset child = new Dataset(
                "customers_cleaned.csv",
                "child-hash",
                90L,
                "text/csv"
        );

        when(
                datasetRepository.findById(datasetId)
        ).thenReturn(Optional.of(child));

        DatasetLineage lineage =
                new DatasetLineage(
                        parent,
                        child,
                        "REMOVE_DUPLICATES",
                        null,
                        10,
                        "10 duplicate rows removed"
                );

        when(
                lineageRepository.findByChildDataset(child)
        ).thenReturn(
                Optional.of(lineage)
        );

        when(
                lineageRepository.findByChildDataset(parent)
        ).thenReturn(
                Optional.empty()
        );

        List<DatasetLineageResponse> result =
                service.getLineage(datasetId);

        assertEquals(1, result.size());

        DatasetLineageResponse response =
                result.get(0);

        assertEquals(
                child.getId(),
                response.datasetId()
        );

        assertEquals(
                parent.getId(),
                response.parentDatasetId()
        );

        assertEquals(
                "REMOVE_DUPLICATES",
                response.operation()
        );

        assertEquals(
                10,
                response.rowsAffected()
        );

        assertEquals(
                "10 duplicate rows removed",
                response.details()
        );
    }

    @Test
    void shouldReturnLineageInChronologicalOrder() {

        UUID datasetId = UUID.randomUUID();

        Dataset original = new Dataset(
                "customers.csv",
                "hash-original",
                100L,
                "text/csv"
        );

        Dataset versionOne = new Dataset(
                "customers_v1.csv",
                "hash-v1",
                95L,
                "text/csv"
        );

        Dataset versionTwo = new Dataset(
                "customers_v2.csv",
                "hash-v2",
                90L,
                "text/csv"
        );

        DatasetLineage firstTransformation =
                new DatasetLineage(
                        original,
                        versionOne,
                        "REMOVE_DUPLICATES",
                        null,
                        5,
                        "5 duplicate rows removed"
                );

        DatasetLineage secondTransformation =
                new DatasetLineage(
                        versionOne,
                        versionTwo,
                        "IMPUTE_MISSING_VALUES",
                        "age",
                        10,
                        "10 missing values imputed"
                );

        when(
                datasetRepository.findById(datasetId)
        ).thenReturn(
                Optional.of(versionTwo)
        );

        when(
                lineageRepository.findByChildDataset(
                        versionTwo
                )
        ).thenReturn(
                Optional.of(secondTransformation)
        );

        when(
                lineageRepository.findByChildDataset(
                        versionOne
                )
        ).thenReturn(
                Optional.of(firstTransformation)
        );

        when(
                lineageRepository.findByChildDataset(
                        original
                )
        ).thenReturn(
                Optional.empty()
        );

        List<DatasetLineageResponse> result =
                service.getLineage(datasetId);

        assertEquals(2, result.size());

        assertEquals(
                "REMOVE_DUPLICATES",
                result.get(0).operation()
        );

        assertEquals(
                "IMPUTE_MISSING_VALUES",
                result.get(1).operation()
        );

        assertEquals(
                original.getId(),
                result.get(0).parentDatasetId()
        );

        assertEquals(
                versionOne.getId(),
                result.get(0).datasetId()
        );

        assertEquals(
                versionOne.getId(),
                result.get(1).parentDatasetId()
        );

        assertEquals(
                versionTwo.getId(),
                result.get(1).datasetId()
        );
    }

    @Test
    void shouldThrowExceptionWhenDatasetDoesNotExist() {

        UUID datasetId = UUID.randomUUID();

        when(
                datasetRepository.findById(datasetId)
        ).thenReturn(Optional.empty());

        DatasetNotFoundException exception =
                assertThrows(
                        DatasetNotFoundException.class,
                        () -> service.getLineage(datasetId)
                );

        assertEquals(
                "Dataset not found: " + datasetId,
                exception.getMessage()
        );

        verifyNoInteractions(
                lineageRepository
        );
    }
}


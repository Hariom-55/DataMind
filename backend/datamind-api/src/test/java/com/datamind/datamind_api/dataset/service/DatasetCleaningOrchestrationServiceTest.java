package com.datamind.datamind_api.dataset.service;

import com.datamind.datamind_api.analysis.integration.python.PythonCleaningClient;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningChange;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningOperation;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningResponse;
import com.datamind.datamind_api.dataset.entity.Dataset;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.List;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;


@ExtendWith(MockitoExtension.class)
class DatasetCleaningOrchestrationServiceTest
{
    @Mock
    private PythonCleaningClient pythonCleaningClient;

    @Mock
    private DatasetStorageService datasetStorageService;

    @Mock
    private DatasetVersionService datasetVersionService;

    private DatasetCleaningOrchestrationService service;


    private Dataset parentDataset;

    @BeforeEach
    void setUp()
    {
        service = new DatasetCleaningOrchestrationService(
                pythonCleaningClient,
                datasetStorageService,
                datasetVersionService
        );

        parentDataset = new Dataset(
                "customers.csv",
                "original-hash",
                100L,
                "text/csv"
        );

        parentDataset.setStoragePath(
                "data/datasets/original-hash.csv"
        );
    }


    @Test
    void shouldCleanDatasetAndCreateVersion()
    {
        UUID datasetId = parentDataset.getId();

        List<PythonCleaningOperation> operations =
                List.of(
                        new PythonCleaningOperation(
                                "IMPUTE_MISSING_VALUES",
                                "age"
                        )
                );

        byte[] cleanedContent =
                "name,age\nHariom,22\nRahul,24\n"
                        .getBytes(StandardCharsets.UTF_8);

        String encodedContent =
                Base64.getEncoder()
                        .encodeToString(cleanedContent);

        PythonCleaningResponse response =
                new PythonCleaningResponse(
                        encodedContent,
                        "cleaned-hash",
                        "csv",
                        3,
                        3,
                        2,
                        2,
                        1,
                        List.of(
                                new PythonCleaningChange(
                                        "IMPUTE_MISSING_VALUES",
                                        "age",
                                        1,
                                        "1 missing value imputed"
                                )
                        )
                );

        Dataset cleanedDataset = new Dataset(
                "customers.csv_cleaned",
                "cleaned-hash",
                (long) cleanedContent.length,
                "csv"
        );

        cleanedDataset.setStoragePath(
                "data/datasets/cleaned-hash.csv"
        );

        when(pythonCleaningClient.clean(
                datasetId,
                parentDataset.getStoragePath(),
                operations,
                "csv"
        )).thenReturn(response);

        when(datasetStorageService.storeBytes(
                cleanedContent,
                "cleaned-hash",
                "csv"
        )).thenReturn(
                "data/datasets/cleaned-hash.csv"
        );

        when(datasetVersionService.createVersion(
                eq(parentDataset),
                eq("customers.csv_cleaned"),
                eq("cleaned-hash"),
                eq((long) cleanedContent.length),
                eq("csv"),
                eq("data/datasets/cleaned-hash.csv"),
                anyString(),
                isNull(),
                eq(1),
                anyString()
        )).thenReturn(cleanedDataset);

        Dataset result =
                service.cleanDataset(
                        parentDataset,
                        operations
                );

        assertNotNull(result);
        assertEquals(
                "cleaned-hash",
                result.getContentHash()
        );

        assertEquals(
                "data/datasets/cleaned-hash.csv",
                result.getStoragePath()
        );

        verify(pythonCleaningClient).clean(
                datasetId,
                parentDataset.getStoragePath(),
                operations,
                "csv"
        );

        verify(datasetStorageService).storeBytes(
                cleanedContent,
                "cleaned-hash",
                "csv"
        );

        verify(datasetVersionService).createVersion(
                eq(parentDataset),
                eq("customers.csv_cleaned"),
                eq("cleaned-hash"),
                eq((long) cleanedContent.length),
                eq("csv"),
                eq("data/datasets/cleaned-hash.csv"),
                eq("IMPUTE_MISSING_VALUES"),
                isNull(),
                eq(1),
                contains("1 missing value imputed")
        );
    }


    @Test
    void shouldAggregateRowsAffectedFromMultipleChanges()
    {
        List<PythonCleaningOperation> operations =
                List.of(
                        new PythonCleaningOperation(
                                "NORMALIZE_CATEGORIES",
                                "city"
                        ),
                        new PythonCleaningOperation(
                                "IMPUTE_MISSING_VALUES",
                                "age"
                        )
                );

        byte[] cleanedContent =
                "city,age\nDelhi,22\nMumbai,24\n"
                        .getBytes(StandardCharsets.UTF_8);

        String encodedContent =
                Base64.getEncoder()
                        .encodeToString(cleanedContent);

        PythonCleaningResponse response =
                new PythonCleaningResponse(
                        encodedContent,
                        "multi-cleaned-hash",
                        "csv",
                        20,
                        20,
                        4,
                        4,
                        2,
                        List.of(
                                new PythonCleaningChange(
                                        "NORMALIZE_CATEGORIES",
                                        "city",
                                        3,
                                        "3 categorical values normalized"
                                ),
                                new PythonCleaningChange(
                                        "IMPUTE_MISSING_VALUES",
                                        "age",
                                        2,
                                        "2 missing values imputed"
                                )
                        )
                );

        Dataset cleanedDataset = new Dataset(
                "customers.csv_cleaned",
                "multi-cleaned-hash",
                (long) cleanedContent.length,
                "csv"
        );

        when(pythonCleaningClient.clean(
                any(),
                anyString(),
                eq(operations),
                eq("csv")
        )).thenReturn(response);

        when(datasetStorageService.storeBytes(
                cleanedContent,
                "multi-cleaned-hash",
                "csv"
        )).thenReturn(
                "data/datasets/multi-cleaned-hash.csv"
        );

        when(datasetVersionService.createVersion(
                any(),
                anyString(),
                eq("multi-cleaned-hash"),
                anyLong(),
                eq("csv"),
                anyString(),
                eq("NORMALIZE_CATEGORIES,IMPUTE_MISSING_VALUES"),
                isNull(),
                eq(5),
                anyString()
        )).thenReturn(cleanedDataset);

        Dataset result =
                service.cleanDataset(
                        parentDataset,
                        operations
                );

        assertNotNull(result);

        verify(datasetVersionService).createVersion(
                eq(parentDataset),
                eq("customers.csv_cleaned"),
                eq("multi-cleaned-hash"),
                eq((long) cleanedContent.length),
                eq("csv"),
                eq("data/datasets/multi-cleaned-hash.csv"),
                eq("NORMALIZE_CATEGORIES,IMPUTE_MISSING_VALUES"),
                isNull(),
                eq(5),
                anyString()
        );
    }


    @Test
    void shouldCreateGenericOperationWhenNoChangesAreReturned()
    {
        List<PythonCleaningOperation> operations =
                List.of();

        byte[] cleanedContent =
                "name,age\nHariom,22\n"
                        .getBytes(StandardCharsets.UTF_8);

        String encodedContent =
                Base64.getEncoder()
                        .encodeToString(cleanedContent);

        PythonCleaningResponse response =
                new PythonCleaningResponse(
                        encodedContent,
                        "unchanged-hash",
                        "csv",
                        1,
                        1,
                        2,
                        2,
                        0,
                        List.of()
                );

        Dataset cleanedDataset = new Dataset(
                "customers.csv_cleaned",
                "unchanged-hash",
                (long) cleanedContent.length,
                "csv"
        );

        when(pythonCleaningClient.clean(
                any(),
                anyString(),
                eq(operations),
                eq("csv")
        )).thenReturn(response);

        when(datasetStorageService.storeBytes(
                cleanedContent,
                "unchanged-hash",
                "csv"
        )).thenReturn(
                "data/datasets/unchanged-hash.csv"
        );

        when(datasetVersionService.createVersion(
                any(),
                anyString(),
                eq("unchanged-hash"),
                anyLong(),
                eq("csv"),
                anyString(),
                eq("CLEAN_DATASET"),
                isNull(),
                eq(0),
                eq("Cleaning completed with no recorded changes")
        )).thenReturn(cleanedDataset);

        Dataset result =
                service.cleanDataset(
                        parentDataset,
                        operations
                );

        assertNotNull(result);

        verify(datasetVersionService).createVersion(
                eq(parentDataset),
                eq("customers.csv_cleaned"),
                eq("unchanged-hash"),
                eq((long) cleanedContent.length),
                eq("csv"),
                eq("data/datasets/unchanged-hash.csv"),
                eq("CLEAN_DATASET"),
                isNull(),
                eq(0),
                eq("Cleaning completed with no recorded changes")
        );
    }


    @Test
    void shouldThrowExceptionWhenPythonCleaningFails()
    {
        List<PythonCleaningOperation> operations =
                List.of(
                        new PythonCleaningOperation(
                                "REMOVE_DUPLICATES",
                                null
                        )
                );

        when(pythonCleaningClient.clean(
                any(),
                anyString(),
                eq(operations),
                eq("csv")
        )).thenThrow(
                new RuntimeException(
                        "Python cleaning service failed"
                )
        );

        RuntimeException exception =
                assertThrows(
                        RuntimeException.class,
                        () -> service.cleanDataset(
                                parentDataset,
                                operations
                        )
                );

        assertEquals(
                "Python cleaning service failed",
                exception.getMessage()
        );

        verify(datasetStorageService, never())
                .storeBytes(
                        any(),
                        anyString(),
                        anyString()
                );

        verify(datasetVersionService, never())
                .createVersion(
                        any(),
                        anyString(),
                        anyString(),
                        anyLong(),
                        anyString(),
                        anyString(),
                        anyString(),
                        any(),
                        any(),
                        anyString()
                );
    }


    @Test
    void shouldRejectInvalidBase64Content()
    {
        List<PythonCleaningOperation> operations =
                List.of(
                        new PythonCleaningOperation(
                                "REMOVE_DUPLICATES",
                                null
                        )
                );

        PythonCleaningResponse response =
                new PythonCleaningResponse(
                        "NOT_VALID_BASE64!!!",
                        "invalid-hash",
                        "csv",
                        3,
                        2,
                        2,
                        2,
                        1,
                        List.of(
                                new PythonCleaningChange(
                                        "REMOVE_DUPLICATES",
                                        null,
                                        1,
                                        "1 duplicate row removed"
                                )
                        )
                );

        when(pythonCleaningClient.clean(
                any(),
                anyString(),
                eq(operations),
                eq("csv")
        )).thenReturn(response);

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> service.cleanDataset(
                                parentDataset,
                                operations
                        )
                );

        assertEquals(
                "Invalid Base64 content returned by Python cleaning service",
                exception.getMessage()
        );

        verify(datasetStorageService, never())
                .storeBytes(
                        any(),
                        anyString(),
                        anyString()
                );

        verify(datasetVersionService, never())
                .createVersion(
                        any(),
                        anyString(),
                        anyString(),
                        anyLong(),
                        anyString(),
                        anyString(),
                        anyString(),
                        any(),
                        any(),
                        anyString()
                );
    }

    @Test
    void shouldNotCreateNewDatasetVersionWhenCleaningProducesSameContent() {
        UUID datasetId =
                UUID.fromString(
                        "11111111-1111-1111-1111-111111111111"
                );

        Dataset parentDataset = new Dataset(
                "customers.csv",
                "same-content-hash",
                100L,
                "text/csv"
        );

        parentDataset.setStoragePath(
                "C:\\temp\\customers.csv"
        );

        PythonCleaningResponse response =
                new PythonCleaningResponse(
                        "dGVzdA==",
                        "same-content-hash",
                        "csv",
                        3,
                        3,
                        3,
                        3,
                        0,
                        List.of()
                );

        List<PythonCleaningOperation> operations =
                List.of(
                        new PythonCleaningOperation(
                                "IMPUTE_MISSING_VALUES",
                                "age"
                        )
                );

        when(
                pythonCleaningClient.clean(
                        isNull(),
                        eq("C:\\temp\\customers.csv"),
                        eq(operations),
                        eq("csv")
                )
        ).thenReturn(response);

        Dataset result =
                service.cleanDataset(
                        parentDataset,
                        operations
                );

        assertSame(
                parentDataset,
                result
        );

        verify(datasetStorageService, never())
                .storeBytes(
                        any(),
                        anyString(),
                        anyString()
                );

        verify(datasetVersionService, never())
                .createVersion(
                        any(),
                        anyString(),
                        anyString(),
                        anyLong(),
                        anyString(),
                        anyString(),
                        anyString(),
                        any(),
                        anyInt(),
                        anyString()
                );
    }
}
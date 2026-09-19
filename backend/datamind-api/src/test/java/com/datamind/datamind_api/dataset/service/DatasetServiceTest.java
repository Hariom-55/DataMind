package com.datamind.datamind_api.dataset.service;

import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.repository.DatasetRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.util.unit.DataSize;
import org.springframework.web.multipart.MultipartFile;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

class DatasetServiceTest {
    @Mock
    private DatasetRepository datasetRepository;

    @Mock
    private DatasetStorageService datasetStorageService;

    private DatasetService datasetService;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        datasetService = new DatasetService(
                datasetRepository,
                datasetStorageService,
                DataSize.ofMegabytes(50),
                "csv,xlsx,xls,json,parquet"
        );
    }

    @Test
    void shouldUploadDataset() {
        MultipartFile file = new MockMultipartFile(
                "file", "customers.csv", "text/csv", "name,age\nHariom,22".getBytes()
        );

        when(datasetRepository.findByContentHash(anyString())).thenReturn(Optional.empty());
        when(datasetStorageService.store(eq(file), anyString())).thenReturn("./data/abc123.csv");
        when(datasetRepository.save(any(Dataset.class))).thenAnswer(invocation -> invocation.getArgument(0));

        Dataset result = datasetService.uploadDataset(file);

        assertNotNull(result);
        assertEquals("customers.csv", result.getName());
        assertEquals("text/csv", result.getFileType());
        assertEquals(file.getSize(), result.getFileSize());
        assertEquals("./data/abc123.csv", result.getStoragePath());
        assertNotNull(result.getContentHash());
        verify(datasetStorageService).store(file, result.getContentHash());
        verify(datasetRepository).save(result);
    }

    @Test
    void shouldReturnExistingDatasetOnDuplicateUpload() {
        MultipartFile file = new MockMultipartFile(
                "file", "customer.csv", "text/csv", "name,age\nHariom,22".getBytes()
        );
        Dataset existingDataset = mock(Dataset.class);
        when(datasetRepository.findByContentHash(anyString())).thenReturn(Optional.of(existingDataset));

        assertSame(existingDataset, datasetService.uploadDataset(file));
        verify(datasetStorageService, never()).store(any(), anyString());
        verify(datasetRepository, never()).save(any());
    }

    @Test
    void shouldRecoverFromRaceConditionOnConcurrentInsert() {
        MultipartFile file = new MockMultipartFile(
                "file", "customer.csv", "text/csv", "name,age\nHariom,22".getBytes()
        );
        Dataset existingDataset = mock(Dataset.class);
        when(datasetRepository.findByContentHash(anyString()))
                .thenReturn(Optional.empty(), Optional.of(existingDataset));
        when(datasetStorageService.store(eq(file), anyString())).thenReturn("./data/abc123.csv");
        when(datasetRepository.save(any(Dataset.class)))
                .thenThrow(new DataIntegrityViolationException("Duplicate content hash"));

        assertSame(existingDataset, datasetService.uploadDataset(file));
        verify(datasetRepository, times(2)).findByContentHash(anyString());
    }

    @Test
    void shouldRejectNullFile() {
        IllegalArgumentException exception = assertThrows(
                IllegalArgumentException.class,
                () -> datasetService.uploadDataset(null)
        );
        assertEquals("Dataset file is required", exception.getMessage());
        verifyNoInteractions(datasetRepository, datasetStorageService);
    }

    @Test
    void shouldRejectEmptyFile() {
        MultipartFile file = new MockMultipartFile(
                "file", "customer.csv", "text/csv", new byte[0]
        );

        IllegalArgumentException exception = assertThrows(
                IllegalArgumentException.class,
                () -> datasetService.uploadDataset(file)
        );
        assertEquals("Dataset file is required", exception.getMessage());
    }

    @Test
    void shouldRejectMissingFilename() {
        MultipartFile file = new MockMultipartFile(
                "file", null, "text/csv", "name,age\nHariom,22".getBytes()
        );

        IllegalArgumentException exception = assertThrows(
                IllegalArgumentException.class,
                () -> datasetService.uploadDataset(file)
        );
        assertEquals("Dataset file name is required", exception.getMessage());
    }

    @Test
    void shouldRejectUnsupportedExtension() {
        MultipartFile file = new MockMultipartFile(
                "file", "customers.exe", "application/octet-stream", "data".getBytes()
        );

        IllegalArgumentException exception = assertThrows(
                IllegalArgumentException.class,
                () -> datasetService.uploadDataset(file)
        );
        assertEquals("Unsupported dataset file type: exe", exception.getMessage());
        verifyNoInteractions(datasetRepository, datasetStorageService);
    }

    @Test
    void shouldRejectFilenameWithPathTraversal() {
        MultipartFile file = new MockMultipartFile(
                "file", "../customers.csv", "text/csv", "data".getBytes()
        );

        IllegalArgumentException exception = assertThrows(
                IllegalArgumentException.class,
                () -> datasetService.uploadDataset(file)
        );
        assertEquals("Dataset file name contains an invalid path", exception.getMessage());
        verifyNoInteractions(datasetRepository, datasetStorageService);
    }

    @Test
    void shouldRejectFilenameWithNullCharacter() {
        MultipartFile file = new MockMultipartFile(
                "file", "customers\0.csv", "text/csv", "data".getBytes()
        );

        IllegalArgumentException exception = assertThrows(
                IllegalArgumentException.class,
                () -> datasetService.uploadDataset(file)
        );
        assertEquals("Dataset file name contains an invalid character", exception.getMessage());
    }

    @Test
    void shouldRejectFileLargerThanConfiguredLimit() {
        DatasetService smallLimitService = new DatasetService(
                datasetRepository,
                datasetStorageService,
                DataSize.ofBytes(3),
                "csv"
        );
        MultipartFile file = new MockMultipartFile(
                "file", "customers.csv", "text/csv", "1234".getBytes()
        );

        IllegalArgumentException exception = assertThrows(
                IllegalArgumentException.class,
                () -> smallLimitService.uploadDataset(file)
        );
        assertTrue(exception.getMessage().contains("maximum allowed size"));
        verifyNoInteractions(datasetRepository, datasetStorageService);
    }

    @Test
    void shouldDefaultFileTypeWhenContentTypeIsNull() {
        MultipartFile file = new MockMultipartFile(
                "file", "customers.csv", null, "name,age\nHariom,22".getBytes()
        );
        when(datasetRepository.findByContentHash(anyString())).thenReturn(Optional.empty());
        when(datasetStorageService.store(any(MultipartFile.class), anyString())).thenReturn("./data/abc123.csv");
        when(datasetRepository.save(any(Dataset.class))).thenAnswer(invocation -> invocation.getArgument(0));

        Dataset result = datasetService.uploadDataset(file);

        assertEquals("application/octet-stream", result.getFileType());
    }
}
